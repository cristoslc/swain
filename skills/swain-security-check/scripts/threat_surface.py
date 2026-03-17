"""Threat surface detection heuristic for tk tasks.

Determines if a task touches a security-sensitive surface based on
task metadata: title, description, tags, SPEC acceptance criteria text,
and file paths touched.

Part of SPEC-062: Threat Surface Detection Heuristic.
"""

from dataclasses import dataclass, field


@dataclass
class ThreatSurfaceResult:
    """Result of threat surface detection."""
    is_security_sensitive: bool = False
    categories: list[str] = field(default_factory=list)


def detect_threat_surface(
    title: str = "",
    description: str = "",
    tags: list[str] | None = None,
    spec_criteria: str = "",
    file_paths: list[str] | None = None,
) -> ThreatSurfaceResult:
    """Detect if a task touches a security-sensitive surface.

    Args:
        title: Task title text.
        description: Task description text.
        tags: List of task tags.
        spec_criteria: SPEC acceptance criteria text.
        file_paths: List of file paths touched by the task.

    Returns:
        ThreatSurfaceResult with is_security_sensitive flag and matched categories.
    """
    # Stub — will be implemented in GREEN phase
    return ThreatSurfaceResult()
