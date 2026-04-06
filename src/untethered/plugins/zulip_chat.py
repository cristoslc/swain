"""Zulip chat adapter plugin — subprocess entry point.

Spawned by the host kernel (ADR-038). Communicates via NDJSON over stdio:
  stdin line 0 : ConfigMessage from kernel (Zulip credentials + routing maps)
  stdin lines 1+: Events from kernel to post to Zulip
  stdout lines  : Commands to kernel from operator Zulip messages
  stderr        : logs (never mixed into stdout protocol stream)

The kernel reads Commands from this process's stdout and routes them to the
correct project bridge. It writes Events to this process's stdin for posting.
"""
from __future__ import annotations

import asyncio
import logging
import sys
from typing import Callable

import zulip

from untethered.protocol import (
    Event, Command, ConfigMessage,
    decode_message, encode_message,
)
from untethered.adapters.zulip_chat import format_event_for_zulip, parse_zulip_message

log = logging.getLogger("untethered.plugins.zulip_chat")


def _emit(cmd: Command) -> None:
    """Write a Command as NDJSON to stdout (to the kernel)."""
    sys.stdout.write(encode_message(cmd))
    sys.stdout.flush()


async def _poll_zulip(
    client: zulip.Client,
    stream_to_project: dict[str, str],
    control_topic: str,
    emit: Callable[[Command], None],
    loop: asyncio.AbstractEventLoop,
) -> None:
    """Long-poll Zulip for operator messages, emit Commands to kernel via stdout."""

    async def _register() -> tuple[str, int]:
        result = await loop.run_in_executor(
            None,
            lambda: client.register(
                event_types=["message"],
                narrow=[["is", "stream"]],
            ),
        )
        if result.get("result") != "success":
            raise RuntimeError(f"Zulip register failed: {result}")
        log.info("Zulip event queue: %s", result["queue_id"])
        return result["queue_id"], result["last_event_id"]

    try:
        queue_id, last_event_id = await _register()
    except Exception as exc:
        log.error("Cannot start Zulip polling: %s", exc)
        return

    while True:
        try:
            result = await loop.run_in_executor(
                None,
                lambda: client.get_events(
                    queue_id=queue_id,
                    last_event_id=last_event_id,
                ),
            )
        except Exception as exc:
            log.error("Zulip poll error: %s", exc)
            await asyncio.sleep(5)
            continue

        if result.get("code") == "BAD_EVENT_QUEUE_ID":
            log.warning("Zulip queue expired, re-registering")
            try:
                queue_id, last_event_id = await _register()
            except Exception as exc:
                log.error("Re-registration failed: %s", exc)
                await asyncio.sleep(5)
            continue

        if result.get("result") != "success":
            log.warning("Zulip events error: %s", result)
            await asyncio.sleep(5)
            continue

        for ev in result.get("events", []):
            last_event_id = max(last_event_id, ev.get("id", last_event_id))
            if ev.get("type") != "message":
                continue
            message = ev.get("message", {})
            if message.get("sender_email") == client.email:
                continue
            stream_name = message.get("display_recipient", "")
            bridge = stream_to_project.get(stream_name, stream_name)
            cmd = parse_zulip_message(
                message, bridge=bridge or "", control_topic=control_topic,
            )
            if cmd:
                emit(cmd)


async def _relay_events(
    client: zulip.Client,
    project_to_stream: dict[str, str],
    operator_email: str | None,
    control_topic: str,
    loop: asyncio.AbstractEventLoop,
) -> None:
    """Read Events from stdin (kernel), post them to Zulip."""
    while True:
        line = await loop.run_in_executor(None, sys.stdin.readline)
        if not line:
            log.info("stdin closed")
            return
        msg = decode_message(line)
        if not isinstance(msg, Event):
            continue
        stream = project_to_stream.get(msg.bridge or "", msg.bridge or "")
        zulip_msg = format_event_for_zulip(
            msg,
            operator_email=operator_email,
            control_topic=control_topic,
        )
        await loop.run_in_executor(
            None,
            lambda: client.send_message({
                "type": "stream",
                "to": stream,
                "topic": zulip_msg["topic"],
                "content": zulip_msg["content"],
            }),
        )


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
    client = zulip.Client(
        email=cfg["bot_email"],
        api_key=cfg["bot_api_key"],
        site=cfg["server_url"],
    )

    await asyncio.gather(
        _poll_zulip(
            client,
            cfg.get("stream_to_project", {}),
            cfg.get("control_topic", "control"),
            _emit,
            loop,
        ),
        _relay_events(
            client,
            cfg.get("project_to_stream", {}),
            cfg.get("operator_email"),
            cfg.get("control_topic", "control"),
            loop,
        ),
    )


def main() -> None:
    asyncio.run(_amain())


if __name__ == "__main__":
    main()
