"""Untethered Operator — host kernel entry point.

Loads bridge config, spawns plugin subprocesses (chat adapter + project
bridges), and routes NDJSON between them per ADR-038 and ADR-039.

Usage:
    uv run python -m untethered.main --config bridge.json
    uv run python -m untethered.main --domain personal
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import signal
import sys
from pathlib import Path
from typing import Any

from untethered.kernel import HostKernel

log = logging.getLogger("untethered")


def load_config(path: str) -> dict[str, Any]:
    with open(path) as f:
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


def resolve_config(args: argparse.Namespace) -> dict[str, Any]:
    """Resolve config from --config path or --domain name.

    Domain lookup: ~/.config/swain/domains/<domain>.json
    Falls back to ./bridge.json if neither flag is given.
    """
    if args.config:
        return load_config(args.config)

    domain = args.domain or "personal"
    zone_path = Path.home() / ".config" / "swain" / "domains" / f"{domain}.json"
    if zone_path.exists():
        log.info("Loading zone config: %s", zone_path)
        return load_config(str(zone_path))

    fallback = Path("bridge.json")
    if fallback.exists():
        log.info("Loading fallback config: %s", fallback)
        return load_config(str(fallback))

    log.error(
        "No config found. Use --config <path> or --domain <name> "
        "(looks in ~/.config/swain/domains/<name>.json)"
    )
    sys.exit(1)


async def run(config: dict[str, Any]) -> None:
    kernel = HostKernel()
    await kernel.run(config)


def main() -> None:
    parser = argparse.ArgumentParser(description="Untethered Operator — host kernel")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--config", help="Path to bridge config file (JSON or YAML)")
    group.add_argument("--domain", help="Security domain name (loads ~/.config/swain/domains/<name>.json)")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    config = resolve_config(args)

    loop = asyncio.new_event_loop()

    def _shutdown(sig: int, _frame: Any) -> None:
        log.info("Signal %s received, shutting down", sig)
        for task in asyncio.all_tasks(loop):
            task.cancel()

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    try:
        loop.run_until_complete(run(config))
    except KeyboardInterrupt:
        log.info("Interrupted")
    finally:
        loop.close()


if __name__ == "__main__":
    main()
