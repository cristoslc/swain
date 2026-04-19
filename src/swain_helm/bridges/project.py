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
import uuid
from dataclasses import dataclass
from typing import Any, Callable

from swain_helm.protocol import Event, Command
from swain_helm.plugin_process import PluginProcess

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


def _runtime_cmd(runtime: str) -> list[str]:
    if runtime == "opencode":
        return ["swain-helm-opencode"]
    if runtime == "claude":
        return ["swain-helm-claude"]
    return ["swain-helm-tmux"]


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
    ):
        self.project = project
        self.project_dir = project_dir
        self.config = config or {}
        self.on_event = on_event
        self.sessions: dict[str, Session] = {}
        self._chat_plugin: PluginProcess | None = None
        self._runtime_plugins: dict[str, PluginProcess] = {}

    async def start(self) -> None:
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

    # --- Routing ---

    def _on_chat_message(self, msg: Event | Command) -> None:
        if not isinstance(msg, Command):
            log.warning("Chat plugin sent an Event — unexpected: %s", msg.type)
            return
        self.handle_command(msg)

    def _on_runtime_message(self, session_id: str, msg: Event | Command) -> None:
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
        elif event.type == "session_died" and session:
            session.state = SessionState.DEAD
        elif event.type == "approval_needed" and session:
            session.state = SessionState.WAITING_APPROVAL
            session.pending_approval_call_id = event.payload.get("call_id")
        elif event.type == "tool_result" and session:
            if session.state == SessionState.WAITING_APPROVAL:
                session.state = SessionState.ACTIVE
                session.pending_approval_call_id = None
        if session and session.origin:
            event.payload["origin"] = session.origin
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
        loop.create_task(plugin.start())

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
