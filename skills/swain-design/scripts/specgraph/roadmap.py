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

import os

from .queries import (
    _find_vision_ancestor,
    _node_is_resolved,
)
from .priority import resolve_vision_weight, _compute_unblock_count

try:
    from jinja2 import Environment, FileSystemLoader
    _HAS_JINJA = True
except ImportError:
    _HAS_JINJA = False


def _jinja_env() -> "Environment":
    template_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'templates', 'roadmap')
    return Environment(
        loader=FileSystemLoader(template_dir),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )


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
            "sort_order": node.get("sort_order", 0),
        })

    items.sort(key=lambda x: (-x["score"], -x.get("sort_order", 0), x["id"]))

    # --- Derived fields (SPEC-108) ---
    # Compute chart positions for EPICs (weight-tier spreading + jitter)
    epics_for_chart = [i for i in items if i["type"] == "EPIC"]
    weight_tiers: dict[str, list[dict]] = {"high": [], "medium": [], "low": []}
    for item in epics_for_chart:
        if item["weight"] >= 3:
            weight_tiers["high"].append(item)
        elif item["weight"] >= 2:
            weight_tiers["medium"].append(item)
        else:
            weight_tiers["low"].append(item)

    tier_index: dict[str, int] = {}
    tier_size: dict[str, int] = {}
    for tier_name, tier_items in weight_tiers.items():
        tier_size[tier_name] = len(tier_items)
        for idx, item in enumerate(tier_items):
            tier_index[item["id"]] = idx

    tier_ranges = {"high": (0.70, 0.95), "medium": (0.25, 0.55), "low": (0.05, 0.20)}
    seen_positions: dict[tuple[float, float], int] = {}

    for item in items:
        item["quadrant"] = _classify_eisenhower(item)
        item["quadrant_label"] = QUADRANT_LABELS[item["quadrant"]][0]
        item["short_id"] = _short_id(item["id"])
        item["operator_decision"] = _operator_decision(item)
        item["display_score"] = item["weight"] + (
            item["score"] + 1 if item["status"] in _ACTIVE_STATUSES else item["score"]
        )

        if item["type"] == "EPIC":
            base_x = _compute_urgency(item)
            tier_name = (
                "high" if item["weight"] >= 3
                else ("medium" if item["weight"] >= 2 else "low")
            )
            y_lo, y_hi = tier_ranges[tier_name]
            n = tier_size[tier_name]
            idx = tier_index[item["id"]]
            base_y = y_lo + (y_hi - y_lo) * idx / (n - 1) if n > 1 else (y_lo + y_hi) / 2

            key = (round(base_x, 2), round(base_y, 2))
            count = seen_positions.get(key, 0)
            seen_positions[key] = count + 1
            jitter = count * 0.06
            direction = count % 4
            dx = jitter if direction in (0, 2) else -jitter
            dy = jitter if direction in (0, 3) else -jitter
            item["chart_x"] = max(0.02, min(0.98, base_x + dx))
            item["chart_y"] = max(0.02, min(0.98, base_y + dy))
        else:
            # INITIATIVE items don't appear in the quadrant chart
            item["chart_x"] = 0.0
            item["chart_y"] = 0.0

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
        quadrants[item["quadrant"]].append(item)
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



def _short_id(artifact_id: str) -> str:
    """Convert EPIC-031 to E31 or INITIATIVE-005 to I5 for compact chart labels."""
    prefix = artifact_id.split("-", 1)[0].upper() if "-" in artifact_id else ""
    num = artifact_id.split("-", 1)[1] if "-" in artifact_id else artifact_id
    letter = "I" if prefix == "INITIATIVE" else "E"
    return f"{letter}{num.lstrip('0') or '0'}"


