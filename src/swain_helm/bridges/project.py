"""Project bridge microkernel — route between chat and runtime subprocess plugins.

Per ADR-046, the ProjectBridge is a self-contained microkernel that spawns
BOTH the chat adapter and runtime adapters as subprocess plugins via
PluginProcess. It sits in the middle: chat commands flow in, runtime
commands flow out; runtime events flow in, chat events flow out.
"""

from __future__ import annotations

import asyncio
import enum
import json
import logging
import time
import uuid
from dataclasses import dataclass
from typing import Any, Callable

from swain_helm.protocol import Event, Command, ConfigMessage
from swain_helm.plugin_process import PluginProcess
from swain_helm.worktree_scanner import WorktreeScanner, WorktreeDiff, WorktreeInfo
from swain_helm.session_registry import SessionRegistry

log = logging.getLogger(__name__)


class SessionState(enum.Enum):
    SPAWNING = "spawning"
    ACTIVE = "active"
    WAITING_APPROVAL = "waiting_approval"
    DEAD = "dead"


@dataclass
class Session:
    session_id: str
    runtime: str
    state: SessionState = SessionState.SPAWNING
    artifact: str | None = None
    origin: str | None = None
    pending_approval_call_id: str | None = None


_RUNTIME_COMMANDS = {
    "opencode": "swain-helm-opencode",
    "claude": "swain-helm-claude",
    "tmux": "swain-helm-tmux",
}


def _runtime_cmd(runtime: str) -> list[str]:
    return [_RUNTIME_COMMANDS.get(runtime, "swain-helm-tmux")]


