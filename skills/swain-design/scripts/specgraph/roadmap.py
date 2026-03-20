"""Deterministic roadmap output based on priority scores.

Renders Initiatives and Epics as a priority-sorted roadmap using
Eisenhower prioritization (importance × urgency).

Visual outputs:
- Quadrant chart: scatter plot positioning items by real weight/urgency data
- Staggered Gantt: priority rank determines timeline position, markers signal decisions
- Dependency graph: only connected nodes, cross-boundary edges highlighted
- Eisenhower table: hyperlinked detail with operator decision callouts

Grouping: by Initiative when one exists; standalone Epics as own group.
Ordering: by computed priority score descending, then artifact ID (tiebreaker).
Leaf level: Epic (SPECs are not rendered, but progress ratios are shown).
"""
from __future__ import annotations

from .queries import (
    _find_vision_ancestor,
    _node_is_resolved,
)
from .priority import resolve_vision_weight, _compute_unblock_count


_CONTAINER_TYPES = frozenset({"INITIATIVE", "EPIC"})
_PARENT_EDGE_TYPES = frozenset({"parent-epic", "parent-vision", "parent-initiative"})
_ACTIVE_STATUSES = frozenset({"Active", "Implementation", "Testing", "In Progress"})

QUADRANT_LABELS = {
    "do": ("Do First", "High priority, active or unblocking"),
    "schedule": ("Schedule", "High priority, not yet started"),
    "delegate": ("In Progress", "Active or unblocking, medium priority"),
    "evaluate": ("Backlog", "Not yet prioritized or started"),
}
QUADRANT_ORDER = ("do", "schedule", "delegate", "evaluate")


# ---------------------------------------------------------------------------
# Data collection
# ---------------------------------------------------------------------------

def _get_children(parent_id: str, edges: list[dict]) -> list[str]:
    children = []
    for e in edges:
        if e.get("type") in _PARENT_EDGE_TYPES and e.get("to") == parent_id:
            children.append(e["from"])
    return children


def _spec_progress(epic_id: str, nodes: dict, edges: list[dict]) -> tuple[int, int]:
    children = _get_children(epic_id, edges)
    total = complete = 0
    for cid in children:
        cnode = nodes.get(cid, {})
        if cnode.get("type", "").upper() != "SPEC":
            continue
        total += 1
        if _node_is_resolved(cid, nodes):
            complete += 1
    return complete, total


def collect_roadmap_items(
    nodes: dict,
    edges: list[dict],
    focus_vision: str | None = None,
) -> list[dict]:
    """Collect Initiatives and Epics with scores and grouping."""
    items: list[dict] = []

    for aid, node in nodes.items():
        atype = node.get("type", "").upper()
        if atype not in _CONTAINER_TYPES:
            continue
        if _node_is_resolved(aid, nodes):
            continue

        vision = _find_vision_ancestor(aid, nodes, edges)
        if focus_vision and vision != focus_vision:
            continue

        weight = resolve_vision_weight(aid, nodes, edges)
        unblocks = _compute_unblock_count(aid, nodes, edges)
        score = unblocks * weight

        if atype == "EPIC":
            parent_init = None
            for e in edges:
                if e.get("from") == aid and e.get("type") == "parent-initiative":
                    parent_init = e.get("to")
                    break
            if parent_init and parent_init in nodes:
                group = parent_init
                group_title = nodes[parent_init].get("title", parent_init)
            else:
                group = aid
                group_title = node.get("title", aid)
            complete, total = _spec_progress(aid, nodes, edges)
        elif atype == "INITIATIVE":
            group = aid
            group_title = node.get("title", aid)
            total = complete = 0
            for child_id in _get_children(aid, edges):
                cnode = nodes.get(child_id, {})
                if cnode.get("type", "").upper() == "EPIC":
                    c, t = _spec_progress(child_id, nodes, edges)
                    complete += c
                    total += t
        else:
            continue

        depends_on = []
        for e in edges:
            if e.get("from") == aid and e.get("type") == "depends-on":
                target = e.get("to", "")
                if target and not _node_is_resolved(target, nodes):
                    target_node = nodes.get(target, {})
                    if target_node.get("type", "").upper() in _CONTAINER_TYPES:
                        depends_on.append(target)

        items.append({
            "id": aid,
            "title": node.get("title", aid),
            "type": atype,
            "score": score,
            "weight": weight,
            "children_total": total,
            "children_complete": complete,
            "depends_on": sorted(depends_on),
            "group": group,
            "group_title": group_title,
            "vision_id": vision,
            "status": node.get("status", ""),
        })

    items.sort(key=lambda x: (-x["score"], x["id"]))
    return items


