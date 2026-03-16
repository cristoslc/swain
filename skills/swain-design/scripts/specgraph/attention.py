"""Attention tracking — computes operator attention distribution from git history.

Scans git log for artifact file changes, attributes each to a vision via the
parent chain, and aggregates into a per-vision activity summary.

No persistent state — recomputed from git history on each invocation.
"""

from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from .queries import _find_vision_ancestor

_ARTIFACT_ID_RE = re.compile(r"\(([A-Z]+-\d+)\)")


def parse_git_log_entry(filepath: str) -> str | None:
    """Extract artifact ID from a docs/ file path.

    Looks for (ARTIFACT-NNN) pattern in the path.
    Returns None for non-artifact files.
    """
    if not filepath.startswith("docs/"):
        return None
    match = _ARTIFACT_ID_RE.search(filepath)
    return match.group(1) if match else None


def attribute_to_vision(
    artifact_id: str,
    nodes: dict,
    edges: list[dict],
) -> str:
    """Attribute an artifact to its vision ancestor. Returns '_unaligned' if none."""
    vision = _find_vision_ancestor(artifact_id, nodes, edges)
    return vision or "_unaligned"


def scan_git_log(
    repo_root: Path,
    days: int = 30,
) -> list[tuple[str, datetime]]:
    """Scan git log for artifact file changes in the last N days.

    Returns list of (artifact_id, commit_date) tuples.
    """
    try:
        result = subprocess.run(
            [
                "git", "log",
                f"--since={days} days ago",
                "--name-only",
                "--pretty=format:%aI",
                "--diff-filter=AMRC",
                "--", "docs/",
            ],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

    entries: list[tuple[str, datetime]] = []
    current_date: datetime | None = None

    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        # Try parsing as ISO date first
        try:
            current_date = datetime.fromisoformat(line)
            continue
        except ValueError:
            pass
        # Must be a file path
        if current_date is not None:
            artifact_id = parse_git_log_entry(line)
            if artifact_id:
                entries.append((artifact_id, current_date))

    return entries


def compute_attention(
    log_entries: list[tuple[str, datetime]],
    nodes: dict,
    edges: list[dict],
) -> dict[str, dict]:
    """Compute attention distribution from parsed log entries.

    Returns: {vision_id: {transitions: N, last_activity: ISO date string}}
    """
    attention: dict[str, dict] = {}

    for artifact_id, commit_date in log_entries:
        vision = attribute_to_vision(artifact_id, nodes, edges)
        if vision not in attention:
            attention[vision] = {"transitions": 0, "last_activity": None}
        attention[vision]["transitions"] += 1
        date_str = commit_date.isoformat()
        if attention[vision]["last_activity"] is None or date_str > attention[vision]["last_activity"]:
            attention[vision]["last_activity"] = date_str

    return attention


def compute_drift(
    attention: dict[str, dict],
    nodes: dict,
    drift_thresholds: dict | None = None,
) -> list[dict]:
    """Detect attention drift — visions with zero activity exceeding threshold.

    Default thresholds: high=14 days, medium=28 days, low=never.
    Returns list of {vision_id, weight, days_since_activity, threshold}.
    """
    if drift_thresholds is None:
        drift_thresholds = {"high": 14, "medium": 28}

    now = datetime.now(timezone.utc)
    drifting: list[dict] = []

    for node_id, node in nodes.items():
        if node.get("type", "").upper() != "VISION":
            continue
        weight_label = node.get("priority_weight", "") or "medium"
        if weight_label == "low":
            continue  # Low-weight visions don't trigger drift

        threshold_days = drift_thresholds.get(weight_label, 28)
        vision_attention = attention.get(node_id, {})
        last_activity = vision_attention.get("last_activity")

        if last_activity:
            last_dt = datetime.fromisoformat(last_activity)
            days_since = (now - last_dt).days
        else:
            days_since = 999  # No activity ever

        if days_since >= threshold_days:
            drifting.append({
                "vision_id": node_id,
                "weight": weight_label,
                "days_since_activity": days_since,
                "threshold": threshold_days,
            })

    return drifting
