"""Runtime state management for untethered processes.

Tracks opencode servers, host bridges, project bridges, and plugins
in a structured JSON file per domain.
"""

from __future__ import annotations

import atexit
import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)


@dataclass
class ProcessEntry:
    """Single process entry in runtime state."""

    type: str  # 'opencode_server', 'host_bridge', 'project_bridge', 'plugin'
    pid: int
    started_at: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ"))
    project: str | None = None
    bridge: str | None = None
    name: str | None = None
    port: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProcessEntry:
        return cls(**data)


@dataclass
class RuntimeState:
    """Complete runtime state for a domain."""

    domain: str
    created_at: str
    processes: list[ProcessEntry]

    def to_dict(self) -> dict[str, Any]:
        return {
            "domain": self.domain,
            "created_at": self.created_at,
            "processes": [p.to_dict() for p in self.processes],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RuntimeState:
        processes = [ProcessEntry.from_dict(p) for p in data.get("processes", [])]
        return cls(
            domain=data["domain"],
            created_at=data["created_at"],
            processes=processes,
        )


class RuntimeStateManager:
    """Manages runtime state for a domain.

    Tracks all processes (opencode servers, bridges, plugins) and provides
    overlap detection before startup.
    """

    def __init__(self, domain: str = "personal"):
        self.domain = domain
        self.state_path = (
            Path.home() / ".config" / "swain" / "domains" / f"{domain}.runtime.json"
        )
        self._current_entries: list[ProcessEntry] = []
        self._registered = False

    def _load_state(self) -> RuntimeState | None:
        """Load existing runtime state from disk."""
        if not self.state_path.exists():
            return None

        try:
            with open(self.state_path) as f:
                data = json.load(f)
            return RuntimeState.from_dict(data)
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            log.warning("Failed to load runtime state: %s", e)
            return None

    def _save_state(self, state: RuntimeState) -> None:
        """Save runtime state to disk."""
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_path, "w") as f:
            json.dump(state.to_dict(), f, indent=2)

    def _cleanup_stale_entries(self, state: RuntimeState) -> RuntimeState:
        """Remove entries for processes that are no longer alive."""
        alive_processes = []
        for entry in state.processes:
            if self._is_process_alive(entry.pid):
                alive_processes.append(entry)
            else:
                log.debug("Removing stale entry: PID %s (%s)", entry.pid, entry.type)

        return RuntimeState(
            domain=state.domain,
            created_at=state.created_at,
            processes=alive_processes,
        )

    def _is_process_alive(self, pid: int) -> bool:
        """Check if a process is still running."""
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False

    def check_for_overlaps(self, entry: ProcessEntry) -> list[ProcessEntry]:
        """Check if there are overlapping processes.

        Returns list of conflicting entries.
        """
        state = self._load_state()
        if not state:
            return []

        # Clean up stale entries first
        state = self._cleanup_stale_entries(state)

        conflicts = []
        for existing in state.processes:
            # Same type + project/bridge is an overlap
            if existing.type == entry.type:
                if entry.project and existing.project == entry.project:
                    conflicts.append(existing)
                elif entry.bridge and existing.bridge == entry.bridge:
                    conflicts.append(existing)
                elif not entry.project and not entry.bridge:
                    # Global singleton (like host_bridge)
                    conflicts.append(existing)

        return conflicts

    def register(self, entry: ProcessEntry) -> None:
        """Register a process in the runtime state.

        Raises RuntimeError if there's an overlap.
        """
        conflicts = self.check_for_overlaps(entry)
        if conflicts:
            conflict_info = ", ".join(f"{c.type} (PID {c.pid})" for c in conflicts)
            raise RuntimeError(
                f"Overlap detected for domain '{self.domain}': {conflict_info}. "
                f"Use 'pkill -f untethered' to clean up or choose a different domain."
            )

        # Load or create state
        state = self._load_state()
        if state:
            state = self._cleanup_stale_entries(state)
        else:
            state = RuntimeState(
                domain=self.domain,
                created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                processes=[],
            )

        # Add our entry
        state.processes.append(entry)
        self._current_entries.append(entry)

        # Save
        self._save_state(state)

        # Register cleanup on exit
        if not self._registered:
            atexit.register(self._cleanup_on_exit)
            self._registered = True

        log.info(
            "Registered %s (PID %s) in runtime state",
            entry.type,
            entry.pid,
        )

    def unregister(self, entry: ProcessEntry) -> None:
        """Unregister a process from the runtime state."""
        state = self._load_state()
        if not state:
            return

        state.processes = [p for p in state.processes if p.pid != entry.pid]
        self._save_state(state)

        if entry in self._current_entries:
            self._current_entries.remove(entry)

        log.debug("Unregistered %s (PID %s)", entry.type, entry.pid)

    def _cleanup_on_exit(self) -> None:
        """Cleanup all registered entries on process exit."""
        for entry in list(self._current_entries):
            try:
                self.unregister(entry)
            except Exception as e:
                log.debug("Failed to unregister %s: %s", entry.type, e)

    def get_state(self) -> RuntimeState | None:
        """Get current runtime state (cleaned of stale entries)."""
        state = self._load_state()
        if state:
            return self._cleanup_stale_entries(state)
        return None

    def is_process_registered(self, pid: int) -> bool:
        """Check if a specific PID is in the runtime state."""
        state = self.get_state()
        if not state:
            return False
        return any(p.pid == pid for p in state.processes)