# ---------------------------------------------------------------------------
# Eisenhower classification
# ---------------------------------------------------------------------------

def _classify_eisenhower(item: dict) -> str:
    important = item["weight"] >= 3
    urgent = item["status"] in _ACTIVE_STATUSES or item["score"] > 0
    if important and urgent:
        return "do"
    elif important and not urgent:
        return "schedule"
    elif not important and urgent:
        return "delegate"
    else:
        return "evaluate"


def classify_epics_eisenhower(items: list[dict]) -> dict[str, list[dict]]:
    quadrants: dict[str, list[dict]] = {q: [] for q in QUADRANT_ORDER}
    for item in items:
        if item["type"] != "EPIC":
            continue
        quadrants[_classify_eisenhower(item)].append(item)
    return quadrants


def _operator_decision(item: dict) -> str:
    """Determine what operator decision an item needs, if any."""
    if item["status"] == "Proposed":
        return "activate or drop"
    if item["children_total"] == 0:
        return "needs decomposition"
    if item["children_complete"] == item["children_total"] and item["children_total"] > 0:
        return "ready to complete"
    return ""


# ---------------------------------------------------------------------------
# Mermaid helpers
# ---------------------------------------------------------------------------

def _safe_mermaid_id(artifact_id: str) -> str:
    return artifact_id.replace("-", "_")


def _escape_mermaid_label(text: str) -> str:
    return text.replace('"', "#quot;").replace(":", "#colon;")


# ---------------------------------------------------------------------------
# 1. Quadrant chart — scatter plot with data-driven positions
# ---------------------------------------------------------------------------

def _compute_urgency(item: dict) -> float:
    """Map item state to urgency score 0.0–1.0."""
    active = item["status"] in _ACTIVE_STATUSES
    unblocks = item["score"] // item["weight"] if item["weight"] else 0
    # Base urgency from status
    if active and unblocks > 0:
        return 0.85 + min(unblocks * 0.03, 0.10)
    elif active:
        return 0.65
    elif unblocks > 0:
        return 0.55 + min(unblocks * 0.05, 0.15)
    else:
        return 0.15


def _compute_importance(item: dict) -> float:
    """Map item weight to importance score 0.0–1.0."""
    if item["weight"] >= 3:
        return 0.80
    elif item["weight"] >= 2:
        return 0.40
    else:
        return 0.15


def render_quadrant_chart(items: list[dict]) -> str:
    """Render a Mermaid quadrantChart with items positioned by real data.

    X-axis = urgency (active status + unblock count)
    Y-axis = importance (vision weight cascade)
    Clusters of dots at similar positions = undifferentiated work (decision needed).
    Empty quadrants = potential blind spots.
    """
    epics = [i for i in items if i["type"] == "EPIC"]

    lines = [
        "quadrantChart",
        "    title Priority Matrix",
        '    x-axis "Low Urgency" --> "High Urgency"',
        '    y-axis "Low Importance" --> "High Importance"',
        "    quadrant-1 Do First",
        "    quadrant-2 Schedule",
        "    quadrant-3 Backlog",
        "    quadrant-4 In Progress",
    ]

    # Spread items within their region using deterministic jitter
    # so overlapping items fan out instead of stacking
    seen_positions: dict[tuple[float, float], int] = {}
    for item in epics:
        base_x = _compute_urgency(item)
        base_y = _compute_importance(item)

        # Deterministic jitter based on position collision count
        key = (round(base_x, 2), round(base_y, 2))
        count = seen_positions.get(key, 0)
        seen_positions[key] = count + 1
        # Fan out diagonally: odd items go up-right, even go down-left
        jitter = count * 0.04
        if count % 2 == 0:
            x = base_x + jitter
            y = base_y - jitter
        else:
            x = base_x - jitter
            y = base_y + jitter

        x = max(0.02, min(0.98, x))
        y = max(0.02, min(0.98, y))

        # Shorten long titles for readability
        title = item["title"]
        if len(title) > 35:
            title = title[:35]

        # quadrantChart labels cannot contain parens/brackets
        lines.append(f"    {title}: [{x:.2f}, {y:.2f}]")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 2. Staggered Gantt — priority rank determines position
