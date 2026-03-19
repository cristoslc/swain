"""VisionTree renderer — renders artifact sets as vision-rooted hierarchy trees.

All lenses and surface integrations consume this renderer. It handles:
- Walking parent edges to Vision roots
- Including structural ancestors (dimmed)
- Flattening when intermediate levels are missing
- Elbow connector rendering
- Depth control and phase filtering
- Unanchored section for parentless artifacts
"""
from __future__ import annotations

from typing import Callable, Optional

from specgraph.resolved import is_resolved as _is_resolved_raw

_PARENT_EDGE_TYPES = {"parent-epic", "parent-vision", "parent-initiative"}
_CHILD_TYPE_LABELS = {"SPEC": "spec", "SPIKE": "spike", "ADR": "adr", "DESIGN": "design",
                      "RUNBOOK": "runbook"}
_STATUS_ICONS = {"ready": "\u2192", "blocked": "\u2298", "in_progress": "\u00b7",
                 "resolved": "\u2713"}


def _node_is_resolved(artifact_id: str, nodes: dict) -> bool:
    """Wrapper: check if a node is resolved using its type/status/track."""
    node = nodes.get(artifact_id, {})
    return _is_resolved_raw(
        node.get("type", ""),
        node.get("status", ""),
        node.get("track"),
    )


_PARENT_SPECIFICITY = {"parent-epic": 3, "parent-initiative": 2, "parent-vision": 1}


def _get_children(parent_id: str, edges: list[dict]) -> list[str]:
    """Return artifact IDs whose most proximate parent is parent_id.

    An epic with both parent-vision and parent-initiative is a child of the
    initiative, not the vision.  Only the edge with the highest specificity
    counts as the "real" parent for tree-nesting purposes.
    """
    candidates = []
    for e in edges:
        if e["type"] in _PARENT_EDGE_TYPES and e.get("to") == parent_id:
            candidates.append((e["from"], e["type"]))

    children = []
    for child_id, edge_type in candidates:
        specificity = _PARENT_SPECIFICITY.get(edge_type, 0)
        # Skip if the child has a more specific parent edge (to any target)
        has_more_specific = any(
            e["from"] == child_id
            and e["type"] in _PARENT_EDGE_TYPES
            and _PARENT_SPECIFICITY.get(e["type"], 0) > specificity
            for e in edges
        )
        if not has_more_specific:
            children.append(child_id)
    return children


def _walk_to_vision(artifact_id: str, edges: list[dict],
                    visited: set | None = None) -> list[str]:
    """Walk parent edges from artifact up to Vision root.

    Returns path [self, parent, ..., vision] (closest ancestor first).
    Prefers the most specific parent edge so intermediate ancestors
    (initiatives, epics) are not skipped.
    """
    if visited is None:
        visited = set()
    if artifact_id in visited:
        return [artifact_id]
    visited.add(artifact_id)
    chain = [artifact_id]
    parent_edges = [e for e in edges
                    if e["from"] == artifact_id and e["type"] in _PARENT_EDGE_TYPES]
    if parent_edges:
        # Pick the most specific parent edge (parent-epic > parent-initiative > parent-vision)
        parent_edges.sort(
            key=lambda e: _PARENT_SPECIFICITY.get(e["type"], 0), reverse=True)
        best = parent_edges[0]
        parent_chain = _walk_to_vision(best["to"], edges, visited)
        chain.extend(parent_chain)
    return chain


def _child_count_label(parent_id: str, all_nodes: dict, edges: list[dict],
                       phase_filter: set[str] | None) -> str:
    """Compute child count summary like '3 specs, 1 spike'."""
    children = _get_children(parent_id, edges)
    counts: dict[str, int] = {}
    for cid in children:
        cnode = all_nodes.get(cid, {})
        if phase_filter and cnode.get("status") not in phase_filter:
            continue
        ctype = cnode.get("type", "SPEC")
        label = _CHILD_TYPE_LABELS.get(ctype, ctype.lower())
        counts[label] = counts.get(label, 0) + 1
    if not counts:
        return ""
    parts = []
    for label in ("spec", "spike", "adr", "design", "runbook"):
        if label in counts:
            n = counts[label]
            parts.append(f"{n} {label}{'s' if n != 1 else ''}")
    for label, n in sorted(counts.items()):
        if label not in ("spec", "spike", "adr", "design", "runbook"):
            parts.append(f"{n} {label}{'s' if n != 1 else ''}")
    return ", ".join(parts)


