"""Prioritization scoring for specgraph artifacts.

Implements the recommendation algorithm from the prioritization layer design spec:
  score = unblock_count × vision_weight

Vision weight cascades: Vision → Initiative (can override) → Epic → Spec.
"""

from __future__ import annotations

from .queries import _walk_parent_chain

WEIGHT_MAP = {"high": 3, "medium": 2, "low": 1}
DEFAULT_WEIGHT = 2  # medium


def resolve_vision_weight(
    artifact_id: str,
    nodes: dict,
    edges: list[dict],
) -> int:
    """Resolve the effective priority weight for an artifact.

    Walk the parent chain upward. If the artifact or any ancestor has a
    priority_weight set, use the closest one (initiative override > vision default).
    If the artifact is a Vision, use its own weight. Default: medium (2).
    """
    node = nodes.get(artifact_id)
    if node is None:
        return DEFAULT_WEIGHT

    # Check self first (Vision with own weight, or Initiative with override)
    own_weight = node.get("priority_weight", "")
    if own_weight and own_weight in WEIGHT_MAP:
        # If this is a Vision, return its weight directly
        if node.get("type", "").upper() == "VISION":
            return WEIGHT_MAP[own_weight]
        # If this is an Initiative with an override, use the override
        if node.get("type", "").upper() == "INITIATIVE":
            return WEIGHT_MAP[own_weight]

    # Walk parent chain and find the nearest weight
    chain = _walk_parent_chain(artifact_id, edges)
    # Check for initiative override first, then vision weight
    for ancestor_id in chain:
        ancestor = nodes.get(ancestor_id, {})
        ancestor_weight = ancestor.get("priority_weight", "")
        if ancestor_weight and ancestor_weight in WEIGHT_MAP:
            ancestor_type = ancestor.get("type", "").upper()
            if ancestor_type == "INITIATIVE":
                # Initiative override — use it
                return WEIGHT_MAP[ancestor_weight]
            if ancestor_type == "VISION":
                # Vision weight — use it (no initiative override found)
                return WEIGHT_MAP[ancestor_weight]

    return DEFAULT_WEIGHT