def render_quadrant_chart(items: list[dict]) -> tuple[str, list[dict]]:
    """Render a Mermaid quadrantChart with short ID labels.

    Returns (mermaid_source, legend_items) where legend_items is
    a list of dicts with {short_id, id, title, quadrant} for the legend table.
    """
    epics = [i for i in items if i["type"] == "EPIC"]

    legend_items: list[dict] = []
    for item in epics:
        legend_items.append({
            "short_id": item["short_id"],
            "id": item["id"],
            "title": item["title"],
            "quadrant": item["quadrant_label"],
        })

    if _HAS_JINJA:
        env = _jinja_env()
        tmpl = env.get_template("quadrant.mmd.j2")
        mermaid_src = tmpl.render(epics=epics).rstrip("\n")
    else:
        lines = [
            "%%{init: {'quadrantChart': {'chartWidth': 700, 'chartHeight': 500, 'pointLabelFontSize': 14}}}%%",
            "quadrantChart",
            "    title Priority Matrix",
            '    x-axis "Low Urgency" --> "High Urgency"',
            '    y-axis "Low Importance" --> "High Importance"',
            "    quadrant-1 Do First",
            "    quadrant-2 Schedule",
            "    quadrant-3 Backlog",
            "    quadrant-4 In Progress",
        ]
        for item in epics:
            lines.append(f"    {item['short_id']}: [{item['chart_x']:.2f}, {item['chart_y']:.2f}]")
        mermaid_src = "\n".join(lines)

    return mermaid_src, legend_items