def _compute_ready_set(nodes: dict, edges: list[dict]) -> set[str]:
    """Return set of artifact IDs that are unresolved and have all deps satisfied."""
    ready = set()
    for aid in nodes:
        if _node_is_resolved(aid, nodes):
            continue
        deps = [e["to"] for e in edges
                if e["from"] == aid and e["type"] == "depends-on"]
        if all(_node_is_resolved(d, nodes) for d in deps):
            ready.add(aid)
    return ready


def _status_icon(artifact_id: str, all_nodes: dict, edges: list[dict],
                 ready_set: set[str]) -> str:
    """Return status icon for an artifact."""
    if _node_is_resolved(artifact_id, all_nodes):
        return _STATUS_ICONS["resolved"]
    if artifact_id in ready_set:
        return _STATUS_ICONS["ready"]
    deps = [e["to"] for e in edges
            if e["from"] == artifact_id and e["type"] == "depends-on"]
    unresolved_deps = [d for d in deps if not _node_is_resolved(d, all_nodes)]
    if unresolved_deps:
        return _STATUS_ICONS["blocked"]
    return _STATUS_ICONS["in_progress"]


def _render_node_line(artifact_id: str, all_nodes: dict, edges: list[dict],
                      ready_set: set[str], annotations: dict[str, str],
                      show_ids: bool, depth: int, current_depth: int,
                      phase_filter: set[str] | None,
                      is_structural: bool) -> str:
    """Render a single node's display text."""
    node = all_nodes.get(artifact_id, {})
    title = node.get("title", artifact_id)
    icon = _status_icon(artifact_id, all_nodes, edges, ready_set)

    at_depth_limit = current_depth >= depth
    child_label = ""
    if at_depth_limit:
        cl = _child_count_label(artifact_id, all_nodes, edges, phase_filter)
        if cl:
            child_label = f"  {cl}"

    annotation = annotations.get(artifact_id, "")
    if annotation:
        annotation = f"  {annotation}"

    id_suffix = f" [{artifact_id}]" if show_ids else ""

    if is_structural:
        return f"{title}{id_suffix}"
    else:
        return f"{icon} {title}{id_suffix}{child_label}{annotation}"


def _render_subtree(artifact_id: str, all_nodes: dict, edges: list[dict],
                    ready_set: set[str], annotations: dict[str, str],
                    sort_key: Callable, show_ids: bool, depth: int,
                    phase_filter: set[str] | None, display_nodes: set[str],
                    current_depth: int, prefix: str, is_last: bool,
                    lines: list[str], visited: set[str]) -> None:
    """Recursively render a subtree with elbow connectors."""
    if artifact_id in visited:
        return
    visited.add(artifact_id)

    node = all_nodes.get(artifact_id, {})

    # Phase filter — skip nodes whose status doesn't match,
    # but always show structural ancestors (needed for tree structure)
    if phase_filter and node.get("status") not in phase_filter:
        is_structural_ancestor = artifact_id not in display_nodes
        if not is_structural_ancestor:
            return  # Display node filtered out by phase

    is_structural = artifact_id not in display_nodes
    connector = "\u2514\u2500\u2500 " if is_last else "\u251c\u2500\u2500 "
    if current_depth == 0:
        connector = ""
        child_prefix = ""
    else:
        child_prefix = prefix + ("    " if is_last else "\u2502   ")

    line = _render_node_line(artifact_id, all_nodes, edges, ready_set,
                             annotations, show_ids, depth, current_depth,
                             phase_filter, is_structural)
    lines.append(f"{prefix}{connector}{line}")

    if current_depth >= depth:
        return

    children = _get_children(artifact_id, edges)
    visible_children = []
    for cid in children:
        cnode = all_nodes.get(cid, {})
        if phase_filter and cnode.get("status") not in phase_filter:
            if cid not in display_nodes:
                continue
        visible_children.append(cid)

    visible_children = sorted(visible_children,
                              key=lambda c: sort_key(c, all_nodes, edges))

    for i, child_id in enumerate(visible_children):
        is_last_child = (i == len(visible_children) - 1)
        _render_subtree(child_id, all_nodes, edges, ready_set, annotations,
                        sort_key, show_ids, depth, phase_filter, display_nodes,
                        current_depth + 1, child_prefix, is_last_child,
                        lines, visited)


