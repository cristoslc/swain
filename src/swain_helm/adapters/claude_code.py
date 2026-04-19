"""Claude Code runtime adapter plugin.

Wraps `claude --output-format stream-json --input-format stream-json` and
translates between Claude Code's native event format and the kernel's
published NDJSON protocol.
"""

from __future__ import annotations

import asyncio
import json
import logging
import subprocess
import sys
from typing import Any, Callable

from swain_helm.protocol import (
    Event,
    Command,
    ConfigMessage,
    encode_message,
    decode_message,
)

log = logging.getLogger(__name__)


def parse_claude_stream_event(
    raw: dict[str, Any],
    bridge: str,
    session_id: str | None = None,
) -> Event | list[Event] | None:
    """Translate a Claude Code stream-json event into protocol Event(s).

    Claude Code emits these top-level types:
    - system (init, result)
    - user (echoed prompts)
    - assistant (text, tool_use content blocks)
    - tool (tool results)
    """
    event_type = raw.get("type")

    if event_type == "system":
        subtype = raw.get("subtype")
        sid = raw.get("session_id") or session_id
        if subtype == "init":
            return Event.session_spawned(
                bridge=bridge,
                session_id=sid or "",
                runtime="claude",
            )
        if subtype == "result":
            reason = raw.get("result", "unknown")
            return Event.session_died(
                bridge=bridge,
                session_id=sid or "",
                reason=str(reason),
            )
        return None

    if event_type == "assistant":
        message = raw.get("message", {})
        content_blocks = message.get("content", [])
        events: list[Event] = []
        sid = session_id or ""

        for block in content_blocks:
            block_type = block.get("type")
            if block_type == "text":
                events.append(
                    Event.text_output(
                        bridge=bridge,
                        session_id=sid,
                        content=block.get("text", ""),
                    )
                )
            elif block_type == "tool_use":
                events.append(
                    Event.tool_call(
                        bridge=bridge,
                        session_id=sid,
                        tool_name=block.get("name", ""),
                        input=block.get("input", {}),
                        call_id=block.get("id", ""),
                    )
                )

        if len(events) == 1:
            return events[0]
        return events if events else None

    if event_type == "tool":
        message = raw.get("message", {})
        call_id = message.get("tool_use_id", "")
        output = message.get("content", "")
        if isinstance(output, list):
            output = "\n".join(b.get("text", "") for b in output if isinstance(b, dict))
        return Event.tool_result(
            bridge=bridge,
            session_id=session_id or "",
            call_id=call_id,
            output=str(output),
            success=True,
        )

    return None


def format_command_for_claude(cmd: Command) -> str:
    """Translate a protocol Command into Claude Code stream-json input format.

    Claude Code's --input-format stream-json expects:
    - User messages: {"type": "user", "message": {"role": "user", "content": "..."}}
    - Permission responses: {"type": "permission", "permission": {"id": "...", "allowed": true/false}}
    """
    if cmd.type == "send_prompt":
        return json.dumps(
            {
                "type": "user",
                "message": {"role": "user", "content": cmd.payload.get("text", "")},
            }
        )

    if cmd.type == "approve":
        return json.dumps(
            {
                "type": "permission",
                "permission": {
                    "id": cmd.payload.get("call_id", ""),
                    "allowed": cmd.payload.get("approved", False),
                },
            }
        )

    if cmd.type == "cancel":
        return json.dumps({"type": "cancel"})

    log.warning("Unsupported command type for Claude adapter: %s", cmd.type)
    return ""


class ClaudeCodeAdapter:
    """Manages a Claude Code subprocess with streaming JSON I/O.

    Spawns `claude` with --output-format stream-json and --input-format stream-json.
    Reads NDJSON events from stdout, writes commands to stdin.
    """

    def __init__(
        self,
        bridge: str,
        session_id: str,
        *,
        allowed_tools: list[str] | None = None,
        project_dir: str | None = None,
        on_event: Callable[[Event], None] | None = None,
    ):
        self.bridge = bridge
        self.session_id = session_id
        self.allowed_tools = allowed_tools
        self.project_dir = project_dir
        self.on_event = on_event
        self._process: asyncio.subprocess.Process | None = None
        self._reader_task: asyncio.Task | None = None

    async def start(self, prompt: str | None = None) -> None:
        """Start the Claude Code process."""
        cmd = [
            "claude",
            "--output-format",
            "stream-json",
            "--input-format",
            "stream-json",
        ]
        if self.allowed_tools:
            cmd.extend(["--allowedTools", ",".join(self.allowed_tools)])
        if prompt:
            cmd.extend(["--prompt", prompt])

        self._process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.project_dir,
        )
        self._reader_task = asyncio.create_task(self._read_stdout())

    async def _read_stdout(self) -> None:
        """Read NDJSON lines from Claude's stdout and emit protocol events."""
        if not self._process or not self._process.stdout:
            return
        while True:
            line = await self._process.stdout.readline()
            if not line:
                break
            try:
                raw = json.loads(line.decode())
            except (json.JSONDecodeError, UnicodeDecodeError):
                log.warning("Malformed line from Claude: %s", line[:200])
                continue

            result = parse_claude_stream_event(
                raw,
                bridge=self.bridge,
                session_id=self.session_id,
            )
            if result and self.on_event:
                if isinstance(result, list):
                    for event in result:
                        self.on_event(event)
                else:
                    self.on_event(result)

    async def send_command(self, cmd: Command) -> None:
        """Send a command to the Claude Code process via stdin."""
        if not self._process or not self._process.stdin:
            log.warning("Cannot send command — process not running")
            return
        formatted = format_command_for_claude(cmd)
        if formatted:
            self._process.stdin.write((formatted + "\n").encode())
            await self._process.stdin.drain()

    async def stop(self) -> None:
        """Stop the Claude Code process."""
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


# ---------------------------------------------------------------------------
# Subprocess entry point (ADR-038)
# ---------------------------------------------------------------------------


async def _amain() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        stream=sys.stderr,
    )
    loop = asyncio.get_running_loop()

    config_line = await loop.run_in_executor(None, sys.stdin.readline)
    config_msg = decode_message(config_line)
    if not isinstance(config_msg, ConfigMessage):
        log.error("Expected ConfigMessage on stdin line 0, got: %r", config_line[:100])
        sys.exit(1)

    cfg = config_msg.config
    bridge = cfg.get("bridge", "swain")
    session_id = cfg.get("session_id", "sess-claude")
    project_dir = cfg.get("project_dir")
    allowed_tools = cfg.get("allowed_tools")
    prompt = cfg.get("prompt")

    def emit(event: Event) -> None:
        sys.stdout.write(encode_message(event))
        sys.stdout.flush()

    adapter = ClaudeCodeAdapter(
        bridge=bridge,
        session_id=session_id,
        allowed_tools=allowed_tools,
        project_dir=project_dir,
        on_event=emit,
    )

    await adapter.start(prompt=prompt)

    while True:
        line = await loop.run_in_executor(None, sys.stdin.readline)
        if not line:
            log.info("stdin closed")
            break
        msg = decode_message(line)
        if isinstance(msg, Command):
            formatted = format_command_for_claude(msg)
            if formatted and adapter._process and adapter._process.stdin:
                adapter._process.stdin.write((formatted + "\n").encode())
                await adapter._process.stdin.drain()
        elif msg is not None:
            log.warning("Unexpected message type: %s", type(msg).__name__)

    await adapter.stop()


def main() -> None:
    asyncio.run(_amain())


if __name__ == "__main__":
    main()
