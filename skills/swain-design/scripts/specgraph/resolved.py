"""Type-aware artifact resolution logic.

Matches the bash jq is_resolved / is_status_resolved functions exactly.
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

# Standing-track types also resolve at "Active"
_STANDING_TYPES = frozenset(
    {"VISION", "JOURNEY", "PERSONA", "ADR", "RUNBOOK", "DESIGN"}
)


def is_status_resolved(status: str) -> bool:
    """Check if a status string is a resolved/terminal status."""
    return status in _TERMINAL_STATUSES


def is_resolved(artifact_type: str, status: str) -> bool:
    """Check if an artifact is resolved, considering its type.

    Standing-track types (VISION, JOURNEY, PERSONA, ADR, RUNBOOK, DESIGN)
    are considered resolved when Active, in addition to terminal statuses.
    """
    if is_status_resolved(status):
        return True
    if artifact_type in _STANDING_TYPES and status == "Active":
        return True
    return False
