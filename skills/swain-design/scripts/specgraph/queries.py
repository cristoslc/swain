"""Query functions for specgraph: blocks, blocked_by, tree, edges_cmd, scope, impact.

These implement the primary graph query commands. Each operates on the
in-memory graph cache (nodes dict + edges list) and returns plain text output.
"""

from __future__ import annotations

import os
import subprocess
from collections import deque

from .links import art_link
from .resolved import is_resolved


def _node_is_resolved(artifact_id: str, nodes: dict) -> bool:
    """Return True if the artifact is resolved (considering its track or type)."""
    node = nodes.get(artifact_id)
    if node is None:
        # Unknown node — treat as unresolved (conservative)
        return False
    return is_resolved(
        node.get("type", ""),
        node.get("status", ""),
        node.get("track") or None,
    )


def _format_id(
    artifact_id: str,
    nodes: dict,
    repo_root: str,
    show_links: bool,
) -> str:
    """Return artifact_id, optionally as an OSC 8 hyperlink."""
    if not show_links:
        return artifact_id
    node = nodes.get(artifact_id, {})
    filepath = node.get("file", "")
    return art_link(artifact_id, filepath, repo_root)


def blocks(
    artifact_id: str,
    nodes: dict,
    edges: list[dict],
    repo_root: str = "",
    show_links: bool = False,
) -> str:
    """Return newline-separated IDs that artifact_id directly depends on (not yet resolved).

    Filter edges where from==artifact_id and type=="depends-on".
    Only show targets that are NOT resolved (i.e., still blocking work).
    """
    result = []
    for edge in edges:
        if edge.get("from") != artifact_id:
            continue
        if edge.get("type") != "depends-on":
            continue
        target = edge.get("to", "")
        if not target:
            continue
        if _node_is_resolved(target, nodes):
            continue
        result.append(_format_id(target, nodes, repo_root, show_links))
    return "\n".join(sorted(result))


def blocked_by(
    artifact_id: str,
    nodes: dict,
    edges: list[dict],
    repo_root: str = "",
    show_links: bool = False,
) -> str:
    """Return newline-separated IDs that depend on artifact_id (i.e., it blocks them).

    Filter edges where to==artifact_id and type=="depends-on".
    Only show sources that are NOT resolved.
    """
    result = []
    for edge in edges:
        if edge.get("to") != artifact_id:
            continue
        if edge.get("type") != "depends-on":
            continue
        source = edge.get("from", "")
        if not source:
            continue
        if _node_is_resolved(source, nodes):
            continue
        result.append(_format_id(source, nodes, repo_root, show_links))
    return "\n".join(sorted(result))


def tree(
    artifact_id: str,
    nodes: dict,
    edges: list[dict],
    repo_root: str = "",
    show_links: bool = False,
) -> str:
    """Return transitive dependency closure — all ancestors of artifact_id.

    BFS following depends-on edges from artifact_id outward (from==current).
    Include only unresolved nodes. Return newline-separated IDs.
    Avoid cycles with a visited set.
    """
    visited: set[str] = {artifact_id}
    queue: deque[str] = deque([artifact_id])
    result: list[str] = []

    while queue:
        current = queue.popleft()
        for edge in edges:
            if edge.get("from") != current:
                continue
            if edge.get("type") != "depends-on":
                continue
            target = edge.get("to", "")
            if not target or target in visited:
                continue
            visited.add(target)
            if _node_is_resolved(target, nodes):
                continue
            result.append(_format_id(target, nodes, repo_root, show_links))
            queue.append(target)

    return "\n".join(sorted(result))


