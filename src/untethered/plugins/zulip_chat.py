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
from typing import Any, Callable

import zulip

from untethered.protocol import (
    Event,
    Command,
    ConfigMessage,
    decode_message,
    encode_message,
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
    """Poll Zulip for operator messages using the SDK's call_on_each_message.

    Runs the blocking SDK poll in a thread. The SDK handles registration,
    heartbeats, re-registration on BAD_EVENT_QUEUE_ID, and error backoff.

    Messages are filtered so only streams matching configured projects are processed.
    This prevents worktree bridges from processing messages intended for trunk.
    """

    seen_ids: set[int] = set()

    def _on_message(message: dict) -> None:
        """Called by the SDK for each incoming message (in a worker thread)."""
        msg_id = message.get("id")
        if msg_id in seen_ids:
            return
        if msg_id is not None:
            seen_ids.add(msg_id)
            # Keep the set bounded
            if len(seen_ids) > 1000:
                seen_ids.clear()

        if message.get("sender_email") == client.email:
            return

        stream_name = message.get("display_recipient", "")

        # Filter: only process messages from streams matching configured projects.
        # This prevents worktree bridges from processing trunk messages (and vice versa).
        if stream_name not in stream_to_project:
            log.debug("Ignoring message from unconfigured stream: %s", stream_name)
            return

        bridge = stream_to_project[stream_name]
        cmd = parse_zulip_message(
            message,
            bridge=bridge or "",
            control_topic=control_topic,
        )
        if not cmd:
            return

        # Resolve Zulip topic → session_id.
        if cmd.session_id and cmd.session_id != control_topic:
            resolved = registry.session_for_topic(cmd.session_id)
            if resolved:
                cmd.session_id = resolved

        log.info("Zulip message → %s (bridge=%s)", cmd.type, cmd.bridge)
        emit(cmd)

    log.info("Starting Zulip message poll...")
    await loop.run_in_executor(
        None,
        lambda: client.call_on_each_message(_on_message),
    )


# ---------------------------------------------------------------------------
# Text output batcher — coalesce rapid-fire lines into single posts
# ---------------------------------------------------------------------------


class TypingIndicator:
    """Sends Zulip typing indicators while a session is working.

    Pulses 'start' every 10s. Stops when output arrives or session dies.
    Uses the Zulip set-typing-status API for stream/topic typing.
    """

    def __init__(self, client: Any, loop: asyncio.AbstractEventLoop) -> None:
        self._client = client
        self._loop = loop
        self._active: dict[tuple[str, str], asyncio.Task] = {}

    def start(self, stream: str, topic: str) -> None:
        """Begin typing indicator for a stream/topic."""
        key = (stream, topic)
        if key in self._active:
            return
        self._active[key] = self._loop.create_task(self._pulse(stream, topic))

    def stop(self, stream: str, topic: str) -> None:
        """Stop typing indicator for a stream/topic."""
        key = (stream, topic)
        task = self._active.pop(key, None)
        if task:
            task.cancel()
        self._send_typing(stream, topic, "stop")

    def stop_all(self) -> None:
        for key in list(self._active):
            self.stop(*key)

    async def _pulse(self, stream: str, topic: str) -> None:
        """Send typing start every 10s until cancelled."""
        try:
            while True:
                self._send_typing(stream, topic, "start")
                await asyncio.sleep(10)
        except asyncio.CancelledError:
            pass

    def _send_typing(self, stream: str, topic: str, op: str) -> None:
        try:
            # Get stream ID from name
            result = self._client.get_stream_id(stream)
            stream_id = result.get("stream_id")
            if stream_id:
                self._client.set_typing_status(
                    {
                        "op": op,
                        "type": "stream",
                        "stream_id": stream_id,
                        "topic": topic,
                    }
                )
        except Exception as exc:
            log.debug("Typing indicator error: %s", exc)


class TextBatcher:
    """Accumulates text_output lines per (stream, topic) and flushes after a quiet period."""

    def __init__(
        self,
        post_fn: Callable,
        delay: float = 2.0,
        on_flush: Callable | None = None,
    ) -> None:
        self._post_fn = post_fn
        self._delay = delay
        self._on_flush = on_flush
        self._buffers: dict[tuple[str, str], list[str]] = {}
        self._timers: dict[tuple[str, str], asyncio.TimerHandle] = {}

    def add(self, stream: str, topic: str, text: str) -> None:
        """Add a line to the buffer. Schedules a flush after the quiet period."""
        key = (stream, topic)
        if key not in self._buffers:
            self._buffers[key] = []
        self._buffers[key].append(text)

        # Reset the flush timer
        if key in self._timers:
            self._timers[key].cancel()

        loop = asyncio.get_running_loop()
        self._timers[key] = loop.call_later(
            self._delay,
            lambda k=key: loop.create_task(self._flush(k)),
        )

    async def _flush(self, key: tuple[str, str]) -> None:
        """Post the accumulated buffer as a single message."""
        lines = self._buffers.pop(key, [])
        self._timers.pop(key, None)
        if not lines:
            return

        # Filter blank lines and join
        content = "\n".join(line for line in lines if line.strip())
        if not content.strip():
            return

        stream, topic = key
        await self._post_fn(stream, topic, content)
        if self._on_flush:
            self._on_flush(stream, topic)

    async def flush_all(self) -> None:
        """Flush all pending buffers immediately."""
        for key in list(self._buffers):
            await self._flush(key)


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
            lambda: client.send_message(
                {
                    "type": "stream",
                    "to": stream,
                    "topic": topic,
                    "content": content,
                }
            ),
        )

    mention = f"@**{operator_email}** " if operator_email else ""
    batcher = TextBatcher(_post, delay=2.0, on_flush=lambda s, t: typing.stop(s, t))
    typing = TypingIndicator(client, loop)

    while True:
        line = await loop.run_in_executor(None, sys.stdin.readline)
        if not line:
            log.info("stdin closed")
            await batcher.flush_all()
            return
        msg = decode_message(line)
        if not isinstance(msg, Event):
            continue

        stream = project_to_stream.get(msg.bridge or "", msg.bridge or "")
        session_id = msg.session_id or ""
        origin = msg.payload.get("origin")

        # --- Control-origin sessions: all output goes to control topic ---
        if origin == "control":
            if msg.type == "session_starting":
                # Start typing indicator immediately when spawn begins
                typing.start(stream, control_topic)
            elif msg.type == "session_spawned":
                # Session confirmed spawned — already typing
                pass
            elif msg.type == "session_died":
                # Stop typing and clean up silently
                typing.stop(stream, control_topic)
            elif msg.type == "text_output":
                # Batch text lines before posting to control
                content = msg.payload.get("content", "")
                if content.strip():
                    batcher.add(stream, control_topic, content)
            else:
                # Non-text events post immediately
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
            explicit_topic = msg.payload.get(
                "topic"
            )  # Use worktree basename if provided
            topic = registry.assign(session_id, explicit_topic or artifact or None)
            suffix = f" on `{artifact}`" if artifact else ""

            # Create the session thread
            await _post(stream, topic, f"Session started{suffix}.")

            # Announce in control so the operator can find the thread
            await _post(
                stream,
                control_topic,
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
                stream,
                control_topic,
                f"{mention}New session in topic **{topic}**{suffix}. "
                f"Reply there to interact or use `/cancel` to stop.",
            )

        elif msg.type == "session_died":
            topic = registry.release(session_id) or session_id
            reason = msg.payload.get("reason", "unknown")
            await _post(stream, topic, f"Session ended: {reason}.")
            await _post(
                stream,
                control_topic,
                f"Session **{topic}** ended: {reason}.",
            )

        else:
            # All other events: post to the session's registered topic.
            topic = registry.topic_for(session_id)
            if not topic:
                log.warning(
                    "Event for unregistered session %r (type: %s) — dropping",
                    session_id,
                    msg.type,
                )
                continue
            if msg.type == "text_output":
                content = msg.payload.get("content", "")
                if content.strip():
                    batcher.add(stream, topic, content)
            else:
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
