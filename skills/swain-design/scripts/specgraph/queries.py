"""Query functions for specgraph: blocks, blocked_by, tree, edges_cmd.

These implement the four primary graph query commands. Each operates on the
in-memory graph cache (nodes dict + edges list) and returns plain text output.
"""

from __future__ import annotations

from collections import deque

from .links import art_link
from .resolved import is_resolved


def _node_is_resolved(artifact_id: str, nodes: dict) -> bool:
    """Return True if the artifact is resolved (considering its type)."""
    node = nodes.get(artifact_id)
    if node is None:
        # Unknown node — treat as unresolved (conservative)
        return False
    return is_resolved(node.get("type", ""), node.get("status", ""))


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
    return "\n".join(result)


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
    return "\n".join(result)


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

    return "\n".join(result)


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
