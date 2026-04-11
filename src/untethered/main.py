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
from untethered.runtime_state import ProcessEntry, RuntimeStateManager

log = logging.getLogger("untethered")


def check_and_register_runtime(domain: str) -> RuntimeStateManager:
    """Check for overlapping servers and register this one."""
    manager = RuntimeStateManager(domain)

    entry = ProcessEntry(
        type="host_bridge",
        pid=os.getpid(),
    )

    manager.register(entry)
    return manager


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


def _show_status(domain: str) -> None:
    """Display runtime status for a domain."""
    manager = RuntimeStateManager(domain)
    state = manager.get_state()

    if not state or not state.processes:
        print(f"No active processes for domain '{domain}'.")
        return

    print(f"Runtime status for domain '{domain}':")
    print(f"  Created: {state.created_at}")
    print(f"  Processes: {len(state.processes)}")
    print("")

    # Group by type
    by_type: dict[str, list[Any]] = {}
    for p in state.processes:
        by_type.setdefault(p.type, []).append(p)

    for proc_type, procs in sorted(by_type.items()):
        print(f"  {proc_type}:")
        for p in procs:
            details = []
            if p.project:
                details.append(f"project={p.project}")
            if p.bridge:
                details.append(f"bridge={p.bridge}")
            if p.port:
                details.append(f"port={p.port}")
            if p.name:
                details.append(f"name={p.name}")

            detail_str = f" ({', '.join(details)})" if details else ""
            print(f"    PID {p.pid}{detail_str} — started {p.started_at}")


def _cleanup_stale(domain: str) -> None:
    """Clean up stale runtime entries for a domain."""
    manager = RuntimeStateManager(domain)

    # Load and clean stale entries
    state = manager._load_state()
    if not state:
        print(f"No runtime state found for domain '{domain}'.")
        return

    original_count = len(state.processes)
    cleaned_state = manager._cleanup_stale_entries(state)
    cleaned_count = original_count - len(cleaned_state.processes)

    if cleaned_count > 0:
        manager._save_state(cleaned_state)
        print(f"Cleaned up {cleaned_count} stale entries for domain '{domain}'.")
        if cleaned_state.processes:
            print(f"  {len(cleaned_state.processes)} active processes remain.")
    else:
        print(f"No stale entries found for domain '{domain}'.")
        if cleaned_state.processes:
            print(f"  {len(cleaned_state.processes)} processes are active.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Untethered Operator — host kernel")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--config", help="Path to bridge config file (JSON or YAML)")
    group.add_argument(
        "--domain",
        help="Security domain name (loads ~/.config/swain/domains/<name>.json)",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show runtime status for the domain and exit",
    )
    parser.add_argument(
        "--cleanup-stale",
        action="store_true",
        help="Clean up stale runtime entries for the domain and exit",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    # Handle status command
    if args.status:
        domain = args.domain or "personal"
        _show_status(domain)
        return

    # Handle cleanup-stale command
    if args.cleanup_stale:
        domain = args.domain or "personal"
        _cleanup_stale(domain)
        return

    config = resolve_config(args)
    domain = config.get("domain", args.domain or "personal")

    # Check for overlapping servers and register this one
    try:
        runtime_manager = check_and_register_runtime(domain)
    except RuntimeError as e:
        log.error("%s", e)
        sys.exit(1)

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
