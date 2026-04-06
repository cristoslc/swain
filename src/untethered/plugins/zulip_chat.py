"""Zulip chat adapter plugin — subprocess entry point.

Spawned by the host kernel (ADR-038). Communicates via NDJSON over stdio:
  stdin line 0 : ConfigMessage from kernel (Zulip credentials + routing maps)
  stdin lines 1+: Events from kernel to post to Zulip
  stdout lines  : Commands to kernel from operator Zulip messages
  stderr        : logs (never mixed into stdout protocol stream)

Thread ownership
----------------
Each session gets its own Zulip topic (thread). The SessionTopicRegistry
owns the assignment:
  - Prefer the artifact name as topic if the topic is not already occupied
    by another active session.
  - Fall back to session_id if the artifact topic is occupied or absent.
  - On session_spawned: create the topic (first post), announce in control.
  - On session_died: post closure to session topic + control, release slot.
  - On operator messages: resolve topic → session_id so the kernel routes
    to the right project bridge session.
"""
from __future__ import annotations

import asyncio
import logging
import sys
from typing import Callable

import zulip

from untethered.protocol import (
    Event, Command, ConfigMessage,
    decode_message, encode_message,
)
from untethered.adapters.zulip_chat import format_event_for_zulip, parse_zulip_message

log = logging.getLogger("untethered.plugins.zulip_chat")


# ---------------------------------------------------------------------------
# Session → topic registry
# ---------------------------------------------------------------------------

class SessionTopicRegistry:
    """Tracks which Zulip topic belongs to each active session.

    Rules:
    - Prefer artifact name as topic (human-readable, matches spec/epic IDs).
    - If the artifact topic is already occupied by another active session,
      fall back to session_id.
    - Reverse lookup (topic → session_id) lets _poll_zulip translate
      incoming operator messages to the correct session.
    """

    def __init__(self) -> None:
        self._session_to_topic: dict[str, str] = {}
        self._topic_to_session: dict[str, str] = {}

    def assign(self, session_id: str, artifact: str | None) -> str:
        """Assign a topic to a session. Returns the topic name.

        If the session already has a topic (reconnect), returns it unchanged.
        """
        if session_id in self._session_to_topic:
            return self._session_to_topic[session_id]

        candidate = artifact or session_id
        if candidate != session_id and candidate in self._topic_to_session:
            # Artifact topic occupied by another active session — use session_id
            candidate = session_id

        self._session_to_topic[session_id] = candidate
        self._topic_to_session[candidate] = session_id
        log.info("Session %s assigned to topic %r", session_id, candidate)
        return candidate

    def release(self, session_id: str) -> str | None:
        """Remove a session from the registry. Returns its topic name."""
        topic = self._session_to_topic.pop(session_id, None)
        if topic:
            self._topic_to_session.pop(topic, None)
        return topic

    def topic_for(self, session_id: str) -> str | None:
        return self._session_to_topic.get(session_id)

    def session_for_topic(self, topic: str) -> str | None:
        return self._topic_to_session.get(topic)


# ---------------------------------------------------------------------------
# stdout emitter
# ---------------------------------------------------------------------------

def _emit(cmd: Command) -> None:
    """Write a Command as NDJSON to stdout (to the kernel)."""
    sys.stdout.write(encode_message(cmd))
    sys.stdout.flush()


# ---------------------------------------------------------------------------
# Zulip → kernel: poll for operator messages
# ---------------------------------------------------------------------------

async def _poll_zulip(
    client: zulip.Client,
    stream_to_project: dict[str, str],
    control_topic: str,
    emit: Callable[[Command], None],
    registry: SessionTopicRegistry,
    loop: asyncio.AbstractEventLoop,
) -> None:
    """Long-poll Zulip for operator messages, emit Commands to kernel via stdout."""

    async def _register() -> tuple[str, int]:
        result = await loop.run_in_executor(
            None,
            lambda: client.register(
                event_types=["message"],
                narrow=[["is", "stream"]],
            ),
        )
        if result.get("result") != "success":
            raise RuntimeError(f"Zulip register failed: {result}")
        log.info("Zulip event queue: %s", result["queue_id"])
        return result["queue_id"], result["last_event_id"]

    try:
        queue_id, last_event_id = await _register()
    except Exception as exc:
        log.error("Cannot start Zulip polling: %s", exc)
        return

    while True:
        log.debug("Polling (queue=%s, last_id=%s)", queue_id, last_event_id)
        try:
            result = await loop.run_in_executor(
                None,
                lambda: client.get_events(
                    queue_id=queue_id,
                    last_event_id=last_event_id,
                ),
            )
        except Exception as exc:
            log.error("Zulip poll error: %s", exc)
            await asyncio.sleep(5)
            continue
        log.debug("Poll returned: %s events", len(result.get("events", [])))

        if result.get("code") == "BAD_EVENT_QUEUE_ID":
            log.warning("Zulip queue expired, re-registering")
            try:
                queue_id, last_event_id = await _register()
            except Exception as exc:
                log.error("Re-registration failed: %s", exc)
                await asyncio.sleep(5)
            continue

        if result.get("result") != "success":
            log.warning("Zulip events error: %s", result)
            await asyncio.sleep(5)
            continue

        for ev in result.get("events", []):
            last_event_id = max(last_event_id, ev.get("id", last_event_id))
            if ev.get("type") != "message":
                continue
            message = ev.get("message", {})
            if message.get("sender_email") == client.email:
                continue

            stream_name = message.get("display_recipient", "")
            bridge = stream_to_project.get(stream_name, stream_name)
            cmd = parse_zulip_message(
                message, bridge=bridge or "", control_topic=control_topic,
            )
            if not cmd:
                continue

            # Resolve Zulip topic → session_id. When the operator writes in
            # topic "SPEC-142", we need to route to the session assigned there,
            # not treat "SPEC-142" as a literal session_id.
            if cmd.session_id and cmd.session_id != control_topic:
                resolved = registry.session_for_topic(cmd.session_id)
                if resolved:
                    cmd.session_id = resolved

            emit(cmd)