def _render_quadrant_png(mermaid_source: str, repo_root: str) -> str | None:
    """Render Mermaid source to PNG via mmdc. Returns relative path or None."""
    import shutil
    import subprocess
    import tempfile

    if not shutil.which("mmdc"):
        return None

    assets_dir = os.path.join(repo_root, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    png_path = os.path.join(assets_dir, "quadrant.png")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".mmd", delete=False) as f:
        f.write(mermaid_source)
        mmd_path = f.name

    try:
        subprocess.run(
            ["mmdc", "-i", mmd_path, "-o", png_path, "-w", "800", "-b", "transparent"],
            capture_output=True, timeout=30,
        )
        return "assets/quadrant.png" if os.path.isfile(png_path) else None
    except (subprocess.TimeoutExpired, OSError):
        return None
    finally:
        os.unlink(mmd_path)


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
        key=lambda i: (q_order.get(i["quadrant"], 9), -i["score"], i["id"]),
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

    # Group by Eisenhower quadrant for sections
    quadrants = classify_epics_eisenhower(items)

    if _HAS_JINJA:
        quadrant_sections: list[dict] = []
        for qkey in QUADRANT_ORDER:
            qitems = quadrants[qkey]
            if not qitems:
                continue
            title, _ = QUADRANT_LABELS[qkey]
            tasks: list[dict] = []
            for item in qitems:
                alias = task_alias[item["id"]]
                progress = f"{item['children_complete']}/{item['children_total']}"
                title_text = item["title"]
                if len(title_text) > 30:
                    title_text = title_text[:30]
                label = _escape_mermaid_label(title_text)

                decision = item["operator_decision"]
                if decision:
                    marker = "crit, "
                elif item["status"] in _ACTIVE_STATUSES:
                    marker = "active, "
                else:
                    marker = ""

                dep_aliases = [
                    task_alias[d] for d in item["depends_on"]
                    if d in task_alias and d != item["id"]
                ]
                if dep_aliases:
                    start = f"after {' '.join(dep_aliases)}"
                else:
                    day = task_start_day[item["id"]]
                    start = f"2026-01-{day:02d}"

                tasks.append({
                    "label": label,
                    "progress": progress,
                    "marker": marker,
                    "alias": alias,
                    "start": start,
                })
            quadrant_sections.append({"title": title, "tasks": tasks})

        env = _jinja_env()
        tmpl = env.get_template("gantt.mmd.j2")
        return tmpl.render(quadrants=quadrant_sections).rstrip("\n")
    else:
        lines = [
            "gantt",
            "    title Roadmap",
            "    dateFormat YYYY-MM-DD",
            "    axisFormat %b %d",
            "    tickInterval 1week",
        ]

        for qkey in QUADRANT_ORDER:
            qitems = quadrants[qkey]
            if not qitems:
                continue
            title, _ = QUADRANT_LABELS[qkey]
            lines.append(f"    section {title}")

            for item in qitems:
                alias = task_alias[item["id"]]
                progress = f"{item['children_complete']}/{item['children_total']}"
                title_text = item["title"]
                if len(title_text) > 30:
                    title_text = title_text[:30]
                label = _escape_mermaid_label(title_text)

                # Determine marker: crit = needs decision, active = in progress
                decision = item["operator_decision"]
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

    qclass = {"do": "doFirst", "schedule": "scheduled",
              "delegate": "inProgress", "evaluate": "backlog"}

    # Group involved nodes by initiative
    by_initiative: dict[str, list[dict]] = {}
    standalone_nodes: list[dict] = []
    for item_id in sorted(involved):
        item = epic_map.get(item_id)
        if item is None:
            continue
        if item["group"] != item["id"]:
            by_initiative.setdefault(item["group"], []).append(item)
        else:
            standalone_nodes.append(item)

    # Fallback: if all subgraphs are single-node, use flat layout
    all_single = all(len(v) <= 1 for v in by_initiative.values())
    use_subgraphs = bool(by_initiative) and not all_single

    if _HAS_JINJA:
        jinja_edges: list[dict] = []
        for src_id, dst_id in sorted(edge_list):
            src = _safe_mermaid_id(src_id)
            dst = _safe_mermaid_id(dst_id)

            cross_boundary = False
            src_item = epic_map.get(src_id)
            dst_item = epic_map.get(dst_id)
            if src_item and dst_item:
                src_rank = q_rank.get(src_item["quadrant"], 9)
                dst_rank = q_rank.get(dst_item["quadrant"], 9)
                if dst_rank > src_rank:
                    cross_boundary = True

            jinja_edges.append({"src": src, "dst": dst, "cross_boundary": cross_boundary})

        subgraph_data = []
        if use_subgraphs:
            for init_id, init_items in sorted(by_initiative.items()):
                init_node = nodes.get(init_id, {})
                subgraph_data.append({
                    "id": _safe_mermaid_id(init_id),
                    "title": _escape_mermaid_label(init_node.get("title", init_id)),
                    "nodes": [{
                        "eid": _safe_mermaid_id(item["id"]),
                        "elabel": _escape_mermaid_label(item["title"]),
                        "cls": qclass[item["quadrant"]],
                    } for item in init_items],
                })

        standalone_data = [{
            "eid": _safe_mermaid_id(item["id"]),
            "elabel": _escape_mermaid_label(item["title"]),
            "cls": qclass[item["quadrant"]],
        } for item in standalone_nodes]

        # If not using subgraphs, put all nodes in standalone
        if not use_subgraphs:
            for init_items in by_initiative.values():
                for item in init_items:
                    standalone_data.append({
                        "eid": _safe_mermaid_id(item["id"]),
                        "elabel": _escape_mermaid_label(item["title"]),
                        "cls": qclass[item["quadrant"]],
                    })
            standalone_data.sort(key=lambda n: n["eid"])

        env = _jinja_env()
        tmpl = env.get_template("deps.mmd.j2")
        return tmpl.render(
            subgraphs=subgraph_data,
            standalone_nodes=standalone_data,
            edges=jinja_edges,
            use_subgraphs=use_subgraphs,
        ).rstrip("\n")
    else:
        lines = ["graph LR"]

        # Style classes for quadrant membership
        lines.append("    classDef doFirst fill:#e03131,stroke:#c92a2a,color:#fff")
        lines.append("    classDef scheduled fill:#f59f00,stroke:#e67700,color:#000")
        lines.append("    classDef inProgress fill:#1c7ed6,stroke:#1864ab,color:#fff")
        lines.append("    classDef backlog fill:#868e96,stroke:#495057,color:#fff")

        if use_subgraphs:
            for init_id, init_items in sorted(by_initiative.items()):
                init_node_data = nodes.get(init_id, {})
                sg_id = _safe_mermaid_id(init_id)
                sg_title = _escape_mermaid_label(init_node_data.get("title", init_id))
                lines.append(f'    subgraph {sg_id}["{sg_title}"]')
                for item in init_items:
                    eid = _safe_mermaid_id(item["id"])
                    elabel = _escape_mermaid_label(item["title"])
                    cls = qclass[item["quadrant"]]
                    lines.append(f'        {eid}["{elabel}"]:::{cls}')
                lines.append("    end")

        # Standalone nodes (outside subgraphs)
        for item in standalone_nodes:
            eid = _safe_mermaid_id(item["id"])
            elabel = _escape_mermaid_label(item["title"])
            cls = qclass[item["quadrant"]]
            lines.append(f'    {eid}["{elabel}"]:::{cls}')

        # If not using subgraphs, render all as flat
        if not use_subgraphs:
            for item_id in sorted(involved):
                item = epic_map.get(item_id)
                if item is None:
                    continue
                eid = _safe_mermaid_id(item_id)
                elabel = _escape_mermaid_label(item["title"])
                cls = qclass[item["quadrant"]]
                lines.append(f'    {eid}["{elabel}"]:::{cls}')

        for src_id, dst_id in sorted(edge_list):
            src = _safe_mermaid_id(src_id)
            dst = _safe_mermaid_id(dst_id)

            src_item = epic_map.get(src_id)
            dst_item = epic_map.get(dst_id)
            if src_item and dst_item:
                src_q = src_item["quadrant"]
                dst_q = dst_item["quadrant"]
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
    """Render Eisenhower quadrant tables with initiative-first grouping.

    Initiative column only shows on the first row of each initiative group.
    Items within each initiative are consecutive, sorted by score descending.
    """
    quadrants = classify_epics_eisenhower(items)

    if _HAS_JINJA:
        quadrant_data: list[dict] = []
        for qkey in QUADRANT_ORDER:
            qitems = quadrants[qkey]
            title, subtitle = QUADRANT_LABELS[qkey]

            if not qitems:
                quadrant_data.append({
                    "title": title,
                    "subtitle": subtitle,
                    "groups": [],
                })
                continue

            by_init: dict[str, list[dict]] = {}
            for item in qitems:
                key = item["group"]
                by_init.setdefault(key, []).append(item)

            for key in by_init:
                by_init[key].sort(key=lambda i: (-i["score"], i["id"]))

            sorted_groups = sorted(
                by_init.items(),
                key=lambda kv: (-max(i["score"] for i in kv[1]), kv[0]),
            )

            groups: list[dict] = []
            for group_key, group_items in sorted_groups:
                rows: list[dict] = []
                for idx, item in enumerate(group_items):
                    progress = f"{item['children_complete']}/{item['children_total']}"
                    unblocks = item["score"] // item["weight"] if item["weight"] else 0
                    epic_link = _md_link(item["id"], item["title"], nodes)
                    decision = item["operator_decision"]
                    needs = f"**{decision}**" if decision else "—"

                    if idx == 0 and item["group"] != item["id"]:
                        init_cell = _md_link(item["group"], item["group_title"], nodes)
                    elif idx == 0:
                        init_cell = "—"
                    else:
                        init_cell = ""

                    rows.append({
                        "init_cell": init_cell,
                        "epic_link": epic_link,
                        "progress": progress,
                        "unblocks": unblocks,
                        "needs": needs,
                    })
                groups.append({"rows": rows})

            quadrant_data.append({
                "title": title,
                "subtitle": subtitle,
                "groups": groups,
            })

        env = _jinja_env()
        tmpl = env.get_template("eisenhower.md.j2")
        return tmpl.render(quadrants=quadrant_data).rstrip("\n") + "\n"
    else:
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

            # Group by initiative, sort initiatives by max score desc
            by_init: dict[str, list[dict]] = {}
            for item in qitems:
                key = item["group"]
                by_init.setdefault(key, []).append(item)

            # Sort each group internally by score desc
            for key in by_init:
                by_init[key].sort(key=lambda i: (-i["score"], i["id"]))

            # Sort initiative groups by max score desc
            sorted_groups = sorted(
                by_init.items(),
                key=lambda kv: (-max(i["score"] for i in kv[1]), kv[0]),
            )

            sections.append("| Initiative | Epic | Progress | Unblocks | Needs |")
            sections.append("|-----------|------|----------|----------|-------|")

            for group_key, group_items in sorted_groups:
                for idx, item in enumerate(group_items):
                    progress = f"{item['children_complete']}/{item['children_total']}"
                    unblocks = item["score"] // item["weight"] if item["weight"] else 0
                    epic_link = _md_link(item["id"], item["title"], nodes)
                    decision = item["operator_decision"]
                    needs = f"**{decision}**" if decision else "—"

                    # Only show initiative on first row of each group
                    if idx == 0 and item["group"] != item["id"]:
                        init_link = _md_link(item["group"], item["group_title"], nodes)
                    elif idx == 0:
                        init_link = "—"
                    else:
                        init_link = ""

                    sections.append(
                        f"| {init_link} | {epic_link} | {progress} | {unblocks} | {needs} |"
                    )
            sections.append("")

        return "\n".join(sections)