# ---------------------------------------------------------------------------

def render_gantt(items: list[dict], nodes: dict) -> str:
    """Render a Mermaid Gantt chart staggered by priority.

    Higher-priority items start earlier. Items needing operator decisions
    are marked `crit`. Active items are marked `active`. Dependencies
    use `after` links. The staggering makes priority visually obvious —
    left = do now, right = do later.
    """
    q_order = {q: idx for idx, q in enumerate(QUADRANT_ORDER)}
    epics = sorted(
        [i for i in items if i["type"] == "EPIC"],
        key=lambda i: (q_order.get(_classify_eisenhower(i), 9), -i["score"], i["id"]),
    )

    if not epics:
        return "gantt\n    title Roadmap\n    %% No active Epics"

    # Assign staggered start dates based on priority rank
    # Group into tiers: same score+weight = same start
    task_alias: dict[str, str] = {}
    task_start_day: dict[str, int] = {}

    current_day = 1
    prev_key = None
    for idx, item in enumerate(epics):
        tier_key = (item["score"], item["weight"])
        if prev_key is not None and tier_key != prev_key:
            current_day += 14  # 2-week stagger between tiers
        prev_key = tier_key
        alias = f"t{idx}"
        task_alias[item["id"]] = alias
        task_start_day[item["id"]] = current_day

    lines = [
        "gantt",
        "    title Roadmap",
        "    dateFormat YYYY-MM-DD",
        "    axisFormat %b %d",
        "    tickInterval 1week",
    ]

    # Group by Eisenhower quadrant for sections
    quadrants = classify_epics_eisenhower(items)

    for qkey in QUADRANT_ORDER:
        qitems = quadrants[qkey]
        if not qitems:
            continue
        title, _ = QUADRANT_LABELS[qkey]
        lines.append(f"    section {title}")

        for item in qitems:
            alias = task_alias[item["id"]]
            progress = f"{item['children_complete']}/{item['children_total']}"
            label = _escape_mermaid_label(item["title"])

            # Determine marker: crit = needs decision, active = in progress
            decision = _operator_decision(item)
            if decision:
                marker = "crit, "
            elif item["status"] in _ACTIVE_STATUSES:
                marker = "active, "
            else:
                marker = ""

            # Dependencies override start position
            dep_aliases = [
                task_alias[d] for d in item["depends_on"]
                if d in task_alias and d != item["id"]
            ]
            if dep_aliases:
                start = f"after {' '.join(dep_aliases)}"
            else:
                day = task_start_day[item["id"]]
                start = f"2026-01-{day:02d}"

            lines.append(f"    {label} ({progress}) :{marker}{alias}, {start}, 14d")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 3. Dependency graph — only connected nodes, cross-boundary annotations
# ---------------------------------------------------------------------------

