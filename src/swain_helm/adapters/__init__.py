"""Adapter subprocess runner — shared _amain boilerplate (ADR-038).

All runtime/chat adapter plugins share the same startup sequence:
read ConfigMessage from stdin line 0, create an adapter instance, then
enter a read-decode-dispatch loop. This module factors out that pattern
so each adapter only provides its factory function.
"""

from __future__ import annotations

import asyncio
import logging
import sys
from typing import Any, Callable

from swain_helm.protocol import (
    Command,
    ConfigMessage,
    Event,
    decode_message,
    encode_message,
)

log = logging.getLogger(__name__)


def _emit(event: Event) -> None:
    """Write a protocol event to stdout and flush."""
    sys.stdout.write(encode_message(event))
    sys.stdout.flush()


async def run_adapter(
    factory: Callable[[ConfigMessage, Callable[[Event], None]], Any],
    *,
    setup: Callable[[Any, ConfigMessage], Any] | None = None,
    default_session_id: str = "sess-unknown",
) -> None:
    """Run an adapter plugin subprocess.

    Reads a ConfigMessage from stdin line 0, calls factory(cfg, emit) to
    create the adapter, then enters the stdin command loop. Each adapter
    only needs to provide a factory function. Optional setup(adapter, cfg)
    is called after creation for pre-loop initialization.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        stream=sys.stderr,
    )
    loop = asyncio.get_running_loop()

    config_line = await loop.run_in_executor(None, sys.stdin.readline)
    config_msg = decode_message(config_line)
    if not isinstance(config_msg, ConfigMessage):
        log.error(
            "Expected ConfigMessage on stdin line 0, got: %r",
            config_line[:100],
        )
        sys.exit(1)

    adapter = factory(config_msg, _emit)

    if setup:
        await setup(adapter, config_msg)

    while True:
        line = await loop.run_in_executor(None, sys.stdin.readline)
        if not line:
            log.info("stdin closed")
            break
        msg = decode_message(line)
        if isinstance(msg, Command):
            await adapter.send_command(msg)
        elif msg is not None:
            log.warning("Unexpected message type: %s", type(msg).__name__)

    if hasattr(adapter, "stop"):
        await adapter.stop()
