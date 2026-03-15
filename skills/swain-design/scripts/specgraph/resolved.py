"""Type-aware artifact resolution logic.

Matches the bash jq is_resolved / is_status_resolved functions exactly.
SPEC-038: is_resolved now uses the artifact's `track` field when present,
falling back to type-based inference for migration compatibility.
"""

from __future__ import annotations

# Terminal/resolved statuses (any type)
_TERMINAL_STATUSES = frozenset(
    {
        "Complete",
        "Retired",
        "Superseded",
        "Abandoned",
        "Implemented",
        "Adopted",
        "Validated",
        "Archived",
        "Sunset",
        "Deprecated",
        "Verified",
        "Declined",
    }
)

# Standing-track types used for migration fallback when `track` field is absent
_STANDING_TYPES = frozenset(
    {"VISION", "JOURNEY", "PERSONA", "ADR", "RUNBOOK", "DESIGN"}
)

# Container-track types for migration fallback
_CONTAINER_TYPES = frozenset({"EPIC", "SPIKE", "INITIATIVE"})


def is_status_resolved(status: str) -> bool:
    """Check if a status string is a resolved/terminal status."""
    return status in _TERMINAL_STATUSES


def _infer_track(artifact_type: str) -> str:
    """Infer lifecycle track from artifact type name (migration fallback).

    Used when the artifact does not have a `track` field in its frontmatter.
    """
    if artifact_type in _STANDING_TYPES:
        return "standing"
    if artifact_type in _CONTAINER_TYPES:
        return "container"
    return "implementable"


def is_resolved(artifact_type: str, status: str, track: str | None = None) -> bool:
    """Check if an artifact is resolved, considering its track.

    Uses the artifact's `track` field if present (SPEC-038); falls back to
    type-based inference for artifacts that predate the track field migration.

    Standing-track artifacts (track='standing') are considered resolved when
    Active, in addition to all terminal statuses.
    """
    if is_status_resolved(status):
        return True
    effective_track = track if track else _infer_track(artifact_type)
    return effective_track == "standing" and status == "Active"