def neighbors(
    artifact_id: str,
    nodes: dict,
    edges: list[dict],
    repo_root: str = "",
    show_links: bool = False,
) -> str:
    """Return TSV of all edges touching artifact_id (both directions).

    Columns: direction\tedge_type\tartifact_id\tstatus\ttitle
    direction: "from" if artifact_id is the source, "to" if it's the target

    For each edge where from==artifact_id: direction="from", other_id=to
    For each edge where to==artifact_id: direction="to", other_id=from

    Include node metadata (status, title) when the other_id is in nodes.
    Sort by: direction, then edge_type, then artifact_id.
    """
    rows: list[tuple[str, str, str, str, str]] = []

    for edge in edges:
        frm = edge.get("from", "")
        to = edge.get("to", "")
        typ = edge.get("type", "")

        if frm == artifact_id and to:
            direction = "from"
            other_id = to
        elif to == artifact_id and frm:
            direction = "to"
            other_id = frm
        else:
            continue

        node = nodes.get(other_id, {})
        status = node.get("status", "")
        title = node.get("title", "")
        display_id = _format_id(other_id, nodes, repo_root, show_links)
        rows.append((direction, typ, display_id, status, title))

    rows.sort(key=lambda r: (r[0], r[1], r[2]))
    return "\n".join(f"{d}\t{et}\t{aid}\t{st}\t{ti}" for d, et, aid, st, ti in rows)


def edges_cmd(
    artifact_id: str | None,
    nodes: dict,
    edges: list[dict],
) -> str:
    """Return TSV of edges: from\\tto\\ttype, optionally filtered by artifact_id.

    If artifact_id is given, only return edges where from==artifact_id or to==artifact_id.
    Sort by from, then to, then type.
    """
    filtered = []
    for edge in edges:
        frm = edge.get("from", "")
        to = edge.get("to", "")
        typ = edge.get("type", "")
        if artifact_id is not None:
            if frm != artifact_id and to != artifact_id:
                continue
        filtered.append((frm, to, typ))

    filtered.sort(key=lambda t: (t[0], t[1], t[2]))
    return "\n".join(f"{frm}\t{to}\t{typ}" for frm, to, typ in filtered)


# ---------------------------------------------------------------------------
# Parent-edge types used by scope/impact for hierarchy traversal
# ---------------------------------------------------------------------------

_PARENT_EDGE_TYPES = frozenset({"parent-epic", "parent-vision"})

# Lateral edge types shown in scope's Laterals section
_LATERAL_EDGE_TYPES = frozenset({"linked-artifact", "addresses", "validates", "superseded-by"})


def _get_immediate_parent(artifact_id: str, edges: list[dict]) -> str | None:
    """Return the first immediate parent ID (via parent-epic or parent-vision), or None."""
    for edge in edges:
        if edge.get("from") == artifact_id and edge.get("type") in _PARENT_EDGE_TYPES:
            return edge.get("to", "") or None
    return None


def _walk_parent_chain(artifact_id: str, edges: list[dict]) -> list[str]:
    """Walk parent-epic / parent-vision edges upward. Return ordered list (closest first).

    Cycle-safe via visited set.
    """
    chain: list[str] = []
    visited: set[str] = {artifact_id}
    current = artifact_id
    while True:
        parent = _get_immediate_parent(current, edges)
        if parent is None or parent in visited:
            break
        visited.add(parent)
        chain.append(parent)
        current = parent
    return chain


def _find_vision_ancestor(artifact_id: str, nodes: dict, edges: list[dict]) -> str | None:
    """Return the VISION-type ancestor ID, if any exists in the parent chain."""
    chain = _walk_parent_chain(artifact_id, edges)
    for ancestor_id in chain:
        node = nodes.get(ancestor_id, {})
        if node.get("type", "").upper() == "VISION":
            return ancestor_id
    return None


