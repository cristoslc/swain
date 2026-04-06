"""Project bridge kernel — session orchestrator for one project.

Manages session lifecycle, emits events to the host bridge, and receives
commands from it. Does not talk to the chat adapter directly.
"""
from __future__ import annotations

import asyncio
import enum
import logging
import uuid
from dataclasses import dataclass
from typing import Any, Callable

from untethered.protocol import Event, Command
from untethered.adapters.claude_code import ClaudeCodeAdapter

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
    origin: str | None = None  # "control" if spawned from control topic
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
        project_dir: str | None = None,
        on_event: Callable[[Event], None] | None = None,
    ):
        self.project = project
        self.project_dir = project_dir
        self.on_event = on_event
        self.sessions: dict[str, Session] = {}
        self._adapters: dict[str, ClaudeCodeAdapter] = {}

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

        # Tag origin so the chat adapter routes control-origin events
        # back to the control topic instead of creating a thread.
        if session and session.origin:
            event.payload["origin"] = session.origin

        if self.on_event:
            self.on_event(event)

    def get_session(self, session_id: str) -> Session | None:
        return self.sessions.get(session_id)

    def active_sessions(self) -> list[Session]:
        return [s for s in self.sessions.values() if s.state == SessionState.ACTIVE]

    # --- Internal helpers ---

    def _schedule(self, coro: Any) -> None:
        """Schedule a coroutine on the running event loop.

        In production this is always called from within an async context
        (main._poll_zulip_events). In unit tests with no running loop, the
        coroutine is closed and logged at debug level — session state is
        still updated synchronously, which is what unit tests verify.
        """
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(coro)
        except RuntimeError:
            log.debug("No running event loop — async operation skipped (test context?)")
            coro.close()

    # --- Command handlers ---

    def _cmd_start_session(self, cmd: Command) -> None:
        session_id = f"sess-{uuid.uuid4().hex[:8]}"
        runtime = cmd.payload.get("runtime", "claude")
        artifact = cmd.payload.get("artifact")
        prompt = cmd.payload.get("prompt") or artifact
        session = Session(session_id=session_id, runtime=runtime, artifact=artifact)
        self.sessions[session_id] = session

        adapter = ClaudeCodeAdapter(
            bridge=self.project,
            session_id=session_id,
            project_dir=self.project_dir,
            on_event=self.handle_runtime_event,
        )
        self._adapters[session_id] = adapter
        self._schedule(adapter.start(prompt=prompt))

    def _cmd_send_prompt(self, cmd: Command) -> None:
        session = self.sessions.get(cmd.session_id or "")
        if not session:
            log.warning("send_prompt for unknown session: %s", cmd.session_id)
            return
        adapter = self._adapters.get(session.session_id)
        if adapter:
            self._schedule(adapter.send_command(cmd))
        else:
            log.warning("No adapter for session: %s", session.session_id)

    def _cmd_approve(self, cmd: Command) -> None:
        session = self.sessions.get(cmd.session_id or "")
        if not session:
            log.warning("approve for unknown session: %s", cmd.session_id)
            return
        if session.state == SessionState.WAITING_APPROVAL:
            session.state = SessionState.ACTIVE
            session.pending_approval_call_id = None
        adapter = self._adapters.get(session.session_id)
        if adapter:
            self._schedule(adapter.send_command(cmd))

    def _cmd_cancel(self, cmd: Command) -> None:
        session = self.sessions.get(cmd.session_id or "")
        if not session:
            log.warning("cancel for unknown session: %s", cmd.session_id)
            return
        session.state = SessionState.DEAD
        adapter = self._adapters.pop(session.session_id, None)
        if adapter:
            self._schedule(adapter.stop())

    def _cmd_control_message(self, cmd: Command) -> None:
        """Handle natural language from the control topic.

        Spawns a session tagged with origin=control. The chat adapter
        routes output from control-origin sessions back to the control
        topic instead of creating a dedicated thread. When a session
        needs real work, it can be promoted to its own thread later.
        """
        text = cmd.payload.get("text", "")
        session_id = f"sess-{uuid.uuid4().hex[:8]}"
        session = Session(session_id=session_id, runtime="claude", origin="control")
        self.sessions[session_id] = session

        adapter = ClaudeCodeAdapter(
            bridge=self.project,
            session_id=session_id,
            project_dir=self.project_dir,
            on_event=self.handle_runtime_event,
        )
        self._adapters[session_id] = adapter
        self._schedule(adapter.start(prompt=text))

    def _cmd_bind_artifact(self, cmd: Command) -> None:
        session = self.sessions.get(cmd.session_id or "")
        if not session:
            log.warning("bind_artifact for unknown session: %s", cmd.session_id)
            return
        session.artifact = cmd.payload.get("artifact_id")
