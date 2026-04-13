"""Project bridge plugin — subprocess entry point.

Spawned by the host kernel (ADR-038). Communicates via NDJSON over stdio:
  stdin line 0 : ConfigMessage from kernel (project config)
  stdin lines 1+: Commands from kernel to route to sessions/adapters
  stdout lines  : Events from sessions/adapters to kernel
  stderr        : logs (never mixed into stdout protocol stream)

The project bridge manages session lifecycle and spawns runtime adapter
subprocesses (e.g., ClaudeCodeAdapter). Events from adapters are written
to stdout; Commands from stdin are routed to the correct session.
"""
from __future__ import annotations

import asyncio
import logging
import sys

from untethered.protocol import (
    Command, ConfigMessage,
    decode_message, encode_message,
)
from untethered.bridges.project import ProjectBridge

log = logging.getLogger("untethered.plugins.project_bridge")


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

    def emit_event(event) -> None:
        """Write an Event as NDJSON to stdout (to the kernel)."""
        sys.stdout.write(encode_message(event))
        sys.stdout.flush()

    bridge = ProjectBridge(
        project=cfg["project"],
        project_dir=cfg.get("project_dir"),
        on_event=emit_event,
    )
    log.info("Project bridge started: %s", cfg["project"])

    # Read Commands from stdin, route to bridge sessions
    while True:
        line = await loop.run_in_executor(None, sys.stdin.readline)
        if not line:
            log.info("stdin closed — shutting down: %s", cfg["project"])
            return
        msg = decode_message(line)
        if isinstance(msg, Command):
            bridge.handle_command(msg)
        elif msg is not None:
            log.warning("Unexpected message type from kernel: %s", type(msg).__name__)


def main() -> None:
    asyncio.run(_amain())


if __name__ == "__main__":
    main()