# ---------------------------------------------------------------------------
# Kernel → Zulip: relay events to the correct thread
# ---------------------------------------------------------------------------

async def _relay_events(
    client: zulip.Client,
    project_to_stream: dict[str, str],
    operator_email: str | None,
    control_topic: str,
    registry: SessionTopicRegistry,
    loop: asyncio.AbstractEventLoop,
) -> None:
    """Read Events from stdin (kernel), post them to the correct Zulip thread."""

    async def _post(stream: str, topic: str, content: str) -> None:
        await loop.run_in_executor(
            None,
            lambda: client.send_message({
                "type": "stream",
                "to": stream,
                "topic": topic,
                "content": content,
            }),
        )

    mention = f"@**{operator_email}** " if operator_email else ""

    while True:
        line = await loop.run_in_executor(None, sys.stdin.readline)
        if not line:
            log.info("stdin closed")
            return
        msg = decode_message(line)
        if not isinstance(msg, Event):
            continue

        stream = project_to_stream.get(msg.bridge or "", msg.bridge or "")
        session_id = msg.session_id or ""
        origin = msg.payload.get("origin")

        # --- Control-origin sessions: all output goes to control topic ---
        if origin == "control":
            if msg.type == "session_spawned":
                # Silently track — no announcement needed
                pass
            elif msg.type == "session_died":
                # Silent cleanup — no "session ended" noise
                pass
            else:
                # Post content directly to control topic
                zulip_msg = format_event_for_zulip(
                    msg,
                    operator_email=operator_email,
                    control_topic=control_topic,
                )
                await _post(stream, control_topic, zulip_msg["content"])
            continue

        # --- Session promoted: interview complete, create the thread ---
        if msg.type == "session_promoted":
            artifact = msg.payload.get("artifact", "")
            topic = registry.assign(session_id, artifact or None)
            suffix = f" on `{artifact}`" if artifact else ""

            # Create the session thread
            await _post(stream, topic, f"Session started{suffix}.")

            # Announce in control so the operator can find the thread
            await _post(
                stream, control_topic,
                f"{mention}Session ready in topic **{topic}**{suffix}. "
                f"Reply there to interact or use `/cancel` to stop.",
            )
            continue

        # --- Regular sessions: dedicated thread per session ---
        if msg.type == "session_spawned":
            artifact = msg.payload.get("artifact")
            topic = registry.assign(session_id, artifact)
            suffix = f" on `{artifact}`" if artifact else ""
            runtime = msg.payload.get("runtime", "claude")

            # Create the session thread with its opening post
            await _post(stream, topic, f"Session started ({runtime}){suffix}.")

            # Announce in control so the operator can find the thread
            await _post(
                stream, control_topic,
                f"{mention}New session in topic **{topic}**{suffix}. "
                f"Reply there to interact or use `/cancel` to stop.",
            )

        elif msg.type == "session_died":
            topic = registry.release(session_id) or session_id
            reason = msg.payload.get("reason", "unknown")
            await _post(stream, topic, f"Session ended: {reason}.")
            await _post(
                stream, control_topic,
                f"Session **{topic}** ended: {reason}.",
            )

        else:
            # All other events: post to the session's registered topic.
            # Skip if we have no record — the session may have been started
            # before this bridge instance came up.
            topic = registry.topic_for(session_id)
            if not topic:
                log.warning(
                    "Event for unregistered session %r (type: %s) — dropping",
                    session_id, msg.type,
                )
                continue
            zulip_msg = format_event_for_zulip(
                msg,
                operator_email=operator_email,
                control_topic=control_topic,
            )
            await _post(stream, topic, zulip_msg["content"])


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def _amain() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        stream=sys.stderr,
    )
    loop = asyncio.get_running_loop()

    config_line = await loop.run_in_executor(None, sys.stdin.readline)
    config_msg = decode_message(config_line)
    if not isinstance(config_msg, ConfigMessage):
        log.error("Expected ConfigMessage on stdin line 0, got: %r", config_line[:100])
        sys.exit(1)

    cfg = config_msg.config
    client = zulip.Client(
        email=cfg["bot_email"],
        api_key=cfg["bot_api_key"],
        site=cfg["server_url"],
    )

    registry = SessionTopicRegistry()

    await asyncio.gather(
        _poll_zulip(
            client,
            cfg.get("stream_to_project", {}),
            cfg.get("control_topic", "control"),
            _emit,
            registry,
            loop,
        ),
        _relay_events(
            client,
            cfg.get("project_to_stream", {}),
            cfg.get("operator_email"),
            cfg.get("control_topic", "control"),
            registry,
            loop,
        ),
    )


def main() -> None:
    asyncio.run(_amain())


if __name__ == "__main__":
    main()
