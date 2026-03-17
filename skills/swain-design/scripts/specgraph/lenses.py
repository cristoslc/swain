"""Chart lenses — define node selection, annotation, sort order, and default depth.

Each lens answers a different question about the project hierarchy.
The tree renderer handles display; lenses handle semantics.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable

from specgraph.tree_renderer import _compute_ready_set, _walk_to_vision, _node_is_resolved
from specgraph.priority import (
    resolve_vision_weight,
    WEIGHT_MAP,
    rank_recommendations,
    compute_decision_debt,
)


class Lens(ABC):
    """Base class for chart lenses."""

    @property
    @abstractmethod
    def default_depth(self) -> int:
        """Default tree depth (2=strategic, 4=execution)."""
        ...

    @abstractmethod
    def select(self, nodes: dict, edges: list[dict]) -> set[str]:
        """Select which artifact IDs to display."""
        ...

    def annotate(self, nodes: dict, edges: list[dict]) -> dict[str, str]:
        """Return annotations for displayed nodes. Default: empty."""
        return {}

    def sort_key(self, artifact_id: str, nodes: dict,
                 edges: list[dict]) -> tuple:
        """Sort key for ordering siblings. Default: alphabetical by title."""
        return (nodes.get(artifact_id, {}).get("title", artifact_id).lower(),)


class DefaultLens(Lens):
    """Default overview — all non-terminal artifacts with status icons."""

    @property
    def default_depth(self) -> int:
        return 2

    def select(self, nodes: dict, edges: list[dict]) -> set[str]:
        return {aid for aid in nodes if not _node_is_resolved(aid, nodes)}


class ReadyLens(Lens):
    """Unblocked artifacts ready for work."""

    @property
    def default_depth(self) -> int:
        return 4

    def select(self, nodes: dict, edges: list[dict]) -> set[str]:
        return _compute_ready_set(nodes, edges)

    def sort_key(self, artifact_id: str, nodes: dict,
                 edges: list[dict]) -> tuple:
        unblock_count = sum(
            1 for e in edges
            if e.get("to") == artifact_id and e.get("type") == "depends-on"
            and not _node_is_resolved(e["from"], nodes)
        )
        title = nodes.get(artifact_id, {}).get("title", artifact_id).lower()
        return (-unblock_count, title)


class RecommendLens(Lens):
    """Scored by priority x unblock count."""

    def __init__(self, focus_vision: str | None = None):
        self._focus = focus_vision
        self._scores: dict[str, int] = {}

    @property
    def default_depth(self) -> int:
        return 2

    def select(self, nodes: dict, edges: list[dict]) -> set[str]:
        ranked = rank_recommendations(nodes, edges, focus_vision=self._focus)
        self._scores = {item["id"]: item["score"] for item in ranked}
        return {item["id"] for item in ranked}

    def annotate(self, nodes: dict, edges: list[dict]) -> dict[str, str]:
        ranked = rank_recommendations(nodes, edges, focus_vision=self._focus)
        return {item["id"]: f"score={item['score']}" for item in ranked}

    def sort_key(self, artifact_id: str, nodes: dict,
                 edges: list[dict]) -> tuple:
        score = self._scores.get(artifact_id)
        if score is None:
            weight = resolve_vision_weight(artifact_id, nodes, edges)
            unblock_count = sum(
                1 for e in edges
                if e.get("to") == artifact_id and e.get("type") == "depends-on"
                and not _node_is_resolved(e["from"], nodes)
            )
            score = unblock_count * weight
        title = nodes.get(artifact_id, {}).get("title", artifact_id).lower()
        return (-score, title)


class AttentionLens(Lens):
    """Recent git activity per vision."""

    def __init__(self, days: int = 30):
        self._days = days

    @property
    def default_depth(self) -> int:
        return 2

    def select(self, nodes: dict, edges: list[dict]) -> set[str]:
        return {aid for aid in nodes if not _node_is_resolved(aid, nodes)}

    def annotate(self, nodes: dict, edges: list[dict]) -> dict[str, str]:
        # Attention data requires git log — computed at CLI level, passed in
        return {}


class DebtLens(Lens):
    """Unresolved decision-type artifacts (Proposed Spikes, ADRs, Epics)."""

    @property
    def default_depth(self) -> int:
        return 2

    def select(self, nodes: dict, edges: list[dict]) -> set[str]:
        debt = compute_decision_debt(nodes, edges)
        result = set()
        for vision_id, info in debt.items():
            for item_id in info.get("items", []):
                result.add(item_id)
        return result

    def annotate(self, nodes: dict, edges: list[dict]) -> dict[str, str]:
        debt = compute_decision_debt(nodes, edges)
        annotations = {}
        for vision_id, info in debt.items():
            for item_id in info.get("items", []):
                node = nodes.get(item_id, {})
                status = node.get("status", "")
                annotations[item_id] = f"[{status}]"
        return annotations

    def sort_key(self, artifact_id: str, nodes: dict,
                 edges: list[dict]) -> tuple:
        return (nodes.get(artifact_id, {}).get("title", artifact_id).lower(),)


class UnanchoredLens(Lens):
    """Artifacts with no Vision ancestry."""

    @property
    def default_depth(self) -> int:
        return 2

    def select(self, nodes: dict, edges: list[dict]) -> set[str]:
        unanchored = set()
        for aid in nodes:
            chain = _walk_to_vision(aid, edges)
            has_vision = any(
                nodes.get(c, {}).get("type") == "VISION" for c in chain
            )
            if not has_vision and not _node_is_resolved(aid, nodes):
                unanchored.add(aid)
        return unanchored


class StatusLens(Lens):
    """All artifacts grouped by phase."""

    @property
    def default_depth(self) -> int:
        return 2

    def select(self, nodes: dict, edges: list[dict]) -> set[str]:
        return set(nodes.keys())

    def annotate(self, nodes: dict, edges: list[dict]) -> dict[str, str]:
        return {aid: f"[{node.get('status', '?')}]"
                for aid, node in nodes.items()}

    def sort_key(self, artifact_id: str, nodes: dict,
                 edges: list[dict]) -> tuple:
        phase_order = {"Proposed": 0, "Active": 1, "Ready": 1, "InProgress": 2,
                       "NeedsManualTest": 3, "Complete": 4, "Abandoned": 5}
        status = nodes.get(artifact_id, {}).get("status", "")
        return (phase_order.get(status, 99),
                nodes.get(artifact_id, {}).get("title", "").lower())


# Lens registry
LENSES = {
    "default": DefaultLens,
    "ready": ReadyLens,
    "recommend": RecommendLens,
    "attention": AttentionLens,
    "debt": DebtLens,
    "unanchored": UnanchoredLens,
    "status": StatusLens,
}
