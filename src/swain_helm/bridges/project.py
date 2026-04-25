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
import os
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from swain_helm.protocol import Event, Command, ConfigMessage
from swain_helm.plugin_process import PluginProcess
from swain_helm.worktree_scanner import WorktreeScanner, WorktreeDiff, WorktreeInfo
from swain_helm.session_registry import SessionRegistry
from swain_helm.config import DEFAULT_WORKTREE_POLL_INTERVAL_S

log = logging.getLogger(__name__)


class SessionState(enum.Enum):
    SPAWNING = "spawning"
    ACTIVE = "active"
    BUSY = "busy"
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
    pending_prompt: str | None = None


_RUNTIME_COMMANDS = {
    "opencode": "swain_helm.adapters.opencode_server",
    "claude": "swain_helm.adapters.claude_code",
    "tmux": "swain_helm.adapters.tmux_pane",
}

_CHAT_COMMAND_MODULE = "swain_helm.plugins.zulip_chat"


def _runtime_cmd(runtime: str) -> list[str]:
    module = _RUNTIME_COMMANDS.get(runtime, "swain_helm.adapters.tmux_pane")
    return [sys.executable, "-m", module]


def _current_branch(project_dir: str) -> str:
    """Get the current branch of a git repo (or worktree) synchronously."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            branch = result.stdout.strip()
            if branch in ("main", "master"):
                return "trunk"
            return branch
    except Exception:
        pass
    return "trunk"


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
        chat_cfg = self.config.get("chat", {})
        stream = self.config.get("stream", self.project)
        self._chat_plugin = PluginProcess(
            name=f"chat:{self.project}",
            cmd=[sys.executable, "-m", _CHAT_COMMAND_MODULE],
            plugin_type="chat",
            config={
                "server_url": chat_cfg.get("server_url", ""),
                "bot_email": chat_cfg.get("bot_email", ""),
                "bot_api_key": chat_cfg.get("bot_api_key", ""),
                "stream_name": stream,
                "control_topic": chat_cfg.get("control_topic", "trunk"),
                "operator_email": chat_cfg.get("operator_email"),
                "bridge": self.project,
                "stream": stream,
                "worktree_path": self.project_dir or "",
            },
            on_message=self._on_chat_message,
        )
        await self._chat_plugin.start()
        if self._chat_plugin:
            await self._chat_plugin.write(
                Event.bridge_online(
                    project=self.project,
                    stream=stream,
                    worktree_path=self.project_dir or "",
                    branch_name=_current_branch(self.project_dir)
                    if self.project_dir
                    else "trunk",
                )
            )
        if self._scanner:
            self._scanner.start_background(self._on_worktree_diff)

    async def run(self) -> None:
        """Start the bridge and keep running until the chat plugin exits."""
        await self.start()
        if self._chat_plugin and self._chat_plugin._reader_task:
            await self._chat_plugin._reader_task
        log.info("Bridge %s chat plugin exited, shutting down", self.project)
        await self.stop()

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
            if self.on_event and wt.branch:
                self.on_event(
                    Event.worktree_added(
                        bridge=self.project,
                        worktree_path=wt.path,
                        branch_name=wt.branch,
                    )
                )
            if self._registry and wt.branch:
                self._registry.update_entry(
                    wt.branch,
                    worktree_path=wt.path or "",
                    state="available",
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
        runtime = self.config.get(
            "default_runtime", self.config.get("runtime", "opencode")
        )
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
                "base_url": opencode_config.get("base_url", "http://127.0.0.1:4098"),
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
        if session_id and session_id in self.sessions:
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
            self._clear_pending_prompt(session)
        elif event.type == "approval_needed" and session:
            session.state = SessionState.WAITING_APPROVAL
            session.pending_approval_call_id = event.payload.get("call_id")
            self._persist_session_state(session)
        elif event.type == "tool_result" and session:
            if session.state == SessionState.WAITING_APPROVAL:
                session.state = SessionState.BUSY
                session.pending_approval_call_id = None
                self._persist_session_state(session)
        elif event.type == "turn_ended" and session:
            was_busy = session.state == SessionState.BUSY
            session.state = SessionState.ACTIVE
            self._persist_session_state(session)
            if was_busy and session.pending_prompt is not None:
                text = session.pending_prompt
                session.pending_prompt = None
                cmd = Command.send_prompt(
                    bridge=self.project,
                    session_id=session.session_id,
                    text=text,
                )
                self.handle_command(cmd)
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

    def _abort_current_turn(self, session: Session) -> None:
        """Send an abort command to the runtime to cancel the current turn.

        The session transitions to ACTIVE when turn_ended arrives from
        the runtime, at which point any queued prompt is sent automatically.
        """
        plugin = self._runtime_plugins.get(session.session_id)
        if not plugin:
            log.warning(
                "Cannot abort — no runtime plugin for session %s",
                session.session_id,
            )
            return
        abort_cmd = Command.cancel(bridge=self.project, session_id=session.session_id)
        asyncio.get_running_loop().create_task(plugin.write(abort_cmd))

    def _clear_pending_prompt(self, session: Session) -> None:
        """Clear any pending prompt for a dead session."""
        session.pending_prompt = None

    def get_session(self, session_id: str) -> Session | None:
        """Look up a session by ID."""
        return self.sessions.get(session_id)

    def active_sessions(self) -> list[Session]:
        """Return all sessions currently active or busy (in a turn)."""
        return [
            s
            for s in self.sessions.values()
            if s.state in (SessionState.ACTIVE, SessionState.BUSY)
        ]

    # --- Command handlers ---

    def _lookup_session(self, cmd: Command) -> Session | None:
        """Look up a session from a command. Logs and returns None if not found."""
        session = self.sessions.get(cmd.session_id or "")
        if not session:
            log.warning("%s for unknown session: %s", cmd.type, cmd.session_id)
        return session

    def _cmd_start_session(self, cmd: Command) -> None:
        session_id = f"sess-{uuid.uuid4().hex[:8]}"
        runtime = cmd.payload.get(
            "runtime",
            self.config.get("default_runtime", self.config.get("runtime", "opencode")),
        )
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
                "base_url": opencode_config.get("base_url", "http://127.0.0.1:4098"),
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
        session_id = cmd.session_id or ""
        session = self.sessions.get(session_id)

        if not session and session_id == "trunk":
            self._ensure_trunk_session(cmd)
            session = self.sessions.get(cmd.session_id or "")
            if not session:
                return
        elif not session:
            log.warning("%s for unknown session: %s", cmd.type, session_id)
            return

        if session.state == SessionState.BUSY:
            log.info(
                "Session %s is busy — aborting current turn and queuing new prompt",
                session.session_id,
            )
            session.pending_prompt = cmd.payload.get("text")
            if self._chat_plugin:
                asyncio.get_running_loop().create_task(
                    self._chat_plugin.write(
                        Event.text_output(
                            bridge=self.project,
                            session_id=session.session_id,
                            content="*Turn interrupted — new prompt queued.*",
                        )
                    )
                )
            self._abort_current_turn(session)
            return

        if session.state == SessionState.WAITING_APPROVAL:
            log.info(
                "Session %s is waiting for approval — queuing prompt behind approval",
                session.session_id,
            )
            session.pending_prompt = cmd.payload.get("text")
            return

        plugin = self._runtime_plugins.get(session.session_id)
        if plugin:
            session.state = SessionState.BUSY
            self._persist_session_state(session)
            asyncio.get_running_loop().create_task(plugin.write(cmd))
        else:
            log.warning("No runtime plugin for session: %s", session.session_id)

    def _cmd_approve(self, cmd: Command) -> None:
        session = self._lookup_session(cmd)
        if not session:
            return
        if session.state == SessionState.WAITING_APPROVAL:
            session.state = SessionState.BUSY
            session.pending_approval_call_id = None
            self._persist_session_state(session)
        plugin = self._runtime_plugins.get(session.session_id)
        if plugin:
            asyncio.get_running_loop().create_task(plugin.write(cmd))

    def _cmd_cancel(self, cmd: Command) -> None:
        session = self._lookup_session(cmd)
        if not session:
            return
        self._clear_pending_prompt(session)
        session.state = SessionState.DEAD
        plugin = self._runtime_plugins.pop(session.session_id, None)
        if plugin:
            asyncio.get_running_loop().create_task(plugin.stop())

    def _ensure_trunk_session(self, cmd: Command) -> None:
        for sid, session in self.sessions.items():
            if session.origin == "trunk" and session.state in (
                SessionState.SPAWNING,
                SessionState.ACTIVE,
                SessionState.BUSY,
            ):
                cmd.session_id = sid
                return

        runtime = self.config.get(
            "default_runtime", self.config.get("runtime", "opencode")
        )
        opencode_config = self.config.get("opencode", {})
        worktree_path = self.project_dir or ""
        session_id = f"sess-{uuid.uuid4().hex[:8]}"
        session = Session(session_id=session_id, runtime=runtime, origin="trunk")
        self.sessions[session_id] = session
        plugin = PluginProcess(
            name=f"runtime:{session_id}",
            cmd=_runtime_cmd(runtime),
            plugin_type="runtime",
            config={
                "bridge": self.project,
                "session_id": session_id,
                "project_dir": worktree_path,
                "base_url": opencode_config.get("base_url", "http://127.0.0.1:4098"),
                "origin": "trunk",
            },
            on_message=lambda msg, sid=session_id: self._on_runtime_message(sid, msg),
        )
        self._runtime_plugins[session_id] = plugin
        loop = asyncio.get_running_loop()
        task = loop.create_task(plugin.start())
        task.add_done_callback(
            lambda t, sid=session_id: self._on_plugin_start_failed(t, sid)
        )
        cmd.session_id = session_id
        if self._chat_plugin:
            asyncio.get_running_loop().create_task(
                self._chat_plugin.write(
                    Event.session_starting(
                        bridge=self.project,
                        session_id=session_id,
                        runtime=runtime,
                        origin="trunk",
                    )
                )
            )
        log.info("Auto-started trunk session %s", session_id)

    def _cmd_bind_artifact(self, cmd: Command) -> None:
        session = self._lookup_session(cmd)
        if not session:
            return
        session.artifact = cmd.payload.get("artifact_id")


def _config_from_env() -> dict[str, Any]:
    """Build bridge config from environment variables in container mode.

    Per ADR-048, when SWAIN_HELM_CONTAINER_MODE=1, the bridge reads config
    from environment variables instead of stdin (since there's no watchdog
    to send a ConfigMessage).
    """
    return {
        "path": os.environ.get("PROJECT_PATH", ""),
        "stream": os.environ.get("PROJECT_NAME", ""),
        "chat": {
            "server_url": os.environ.get(
                "ZULIP_SITE", "https://cristoslc.zulipchat.com"
            ),
            "bot_email": os.environ.get("ZULIP_BOT_EMAIL", ""),
            "bot_api_key": os.environ.get("ZULIP_BOT_API_KEY", ""),
            "operator_email": os.environ.get("ZULIP_OPERATOR_EMAIL", ""),
        },
        "opencode": {
            "base_url": "http://127.0.0.1:4098",
            "default_port": 4098,
        },
    }


def main() -> None:
    """CLI entry point for bridge subprocess.

    Reads a ConfigMessage from stdin (sent by the watchdog with fully-resolved
    credentials — no op:// references ever reach this process), creates a
    ProjectBridge, and runs its event loop.

    Per ADR-049, runs startup zombie cleanup before initializing to prevent
    orphan processes from interfering with the new bridge instance.
    """
    import argparse
    import asyncio
    from pathlib import Path

    from swain_helm.zombie_cleanup import (
        cleanup_stale_processes,
        cleanup_orphan_subprocesses,
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    parser = argparse.ArgumentParser(description="swain-helm project bridge")
    parser.add_argument("--project", required=True, help="Project name")
    args = parser.parse_args()

    log.info("Bridge main() starting for project: %s", args.project)

    stale_killed = cleanup_stale_processes(
        Path.home() / ".config" / "swain-helm" / "run" / "bridges"
    )
    orphan_killed = cleanup_orphan_subprocesses()
    if stale_killed or orphan_killed:
        log.warning(
            "Startup cleanup: killed %d stale and %d orphan processes",
            stale_killed,
            orphan_killed,
        )

    container_mode = os.environ.get("SWAIN_HELM_CONTAINER_MODE", "") == "1"

    if container_mode:
        cfg = _config_from_env()
        project_dir = cfg.get("path", os.environ.get("PROJECT_PATH", ""))
        log.info("Bridge running in container mode, project_dir=%s", project_dir)
    else:
        config_line = sys.stdin.readline()
        if not config_line:
            log.error(
                "No config received on stdin — bridge must be spawned by watchdog"
            )
            sys.exit(1)

        log.info("Bridge received config (%d bytes)", len(config_line))

        from swain_helm.protocol import decode_message, ConfigMessage as CMsg

        config_msg = decode_message(config_line)
        if not isinstance(config_msg, CMsg):
            log.error("Expected ConfigMessage on stdin, got: %r", config_line[:100])
            sys.exit(1)

        cfg = getattr(config_msg, "config", {})
        project_dir = cfg.get("path", "")
    log.info(
        "Bridge config: project_dir=%s, chat_keys=%s",
        project_dir,
        list(cfg.get("chat", {}).keys()),
    )
    registry = SessionRegistry(project_dir) if project_dir else None
    scanner = WorktreeScanner(project_dir) if project_dir else None

    bridge = ProjectBridge(
        project=args.project,
        project_dir=project_dir,
        config=cfg,
        scanner=scanner,
        registry=registry,
    )

    log.info("Bridge starting event loop...")
    asyncio.run(bridge.run())
    log.info("Bridge event loop exited")


if __name__ == "__main__":
    main()
