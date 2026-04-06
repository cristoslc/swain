"""Project bridge kernel — session orchestrator for one project.

Manages session lifecycle, emits events to the host bridge, and receives
commands from it. Does not talk to the chat adapter directly.
"""
from __future__ import annotations

import enum
import logging
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable

from untethered.protocol import Event, Command

log = logging.getLogger(__name__)


class SessionState(enum.Enum):
    SPAWNING = "spawning"
    ACTIVE = "active"
    WAITING_APPROVAL = "waiting_approval"
    IDLE = "idle"
    DEAD = "dead"


@dataclass
class Session:
    session_id: str
    runtime: str
    state: SessionState = SessionState.SPAWNING
    artifact: str | None = None
    pending_approval_call_id: str | None = None


class ProjectBridge:
    """Session orchestrator for a single project.

    Manages sessions, spawns runtime adapter plugins, and communicates
    with the host bridge via the on_event callback.
    """

    def __init__(
        self,
        project: str,
        *,
        on_event: Callable[[Event], None] | None = None,
    ):
        self.project = project
        self.on_event = on_event
        self.sessions: dict[str, Session] = {}

    def handle_command(self, cmd: Command) -> None:
        """Handle a command routed from the host bridge."""
        handler = getattr(self, f"_cmd_{cmd.type}", None)
        if handler:
            handler(cmd)
        else:
            log.warning("Unknown command type: %s", cmd.type)

    def handle_runtime_event(self, event: Event) -> None:
        """Handle an event from a runtime adapter plugin."""
        session = self.sessions.get(event.session_id or "")

        if event.type == "session_spawned" and session:
            session.state = SessionState.ACTIVE
        elif event.type == "session_died" and session:
            session.state = SessionState.DEAD
        elif event.type == "approval_needed" and session:
            session.state = SessionState.WAITING_APPROVAL
            session.pending_approval_call_id = event.payload.get("call_id")
        elif event.type == "tool_result" and session:
            if session.state == SessionState.WAITING_APPROVAL:
                session.state = SessionState.ACTIVE
                session.pending_approval_call_id = None

        if self.on_event:
            self.on_event(event)

    def get_session(self, session_id: str) -> Session | None:
        return self.sessions.get(session_id)

    def active_sessions(self) -> list[Session]:
        return [s for s in self.sessions.values() if s.state == SessionState.ACTIVE]

    # --- Command handlers ---

    def _cmd_start_session(self, cmd: Command) -> None:
        session_id = f"sess-{uuid.uuid4().hex[:8]}"
        runtime = cmd.payload.get("runtime", "claude")
        session = Session(session_id=session_id, runtime=runtime)
        self.sessions[session_id] = session

        if self.on_event:
            self.on_event(Event.session_spawned(
                bridge=self.project,
                session_id=session_id,
                runtime=runtime,
            ))

    def _cmd_send_prompt(self, cmd: Command) -> None:
        session = self.sessions.get(cmd.session_id or "")
        if not session:
            log.warning("send_prompt for unknown session: %s", cmd.session_id)
            return
        # In the full implementation, this would forward to the runtime adapter.
        # For now, the command is accepted and would be routed by the async loop.

    def _cmd_approve(self, cmd: Command) -> None:
        session = self.sessions.get(cmd.session_id or "")
        if not session:
            log.warning("approve for unknown session: %s", cmd.session_id)
            return
        if session.state == SessionState.WAITING_APPROVAL:
            session.state = SessionState.ACTIVE
            session.pending_approval_call_id = None

    def _cmd_cancel(self, cmd: Command) -> None:
        session = self.sessions.get(cmd.session_id or "")
        if not session:
            log.warning("cancel for unknown session: %s", cmd.session_id)
            return
        session.state = SessionState.DEAD

    def _cmd_bind_artifact(self, cmd: Command) -> None:
        session = self.sessions.get(cmd.session_id or "")
        if not session:
            log.warning("bind_artifact for unknown session: %s", cmd.session_id)
            return
        session.artifact = cmd.payload.get("artifact_id")
