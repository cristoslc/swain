"""Host bridge kernel — spawns and supervises plugin subprocesses.

Implements ADR-038 (microkernel plugin architecture), ADR-039 (hub-and-spoke),
and ADR-046 (per-project chat adapter subprocesses).

Per ADR-046, each project bridge gets its own Zulip chat adapter subprocess
that subscribes to only its project's stream via a narrow filter. The kernel
spawns one chat adapter per project (not one shared chat adapter) and one
project bridge plugin per configured project.

All inter-component communication is NDJSON over stdio.
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

    Topology (ADR-046 per-project chat adapters):
      Chat plugin (per project) → Commands → HostKernel → Commands → Project plugin
      Project plugin → Events → HostKernel → Events → Chat plugin (same project)

    Each project has its own chat adapter subscribed to its stream.
    """

    def __init__(self) -> None:
        self._chat_plugins: dict[str, PluginProcess] = {}
        self._project_plugins: dict[str, PluginProcess] = {}
        self._project_to_stream: dict[str, str] = {}

    async def run(self, config: dict[str, Any]) -> None:
        domain = config.get("domain", "personal")
        projects = config.get("projects", [])

        for proj in projects:
            stream = proj.get("stream", proj["name"])
            self._project_to_stream[proj["name"]] = stream

        for proj in projects:
            await self._spawn_project_plugin(proj)
            await self._spawn_chat_plugin(config["chat"], proj)

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
        self, chat_cfg: dict[str, Any], proj: dict[str, Any]
    ) -> None:
        name = proj["name"]
        stream = proj.get("stream", name)
        plugin_config = {
            "server_url": chat_cfg["server_url"],
            "bot_email": chat_cfg["bot_email"],
            "bot_api_key": chat_cfg["bot_api_key"],
            "operator_email": chat_cfg.get("operator_email"),
            "control_topic": chat_cfg.get("control_topic", "control"),
            "stream_name": stream,
            "bridge": name,
        }
        cmd = [sys.executable, "-m", "swain_helm.plugins.zulip_chat"]
        plugin = PluginProcess(
            name=f"chat:{name}",
            cmd=cmd,
            plugin_type="chat",
            config=plugin_config,
            on_message=self._on_chat_message,
        )
        await plugin.start()
        self._chat_plugins[name] = plugin

    def _on_project_message(self, msg: Event | Command) -> None:
        """Route an event from a project bridge to its chat adapter."""
        if not isinstance(msg, Event):
            log.warning("Project plugin sent a Command — unexpected: %s", msg.type)
            return
        project_name = msg.bridge or ""
        chat_plugin = self._chat_plugins.get(project_name)
        if chat_plugin:
            loop = asyncio.get_running_loop()
            loop.create_task(chat_plugin.write(msg))
        else:
            log.warning("No chat adapter for project: %r", project_name)

    def _on_chat_message(self, msg: Event | Command) -> None:
        """Route a command from a chat adapter to the correct project bridge."""
        if not isinstance(msg, Command):
            log.warning("Chat plugin sent an Event — unexpected: %s", msg.type)
            return
        if msg.type in _HOST_COMMAND_TYPES or msg.bridge in (None, "__host__"):
            self._handle_host_command(msg)
            return
        project_name = msg.bridge or ""
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
        for plugin in self._chat_plugins.values():
            tasks.append(plugin.stop())
        for plugin in self._project_plugins.values():
            tasks.append(plugin.stop())
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