class ProjectBridge:
    """Session orchestrator for one project — microkernel plugin router.

    Spawns a chat adapter subprocess and per-session runtime adapter
    subprocesses. Routes Commands from chat to runtime, and Events
    from runtime to chat. No in-process adapter imports.
    """

    def __init__(
        self,
        project: str,
        *,
        project_dir: str | None = None,
        config: dict[str, Any] | None = None,
        on_event: Callable[[Event], None] | None = None,
        scanner: WorktreeScanner | None = None,
        registry: SessionRegistry | None = None,
    ):
        self.project = project
        self.project_dir = project_dir
        self.config = config or {}
        self.on_event = on_event
        self.sessions: dict[str, Session] = {}
        self._chat_plugin: PluginProcess | None = None
        self._runtime_plugins: dict[str, PluginProcess] = {}
        self._scanner = scanner
        self._registry = registry
        self._branch_to_session: dict[str, str] = {}

    async def start(self) -> None:
        if self._registry:
            self._registry.read()
        if self._scanner:
            poll_s = self.config.get("worktree_poll_interval_s", 15.0)
            self._scanner.poll_interval_s = poll_s
            self._scanner.start_background(self._on_worktree_diff)
        chat_cfg = self.config.get("chat", {})
        stream = self.config.get("stream", self.project)
        self._chat_plugin = PluginProcess(
            name=f"chat:{self.project}",
            cmd=["swain-helm-zulip-chat"],
            plugin_type="chat",
            config={
                "server_url": chat_cfg.get("server_url", ""),
                "bot_email": chat_cfg.get("bot_email", ""),
                "bot_api_key": chat_cfg.get("bot_api_key", ""),
                "stream_name": stream,
                "control_topic": chat_cfg.get("control_topic", "control"),
                "operator_email": chat_cfg.get("operator_email"),
                "bridge": self.project,
            },
            on_message=self._on_chat_message,
        )
        await self._chat_plugin.start()

    async def stop(self) -> None:
        tasks: list[Any] = []
        if self._chat_plugin:
            tasks.append(self._chat_plugin.stop())
        for plugin in self._runtime_plugins.values():
            tasks.append(plugin.stop())
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self._runtime_plugins.clear()
        if self._scanner:
            self._scanner.stop_background()

    def _on_plugin_start_failed(self, task: asyncio.Task, session_id: str) -> None:
        """Handle plugin start failures by logging and marking session as dead."""
        try:
            task.result()
        except Exception:
            log.exception("Plugin start failed for session %s", session_id)
            session = self.sessions.get(session_id)
            if session:
                session.state = SessionState.DEAD
            plugin = self._runtime_plugins.pop(session_id, None)
            if plugin:
                if self._registry and session and session.origin:
                    self._registry.update_entry(session.origin, state="dead")

    # --- Worktree-driven session management ---

    def _on_worktree_diff(self, diff: WorktreeDiff) -> None:
        for wt in diff.added:
            self._ensure_session_for_worktree(wt)
            if self.on_event and wt.branch:
                self.on_event(
                    Event.worktree_added(
                        bridge=self.project,
                        worktree_path=wt.path,
                        branch_name=wt.branch,
                    )
                )
        for wt in diff.removed:
            self._remove_session_for_worktree(wt)
            if self.on_event and wt.branch:
                self.on_event(
                    Event.worktree_removed(
                        bridge=self.project,
                        worktree_path=wt.path,
                        branch_name=wt.branch,
                    )
                )

    def _ensure_session_for_worktree(self, wt: Any) -> None:
        if not isinstance(wt, WorktreeInfo):
            return
        if wt.branch in self._branch_to_session:
            return
        runtime = self.config.get("default_runtime", "opencode")
        worktree_path = wt.path
        opencode_config = self.config.get("opencode", {})
        session_id = f"sess-{uuid.uuid4().hex[:8]}"
        session = Session(session_id=session_id, runtime=runtime, origin=wt.branch)
        self.sessions[session_id] = session
        self._branch_to_session[wt.branch] = session_id
        plugin = PluginProcess(
            name=f"runtime:{session_id}",
            cmd=_runtime_cmd(runtime),
            plugin_type="runtime",
            config={
                "bridge": self.project,
                "session_id": session_id,
                "project_dir": worktree_path or "",
                "base_url": opencode_config.get("base_url", "http://127.0.0.1:4096"),
            },
            on_message=lambda msg, sid=session_id: self._on_runtime_message(sid, msg),
        )
        self._runtime_plugins[session_id] = plugin
        loop = asyncio.get_running_loop()
        task = loop.create_task(plugin.start())
        task.add_done_callback(
            lambda t, sid=session_id: self._on_plugin_start_failed(t, sid)
        )
        if self._registry and wt.branch:
            self._registry.update_entry(
                wt.branch,
                opencode_session_id=session_id,
                state="spawning",
                topic=wt.branch,
                worktree_path=worktree_path or "",
                started_at=time.time(),
                artifact=None,
            )

    def _remove_session_for_worktree(self, wt: Any) -> None:
        if not isinstance(wt, WorktreeInfo):
            return
        session_id = self._branch_to_session.pop(wt.branch, None)
        if not session_id or session_id not in self.sessions:
            return
        self.sessions[session_id].state = SessionState.DEAD
        plugin = self._runtime_plugins.pop(session_id, None)
        if plugin:
            asyncio.get_running_loop().create_task(plugin.stop())
        if self._registry and wt.branch:
            self._registry.update_entry(wt.branch, state="dead")

    # --- Routing ---

    def _on_chat_message(self, msg: Event | Command | ConfigMessage) -> None:
        if isinstance(msg, ConfigMessage):
            log.debug("Chat plugin sent ConfigMessage — ignoring")
            return
        if not isinstance(msg, Command):
            log.warning("Chat plugin sent an Event — unexpected: %s", msg.type)
            return
        self.handle_command(msg)

    def _on_runtime_message(
        self, session_id: str, msg: Event | Command | ConfigMessage
    ) -> None:
        if isinstance(msg, ConfigMessage):
            log.debug(
                "Runtime plugin sent ConfigMessage — ignoring for session %s",
                session_id,
            )
            return
        if not isinstance(msg, Event):
            log.warning("Runtime plugin sent a Command — unexpected: %s", msg.type)
            return
        self.handle_runtime_event(msg)
        if self._chat_plugin:
            asyncio.get_running_loop().create_task(self._chat_plugin.write(msg))

    # --- Public interface ---

    def handle_command(self, cmd: Command) -> None:
        handler = getattr(self, f"_cmd_{cmd.type}", None)
        if handler:
            handler(cmd)
        else:
            log.warning("Unknown command type: %s", cmd.type)

    def handle_runtime_event(self, event: Event) -> None:
        session = self.sessions.get(event.session_id or "")
        if event.type == "session_spawned" and session:
            session.state = SessionState.ACTIVE
            self._persist_session_state(session)
        elif event.type == "session_died" and session:
            session.state = SessionState.DEAD
            self._persist_session_state(session)
        elif event.type == "approval_needed" and session:
            session.state = SessionState.WAITING_APPROVAL
            session.pending_approval_call_id = event.payload.get("call_id")
            self._persist_session_state(session)
        elif event.type == "tool_result" and session:
            if session.state == SessionState.WAITING_APPROVAL:
                session.state = SessionState.ACTIVE
                session.pending_approval_call_id = None
                self._persist_session_state(session)
        if session and session.origin:
            event.payload["origin"] = session.origin
        if self.on_event:
            self.on_event(event)

    def _persist_session_state(self, session: Session) -> None:
        """Persist session state changes to the registry."""
        if self._registry and session.origin:
            self._registry.update_entry(
                session.origin,
                opencode_session_id=session.session_id,
                state=session.state.value,
            )

    def get_session(self, session_id: str) -> Session | None:
        """Look up a session by ID."""
        return self.sessions.get(session_id)

    def active_sessions(self) -> list[Session]:
        """Return all sessions currently in ACTIVE state."""
        return [s for s in self.sessions.values() if s.state == SessionState.ACTIVE]

    # --- Command handlers ---

    def _cmd_start_session(self, cmd: Command) -> None:
        session_id = f"sess-{uuid.uuid4().hex[:8]}"
        runtime = cmd.payload.get("runtime", "claude")
        artifact = cmd.payload.get("artifact")
        worktree_path = cmd.payload.get("worktree_path") or self.project_dir
        opencode_config = self.config.get("opencode", {})

        session = Session(session_id=session_id, runtime=runtime, artifact=artifact)
        self.sessions[session_id] = session

        plugin = PluginProcess(
            name=f"runtime:{session_id}",
            cmd=_runtime_cmd(runtime),
            plugin_type="runtime",
            config={
                "bridge": self.project,
                "session_id": session_id,
                "project_dir": worktree_path or "",
                "base_url": opencode_config.get("base_url", "http://127.0.0.1:4096"),
            },
            on_message=lambda msg, sid=session_id: self._on_runtime_message(sid, msg),
        )
        self._runtime_plugins[session_id] = plugin

        loop = asyncio.get_running_loop()
        task = loop.create_task(plugin.start())
        task.add_done_callback(
            lambda t, sid=session_id: self._on_plugin_start_failed(t, sid)
        )

    def _cmd_send_prompt(self, cmd: Command) -> None:
        session = self.sessions.get(cmd.session_id or "")
        if not session:
            log.warning("send_prompt for unknown session: %s", cmd.session_id)
            return
        plugin = self._runtime_plugins.get(session.session_id)
        if plugin:
            asyncio.get_running_loop().create_task(plugin.write(cmd))
        else:
            log.warning("No runtime plugin for session: %s", session.session_id)

    def _cmd_approve(self, cmd: Command) -> None:
        session = self.sessions.get(cmd.session_id or "")
        if not session:
            log.warning("approve for unknown session: %s", cmd.session_id)
            return
        if session.state == SessionState.WAITING_APPROVAL:
            session.state = SessionState.ACTIVE
            session.pending_approval_call_id = None
        plugin = self._runtime_plugins.get(session.session_id)
        if plugin:
            asyncio.get_running_loop().create_task(plugin.write(cmd))

    def _cmd_cancel(self, cmd: Command) -> None:
        session = self.sessions.get(cmd.session_id or "")
        if not session:
            log.warning("cancel for unknown session: %s", cmd.session_id)
            return
        session.state = SessionState.DEAD
        plugin = self._runtime_plugins.pop(session.session_id, None)
        if plugin:
            asyncio.get_running_loop().create_task(plugin.stop())

    def _cmd_control_message(self, cmd: Command) -> None:
        text = cmd.payload.get("text", "")
        for sid, session in self.sessions.items():
            if session.origin == "control" and session.state in (
                SessionState.SPAWNING,
                SessionState.ACTIVE,
            ):
                plugin = self._runtime_plugins.get(sid)
                if plugin:
                    follow_up = Command.send_prompt(
                        bridge=self.project,
                        session_id=sid,
                        text=text,
                    )
                    asyncio.get_running_loop().create_task(plugin.write(follow_up))
                    return

    def _cmd_bind_artifact(self, cmd: Command) -> None:
        session = self.sessions.get(cmd.session_id or "")
        if not session:
            log.warning("bind_artifact for unknown session: %s", cmd.session_id)
            return
        session.artifact = cmd.payload.get("artifact_id")
