"""Prioritization scoring for specgraph artifacts.

Implements the recommendation algorithm:
  score = unblock_count × priority_rank × roi_multiplier

Priority rank cascades via ancestry (ADR-010).
ROI multiplier derives from value-estimate and cost-estimate fields:
  roi = composite_value / cost_numeric  (floor 1.0 when estimates absent)
"""

from __future__ import annotations

from .queries import _walk_parent_chain, _compute_ready_set, _find_vision_ancestor, _node_is_resolved

WEIGHT_MAP = {"high": 3, "medium": 2, "low": 1}
DEFAULT_WEIGHT = 2  # medium

COST_MAP = {"XS": 1, "S": 2, "M": 3, "L": 5, "XL": 8}
DEFAULT_COST = 3  # medium


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


def compute_composite_value(value_estimate: dict | None) -> int:
    """Compute composite value from the three appraisal dimensions.

    value_estimate is a dict with keys: capability, efficiency, risk-reduction.
    Each scored 0-3. Composite is the sum (range 0-9).
    Returns 0 when no estimate is provided.
    """
    if not value_estimate or not isinstance(value_estimate, dict):
        return 0
    total = 0
    for key in ("capability", "efficiency", "risk-reduction"):
        raw = value_estimate.get(key, 0)
        try:
            val = int(raw)
        except (TypeError, ValueError):
            val = 0
        total += max(0, min(3, val))
    return total


def compute_cost_numeric(cost_estimate: str | None) -> int:
    """Map t-shirt size to numeric cost. Returns DEFAULT_COST when absent."""
    if not cost_estimate:
        return DEFAULT_COST
    return COST_MAP.get(cost_estimate.upper().strip(), DEFAULT_COST)


def compute_roi(value_estimate: dict | None, cost_estimate: str | None) -> float:
    """Compute ROI as composite_value / cost_numeric.

    Returns 0.0 when no value estimate is provided (artifact has no ROI data).
    This lets callers distinguish "no data" from "low ROI".
    """
    composite = compute_composite_value(value_estimate)
    if composite == 0:
        return 0.0
    cost = compute_cost_numeric(cost_estimate)
    return composite / cost


def _resolve_roi(artifact_id: str, nodes: dict, edges: list[dict]) -> float:
    """Resolve effective ROI for an artifact.

    Check self first, then walk parent chain for the nearest ancestor
    with value-estimate data. Returns 0.0 if no ancestor has estimates.
    """
    node = nodes.get(artifact_id)
    if node is None:
        return 0.0

    # Check self
    ve = node.get("value_estimate") or node.get("value-estimate")
    ce = node.get("cost_estimate") or node.get("cost-estimate")
    roi = compute_roi(ve, ce)
    if roi > 0.0:
        return roi

    # Walk parent chain
    chain = _walk_parent_chain(artifact_id, edges)
    for ancestor_id in chain:
        ancestor = nodes.get(ancestor_id, {})
        ve = ancestor.get("value_estimate") or ancestor.get("value-estimate")
        ce = ancestor.get("cost_estimate") or ancestor.get("cost-estimate")
        roi = compute_roi(ve, ce)
        if roi > 0.0:
            return roi

    return 0.0


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
    """Rank all ready items by score = unblock_count × vision_weight × roi_multiplier.

    ROI multiplier = max(1.0, roi) when ROI data exists, else 1.0 (neutral).
    This means ROI amplifies structural leverage and priority — it never
    reduces a score below what the old formula would produce. Artifacts
    without value/cost estimates behave exactly as before.

    If focus_vision is set, only score items under that vision.
    Returns list of dicts sorted descending by score.

    Tiebreakers (after score):
    1. ROI (higher return first)
    2. sort_order
    3. Higher decision debt in the item's vision
    4. Decision-type artifacts over implementation-type
    5. Artifact ID (deterministic fallback)
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
        roi = _resolve_roi(rid, nodes, edges)

        # ROI multiplier: amplifies score when ROI data exists and is > 1.
        # Neutral (1.0) when no estimates are provided — backwards compatible.
        roi_multiplier = max(1.0, roi) if roi > 0.0 else 1.0
        base_score = unblock_count * weight
        final_score = base_score * roi_multiplier

        scored.append({
            "id": rid,
            "score": final_score,
            "base_score": base_score,
            "unblock_count": unblock_count,
            "vision_weight": weight,
            "roi": roi,
            "roi_multiplier": roi_multiplier,
            "vision_id": vision,
            "vision_debt": vision_debt,
            "is_decision": _is_decision_type(node),
            "type": node.get("type", ""),
            "sort_order": node.get("sort_order", 0),
        })

    # Sort: score desc, roi desc, sort_order desc, vision_debt desc, is_decision desc, id asc
    scored.sort(key=lambda x: (
        -x["score"],
        -x["roi"],
        -x["sort_order"],
        -x["vision_debt"],
        -int(x["is_decision"]),
        x["id"],
    ))
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