def render_dependency_graph(items: list[dict], nodes: dict) -> str | None:
    """Render a Mermaid flowchart showing only items with dependencies.

    Cross-priority-boundary edges (e.g., a Backlog item blocking a Do First
    item) use thick red arrows to surface prioritization smells.
    """
    epic_map = {i["id"]: i for i in items if i["type"] == "EPIC"}
    edge_list: list[tuple[str, str]] = []
    involved: set[str] = set()

    for item in epic_map.values():
        for dep in item["depends_on"]:
            edge_list.append((item["id"], dep))
            involved.add(item["id"])
            involved.add(dep)

    if not edge_list:
        return None

    # Quadrant classification for cross-boundary detection
    q_rank = {"do": 0, "schedule": 1, "delegate": 2, "evaluate": 3}

    lines = ["graph LR"]

    # Style classes for quadrant membership
    lines.append("    classDef doFirst fill:#ff6b6b,stroke:#c92a2a,color:#fff")
    lines.append("    classDef scheduled fill:#ffd43b,stroke:#e67700,color:#000")
    lines.append("    classDef inProgress fill:#74c0fc,stroke:#1971c2,color:#000")
    lines.append("    classDef backlog fill:#dee2e6,stroke:#868e96,color:#000")

    qclass = {"do": "doFirst", "schedule": "scheduled",
              "delegate": "inProgress", "evaluate": "backlog"}

    for item_id in sorted(involved):
        item = epic_map.get(item_id)
        if item is None:
            continue
        eid = _safe_mermaid_id(item_id)
        elabel = _escape_mermaid_label(item["title"])
        q = _classify_eisenhower(item)
        cls = qclass[q]
        lines.append(f'    {eid}["{elabel}"]:::{cls}')

    for src_id, dst_id in sorted(edge_list):
        src = _safe_mermaid_id(src_id)
        dst = _safe_mermaid_id(dst_id)

        src_item = epic_map.get(src_id)
        dst_item = epic_map.get(dst_id)
        if src_item and dst_item:
            src_q = _classify_eisenhower(src_item)
            dst_q = _classify_eisenhower(dst_item)
            src_rank = q_rank.get(src_q, 9)
            dst_rank = q_rank.get(dst_q, 9)
            # Cross-boundary: blocker is lower priority than the blocked item
            if dst_rank > src_rank:
                lines.append(f"    {src} ==>|blocked by lower priority| {dst}")
                continue

        lines.append(f"    {src} -->|blocks| {dst}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Markdown helpers
# ---------------------------------------------------------------------------

def _md_link(artifact_id: str, title: str, nodes: dict) -> str:
    node = nodes.get(artifact_id, {})
    filepath = node.get("file", "")
    if filepath:
        return f"[{title}]({filepath})"
    return title


# ---------------------------------------------------------------------------
# 4. Eisenhower table — detail view with decision callouts
# ---------------------------------------------------------------------------

def render_eisenhower_table(items: list[dict], nodes: dict) -> str:
    """Render Eisenhower quadrant tables with hyperlinks and decision signals."""
    quadrants = classify_epics_eisenhower(items)

    sections = []
    for qkey in QUADRANT_ORDER:
        qitems = quadrants[qkey]
        title, subtitle = QUADRANT_LABELS[qkey]
        sections.append(f"### {title}")
        sections.append(f"*{subtitle}*")
        sections.append("")
        if not qitems:
            sections.append("*(none)*")
            sections.append("")
            continue
        sections.append("| Epic | Initiative | Progress | Unblocks | Needs |")
        sections.append("|------|-----------|----------|----------|-------|")
        for item in qitems:
            progress = f"{item['children_complete']}/{item['children_total']}"
            unblocks = item["score"] // item["weight"] if item["weight"] else 0
            epic_link = _md_link(item["id"], item["title"], nodes)
            if item["group"] != item["id"]:
                init_link = _md_link(item["group"], item["group_title"], nodes)
            else:
                init_link = "—"
            decision = _operator_decision(item)
            needs = f"**{decision}**" if decision else "—"
            sections.append(
                f"| {epic_link} | {init_link} | {progress} | {unblocks} | {needs} |"
            )
        sections.append("")

    return "\n".join(sections)


# ---------------------------------------------------------------------------
# Markdown assembly
# ---------------------------------------------------------------------------

def render_roadmap_markdown(
    items: list[dict],
    nodes: dict,
) -> str:
    """Render a full ROADMAP.md with all visual and tabular views."""
    quadrant = render_quadrant_chart(items)
    eisenhower = render_eisenhower_table(items, nodes)
    gantt = render_gantt(items, nodes)
    dep_graph = render_dependency_graph(items, nodes)

    lines = [
        "# Roadmap",
        "",
        "<!-- Auto-generated by `chart.sh roadmap`. Do not edit manually. -->",
        "",
        "```mermaid",
        quadrant,
        "```",
        "",
        eisenhower,
        "## Timeline",
        "",
        "```mermaid",
        gantt,
        "```",
        "",
    ]

    if dep_graph:
        lines.extend([
            "## Blocking Dependencies",
            "",
            "```mermaid",
            dep_graph,
            "```",
            "",
        ])

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI entry point (raw format output)
# ---------------------------------------------------------------------------

def render_roadmap(
    nodes: dict,
    edges: list[dict],
    fmt: str = "mermaid-gantt",
    focus_vision: str | None = None,
    json_output: bool = False,
) -> str:
    items = collect_roadmap_items(nodes, edges, focus_vision)

    if json_output:
        import json
        return json.dumps(items, indent=2)

    if fmt == "mermaid-flowchart":
        dep = render_dependency_graph(items, nodes)
        return dep or "graph LR\n    %% No Epic-level dependencies"
    elif fmt == "both":
        gantt = render_gantt(items, nodes)
        dep = render_dependency_graph(items, nodes)
        parts = [gantt]
        if dep:
            parts.append(dep)
        return "\n\n".join(parts)
    else:
        return render_gantt(items, nodes)
