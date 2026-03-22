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
Direct children of Initiatives (SPECs, Spikes) also count toward progress.
"""
from __future__ import annotations

import os

from .queries import (
    _find_vision_ancestor,
    _node_is_resolved,
)
from .priority import (
    resolve_vision_weight,
    _compute_unblock_count,
    _is_decision_type,
    rank_recommendations,
    compute_decision_debt,
)

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


def _compute_descendants(artifact_id: str, edges: list[dict]) -> set[str]:
    """BFS to collect all descendants (children, grandchildren, etc.), including self."""
    visited: set[str] = {artifact_id}
    queue = [artifact_id]
    while queue:
        current = queue.pop(0)
        for child in _get_children(current, edges):
            if child not in visited:
                visited.add(child)
                queue.append(child)
    return visited


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
    scope: str | None = None,
) -> list[dict]:
    """Collect Initiatives and Epics with scores and grouping."""
    items: list[dict] = []

    # Scope filtering: compute the set of artifact IDs in scope
    scope_ids: set[str] | None = None
    if scope:
        if scope not in nodes:
            return []
        scope_ids = _compute_descendants(scope, edges)
    elif focus_vision:
        # Legacy: treat as scope for backward compat during transition
        if focus_vision not in nodes:
            return []
        scope_ids = _compute_descendants(focus_vision, edges)

    # Track direct-child specs/spikes of initiatives for second pass
    initiative_direct_children: list[tuple[str, str]] = []  # (child_id, parent_init_id)

    for aid, node in nodes.items():
        atype = node.get("type", "").upper()
        if atype not in _CONTAINER_TYPES:
            continue
        if _node_is_resolved(aid, nodes):
            continue

        if scope_ids is not None and aid not in scope_ids:
            continue

        vision = _find_vision_ancestor(aid, nodes, edges)

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
                child_type = cnode.get("type", "").upper()
                if child_type == "EPIC":
                    c, t = _spec_progress(child_id, nodes, edges)
                    complete += c
                    total += t
                elif child_type in ("SPEC", "SPIKE"):
                    total += 1
                    if _node_is_resolved(child_id, nodes):
                        complete += 1
                    else:
                        initiative_direct_children.append((child_id, aid))
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

    # Second pass: emit unresolved direct-child SPECs/Spikes as items
    # grouped under their parent Initiative (SPEC-115)
    for child_id, parent_init_id in initiative_direct_children:
        child_node = nodes.get(child_id, {})
        if scope_ids is not None and child_id not in scope_ids:
            continue
        vision = _find_vision_ancestor(child_id, nodes, edges)
        weight = resolve_vision_weight(child_id, nodes, edges)
        unblocks = _compute_unblock_count(child_id, nodes, edges)
        score = unblocks * weight
        init_node = nodes.get(parent_init_id, {})

        depends_on = []
        for e in edges:
            if e.get("from") == child_id and e.get("type") == "depends-on":
                target = e.get("to", "")
                if target and not _node_is_resolved(target, nodes):
                    depends_on.append(target)

        items.append({
            "id": child_id,
            "title": child_node.get("title", child_id),
            "type": child_node.get("type", "").upper(),
            "score": score,
            "weight": weight,
            "children_total": 0,
            "children_complete": 0,
            "depends_on": sorted(depends_on),
            "group": parent_init_id,
            "group_title": init_node.get("title", parent_init_id),
            "vision_id": vision,
            "status": child_node.get("status", ""),
            "sort_order": child_node.get("sort_order", 0),
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

    # Y ranges must not cross the 0.5 midline (Mermaid quadrant boundary)
    # to prevent items appearing in the wrong visual quadrant.
    tier_ranges = {"high": (0.70, 0.95), "medium": (0.25, 0.48), "low": (0.05, 0.20)}

    # First pass: compute base positions and derived fields
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
            item["chart_x"] = base_x
            item["chart_y"] = base_y
        else:
            item["chart_x"] = 0.0
            item["chart_y"] = 0.0

    # Second pass: X-axis jitter for items sharing the same base urgency.
    # When multiple EPICs land on the same X, alternate them left/right
    # so labels don't stack into an illegible vertical column.
    from collections import defaultdict
    x_groups: dict[float, list[dict]] = defaultdict(list)
    for item in items:
        if item["type"] == "EPIC":
            x_groups[round(item["chart_x"], 2)].append(item)

    for base_x_rounded, group in x_groups.items():
        if len(group) <= 1:
            continue
        # Spread items around their base X using a zigzag pattern.
        # Step size scales down when there are many items so they
        # stay within a reasonable band (~0.12 total width).
        step = min(0.04, 0.12 / len(group))
        for i, item in enumerate(group):
            # Alternate: 0, +step, -step, +2*step, -2*step, ...
            offset_idx = (i + 1) // 2
            sign = 1 if i % 2 == 1 else -1
            if i == 0:
                dx = 0.0  # first item stays at base
            else:
                dx = sign * offset_idx * step
            item["chart_x"] = max(0.02, min(0.98, item["chart_x"] + dx))

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
        if item["type"] == "INITIATIVE":
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
    _PREFIX_LETTERS = {"INITIATIVE": "I", "EPIC": "E", "SPEC": "S", "SPIKE": "SK"}
    letter = _PREFIX_LETTERS.get(prefix, prefix[0] if prefix else "?")
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
    leaf_items = sorted(
        [i for i in items if i["type"] != "INITIATIVE"],
        key=lambda i: (q_order.get(i["quadrant"], 9), -i["score"], i["id"]),
    )

    if not leaf_items:
        return "gantt\n    title Roadmap\n    %% No active items"

    # Assign staggered start dates based on priority rank
    # Group into tiers: same score+weight = same start
    task_alias: dict[str, str] = {}
    task_start_day: dict[str, int] = {}

    current_day = 1
    prev_key = None
    for idx, item in enumerate(leaf_items):
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
        lines = ["flowchart TD"]

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


def render_decisions_section(
    items: list[dict],
    nodes: dict,
    edges: list[dict],
) -> str:
    """Render the Decisions section for ROADMAP.md.

    Buckets ready items into "Decisions Waiting on You" (operator-gated)
    and "Implementation Ready (agent can handle)" (agent-delegatable).
    Returns markdown string. Shows empty-state message when no decisions exist.
    """
    recommendations = rank_recommendations(nodes, edges)
    rec_by_id = {r["id"]: r for r in recommendations}

    # Only include items that are in the ready set (from recommendations)
    ready_ids = set(rec_by_id.keys())

    operator_items: list[dict] = []
    impl_items: list[dict] = []

    for rec in recommendations:
        rid = rec["id"]
        node = nodes.get(rid, {})
        title = node.get("title", rid)
        unblocks = rec["unblock_count"]

        entry = {
            "id": rid,
            "title": title,
            "unblocks": unblocks,
            "score": rec["score"],
        }

        if rec["is_decision"]:
            operator_items.append(entry)
        else:
            impl_items.append(entry)

    # Sort by unblocks descending, then score descending
    operator_items.sort(key=lambda x: (-x["unblocks"], -x["score"], x["id"]))
    impl_items.sort(key=lambda x: (-x["unblocks"], -x["score"], x["id"]))

    lines: list[str] = []

    if not operator_items and not impl_items:
        lines.append("## Decisions")
        lines.append("")
        lines.append("No decisions needed right now.")
        lines.append("")
        return "\n".join(lines)

    if operator_items:
        lines.append("## Decisions Waiting on You")
        lines.append("")
        lines.append("| Artifact | Unblocks |")
        lines.append("|----------|----------|")
        for item in operator_items:
            unblocks_str = str(item["unblocks"]) if item["unblocks"] > 0 else "—"
            lines.append(f"| {item['id']}: {item['title']} | {unblocks_str} |")
        lines.append("")

    if impl_items:
        lines.append("## Implementation Ready (agent can handle)")
        lines.append("")
        lines.append("| Artifact | Unblocks |")
        lines.append("|----------|----------|")
        for item in impl_items:
            unblocks_str = str(item["unblocks"]) if item["unblocks"] > 0 else "—"
            lines.append(f"| {item['id']}: {item['title']} | {unblocks_str} |")
        lines.append("")

    return "\n".join(lines)


def render_recommendation_section(
    items: list[dict],
    nodes: dict,
    edges: list[dict],
) -> str:
    """Render the Recommended Next callout for ROADMAP.md.

    Shows the single highest-leverage item with a one-line rationale.
    Returns empty string when no ready items exist.
    """
    recommendations = rank_recommendations(nodes, edges)
    if not recommendations:
        return ""

    top = recommendations[0]
    node = nodes.get(top["id"], {})
    title = node.get("title", top["id"])
    weight_label = {3: "high", 2: "medium", 1: "low"}.get(top["vision_weight"], "medium")

    rationale_parts = []
    if top["unblock_count"] > 0:
        rationale_parts.append(f"unblocks {top['unblock_count']} item{'s' if top['unblock_count'] != 1 else ''}")
    rationale_parts.append(f"weight: {weight_label}")
    if top["score"] > 0:
        rationale_parts.append(f"score: {top['score']}")
    rationale = ", ".join(rationale_parts)

    lines = [
        "## Recommended Next",
        "",
        f"> **{top['id']}**: {title} — {rationale}",
        "",
    ]
    return "\n".join(lines)


_AUTO_GENERATED_MARKER = "<!-- Auto-generated by chart.sh roadmap --scope. Do not edit. -->"


def _get_recent_commits(
    artifact_ids: list[str], repo_root: str, limit: int = 3
) -> list[dict]:
    """Get the last N git commits whose messages reference any of the given artifact IDs.

    Returns dicts with hash, message, date (ISO), date_human (relative).
    Sorted newest first by author date.
    """
    if not repo_root or not artifact_ids:
        return []
    import subprocess as _sp

    commits: list[dict] = []
    seen: set[str] = set()
    for aid in artifact_ids:
        try:
            result = _sp.run(
                [
                    "git", "log", "--all",
                    f"--grep={aid}", f"-{limit}",
                    "--format=%h\t%s\t%aI\t%ai",
                ],
                capture_output=True, text=True, cwd=repo_root, timeout=10,
            )
            for line in result.stdout.strip().splitlines():
                if not line:
                    continue
                parts = line.split("\t", 3)
                if len(parts) < 4:
                    continue
                h, msg, date_iso, date_human = parts
                if h not in seen:
                    seen.add(h)
                    # Parse "2026-03-21 14:32:05 -0600" into date and time
                    dt_parts = date_human.split(" ", 2)
                    c_date = dt_parts[0] if len(dt_parts) >= 1 else ""
                    c_time = dt_parts[1].rsplit(":", 1)[0] if len(dt_parts) >= 2 else ""  # drop seconds
                    commits.append({
                        "hash": h,
                        "message": msg,
                        "date": date_iso,
                        "c_date": c_date,
                        "c_time": c_time,
                    })
        except (_sp.TimeoutExpired, FileNotFoundError):
            pass
    # Sort newest first by date
    commits.sort(key=lambda c: c.get("date", ""), reverse=True)
    return commits[:limit]


def render_scoped_roadmap(
    artifact_id: str,
    nodes: dict,
    edges: list[dict],
    repo_root: str = "",
) -> str:
    """Render a scoped roadmap slice for a single Vision or Initiative."""
    node = nodes.get(artifact_id, {})
    title = node.get("title", artifact_id)

    # Intent: prefer brief_description, fall back to placeholder
    brief = node.get("brief_description", "")
    intent = brief if brief else f"{{{{INTENT: {artifact_id}}}}}"

    # Build children tree (one level of nesting)
    _RESOLVED_PHASES = {"Complete", "Superseded", "Archived"}
    artifact_file = node.get("file", "")
    children_ids = _get_children(artifact_id, edges)
    children: list[dict] = []
    complete = 0
    total = 0

    def _make_child_entry(cid: str) -> dict | None:
        cnode = nodes.get(cid, {})
        if not cnode:
            return None
        ctype = cnode.get("type", "").upper()
        cstatus = cnode.get("status", "")
        child_file = cnode.get("file", "")
        link = os.path.relpath(child_file, os.path.dirname(artifact_file)) if (child_file and artifact_file) else cid
        if ctype == "EPIC":
            c, t = _spec_progress(cid, nodes, edges)
            progress_str = f"{c}/{t}" if t > 0 else "\u2014"
        elif _node_is_resolved(cid, nodes):
            progress_str = "done"
        else:
            progress_str = "in progress"
        return {
            "id": cid,
            "title": cnode.get("title", cid),
            "phase": cstatus,
            "progress": progress_str,
            "link": link,
            "type": ctype,
            "children": [],
        }

    for cid in sorted(children_ids):
        entry = _make_child_entry(cid)
        if entry is None:
            continue

        # Count this child
        total += 1
        if _node_is_resolved(cid, nodes):
            complete += 1

        # Nest grandchildren (one level deep) and count them too
        grandchild_ids = _get_children(cid, edges)
        for gcid in sorted(grandchild_ids):
            gc_entry = _make_child_entry(gcid)
            if gc_entry is not None:
                entry["children"].append(gc_entry)
                total += 1
                if _node_is_resolved(gcid, nodes):
                    complete += 1
        # Sort grandchildren: active first
        entry["children"].sort(
            key=lambda c: (1 if c["phase"] in _RESOLVED_PHASES else 0, c["id"])
        )
        children.append(entry)

    # Group children by phase of the direct child (highest ancestor in the tree)
    _PHASE_ORDER = ["Active", "In Progress", "Proposed", "Complete", "Superseded", "Archived"]
    _phase_rank = {p: i for i, p in enumerate(_PHASE_ORDER)}
    children.sort(key=lambda c: (_phase_rank.get(c["phase"], 99), c["id"]))

    from collections import OrderedDict
    children_by_phase: OrderedDict[str, list[dict]] = OrderedDict()
    for c in children:
        phase = c["phase"] or "Unknown"
        children_by_phase.setdefault(phase, []).append(c)

    # Progress bar
    pct = round(100 * complete / total) if total > 0 else 0
    bar_filled = round(pct / 100 * 12)
    progress_bar = "\u2588" * bar_filled + "\u2591" * (12 - bar_filled)

    # Recent commits referencing child artifact IDs
    recent_commits = _get_recent_commits(children_ids, repo_root)

    # Eisenhower subset: collect items in scope and render
    scoped_items = collect_roadmap_items(nodes, edges, scope=artifact_id)
    eisenhower_subset = render_eisenhower_table(scoped_items, nodes) if scoped_items else ""

    if _HAS_JINJA:
        env = _jinja_env()
        tmpl = env.get_template("roadmap-slice.md.j2")
        return tmpl.render(
            artifact_id=artifact_id,
            title=title,
            intent=intent,
            children_by_phase=children_by_phase,
            progress_bar=progress_bar,
            complete=complete,
            total=total,
            pct=pct,
            recent_commits=recent_commits,
            eisenhower_subset=eisenhower_subset,
        ).rstrip("\n") + "\n"
    else:
        lines = [
            _AUTO_GENERATED_MARKER,
            f"# {artifact_id}: {title}",
            "",
            f"> {intent}",
            "",
            "## Progress",
            "",
            f"{progress_bar} {complete}/{total} complete ({pct}%)",
            "",
            "## Recent Activity",
            "",
        ]
        if recent_commits:
            lines.extend([
                "| Date | Time | Commit | Message |",
                "|------|------|--------|---------|",
            ])
            for c in recent_commits:
                lines.append(f"| {c.get('c_date', '')} | {c.get('c_time', '')} | `{c['hash']}` | {c['message']} |")
        else:
            lines.append("_No recent commits reference child artifacts._")
        lines.append("")
        if eisenhower_subset:
            lines.extend(["## Priority Subset", "", eisenhower_subset, ""])
        lines.append("## Children")
        lines.append("")
        for phase, phase_children in children_by_phase.items():
            lines.append(f"### {phase}")
            lines.append("")
            for c in phase_children:
                prog = f", {c['progress']}" if c.get("progress") else ""
                lines.append(f"- [{c['id']}]({c['link']}) \u2014 {c['title']}{prog}")
                for gc in c.get("children", []):
                    gprog = f", {gc['progress']}" if gc.get("progress") else ""
                    lines.append(f"  - [{gc['id']}]({gc['link']}) \u2014 {gc['title']} ({gc['phase']}{gprog})")
            lines.append("")
        return "\n".join(lines) + "\n"


def _write_scoped_slice(
    artifact_id: str,
    nodes: dict,
    edges: list[dict],
    repo_root: str,
) -> str | None:
    """Write a scoped roadmap slice to the artifact's folder. Returns path or None."""
    node = nodes.get(artifact_id)
    if not node or not node.get("file"):
        return None

    artifact_file = os.path.join(repo_root, node["file"])
    artifact_dir = os.path.dirname(artifact_file)
    roadmap_path = os.path.join(artifact_dir, "roadmap.md")

    # Backup existing manual roadmap
    if os.path.exists(roadmap_path):
        with open(roadmap_path, "r", encoding="utf-8") as f:
            existing = f.read()
        if _AUTO_GENERATED_MARKER not in existing:
            backup_path = os.path.join(artifact_dir, "roadmap.manual-backup.md")
            if not os.path.exists(backup_path):
                import shutil
                shutil.copy2(roadmap_path, backup_path)

    md = render_scoped_roadmap(artifact_id, nodes, edges, repo_root)
    os.makedirs(artifact_dir, exist_ok=True)
    with open(roadmap_path, "w", encoding="utf-8") as f:
        f.write(md)
    return roadmap_path


