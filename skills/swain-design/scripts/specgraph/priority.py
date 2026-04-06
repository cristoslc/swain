"""Prioritization scoring for specgraph artifacts.

Implements the recommendation algorithm from the prioritization layer design spec:
  score = unblock_count × vision_weight

Vision weight cascades: Vision → Initiative (can override) → Epic (can override) → Spec (can override).
"""

from __future__ import annotations

from .queries import _walk_parent_chain, _compute_ready_set, _find_vision_ancestor, _node_is_resolved

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

    # Check self first — honor own weight for any artifact type
    own_weight = node.get("priority_weight", "")
    if own_weight and own_weight in WEIGHT_MAP:
        return WEIGHT_MAP[own_weight]

    # Walk parent chain and find the nearest weight
    # Cascade: Epic override > Initiative override > Vision default
    chain = _walk_parent_chain(artifact_id, edges)
    for ancestor_id in chain:
        ancestor = nodes.get(ancestor_id, {})
        ancestor_weight = ancestor.get("priority_weight", "")
        if ancestor_weight and ancestor_weight in WEIGHT_MAP:
            ancestor_type = ancestor.get("type", "").upper()
            if ancestor_type in ("EPIC", "INITIATIVE", "VISION"):
                return WEIGHT_MAP[ancestor_weight]

    return DEFAULT_WEIGHT


# Decision-type detection (matches swain-status is_decision logic)
_DECISION_ONLY_TYPES = {"VISION", "JOURNEY", "PERSONA", "ADR", "DESIGN"}
_DECISION_PHASES = {"Proposed", "Draft", "Review", "Planned"}


def _is_decision_type(node: dict) -> bool:
    """Check if an artifact is a decision (requires operator, not agent)."""
    t = node.get("type", "").upper()
    if t in _DECISION_ONLY_TYPES:
        return True
    if t in ("EPIC", "INITIATIVE", "SPIKE") and node.get("status", "") in _DECISION_PHASES:
        return True
    if t == "SPEC" and node.get("status", "") in _DECISION_PHASES:
        return True
    return False


def _compute_unblock_count(artifact_id: str, nodes: dict, edges: list[dict]) -> int:
    """Count how many unresolved artifacts depend on this one."""
    count = 0
    for edge in edges:
        if edge.get("to") == artifact_id and edge.get("type") == "depends-on":
            source = edge.get("from", "")
            if source and source in nodes and not _node_is_resolved(source, nodes):
                count += 1
    return count


def rank_recommendations(
    nodes: dict,
    edges: list[dict],
    focus_vision: str | None = None,
) -> list[dict]:
    """Rank all ready items by score = unblock_count × vision_weight.

    If focus_vision is set, only score items under that vision.
    Returns list of {id, score, unblock_count, vision_weight, vision_id, type, is_decision, vision_debt}
    sorted descending by score.

    Tiebreakers:
    1. Higher decision debt in the item's vision
    2. Decision-type artifacts over implementation-type
    3. Artifact ID (deterministic fallback)
    """
    ready_set = _compute_ready_set(nodes, edges)
    debt = compute_decision_debt(nodes, edges)

    scored: list[dict] = []
    for rid in ready_set:
        node = nodes.get(rid, {})
        vision = _find_vision_ancestor(rid, nodes, edges)

        if focus_vision and vision != focus_vision:
            continue

        weight = resolve_vision_weight(rid, nodes, edges)
        unblock_count = _compute_unblock_count(rid, nodes, edges)
        vision_debt = debt.get(vision or "_unaligned", {}).get("count", 0)

        scored.append({
            "id": rid,
            "score": unblock_count * weight,
            "unblock_count": unblock_count,
            "vision_weight": weight,
            "vision_id": vision,
            "vision_debt": vision_debt,
            "is_decision": _is_decision_type(node),
            "type": node.get("type", ""),
            "sort_order": node.get("sort_order", 0),
        })

    # Sort: score desc, then sort_order desc, then vision_debt desc, then is_decision desc, then id asc
    scored.sort(key=lambda x: (-x["score"], -x["sort_order"], -x["vision_debt"], -int(x["is_decision"]), x["id"]))
    return scored


def compute_decision_debt(
    nodes: dict,
    edges: list[dict],
) -> dict[str, dict]:
    """Compute decision debt per vision.

    Only counts decision-type artifacts (operator-gated), not implementation work.
    Returns: {vision_id: {count: N, total_unblocks: N, items: [...]}}
    Items not attached to any vision go into an "_unaligned" bucket.
    """
    ready_set = _compute_ready_set(nodes, edges)

    # Group decision-type ready items by vision
    debt: dict[str, dict] = {}
    for rid in ready_set:
        node = nodes.get(rid, {})
        if not _is_decision_type(node):
            continue  # Skip implementation-type items
        vision = _find_vision_ancestor(rid, nodes, edges)
        bucket = vision or "_unaligned"
        unblocks = _compute_unblock_count(rid, nodes, edges)
        if bucket not in debt:
            debt[bucket] = {"count": 0, "total_unblocks": 0, "items": []}
        debt[bucket]["count"] += 1
        debt[bucket]["total_unblocks"] += unblocks
        debt[bucket]["items"].append(rid)

    return debt
