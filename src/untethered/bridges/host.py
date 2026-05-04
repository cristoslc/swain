"""Host bridge kernel — the hub daemon.

Manages project bridges, spawns the shared chat adapter, and routes
all events between them. Scoped to a security domain.
"""
from __future__ import annotations

import logging
from typing import Callable

from untethered.protocol import Event, Command

log = logging.getLogger(__name__)

# Host-scope command types handled by the host bridge, not forwarded
_HOST_COMMAND_TYPES = {
    "clone_project", "init_project", "start_bridge", "stop_bridge",
    "adopt_session",
}


class HostBridge:
    """Hub daemon for one security domain.

    Routes events from project bridges to the chat adapter, and commands
    from the chat adapter to the correct project bridge. Host-scope
    commands are handled locally.
    """

    def __init__(
        self,
        domain: str,
        *,
        on_chat_event: Callable[[Event], None] | None = None,
    ):
        self.domain = domain
        self.on_chat_event = on_chat_event
        self.projects: set[str] = set()
        self._project_command_handlers: dict[str, Callable[[Command], None]] = {}

    def register_project(
        self,
        project: str,
        *,
        on_command: Callable[[Command], None] | None = None,
    ) -> None:
        """Register a project bridge with the host bridge."""
        self.projects.add(project)
        if on_command:
            self._project_command_handlers[project] = on_command
        log.info("Registered project: %s (domain: %s)", project, self.domain)

    def unregister_project(self, project: str) -> None:
        """Unregister a project bridge."""
        self.projects.discard(project)
        self._project_command_handlers.pop(project, None)
        log.info("Unregistered project: %s", project)

    def route_project_event(self, event: Event) -> None:
        """Route an event from a project bridge to the chat adapter."""
        if self.on_chat_event:
            self.on_chat_event(event)

    def route_chat_command(self, cmd: Command) -> None:
        """Route a command from the chat adapter to the correct project bridge."""
        if cmd.type in _HOST_COMMAND_TYPES:
            self._handle_host_command(cmd)
            return

        bridge = cmd.bridge
        if not bridge or bridge == "__host__":
            self._handle_host_command(cmd)
            return

        handler = self._project_command_handlers.get(bridge)
        if handler:
            handler(cmd)
        else:
            log.warning(
                "Command for unknown project bridge %r (domain: %s)",
                bridge, self.domain,
            )

    def emit_host_event(self, event: Event) -> None:
        """Emit a host-scope event to the chat adapter."""
        if self.on_chat_event:
            self.on_chat_event(event)

    def _handle_host_command(self, cmd: Command) -> None:
        """Handle host-scope commands."""
        handler = getattr(self, f"_host_cmd_{cmd.type}", None)
        if handler:
            handler(cmd)
        else:
            log.warning("Unhandled host command: %s", cmd.type)

    def _host_cmd_stop_bridge(self, cmd: Command) -> None:
        project = cmd.payload.get("project", "")
        if project in self.projects:
            log.info("Stopping bridge for project: %s", project)
            self.unregister_project(project)
            self.emit_host_event(Event.bridge_stopped(
                project=project, bridge_id=project, reason="operator requested",
            ))

    def _host_cmd_start_bridge(self, cmd: Command) -> None:
        project_path = cmd.payload.get("project_path", "")
        project = project_path.rstrip("/").split("/")[-1] if project_path else ""
        if project:
            self.register_project(project)
            self.emit_host_event(Event.bridge_started(
                project=project, bridge_id=project,
            ))

    def _host_cmd_clone_project(self, cmd: Command) -> None:
        log.info("Clone project: %s", cmd.payload.get("repo_url", ""))
        # MVP: log only. Full implementation would run git clone.

    def _host_cmd_init_project(self, cmd: Command) -> None:
        log.info("Init project: %s", cmd.payload.get("project_path", ""))
        # MVP: log only. Full implementation would run swain init.

    def _host_cmd_adopt_session(self, cmd: Command) -> None:
        project = cmd.payload.get("project", "")
        tmux_target = cmd.payload.get("tmux_target", "")
        log.info("Adopt session %s into project %s", tmux_target, project)
        # MVP: log only. Full implementation would attach runtime adapter.