def scope(
    artifact_id: str,
    nodes: dict,
    edges: list[dict],
    repo_root: str = "",
    show_links: bool = False,
) -> str:
    """Show the scope context of an artifact.

    Output sections:
    1. Parent chain: walk parent-epic and parent-vision edges BFS upward
    2. Siblings: other artifacts sharing the same immediate parent
    3. Laterals: linked-artifacts, addresses, validates, superseded-by edges
    4. Architecture overview: if a VISION ancestor exists, check for
       architecture-overview.md adjacent to the Vision file (filesystem check)

    Format each section with a header like "=== Parent Chain ===" etc.
    Return empty string if artifact_id not in nodes.
    """
    if artifact_id not in nodes:
        return ""

    sections: list[str] = []

    # --- 1. Parent chain ---
    chain = _walk_parent_chain(artifact_id, edges)
    chain_lines = [_format_id(pid, nodes, repo_root, show_links) for pid in chain]
    sections.append("=== Parent Chain ===")
    sections.extend(chain_lines)

    # --- 2. Siblings (other artifacts sharing the same immediate parent) ---
    immediate_parent = chain[0] if chain else None
    sibling_ids: list[str] = []
    if immediate_parent is not None:
        for edge in edges:
            if edge.get("to") != immediate_parent:
                continue
            if edge.get("type") not in _PARENT_EDGE_TYPES:
                continue
            sibling = edge.get("from", "")
            if sibling and sibling != artifact_id:
                sibling_ids.append(sibling)
    sibling_ids.sort()
    sections.append("=== Siblings ===")
    sections.extend(_format_id(sid, nodes, repo_root, show_links) for sid in sibling_ids)

    # --- 3. Laterals ---
    lateral_ids: list[str] = []
    for edge in edges:
        if edge.get("from") != artifact_id:
            continue
        if edge.get("type") not in _LATERAL_EDGE_TYPES:
            continue
        target = edge.get("to", "")
        if target:
            lateral_ids.append(target)
    lateral_ids.sort()
    sections.append("=== Laterals ===")
    sections.extend(_format_id(lid, nodes, repo_root, show_links) for lid in lateral_ids)

    # --- 4. Architecture overview ---
    # Walk the full parent chain (epic-level first, then vision-level), checking each
    # ancestor's folder for an architecture-overview.md. Include the artifact itself
    # if it is an EPIC or VISION type. Show all levels found (Epic before Vision).
    sections.append("=== Architecture Overview ===")
    arch_ancestor_ids: list[str] = []
    node_type = nodes.get(artifact_id, {}).get("type", "").upper()
    if node_type in ("EPIC", "VISION"):
        arch_ancestor_ids.append(artifact_id)
    arch_ancestor_ids.extend(_walk_parent_chain(artifact_id, edges))

    arch_paths: list[str] = []
    if repo_root:
        for ancestor_id in arch_ancestor_ids:
            ancestor_file = nodes.get(ancestor_id, {}).get("file", "")
            if not ancestor_file:
                continue
            ancestor_dir = os.path.dirname(os.path.join(repo_root, ancestor_file))
            candidate = os.path.join(ancestor_dir, "architecture-overview.md")
            if os.path.isfile(candidate):
                arch_paths.append(candidate)

    sections.extend(arch_paths)

    return "\n".join(sections)


