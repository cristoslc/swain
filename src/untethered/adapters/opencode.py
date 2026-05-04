"""OpenCode runtime adapter.

Wraps `opencode run --format json` and translates between OpenCode's native
event format and the kernel's published NDJSON protocol.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Callable

from untethered.protocol import Event, Command

log = logging.getLogger(__name__)


def parse_opencode_event(
    raw: dict[str, Any],
    bridge: str,
    session_id: str | None = None,
) -> Event | list[Event] | None:
    """Translate an OpenCode JSON event into protocol Event(s)."""
    event_type = raw.get("type")
    sid = session_id or ""

    if event_type == "text":
        content = raw.get("content", "")
        if content:
            return Event.text_output(bridge=bridge, session_id=sid, content=content)

    elif event_type == "tool_call":
        return Event.tool_call(
            bridge=bridge, session_id=sid,
            tool_name=raw.get("name", ""),
            input=raw.get("input", {}),
            call_id=raw.get("id", ""),
        )

    elif event_type == "tool_result":
        return Event.tool_result(
            bridge=bridge, session_id=sid,
            call_id=raw.get("id", ""),
            output=raw.get("output", ""),
            success=raw.get("success", True),
        )

    elif event_type == "error":
        error = raw.get("error", {})
        msg = error.get("message", str(error)) if isinstance(error, dict) else str(error)
        return Event.text_output(bridge=bridge, session_id=sid, content=f"Error: {msg}")

    elif event_type == "finish":
        return Event.session_died(
            bridge=bridge, session_id=sid,
            reason=raw.get("reason", "completed"),
        )

    return None


class OpenCodeAdapter:
    """Manages an opencode run subprocess with JSON I/O.

    Spawns `opencode run --format json` and reads NDJSON events from stdout.
    """

    def __init__(
        self,
        bridge: str,
        session_id: str,
        *,
        project_dir: str | None = None,
        on_event: Callable[[Event], None] | None = None,
    ):
        self.bridge = bridge
        self.session_id = session_id
        self.project_dir = project_dir
        self.on_event = on_event
        self._process: asyncio.subprocess.Process | None = None
        self._reader_task: asyncio.Task | None = None

    async def start(self, prompt: str | None = None) -> None:
        cmd = ["opencode", "run", "--format", "json"]
        if prompt:
            cmd.append(prompt)

        self._process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.project_dir,
        )

        # Emit session_spawned
        if self.on_event:
            self.on_event(Event.session_spawned(
                bridge=self.bridge, session_id=self.session_id,
                runtime="opencode",
            ))

        self._reader_task = asyncio.create_task(self._read_stdout())

    async def _read_stdout(self) -> None:
        if not self._process or not self._process.stdout:
            return
        while True:
            line = await self._process.stdout.readline()
            if not line:
                break
            try:
                raw = json.loads(line.decode())
            except (json.JSONDecodeError, UnicodeDecodeError):
                log.warning("Malformed line from opencode: %s", line[:200])
                continue

            result = parse_opencode_event(
                raw, bridge=self.bridge, session_id=self.session_id,
            )
            if result and self.on_event:
                if isinstance(result, list):
                    for event in result:
                        self.on_event(event)
                else:
                    self.on_event(result)

        # Process exited — emit session_died if we haven't already
        if self.on_event:
            self.on_event(Event.session_died(
                bridge=self.bridge, session_id=self.session_id,
                reason="process exited",
            ))

    async def send_command(self, cmd: Command) -> None:
        """opencode run is single-shot — no stdin commands supported."""
        log.warning("opencode run does not support interactive commands: %s", cmd.type)

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