# ---------------------------------------------------------------------------
# Markdown assembly
# ---------------------------------------------------------------------------

def _render_legend_single_row(legend_items: list[dict], nodes: dict, all_items: list[dict]) -> str:
    """Render legend as a single-line string for one markdown table cell.

    Groups by quadrant, then by initiative. Double <br> between quadrants
    for visual breathing room. Score-ordered within each quadrant.
    """
    init_for_epic: dict[str, str] = {}
    init_title: dict[str, str] = {}
    item_score: dict[str, float] = {}
    for item in all_items:
        if item["type"] == "EPIC":
            if item["group"] != item["id"]:
                init_for_epic[item["id"]] = item["group"]
                init_title[item["group"]] = item["group_title"]
            item_score[item["id"]] = item["display_score"]

    grouped: dict[str, list[dict]] = {}
    for item in legend_items:
        grouped.setdefault(item["quadrant"], []).append(item)

    # Build parts lists per quadrant (shared logic for both paths)
    quadrant_parts: list[list[str]] = []
    for qkey in QUADRANT_ORDER:
        qlabel = QUADRANT_LABELS[qkey][0]
        qitems = grouped.get(qlabel, [])
        if not qitems:
            continue

        by_init: dict[str, list[dict]] = {}
        standalone: list[dict] = []
        for item in qitems:
            iid = init_for_epic.get(item["id"])
            if iid:
                by_init.setdefault(iid, []).append(item)
            else:
                standalone.append(item)

        for iid in by_init:
            by_init[iid].sort(key=lambda e: -item_score.get(e["id"], 0))

        sorted_inits = sorted(
            by_init.items(),
            key=lambda kv: -max(item_score.get(e["id"], 0) for e in kv[1]),
        )

        parts: list[str] = [f"**{qlabel}**"]
        for iid, epics in sorted_inits:
            iname = init_title.get(iid, iid)
            epic_links = ", ".join(
                _md_link(e["id"], e["short_id"], nodes) for e in epics
            )
            parts.append(f"*{iname}* — {epic_links}")

        for item in sorted(standalone, key=lambda e: -item_score.get(e["id"], 0)):
            link = _md_link(item["id"], item["short_id"], nodes)
            parts.append(f"{link} {item['title']}")

        quadrant_parts.append(parts)

    if _HAS_JINJA:
        quadrant_blocks = [{"parts": p} for p in quadrant_parts]
        env = _jinja_env()
        tmpl = env.get_template("legend.md.j2")
        return tmpl.render(quadrant_blocks=quadrant_blocks).rstrip("\n")
    else:
        return " <br> <br> ".join(" <br> ".join(parts) for parts in quadrant_parts)


