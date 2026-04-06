"""Project bridge kernel — session orchestrator for one project.

Manages session lifecycle, emits events to the host bridge, and receives
commands from it. Does not talk to the chat adapter directly.
"""
from __future__ import annotations

import asyncio
import enum
import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from untethered.protocol import Event, Command
from untethered.adapters.claude_code import ClaudeCodeAdapter
from untethered.adapters.opencode import OpenCodeAdapter

log = logging.getLogger(__name__)


class SessionState(enum.Enum):
    SPAWNING = "spawning"
    INTERVIEWING = "interviewing"
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


class LauncherProcess:
    """Manages a bin/swain --non-interactive --format ndjson subprocess.

    Reads NDJSON from its stdout (questions, info, ready, error).
    Writes NDJSON to its stdin (answers from the operator).
    """

    def __init__(
        self,
        session_id: str,
        project_dir: str | None,
        on_output: Callable[[str, dict[str, Any]], None] | None = None,
    ):
        self.session_id = session_id
        self.project_dir = project_dir
        self.on_output = on_output
        self._process: asyncio.subprocess.Process | None = None
        self._reader_task: asyncio.Task | None = None

    async def start(self, purpose_args: list[str] | None = None) -> None:
        repo_root = self._find_repo_root()
        launcher = os.path.join(repo_root, "bin", "swain")
        if not os.path.exists(launcher):
            log.error("bin/swain not found at %s", launcher)
            if self.on_output:
                self.on_output("error", {"text": "bin/swain not found"})
            return

        cmd = [launcher, "--_non_interactive", "--format", "ndjson"]
        if purpose_args:
            cmd.extend(purpose_args)

        self._process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.project_dir or repo_root,
        )
        self._reader_task = asyncio.create_task(self._read_stdout())

    async def send_answer(self, text: str) -> None:
        if not self._process or not self._process.stdin:
            log.warning("Cannot send answer — launcher not running")
            return
        msg = json.dumps({"type": "answer", "text": text})
        self._process.stdin.write((msg + "\n").encode())
        await self._process.stdin.drain()

    async def stop(self) -> None:
        if self._reader_task:
            self._reader_task.cancel()
            try:
                await self._reader_task
            except asyncio.CancelledError:
                pass
        if self._process:
            self._process.terminate()
            try:
                await asyncio.wait_for(self._process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self._process.kill()

    async def _read_stdout(self) -> None:
        if not self._process or not self._process.stdout:
            return
        while True:
            line = await self._process.stdout.readline()
            if not line:
                break
            try:
                data = json.loads(line.decode())
            except (json.JSONDecodeError, UnicodeDecodeError):
                log.warning("Malformed line from launcher: %s", line[:200])
                continue
            msg_type = data.get("type", "")
            if self.on_output:
                self.on_output(msg_type, data)

    def _find_repo_root(self) -> str:
        if self.project_dir:
            p = Path(self.project_dir)
            while p != p.parent:
                if (p / ".git").exists() or (p / "bin" / "swain").exists():
                    return str(p)
                p = p.parent
            return self.project_dir
        return os.getcwd()


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
        self._launchers: dict[str, LauncherProcess] = {}

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

    # --- Launcher output handler ---

    def _on_launcher_output(self, session_id: str, msg_type: str, data: dict[str, Any]) -> None:
        """Handle NDJSON output from the launcher subprocess."""
        session = self.sessions.get(session_id)
        if not session:
            return

        if msg_type == "info":
            # Relay info messages as text_output to the control topic.
            if self.on_event:
                event = Event.text_output(
                    bridge=self.project, session_id=session_id,
                    content=data.get("text", ""),
                )
                event.payload["origin"] = "control"
                self.on_event(event)

        elif msg_type == "question":
            # Relay questions as text_output to the control topic.
            text = data.get("text", "")
            options = data.get("options", [])
            if options:
                text += " (" + "/".join(options) + ")"
            if self.on_event:
                event = Event.text_output(
                    bridge=self.project, session_id=session_id,
                    content=text,
                )
                event.payload["origin"] = "control"
                self.on_event(event)

        elif msg_type == "ready":
            # Launcher setup complete. Promote the session.
            purpose = data.get("purpose", "")
            worktree = data.get("worktree", self.project_dir)
            runtime = data.get("runtime", "claude")
            prompt = data.get("prompt", "")

            session.artifact = purpose or None
            session.origin = None  # No longer control-origin after promotion
            session.state = SessionState.SPAWNING

            # Clean up launcher.
            launcher = self._launchers.pop(session_id, None)
            if launcher:
                self._schedule(launcher.stop())

            # Emit session_promoted so the chat adapter creates the thread.
            if self.on_event:
                self.on_event(Event.session_promoted(
                    bridge=self.project, session_id=session_id,
                    artifact=purpose or session_id,
                    topic=purpose or None,
                ))

            # Spawn the runtime adapter in the launcher's worktree.
            adapter = ClaudeCodeAdapter(
                bridge=self.project,
                session_id=session_id,
                project_dir=worktree or self.project_dir,
                on_event=self.handle_runtime_event,
            )
            self._adapters[session_id] = adapter
            self._schedule(adapter.start(prompt=prompt or None))

        elif msg_type == "error":
            log.error("Launcher error for %s: %s", session_id, data.get("text", ""))
            if self.on_event:
                event = Event.text_output(
                    bridge=self.project, session_id=session_id,
                    content=f"Launcher error: {data.get('text', '')}",
                )
                event.payload["origin"] = "control"
                self.on_event(event)
            session.state = SessionState.DEAD

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
        # Clean up launcher if still interviewing.
        launcher = self._launchers.pop(session.session_id, None)
        if launcher:
            self._schedule(launcher.stop())
        adapter = self._adapters.pop(session.session_id, None)
        if adapter:
            self._schedule(adapter.stop())

    def _cmd_control_message(self, cmd: Command) -> None:
        """Handle natural language from the control topic.

        If there's an active launcher interview, relay as an answer.
        Otherwise, spawn a lightweight Claude session that answers in
        the control topic. No launcher interview, no dedicated thread.
        """
        text = cmd.payload.get("text", "")

        # Relay to active interview if one exists.
        for sid, session in self.sessions.items():
            if session.origin == "control" and session.state == SessionState.INTERVIEWING:
                launcher = self._launchers.get(sid)
                if launcher:
                    self._schedule(launcher.send_answer(text))
                    return

        # No active interview — lightweight query session via opencode.
        session_id = f"sess-{uuid.uuid4().hex[:8]}"
        session = Session(session_id=session_id, runtime="opencode", origin="control")
        self.sessions[session_id] = session

        adapter = OpenCodeAdapter(
            bridge=self.project,
            session_id=session_id,
            project_dir=self.project_dir,
            on_event=self.handle_runtime_event,
        )
        self._adapters[session_id] = adapter
        self._schedule(adapter.start(prompt=text))

    def _cmd_launch_session(self, cmd: Command) -> None:
        """Handle /work or /session — full launcher interview flow.

        Spawns bin/swain --non-interactive --format ndjson. The launcher
        runs the session interview (crash recovery, worktree selection,
        purpose). Output posts to control topic. On ready, promotes the
        session to a dedicated thread and spawns the runtime adapter.

        Follow-up control_messages while INTERVIEWING are relayed as
        answers to the launcher's stdin.
        """
        text = cmd.payload.get("text", "")

        # Check if there's an active interviewing session to relay to.
        for sid, session in self.sessions.items():
            if session.origin == "control" and session.state == SessionState.INTERVIEWING:
                launcher = self._launchers.get(sid)
                if launcher:
                    self._schedule(launcher.send_answer(text))
                    return

        # Start a new launcher interview.
        session_id = f"sess-{uuid.uuid4().hex[:8]}"
        session = Session(
            session_id=session_id, runtime="claude",
            origin="control", state=SessionState.INTERVIEWING,
        )
        self.sessions[session_id] = session

        launcher = LauncherProcess(
            session_id=session_id,
            project_dir=self.project_dir,
            on_output=lambda msg_type, data: self._on_launcher_output(
                session_id, msg_type, data,
            ),
        )
        self._launchers[session_id] = launcher

        purpose_args = text.split() if text else []
        self._schedule(launcher.start(purpose_args=purpose_args))

    def _cmd_bind_artifact(self, cmd: Command) -> None:
        session = self.sessions.get(cmd.session_id or "")
        if not session:
            log.warning("bind_artifact for unknown session: %s", cmd.session_id)
            return
        session.artifact = cmd.payload.get("artifact_id")