def _write_all_slices(
    nodes: dict,
    edges: list[dict],
    repo_root: str,
) -> int:
    """Regenerate all per-Vision and per-Initiative roadmap slices. Returns count."""
    count = 0
    for aid, node in sorted(nodes.items()):
        atype = node.get("type", "").upper()
        if atype in ("VISION", "INITIATIVE"):
            result = _write_scoped_slice(aid, nodes, edges, repo_root)
            if result:
                count += 1
    return count


def render_roadmap_markdown(
    items: list[dict],
    nodes: dict,
    repo_root: str = "",
    edges: list[dict] | None = None,
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

    # Decision and recommendation sections (SPEC-120)
    decisions = render_decisions_section(items, nodes, edges or [])
    recommendation = render_recommendation_section(items, nodes, edges or [])

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
            recommendation=recommendation,
            decisions=decisions,
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

        # Decision and recommendation sections before Eisenhower tables
        if recommendation:
            lines.append(recommendation)
        if decisions:
            lines.append(decisions)

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
    scope: str | None = None,
    json_output: bool = False,
) -> str:
    items = collect_roadmap_items(nodes, edges, scope=scope)

    if json_output:
        import json
        return json.dumps(items, indent=2)

    if fmt == "mermaid-flowchart":
        dep = render_dependency_graph(items, nodes)
        return dep or "flowchart TD\n    %% No Epic-level dependencies"
    elif fmt == "both":
        gantt = render_gantt(items, nodes)
        dep = render_dependency_graph(items, nodes)
        parts = [gantt]
        if dep:
            parts.append(dep)
        return "\n\n".join(parts)
    else:
        return render_gantt(items, nodes)


