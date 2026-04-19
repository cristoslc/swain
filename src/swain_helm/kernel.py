"""Host bridge kernel — spawns and supervises plugin subprocesses.

Implements ADR-038 (microkernel plugin architecture) and ADR-039 (hub-and-spoke).
The kernel spawns one chat adapter plugin and one project bridge plugin per
configured project. All inter-component communication is NDJSON over stdio.

Per ADR-038:
  - Host bridge is the microkernel for chat adapter plugins.
  - Project bridge is the microkernel for runtime adapter plugins.
  - Plugins are subprocess executables speaking NDJSON over stdio.
  - Each plugin receives only its own scoped config on stdin line 0.
"""

from __future__ import annotations

import asyncio
import logging
import sys
from typing import Any, Callable

from swain_helm.protocol import (
    Event,
    Command,
    _HOST_COMMAND_TYPES,
)
from swain_helm.plugin_process import PluginProcess

log = logging.getLogger("swain_helm.kernel")


class HostKernel:
    """Microkernel: spawns plugin subprocesses and routes NDJSON between them.

    Topology (ADR-039 hub-and-spoke):
      Chat plugin → Commands → HostKernel → Commands → Project plugin
      Project plugin → Events → HostKernel → Events → Chat plugin

    Project bridges never talk to the chat adapter directly.
    """

    def __init__(self) -> None:
        self._chat_plugin: PluginProcess | None = None
        self._project_plugins: dict[str, PluginProcess] = {}
        # stream name → project name (for routing commands from chat plugin)
        self._stream_to_project: dict[str, str] = {}
        # project name → stream name (for routing events to correct Zulip stream)
        self._project_to_stream: dict[str, str] = {}

    async def run(self, config: dict[str, Any]) -> None:
        domain = config.get("domain", "personal")
        projects = config.get("projects", [])

        for proj in projects:
            stream = proj.get("stream", proj["name"])
            self._stream_to_project[stream] = proj["name"]
            self._project_to_stream[proj["name"]] = stream

        for proj in projects:
            await self._spawn_project_plugin(proj)

        await self._spawn_chat_plugin(config["chat"], projects)

        log.info(
            "Host kernel running — domain: %s, projects: %s",
            domain,
            list(self._project_plugins),
        )
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            pass
        finally:
            await self._shutdown()

    async def _spawn_project_plugin(self, proj: dict[str, Any]) -> None:
        name = proj["name"]
        plugin_config = {
            "project": name,
            "project_dir": proj.get("path", ""),
            "stream": proj.get("stream", name),
            "runtime": proj.get("runtime", "claude"),
        }
        cmd = [sys.executable, "-m", "swain_helm.plugins.project_bridge"]
        plugin = PluginProcess(
            name=f"project:{name}",
            cmd=cmd,
            plugin_type="project",
            config=plugin_config,
            on_message=self._on_project_message,
        )
        await plugin.start()
        self._project_plugins[name] = plugin

    async def _spawn_chat_plugin(
        self, chat_cfg: dict[str, Any], projects: list[dict[str, Any]]
    ) -> None:
        plugin_config = {
            "server_url": chat_cfg["server_url"],
            "bot_email": chat_cfg["bot_email"],
            "bot_api_key": chat_cfg["bot_api_key"],
            "operator_email": chat_cfg.get("operator_email"),
            "control_topic": chat_cfg.get("control_topic", "control"),
            # Scoped routing maps so the chat plugin can set bridge fields
            "stream_to_project": self._stream_to_project,
            "project_to_stream": self._project_to_stream,
        }
        cmd = [sys.executable, "-m", "swain_helm.plugins.zulip_chat"]
        plugin = PluginProcess(
            name="chat:zulip",
            cmd=cmd,
            plugin_type="chat",
            config=plugin_config,
            on_message=self._on_chat_message,
        )
        await plugin.start()
        self._chat_plugin = plugin

    def _on_project_message(self, msg: Event | Command) -> None:
        """Route an event from a project bridge to the chat adapter."""
        if not isinstance(msg, Event):
            log.warning("Project plugin sent a Command — unexpected: %s", msg.type)
            return
        if self._chat_plugin:
            loop = asyncio.get_running_loop()
            loop.create_task(self._chat_plugin.write(msg))

    def _on_chat_message(self, msg: Event | Command) -> None:
        """Route a command from the chat adapter to the correct project bridge."""
        if not isinstance(msg, Command):
            log.warning("Chat plugin sent an Event — unexpected: %s", msg.type)
            return
        if msg.type in _HOST_COMMAND_TYPES or msg.bridge in (None, "__host__"):
            self._handle_host_command(msg)
            return
        project_name = self._stream_to_project.get(msg.bridge or "", msg.bridge or "")
        plugin = self._project_plugins.get(project_name)
        if plugin:
            loop = asyncio.get_running_loop()
            loop.create_task(plugin.write(msg))
        else:
            log.warning("Command for unknown project: %r", project_name)

    def _handle_host_command(self, cmd: Command) -> None:
        log.info("Host command: %s (MVP: log only)", cmd.type)

    async def _shutdown(self) -> None:
        log.info("Host kernel shutting down...")
        tasks: list[Any] = []
        if self._chat_plugin:
            tasks.append(self._chat_plugin.stop())
        for plugin in self._project_plugins.values():
            tasks.append(plugin.stop())
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
