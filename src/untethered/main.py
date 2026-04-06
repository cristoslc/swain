"""Untethered Operator MVP — entry point.

Wires host bridge + project bridge + Zulip chat adapter + Claude Code
runtime adapter and runs the async event loop.

Usage:
    uv run python -m untethered.main --config bridge.yaml
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import signal
import sys
from pathlib import Path
from typing import Any

import zulip

from untethered.protocol import Event, Command
from untethered.bridges.host import HostBridge
from untethered.bridges.project import ProjectBridge
from untethered.adapters.zulip_chat import ZulipChatAdapter, format_event_for_zulip, parse_zulip_message
from untethered.adapters.claude_code import ClaudeCodeAdapter

log = logging.getLogger("untethered")


def load_config(path: str) -> dict[str, Any]:
    with open(path) as f:
        # Support both JSON and YAML (YAML is a superset of JSON)
        content = f.read()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            try:
                import yaml
                return yaml.safe_load(content)
            except ImportError:
                log.error("Config is not valid JSON and PyYAML is not installed")
                sys.exit(1)


async def run_bridge(config: dict[str, Any]) -> None:
    """Main async entry point — sets up all components and runs the event loop."""
    chat_config = config.get("chat", {})
    projects_config = config.get("projects", [])
    domain = config.get("domain", "personal")

    # Set up Zulip client
    zulip_client = zulip.Client(
        email=chat_config.get("bot_email", ""),
        api_key=chat_config.get("bot_api_key", ""),
        site=chat_config.get("server_url", ""),
    )

    # Set up host bridge
    host = HostBridge(domain=domain)

    # Set up Zulip chat adapter
    chat_adapter = ZulipChatAdapter(
        zulip_client=zulip_client,
        operator_email=chat_config.get("operator_email"),
        control_topic=chat_config.get("control_topic", "control"),
        on_command=host.route_chat_command,
    )

    # Wire host bridge → chat adapter
    def forward_to_chat(event: Event) -> None:
        stream = _resolve_stream(event, projects_config)
        chat_adapter.post_event(event, stream=stream)

    host.on_chat_event = forward_to_chat

    # Set up project bridges
    runtime_adapters: dict[str, ClaudeCodeAdapter] = {}

    for proj_config in projects_config:
        project_name = proj_config.get("name", "")
        project_dir = proj_config.get("path", "")
        stream_name = proj_config.get("stream", project_name)

        project_bridge = ProjectBridge(
            project=project_name,
            project_dir=project_dir,
            on_event=host.route_project_event,
        )

        host.register_project(
            project_name,
            on_command=project_bridge.handle_command,
        )

        log.info("Registered project: %s (stream: %s)", project_name, stream_name)

    # Start Zulip event polling
    log.info("Starting Zulip event polling...")
    await _poll_zulip_events(
        zulip_client, chat_adapter, host,
        projects_config=projects_config,
    )


def _resolve_stream(event: Event, projects_config: list[dict]) -> str | None:
    """Resolve which Zulip stream to post an event to."""
    bridge = event.bridge
    if bridge == "__host__" or not bridge:
        return None  # Use default stream
    for proj in projects_config:
        if proj.get("name") == bridge:
            return proj.get("stream", bridge)
    return bridge


async def _poll_zulip_events(
    client: Any,
    chat_adapter: ZulipChatAdapter,
    host: HostBridge,
    *,
    projects_config: list[dict],
) -> None:
    """Long-poll Zulip for new messages and route them as commands.

    Zulip's SDK calls are synchronous blocking HTTP. We run them in a thread
    pool executor so they don't freeze the event loop. get_events blocks for
    up to ~90s (Zulip's server-side long-poll timeout), so this is important.
    """
    loop = asyncio.get_event_loop()

    async def _register() -> tuple[str, int]:
        result = await loop.run_in_executor(
            None,
            lambda: client.register(
                event_types=["message"],
                narrow=[["is", "stream"]],
            ),
        )
        if result.get("result") != "success":
            raise RuntimeError(f"Failed to register Zulip event queue: {result}")
        log.info("Zulip event queue registered: %s", result["queue_id"])
        return result["queue_id"], result["last_event_id"]

    try:
        queue_id, last_event_id = await _register()
    except Exception as e:
        log.error("Cannot start Zulip polling: %s", e)
        return

    while True:
        try:
            events_result = await loop.run_in_executor(
                None,
                lambda: client.get_events(
                    queue_id=queue_id,
                    last_event_id=last_event_id,
                ),
            )
        except Exception as e:
            log.error("Zulip polling error: %s", e)
            await asyncio.sleep(5)
            continue

        if events_result.get("code") == "BAD_EVENT_QUEUE_ID":
            log.warning("Zulip event queue expired, re-registering")
            try:
                queue_id, last_event_id = await _register()
            except Exception as e:
                log.error("Re-registration failed: %s", e)
                await asyncio.sleep(5)
            continue

        if events_result.get("result") != "success":
            log.warning("Zulip events error: %s", events_result)
            await asyncio.sleep(5)
            continue

        for event in events_result.get("events", []):
            last_event_id = max(last_event_id, event.get("id", last_event_id))

            if event.get("type") == "message":
                message = event.get("message", {})
                # Skip bot's own messages
                if message.get("sender_email") == client.email:
                    continue

                # Determine which bridge this message targets
                stream_name = message.get("display_recipient", "")
                bridge = _stream_to_bridge(stream_name, projects_config)
                if bridge:
                    cmd = parse_zulip_message(
                        message, bridge=bridge,
                        control_topic=chat_adapter.control_topic,
                    )
                    if cmd:
                        host.route_chat_command(cmd)


def _stream_to_bridge(stream_name: str, projects_config: list[dict]) -> str | None:
    """Map a Zulip stream name back to a project bridge name."""
    for proj in projects_config:
        if proj.get("stream", proj.get("name", "")) == stream_name:
            return proj["name"]
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Untethered Operator — chat bridge")
    parser.add_argument("--config", required=True, help="Path to bridge config file")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    config = load_config(args.config)

    # Handle graceful shutdown
    loop = asyncio.new_event_loop()

    def shutdown(sig: int, frame: Any) -> None:
        log.info("Received signal %s, shutting down...", sig)
        loop.stop()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        loop.run_until_complete(run_bridge(config))
    except KeyboardInterrupt:
        log.info("Shutting down...")
    finally:
        loop.close()


if __name__ == "__main__":
    main()
