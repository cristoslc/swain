"""Zulip chat adapter plugin.

Maps protocol events to Zulip messages and Zulip messages to protocol
commands. Uses Zulip streams as project rooms and topics as session threads.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Callable

from untethered.protocol import Event, Command

log = logging.getLogger(__name__)


def format_event_for_zulip(
    event: Event,
    *,
    operator_email: str | None = None,
    control_topic: str = "control",
) -> dict[str, str]:
    """Convert a protocol Event into a Zulip message dict (topic + content).

    Returns {"topic": ..., "content": ...} ready for the Zulip send_message API.
    """
    topic = event.session_id or control_topic

    # Host-scope events go to the control topic
    if event.bridge == "__host__":
        topic = control_topic

    content = _render_event_content(event, operator_email=operator_email)
    return {"topic": topic, "content": content}


def _render_event_content(event: Event, *, operator_email: str | None = None) -> str:
    """Render event payload as a readable Zulip message."""
    t = event.type
    p = event.payload

    if t == "text_output":
        return p.get("content", "")

    if t == "tool_call":
        tool = p.get("tool_name", "?")
        inp = p.get("input", {})
        call_id = p.get("call_id", "")
        inp_str = json.dumps(inp, indent=2) if inp else ""
        return f"**Tool call:** `{tool}` (`{call_id}`)\n```json\n{inp_str}\n```"

    if t == "tool_result":
        call_id = p.get("call_id", "")
        output = p.get("output", "")
        success = p.get("success", True)
        status = "completed" if success else "failed"
        truncated = output[:500] + ("..." if len(output) > 500 else "")
        return f"**Tool result** (`{call_id}`, {status}):\n```\n{truncated}\n```"

    if t == "approval_needed":
        tool = p.get("tool_name", "?")
        desc = p.get("description", "")
        call_id = p.get("call_id", "")
        mention = f"@**{operator_email}** " if operator_email else ""
        return (
            f"{mention}**Approval needed** — `{tool}`\n"
            f"> {desc}\n\n"
            f"Reply `/approve {call_id}` or `/deny {call_id}`"
        )

    if t == "session_spawned":
        runtime = p.get("runtime", "?")
        artifact = p.get("artifact", "")
        suffix = f" on {artifact}" if artifact else ""
        return f"Session started ({runtime}){suffix}."

    if t == "session_promoted":
        artifact = p.get("artifact", "")
        topic = p.get("topic", "")
        return f"Session promoted to topic **{topic or artifact}**."

    if t == "session_died":
        reason = p.get("reason", "unknown")
        return f"Session ended: {reason}."

    if t == "web_output_available":
        label = p.get("label", "Preview")
        path = p.get("path_or_port", "")
        return f"**{label}** ready: `{path}`"

    if t == "unmanaged_session_found":
        target = p.get("tmux_target", "?")
        hint = p.get("runtime_hint", "")
        proj = p.get("project_path", "")
        parts = [f"Adoptable session: `{target}`"]
        if hint:
            parts.append(f"runtime: {hint}")
        if proj:
            parts.append(f"project: {proj}")
        return " — ".join(parts)

    if t == "unmanaged_session_gone":
        target = p.get("tmux_target", "?")
        return f"Session `{target}` no longer available."

    if t == "host_status":
        bridges = p.get("bridges_running", 0)
        return f"Host status: {bridges} bridge(s) running."

    if t == "bridge_started":
        project = p.get("project", "?")
        return f"Bridge started for project `{project}`."

    if t == "bridge_stopped":
        project = p.get("project", "?")
        reason = p.get("reason", "")
        return f"Bridge stopped for project `{project}`: {reason}."

    return f"[{t}] {json.dumps(p)}"


def parse_zulip_message(
    msg: dict[str, Any],
    *,
    bridge: str,
    control_topic: str = "control",
) -> Command | None:
    """Convert a Zulip message into a protocol Command.

    Slash commands (/approve, /deny, /cancel, /work, /kill) are parsed.
    Plain text in a session topic becomes a send_prompt.
    """
    content = msg.get("content", "").strip()
    topic = msg.get("subject", "")

    # Slash commands
    if content.startswith("/"):
        return _parse_slash_command(content, topic=topic, bridge=bridge,
                                    control_topic=control_topic)

    # Plain text in control topic → control_message for bridge triage
    if topic == control_topic:
        return Command.control_message(bridge=bridge, text=content)

    # Plain text in a session topic → send_prompt to that session
    if topic:
        return Command.send_prompt(
            bridge=bridge, session_id=topic, text=content,
        )

    return None


def _parse_slash_command(
    content: str, *, topic: str, bridge: str, control_topic: str,
) -> Command | None:
    """Parse a slash command from a Zulip message."""
    parts = content.split(maxsplit=2)
    cmd_name = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []

    if cmd_name == "/approve" and args:
        return Command.approve(
            bridge=bridge, session_id=topic,
            call_id=args[0], approved=True,
        )

    if cmd_name == "/deny" and args:
        return Command.approve(
            bridge=bridge, session_id=topic,
            call_id=args[0], approved=False,
        )

    if cmd_name == "/cancel":
        session_id = topic if topic != control_topic else ""
        return Command.cancel(bridge=bridge, session_id=session_id)

    if cmd_name == "/work" and topic == control_topic:
        artifact = args[0] if args else None
        return Command.start_session(
            bridge=bridge, runtime="claude",
            artifact=artifact,
        )

    if cmd_name == "/kill" and topic == control_topic and args:
        return Command.cancel(bridge=bridge, session_id=args[0])

    log.warning("Unknown slash command: %s", content)
    return None


class ZulipChatAdapter:
    """Zulip chat adapter — posts events as messages, reads operator messages.

    Uses the zulip Python SDK. One instance per security domain, shared
    across all project bridges via the host bridge.
    """

    def __init__(
        self,
        *,
        zulip_client: Any = None,
        operator_email: str | None = None,
        stream_name: str | None = None,
        control_topic: str = "control",
        on_command: Callable[[Command], None] | None = None,
    ):
        self.client = zulip_client
        self.operator_email = operator_email
        self.stream_name = stream_name
        self.control_topic = control_topic
        self.on_command = on_command

    def post_event(self, event: Event, *, stream: str | None = None) -> None:
        """Post a protocol event as a Zulip message."""
        msg = format_event_for_zulip(
            event,
            operator_email=self.operator_email,
            control_topic=self.control_topic,
        )
        if self.client:
            self.client.send_message({
                "type": "stream",
                "to": stream or self.stream_name,
                "topic": msg["topic"],
                "content": msg["content"],
            })

    def start_listening(self, *, bridge: str) -> None:
        """No-op stub — polling is owned by main._poll_zulip_events.

        The host bridge's async event loop handles Zulip event queue
        registration and long-polling via run_in_executor. This method
        exists to satisfy the plugin interface contract.
        """