def impact(
    artifact_id: str,
    nodes: dict,
    edges: list[dict],
    repo_root: str = "",
    show_links: bool = False,
) -> str:
    """Show what would be impacted if this artifact changed.

    Find all edges where to==artifact_id (direct references).
    Then walk parent chains of those referencing artifacts.

    Output format:
    DIRECT: count
    list of direct references

    AFFECTED CHAINS: count
    list of artifacts in chains

    TOTAL: count
    """
    # --- Direct references: any edge where to==artifact_id ---
    direct_ids: list[str] = []
    for edge in edges:
        if edge.get("to") == artifact_id:
            source = edge.get("from", "")
            if source and source not in direct_ids:
                direct_ids.append(source)
    direct_ids.sort()

    # --- Affected chains: walk the parent chain of each direct referrer
    # (children of the direct referrers, i.e., things that reference them) ---
    chain_ids_set: set[str] = set()
    # For each direct referrer, find all artifacts whose parent chain passes through it
    # Walk "downward": find everything that has direct_id in its parent chain
    # i.e., for each artifact, check if artifact_id appears in its ancestry

    # Build a map: artifact → immediate parent
    # Then for each direct referrer, find all artifacts that ultimately have it as ancestor
    # We do this by BFS "downward" — follow edges in reverse (to→from for parent edges)
    for direct_id in direct_ids:
        # Find children of direct_id (edges where to==direct_id and type is parent edge)
        queue: deque[str] = deque([direct_id])
        visited: set[str] = {direct_id, artifact_id}
        while queue:
            current = queue.popleft()
            for edge in edges:
                if edge.get("to") != current:
                    continue
                if edge.get("type") not in _PARENT_EDGE_TYPES:
                    continue
                child = edge.get("from", "")
                if child and child not in visited:
                    visited.add(child)
                    chain_ids_set.add(child)
                    queue.append(child)

    # Remove any that are already in direct_ids
    chain_ids = sorted(chain_ids_set - set(direct_ids))

    total = len(direct_ids) + len(chain_ids)

    lines: list[str] = []
    lines.append(f"DIRECT: {len(direct_ids)}")
    lines.extend(_format_id(did, nodes, repo_root, show_links) for did in direct_ids)
    lines.append(f"AFFECTED CHAINS: {len(chain_ids)}")
    lines.extend(_format_id(cid, nodes, repo_root, show_links) for cid in chain_ids)
    lines.append(f"TOTAL: {total}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Mermaid diagram
# ---------------------------------------------------------------------------

# Edge types always included in mermaid output
_MERMAID_CORE_EDGE_TYPES = frozenset({"depends-on", "parent-epic", "parent-vision"})


def mermaid_cmd(nodes: dict, edges: list[dict], show_all: bool = False, all_edges: bool = False) -> str:
    """Emit a Mermaid graph TD diagram.

    - Only include nodes that are not resolved (unless show_all=True)
    - Node labels: ARTIFACT-NNN["Title"] or ARTIFACT-NNN["ARTIFACT-NNN"] if no title
    - Escape double quotes in titles with #quot;
    - Edge types to include:
      - Always: "depends-on", "parent-epic", "parent-vision"
      - If all_edges=True: also "linked-artifacts", "validates", "addresses", etc.
    - Only emit edges where BOTH from and to nodes are visible
    - Sort node definitions and edges for deterministic output
    - Wrap with: graph TD\\n...
    """
    # Determine visible node set
    visible: set[str] = set()
    for artifact_id, node in nodes.items():
        if show_all or not _node_is_resolved(artifact_id, nodes):
            visible.add(artifact_id)

    # Build node definition lines
    node_lines: list[str] = []
    for artifact_id in sorted(visible):
        node = nodes[artifact_id]
        raw_title = node.get("title", "") or artifact_id
        label = raw_title.replace('"', "#quot;")
        node_lines.append(f'{artifact_id}["{label}"]')

    # Determine which edge types to include
    if all_edges:
        # Include all edge types
        allowed_types: frozenset[str] | None = None
    else:
        allowed_types = _MERMAID_CORE_EDGE_TYPES

    # Build edge lines
    edge_lines: list[str] = []
    seen_edges: set[tuple[str, str]] = set()
    for edge in edges:
        frm = edge.get("from", "")
        to = edge.get("to", "")
        typ = edge.get("type", "")
        if not frm or not to:
            continue
        if allowed_types is not None and typ not in allowed_types:
            continue
        if frm not in visible or to not in visible:
            continue
        pair = (frm, to)
        if pair in seen_edges:
            continue
        seen_edges.add(pair)
        edge_lines.append(f"{frm} --> {to}")

    edge_lines.sort()

    lines: list[str] = ["graph TD"]
    lines.extend(f"  {nl}" for nl in node_lines)
    lines.extend(f"  {el}" for el in edge_lines)

    # Remove trailing blank lines beyond "graph TD" when nothing else present
    if len(lines) == 1:
        return "graph TD"

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Status table
# ---------------------------------------------------------------------------


def status_cmd(nodes: dict, edges: list[dict], show_all: bool = False) -> str:
    """Emit a summary table grouped by artifact type.

    - Group nodes by type (SPEC, EPIC, SPIKE, ADR, etc.)
    - Within each group, sort by artifact ID
    - Each row: artifact_id, status, title
    - If not show_all: exclude resolved artifacts
    - Include a count of hidden resolved artifacts if any were excluded
    - Format: simple aligned columns (not markdown table)
    """
    # Bucket nodes by type, track how many were hidden
    by_type: dict[str, list[tuple[str, str, str]]] = {}  # type → [(id, status, title)]
    hidden_count = 0

    for artifact_id, node in nodes.items():
        resolved = _node_is_resolved(artifact_id, nodes)
        if not show_all and resolved:
            hidden_count += 1
            continue
        artifact_type = node.get("type", "UNKNOWN").upper()
        status = node.get("status", "")
        title = node.get("title", "")
        by_type.setdefault(artifact_type, []).append((artifact_id, status, title))

    if not by_type:
        if hidden_count > 0 and not show_all:
            return f"({hidden_count} resolved artifacts hidden)"
        return ""

    # Sort types alphabetically; within each type sort by artifact ID
    lines: list[str] = []
    for artifact_type in sorted(by_type):
        rows = sorted(by_type[artifact_type], key=lambda r: r[0])
        lines.append(f"--- {artifact_type} ---")
        # Compute column widths for alignment
        id_width = max(len(r[0]) for r in rows)
        status_width = max((len(r[1]) for r in rows), default=0)
        for artifact_id, status, title in rows:
            lines.append(f"  {artifact_id:<{id_width}}  {status:<{status_width}}  {title}")

    if hidden_count > 0 and not show_all:
        lines.append(f"({hidden_count} resolved artifact{'s' if hidden_count != 1 else ''} hidden)")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Ready and Next
# ---------------------------------------------------------------------------


def _compute_ready_set(nodes: dict, edges: list[dict]) -> set[str]:
    """Return the set of artifact IDs that are ready.

    An artifact is ready if:
    - It is not resolved
    - All of its depends-on targets are resolved (or it has no depends-on edges)
    """
    ready: set[str] = set()
    for artifact_id in nodes:
        if _node_is_resolved(artifact_id, nodes):
            continue
        # Check all depends-on edges from this artifact
        is_ready = True
        for edge in edges:
            if edge.get("from") != artifact_id:
                continue
            if edge.get("type") != "depends-on":
                continue
            target = edge.get("to", "")
            if not target:
                continue
            if not _node_is_resolved(target, nodes):
                is_ready = False
                break
        if is_ready:
            ready.add(artifact_id)
    return ready


def ready(
    nodes: dict,
    edges: list[dict],
    repo_root: str = "",
    show_links: bool = False,
) -> str:
    """Return a formatted list of ready artifacts.

    Ready = unresolved nodes whose all depends-on targets are resolved.
    Output format per line: {display_id}  {status}  {title}
    Sorted by artifact ID. Returns empty string if nothing is ready.
    """
    ready_set = _compute_ready_set(nodes, edges)
    if not ready_set:
        return ""

    lines: list[str] = []
    for artifact_id in sorted(ready_set):
        node = nodes[artifact_id]
        display_id = _format_id(artifact_id, nodes, repo_root, show_links)
        status = node.get("status", "")
        title = node.get("title", "")
        lines.append(f"{display_id}  {status}  {title}")

    return "\n".join(lines)


def next_cmd(
    nodes: dict,
    edges: list[dict],
    repo_root: str = "",
    show_links: bool = False,
) -> str:
    """Compute ready set and show what each ready item would unblock, plus blocked items.

    Format:
    READY:
      ARTIFACT-001  In Progress  Title
        -> would unblock: ARTIFACT-002, ARTIFACT-003

    BLOCKED:
      ARTIFACT-004  In Progress  Title  (needs: EPIC-001, ARTIFACT-005)
    """
    ready_set = _compute_ready_set(nodes, edges)

    lines: list[str] = []

    # --- READY section ---
    lines.append("READY:")
    if not ready_set:
        lines.append("  (none)")
    else:
        for artifact_id in sorted(ready_set):
            node = nodes[artifact_id]
            display_id = _format_id(artifact_id, nodes, repo_root, show_links)
            status = node.get("status", "")
            title = node.get("title", "")
            lines.append(f"  {display_id}  {status}  {title}")

            # Compute "would unblock": non-ready, non-resolved artifacts that would
            # enter ready_set if this artifact were resolved
            would_unblock: list[str] = []
            for candidate_id in nodes:
                if candidate_id in ready_set:
                    continue
                if _node_is_resolved(candidate_id, nodes):
                    continue
                # Collect all unresolved depends-on targets for this candidate
                unresolved_deps: list[str] = []
                for edge in edges:
                    if edge.get("from") != candidate_id:
                        continue
                    if edge.get("type") != "depends-on":
                        continue
                    target = edge.get("to", "")
                    if not target:
                        continue
                    if not _node_is_resolved(target, nodes):
                        unresolved_deps.append(target)
                # If artifact_id is the only unresolved dep, resolving it would unblock candidate
                if unresolved_deps == [artifact_id]:
                    would_unblock.append(candidate_id)

            if would_unblock:
                unblock_str = ", ".join(sorted(would_unblock))
                lines.append(f"    -> would unblock: {unblock_str}")

    # --- BLOCKED section ---
    lines.append("")
    lines.append("BLOCKED:")

    blocked_ids = [
        artifact_id for artifact_id in nodes
        if not _node_is_resolved(artifact_id, nodes) and artifact_id not in ready_set
    ]

    if not blocked_ids:
        lines.append("  (none)")
    else:
        for artifact_id in sorted(blocked_ids):
            node = nodes[artifact_id]
            display_id = _format_id(artifact_id, nodes, repo_root, show_links)
            status = node.get("status", "")
            title = node.get("title", "")
            # Collect unresolved deps
            unresolved_deps: list[str] = []
            for edge in edges:
                if edge.get("from") != artifact_id:
                    continue
                if edge.get("type") != "depends-on":
                    continue
                target = edge.get("to", "")
                if not target:
                    continue
                if not _node_is_resolved(target, nodes):
                    unresolved_deps.append(target)
            needs_str = ", ".join(sorted(unresolved_deps))
            lines.append(f"  {display_id}  {status}  {title}  (needs: {needs_str})")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Overview — hierarchy tree view
# ---------------------------------------------------------------------------


def _status_icon(artifact_id: str, nodes: dict, edges: list[dict], ready_set: set[str]) -> str:
    """Return a status icon for the artifact.

    Icons:
    - checkmark  resolved artifact (only shown when show_all=True)
    - blocked    unresolved with unresolved deps
    - ready      unresolved with all deps satisfied
    - dot        otherwise (in progress, no specific ready/blocked state)
    """
    if _node_is_resolved(artifact_id, nodes):
        return "\u2713"  # checkmark ✓
    if artifact_id in ready_set:
        return "\u2192"  # right arrow →
    # Check if it has any unresolved depends-on deps
    for edge in edges:
        if edge.get("from") != artifact_id:
            continue
        if edge.get("type") != "depends-on":
            continue
        target = edge.get("to", "")
        if target and not _node_is_resolved(target, nodes):
            return "\u2298"  # circled division slash ⊘
    return "\u00b7"  # middle dot ·


def _render_subtree_v2(
    artifact_id: str,
    nodes: dict,
    edges: list[dict],
    children: dict,
    ready_set: set[str],
    show_all: bool,
    repo_root: str,
    show_links: bool,
    prefix: str,
    connector: str,
    visited: set[str],
    lines: list[str],
) -> None:
    """Recursively render artifact_id and its children into lines.

    prefix: the running indent prefix (accumulated from ancestors)
    connector: the connector to prepend to this node's line (e.g., "├── " or "└── " or "")
    """
    visited.add(artifact_id)
    node = nodes.get(artifact_id, {})
    display_id = _format_id(artifact_id, nodes, repo_root, show_links)
    status = node.get("status", "")
    title = node.get("title", "")
    icon = _status_icon(artifact_id, nodes, edges, ready_set)

    # Collect unresolved depends-on deps for blocked indicator
    unresolved_deps: list[str] = []
    for edge in edges:
        if edge.get("from") != artifact_id:
            continue
        if edge.get("type") != "depends-on":
            continue
        target = edge.get("to", "")
        if target and not _node_is_resolved(target, nodes):
            unresolved_deps.append(target)
    unresolved_deps.sort()

    blocking_info = ""
    if unresolved_deps:
        blocking_info = f"  [blocked by: {', '.join(unresolved_deps)}]"

    lines.append(f"{prefix}{connector}{icon} {display_id}  {status}  {title}{blocking_info}")

    # Get visible children
    child_ids = sorted(children.get(artifact_id, []))
    visible_children: list[str] = []
    for child_id in child_ids:
        if not show_all and _node_is_resolved(child_id, nodes):
            continue
        visible_children.append(child_id)

    for i, child_id in enumerate(visible_children):
        is_last = i == len(visible_children) - 1
        child_connector = "\u2514\u2500\u2500 " if is_last else "\u251c\u2500\u2500 "  # └── or ├──
        # Determine continuation prefix for children of this child
        if connector in ("\u2514\u2500\u2500 ", ""):
            child_prefix = prefix + "    "
        else:
            child_prefix = prefix + "\u2502   "  # │
        # For root nodes (connector==""), use empty continuation
        if connector == "":
            child_prefix = ""
        _render_subtree_v2(
            child_id,
            nodes,
            edges,
            children,
            ready_set,
            show_all,
            repo_root,
            show_links,
            child_prefix,
            child_connector,
            visited,
            lines,
        )


def overview(
    nodes: dict,
    edges: list[dict],
    show_all: bool = False,
    repo_root: str = "",
    show_links: bool = False,
) -> str:
    """Build a tree view of the artifact hierarchy.

    Artifacts are organized by parent-epic / parent-vision relationships.
    Roots (no parent edge outgoing) are rendered at the top level.
    Children are indented with classic Unix tree connectors.

    Sections:
    1. Hierarchy tree
    2. === Unparented === (unresolved artifacts not reachable from visible roots)
    3. === Cross-cutting === (artifacts in lateral edges)
    4. === Summary === (Ready / Blocked / Total unresolved counts)
    5. === Execution Tracking (tk ready) === (output of `tk ready` command)
    """
    # --- Step 1: Build adjacency maps ---
    # children[parent_id] = list of artifact IDs that have parent_id as parent
    children: dict[str, list[str]] = {}
    # has_parent = set of artifact IDs that have at least one outgoing parent edge
    has_parent: set[str] = set()

    for edge in edges:
        if edge.get("type") not in _PARENT_EDGE_TYPES:
            continue
        child_id = edge.get("from", "")
        parent_id = edge.get("to", "")
        if not child_id or not parent_id:
            continue
        has_parent.add(child_id)
        children.setdefault(parent_id, []).append(child_id)

    # --- Step 2: Find roots ---
    roots = sorted(artifact_id for artifact_id in nodes if artifact_id not in has_parent)

    # --- Step 3: Compute ready set ---
    ready_set = _compute_ready_set(nodes, edges)

    # --- Step 4: Render tree ---
    visited: set[str] = set()
    tree_lines: list[str] = []

    for root_id in roots:
        # Apply visibility filter for roots
        if not show_all and _node_is_resolved(root_id, nodes):
            # Mark as visited so we don't show it in unparented either
            visited.add(root_id)
            continue
        _render_subtree_v2(
            root_id,
            nodes,
            edges,
            children,
            ready_set,
            show_all,
            repo_root,
            show_links,
            "",   # prefix
            "",   # connector (root has no connector)
            visited,
            tree_lines,
        )

    lines: list[str] = list(tree_lines)

    # --- Step 5: Unparented section ---
    # Collect unresolved (or all, if show_all) artifacts NOT visited during tree walk
    unparented: list[str] = []
    for artifact_id in sorted(nodes):
        if artifact_id in visited:
            continue
        if not show_all and _node_is_resolved(artifact_id, nodes):
            continue
        unparented.append(artifact_id)

    if unparented:
        lines.append("")
        lines.append("=== Unparented ===")
        for artifact_id in unparented:
            node = nodes.get(artifact_id, {})
            display_id = _format_id(artifact_id, nodes, repo_root, show_links)
            status = node.get("status", "")
            title = node.get("title", "")
            icon = _status_icon(artifact_id, nodes, edges, ready_set)
            unresolved_deps_list: list[str] = []
            for edge in edges:
                if edge.get("from") != artifact_id:
                    continue
                if edge.get("type") != "depends-on":
                    continue
                target = edge.get("to", "")
                if target and not _node_is_resolved(target, nodes):
                    unresolved_deps_list.append(target)
            unresolved_deps_list.sort()
            blocking_info_u = f"  [blocked by: {', '.join(unresolved_deps_list)}]" if unresolved_deps_list else ""
            lines.append(f"{icon} {display_id}  {status}  {title}{blocking_info_u}")

    # --- Step 6: Cross-cutting section ---
    # Artifacts that appear in lateral edges where both endpoints are visible
    visible_ids: set[str] = set()
    for artifact_id in nodes:
        if show_all or not _node_is_resolved(artifact_id, nodes):
            visible_ids.add(artifact_id)

    cross_pairs: list[tuple[str, str]] = []
    seen_pairs: set[frozenset] = set()
    for edge in edges:
        if edge.get("type") not in _LATERAL_EDGE_TYPES:
            continue
        frm = edge.get("from", "")
        to = edge.get("to", "")
        if not frm or not to:
            continue
        if frm not in visible_ids or to not in visible_ids:
            continue
        pair: frozenset = frozenset({frm, to})
        if pair in seen_pairs:
            continue
        seen_pairs.add(pair)
        cross_pairs.append((frm, to))

    if cross_pairs:
        lines.append("")
        lines.append("=== Cross-cutting ===")
        for frm, to in sorted(cross_pairs):
            frm_display = _format_id(frm, nodes, repo_root, show_links)
            to_display = _format_id(to, nodes, repo_root, show_links)
            lines.append(f"{frm_display} <--> {to_display}")

    # --- Step 7: Summary ---
    all_unresolved = [aid for aid in nodes if not _node_is_resolved(aid, nodes)]
    ready_count = len(ready_set)
    blocked_count = sum(1 for aid in all_unresolved if aid not in ready_set)
    total_unresolved = len(all_unresolved)

    lines.append("")
    lines.append("=== Summary ===")
    lines.append(f"Ready: {ready_count}  Blocked: {blocked_count}  Total unresolved: {total_unresolved}")

    # --- Step 8: tk integration ---
    lines.append("")
    lines.append("=== Execution Tracking (tk ready) ===")
    try:
        result = subprocess.run(
            ["tk", "ready"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        tk_output = result.stdout.strip()
        if tk_output:
            lines.append(tk_output)
        else:
            lines.append("(no ready tasks)")
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        lines.append("(tk not found)")

    return "\n".join(lines)