def render_roadmap_markdown(
    items: list[dict],
    nodes: dict,
    repo_root: str = "",
) -> str:
    """Render a full ROADMAP.md with all visual and tabular views.

    If mmdc is available, renders the quadrant chart to PNG and embeds it
    in a markdown table with a side-by-side legend. Falls back to inline
    Mermaid if mmdc is not found.
    """
    quadrant_src, legend_items = render_quadrant_chart(items)
    eisenhower = render_eisenhower_table(items, nodes)
    gantt = render_gantt(items, nodes)
    dep_graph = render_dependency_graph(items, nodes)

    # Quadrant chart: try PNG side-by-side, fall back to inline Mermaid
    png_path = _render_quadrant_png(quadrant_src, repo_root) if repo_root else None
    legend_cell = _render_legend_single_row(legend_items, nodes, items) if png_path else ""

    if _HAS_JINJA:
        env = _jinja_env()
        tmpl = env.get_template("roadmap.md.j2")
        return tmpl.render(
            png_path=png_path,
            quadrant_src=quadrant_src,
            legend_cell=legend_cell,
            eisenhower=eisenhower,
            gantt=gantt,
            dep_graph=dep_graph,
        ).rstrip("\n") + "\n"
    else:
        lines = [
            "# Roadmap",
            "",
            "<!-- Auto-generated by `chart.sh roadmap`. Do not edit manually. -->",
            "",
        ]

        if png_path:
            lines.extend([
                "| Priority Matrix | Legend |",
                "|:---:|:---|",
                f"| ![Priority Matrix]({png_path}) | {legend_cell} |",
                "",
            ])
        else:
            # Fallback: inline Mermaid (no side-by-side)
            lines.extend([
                "```mermaid",
                quadrant_src,
                "```",
                "",
            ])

        lines.extend([
            eisenhower,
            "## Timeline",
            "",
            "```mermaid",
            gantt,
            "```",
            "",
        ])

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