def _default_sort_key(artifact_id: str, all_nodes: dict,
                      edges: list[dict]) -> str:
    """Default sort: alphabetical by title."""
    return all_nodes.get(artifact_id, {}).get("title", artifact_id).lower()


def render_vision_tree(
    nodes: set[str],
    all_nodes: dict,
    edges: list[dict],
    depth: int = 2,
    phase_filter: set[str] | None = None,
    annotations: dict[str, str] | None = None,
    sort_key: Callable | None = None,
    show_ids: bool = False,
) -> list[str]:
    """Render a vision-rooted hierarchy tree.

    Args:
        nodes: Set of artifact IDs to display (the lens's result set).
        all_nodes: Complete node dict from graph cache.
        edges: Complete edge list from graph cache.
        depth: Max tree depth (0=Vision only, 2=strategic, 4=execution).
        phase_filter: If set, only show artifacts in these phases.
        annotations: Dict of artifact_id -> annotation string.
        sort_key: Callable(artifact_id, all_nodes, edges) -> sort value.
        show_ids: Whether to show artifact IDs alongside titles.

    Returns:
        List of rendered lines (join with newlines for display).
    """
    if annotations is None:
        annotations = {}
    if sort_key is None:
        sort_key = _default_sort_key

    ready_set = _compute_ready_set(all_nodes, edges)

    display_nodes = set(nodes)
    all_ancestors: set[str] = set()
    for nid in nodes:
        chain = _walk_to_vision(nid, edges)
        all_ancestors.update(chain)

    render_nodes = display_nodes | all_ancestors

    vision_roots = sorted(
        [nid for nid in render_nodes
         if all_nodes.get(nid, {}).get("type") == "VISION"],
        key=lambda v: sort_key(v, all_nodes, edges)
    )

    # Find unanchored artifacts
    anchored = set()
    for nid in display_nodes:
        chain = _walk_to_vision(nid, edges)
        if any(all_nodes.get(c, {}).get("type") == "VISION" for c in chain):
            anchored.add(nid)
    unanchored = display_nodes - anchored

    lines: list[str] = []
    visited: set[str] = set()

    for i, vid in enumerate(vision_roots):
        if i > 0:
            lines.append("")
        _render_subtree(vid, all_nodes, edges, ready_set, annotations,
                        sort_key, show_ids, depth, phase_filter, display_nodes,
                        0, "", True, lines, visited)

    if unanchored:
        lines.append("")
        lines.append("=== Unanchored ===")
        for uid in sorted(unanchored,
                          key=lambda u: sort_key(u, all_nodes, edges)):
            node = all_nodes.get(uid, {})
            title = node.get("title", uid)
            id_suffix = f" [{uid}]" if show_ids else ""
            partial_chain = _walk_to_vision(uid, edges)
            if len(partial_chain) > 1:
                ancestors = " > ".join(
                    all_nodes.get(a, {}).get("title", a)
                    for a in reversed(partial_chain[1:])
                )
                lines.append(f"\u26a0 {title}{id_suffix} (under: {ancestors})")
            else:
                lines.append(
                    f"\u26a0 {title}{id_suffix} [no Vision ancestry]")

    lines.append("")
    lines.append("---")
    lines.append(
        "\u2192 ready   \u2298 blocked   \u00b7 in progress   "
        "\u2713 complete (hidden by default)")

    return lines


def render_breadcrumb(
    artifact_id: str,
    all_nodes: dict,
    edges: list[dict],
) -> str:
    """Render a Vision ancestry breadcrumb for an artifact.

    Returns string like: "Swain > Operator Awareness > Chart Hierarchy"
    """
    chain = _walk_to_vision(artifact_id, edges)
    titles = [
        all_nodes.get(aid, {}).get("title", aid)
        for aid in reversed(chain)
    ]
    return " > ".join(titles)
