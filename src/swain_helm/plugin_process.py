"""Plugin subprocess manager — spawns and supervises NDJSON-over-stdio plugins.

Implements ADR-038 (microkernel plugin architecture).
A PluginProcess manages one subprocess (chat adapter or runtime adapter).
Protocol:
  stdin line 0 : ConfigMessage (JSON, sent by kernel on startup)
  stdin lines 1+: NDJSON Events or Commands from kernel
  stdout lines  : NDJSON Commands or Events to kernel
  stderr        : logged at DEBUG level
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable

from swain_helm.protocol import (
    Event,
    Command,
    ConfigMessage,
    encode_message,
    decode_message,
)

log = logging.getLogger("swain_helm.plugin_process")


class PluginProcess:
    """One plugin subprocess — chat adapter, runtime adapter, or project bridge."""

    def __init__(
        self,
        name: str,
        cmd: list[str],
        *,
        plugin_type: str,
        config: dict[str, Any],
        on_message: Callable[[Event | Command], None] | None = None,
    ) -> None:
        self.name = name
        self.cmd = cmd
        self.plugin_type = plugin_type
        self.config = config
        self.on_message = on_message
        self._proc: asyncio.subprocess.Process | None = None
        self._reader_task: asyncio.Task | None = None
        self._stderr_task: asyncio.Task | None = None

    @property
    def pid(self) -> int | None:
        return self._proc.pid if self._proc else None

    @property
    def is_running(self) -> bool:
        return self._proc is not None and self._proc.returncode is None

    async def start(self) -> None:
        self._proc = await asyncio.create_subprocess_exec(
            *self.cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        cfg_msg = ConfigMessage(plugin_type=self.plugin_type, config=self.config)
        assert self._proc.stdin is not None
        self._proc.stdin.write(encode_message(cfg_msg).encode())
        await self._proc.stdin.drain()
        self._reader_task = asyncio.create_task(
            self._read_stdout(), name=f"{self.name}.stdout"
        )
        self._stderr_task = asyncio.create_task(
            self._log_stderr(), name=f"{self.name}.stderr"
        )
        log.info("Plugin started: %s (pid %s)", self.name, self._proc.pid)

    async def write(self, msg: Event | Command) -> None:
        if not self._proc or not self._proc.stdin:
            log.warning("Cannot write to %s — process not running", self.name)
            return
        assert self._proc.stdin is not None
        self._proc.stdin.write(encode_message(msg).encode())
        await self._proc.stdin.drain()

    async def stop(self, timeout: float = 5.0) -> None:
        for task in (self._reader_task, self._stderr_task):
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        if self._proc:
            if self._proc.returncode is None:
                try:
                    self._proc.terminate()
                except ProcessLookupError:
                    pass
                try:
                    await asyncio.wait_for(self._proc.wait(), timeout=timeout)
                except asyncio.TimeoutError:
                    self._proc.kill()
            log.info("Plugin stopped: %s", self.name)

    async def _read_stdout(self) -> None:
        if not self._proc or not self._proc.stdout:
            return
        while True:
            line = await self._proc.stdout.readline()
            if not line:
                log.warning("Plugin %s stdout closed", self.name)
                break
            msg = decode_message(line.decode())
            if msg is not None and self.on_message:
                self.on_message(msg)

    async def _log_stderr(self) -> None:
        if not self._proc or not self._proc.stderr:
            return
        while True:
            line = await self._proc.stderr.readline()
            if not line:
                break
            log.debug("[%s] %s", self.name, line.decode().rstrip())