def render_roadmap_cli(items: list[dict]) -> str:
    """Render roadmap items as CLI-friendly plain text.

    Groups items by quadrant, nests children (EPICs, SPECs, SPIKEs)
    under their parent initiative. All first-degree children are shown
    equally regardless of type.
    """
    from collections import defaultdict

    QUADRANT_ORDER = ["Do First", "Schedule", "In Progress", "Backlog"]

    # Group by quadrant, then by initiative (group field)
    quads: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for item in items:
        ql = item.get("quadrant_label", "Backlog")
        g = item.get("group", item["id"])
        quads[ql][g].append(item)

    lines: list[str] = []

    for quad in QUADRANT_ORDER:
        if quad not in quads:
            continue
        groups = quads[quad]

        lines.append(quad.upper())

        # Sort initiatives by max score of their members (descending)
        sorted_groups = sorted(
            groups.items(),
            key=lambda kv: max(i["score"] for i in kv[1]),
            reverse=True,
        )

        for group_id, group_items in sorted_groups:
            # Separate initiative item from children
            init_items = [i for i in group_items if i["type"] == "INITIATIVE"]
            children = [i for i in group_items if i["type"] != "INITIATIVE"]
            children.sort(key=lambda x: -x["score"])

            # Initiative header
            if init_items:
                init = init_items[0]
                title = init["title"]
                short = _short_id(init["id"])
                progress = f"{init['children_complete']}/{init['children_total']}"
                decision = f"  {init['operator_decision']}" if init.get("operator_decision") else ""
                lines.append(f"  {title} ({short}){' ' * max(1, 48 - len(title) - len(short))}{progress}{decision}")
            else:
                # No initiative item in this quadrant — use group_title from first child
                title = group_items[0].get("group_title", group_id)
                short = _short_id(group_id)
                lines.append(f"  {title} ({short})")

            # Children (EPICs, SPECs, SPIKEs)
            for child in children:
                cid = child["id"]
                ctitle = child["title"][:40]
                progress = f"{child['children_complete']}/{child['children_total']}"
                decision = f"  {child['operator_decision']}" if child.get("operator_decision") else ""
                lines.append(f"    {cid:<12s}  {ctitle:<40s}  {progress}{decision}")

        lines.append("")  # blank line between quadrants

    # Blocking dependencies
    deps = []
    for item in items:
        for dep_id in item.get("depends_on", []):
            deps.append((item["id"], dep_id))
    if deps:
        lines.append("BLOCKED")
        for blocked, blocker in sorted(set(deps)):
            lines.append(f"  {blocked} depends on {blocker}")
        lines.append("")

    return "\n".join(lines).rstrip()
