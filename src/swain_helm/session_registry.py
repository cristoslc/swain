"""Persistent session registry — JSON file keyed by worktree branch name.

Per SPEC-324, the SessionRegistry persists session state to
<project-root>/.swain/swain-helm/session-registry.json so bridge
restarts don't lose tracking. Reconciles with live opencode sessions
on startup.
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

REGISTRY_FILENAME = "session-registry.json"


class SessionRegistry:
    """JSON-backed session registry keyed by worktree branch name."""

    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        resolved = Path(project_dir).resolve()
        registry_path = resolved / ".swain" / "swain-helm" / REGISTRY_FILENAME
        if not str(registry_path).startswith(str(resolved)):
            raise ValueError(
                f"Registry path {registry_path} escapes project root {resolved}"
            )
        self._path = registry_path
        self._data: dict[str, dict[str, Any]] = {}

    @property
    def path(self) -> Path:
        return self._path

    def read(self) -> dict[str, dict[str, Any]]:
        """Read the registry from disk. Returns empty dict if missing."""
        if not self._path.exists():
            self._data = {}
            return self._data
        try:
            raw = self._path.read_text()
            self._data = json.loads(raw) if raw.strip() else {}
        except (json.JSONDecodeError, OSError) as exc:
            log.warning("Failed to read session registry: %s", exc)
            self._data = {}
        return self._data

    def write(self) -> None:
        """Write the full registry dict to disk (atomic)."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_suffix(".tmp")
        try:
            tmp.write_text(json.dumps(self._data, indent=2, sort_keys=True) + "\n")
            tmp.chmod(0o600)
            tmp.replace(self._path)
        except OSError as exc:
            log.error("Failed to write session registry: %s", exc)
            if tmp.exists():
                tmp.unlink()

    def update_entry(self, branch: str, **fields: Any) -> None:
        """Merge fields into a registry entry and write."""
        entry = self._data.setdefault(branch, {})
        for k, v in fields.items():
            entry[k] = v
        entry["last_activity"] = time.time()
        self.write()

    def delete_entry(self, branch: str) -> None:
        """Remove a registry entry and write."""
        self._data.pop(branch, None)
        self.write()

    def get_entry(self, branch: str) -> dict[str, Any] | None:
        """Get a single entry by branch name."""
        return self._data.get(branch)

    @property
    def entries(self) -> dict[str, dict[str, Any]]:
        return self._data

    def reconcile(self, live_session_ids: set[str]) -> list[str]:
        """Remove entries whose opencode_session_id is not in live set.

        Returns list of removed branch names.
        """
        removed: list[str] = []
        for branch, entry in list(self._data.items()):
            sid = entry.get("opencode_session_id")
            state = entry.get("state", "")
            if sid and sid not in live_session_ids and state != "dead":
                log.info(
                    "Reconcile: removing orphaned entry for %s (sid=%s)", branch, sid
                )
                removed.append(branch)
                self._data[branch]["state"] = "dead"
        if removed:
            self.write()
        return removed

    def cleanup_dead(self, existing_paths: set[str] | None = None) -> list[str]:
        """Remove dead entries and entries whose worktree_path no longer exists.

        Returns list of removed branch names.
        """
        removed: list[str] = []
        for branch, entry in list(self._data.items()):
            state = entry.get("state", "")
            wt_path = entry.get("worktree_path", "")
            if state == "dead":
                removed.append(branch)
                del self._data[branch]
            elif (
                existing_paths is not None and wt_path and wt_path not in existing_paths
            ):
                removed.append(branch)
                del self._data[branch]
        if removed:
            self.write()
        return removed
