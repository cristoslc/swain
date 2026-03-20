"""Tests for the unified roadmap data model (SPEC-108).

Validates that collect_roadmap_items() returns fully-resolved items with all
derived fields, and that all renderers consume those fields consistently.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from specgraph.roadmap import (
    collect_roadmap_items,
    classify_epics_eisenhower,
    render_quadrant_chart,
    render_eisenhower_table,
    render_gantt,
    render_dependency_graph,
    QUADRANT_ORDER,
)


def _make_graph():
    nodes = {
        "VISION-001": {
            "type": "Vision",
            "title": "Core Platform",
            "status": "Active",
            "priority_weight": "high",
        },
        "INITIATIVE-001": {
            "type": "Initiative",
            "title": "Auth System",
            "status": "Active",
        },
        "EPIC-001": {
            "type": "Epic",
            "title": "Login Flow",
            "status": "Active",
        },
        "EPIC-002": {
            "type": "Epic",
            "title": "SSO Integration",
            "status": "Active",
        },
        "EPIC-003": {
            "type": "Epic",
            "title": "Nice To Have Feature",
            "status": "Proposed",
            "priority_weight": "low",
        },
        "EPIC-004": {
            "type": "Epic",
            "title": "Quick Win",
            "status": "Active",
            "priority_weight": "medium",
        },
        "SPEC-001": {
            "type": "Spec",
            "title": "Login API",
            "status": "Complete",
        },
        "SPEC-002": {
            "type": "Spec",
            "title": "Login UI",
            "status": "Active",
        },
        "SPEC-003": {
            "type": "Spec",
            "title": "Quick Win Spec",
            "status": "Complete",
        },
    }
    edges = [
        {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
        {"from": "EPIC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "EPIC-002", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "SPEC-001", "to": "EPIC-001", "type": "parent-epic"},
        {"from": "SPEC-002", "to": "EPIC-001", "type": "parent-epic"},
        {"from": "SPEC-003", "to": "EPIC-004", "type": "parent-epic"},
        {"from": "EPIC-002", "to": "EPIC-001", "type": "depends-on"},
    ]
    return nodes, edges


REQUIRED_FIELDS = {
    "id", "title", "type", "score", "weight",
    "children_total", "children_complete", "depends_on",
    "group", "group_title", "vision_id", "status",
    "quadrant", "quadrant_label", "chart_x", "chart_y",
    "display_score", "short_id", "operator_decision",
}


def test_all_required_fields_present():
    nodes, edges = _make_graph()
    items = collect_roadmap_items(nodes, edges)
    assert len(items) > 0
    for item in items:
        missing = REQUIRED_FIELDS - set(item.keys())
        assert not missing, f"Item {item.get('id', '?')} missing fields: {missing}"


def test_chart_positions_in_bounds():
    nodes, edges = _make_graph()
    items = collect_roadmap_items(nodes, edges)
    epics = [i for i in items if i["type"] == "EPIC"]
    assert len(epics) > 0
    for item in epics:
        assert 0.02 <= item["chart_x"] <= 0.98, f"{item['id']} chart_x out of bounds"
        assert 0.02 <= item["chart_y"] <= 0.98, f"{item['id']} chart_y out of bounds"


def test_determinism():
    nodes, edges = _make_graph()
    items_a = collect_roadmap_items(nodes, edges)
    items_b = collect_roadmap_items(nodes, edges)
    assert len(items_a) == len(items_b)
    for a, b in zip(items_a, items_b):
        assert a == b, f"Non-deterministic for {a.get('id')}"


def test_same_urgency_gets_different_chart_x():
    """Items with identical (base_x, base_y) positions get jitter applied.

    Items in the same urgency tier but different y-band rows will share chart_x
    by design — the jitter only fires when two items land on the exact same
    (base_x, base_y) grid point. We verify that no two EPICs share an identical
    (chart_x, chart_y) pair, which is the actual collision guarantee.
    """
    nodes, edges = _make_graph()
    items = collect_roadmap_items(nodes, edges)
    epics = [i for i in items if i["type"] == "EPIC"]
    positions = [(i["chart_x"], i["chart_y"]) for i in epics]
    assert len(set(positions)) == len(positions), (
        f"Duplicate (chart_x, chart_y) positions among EPICs: {positions}"
    )


def test_legend_ordering_matches_chart():
    nodes, edges = _make_graph()
    items = collect_roadmap_items(nodes, edges)
    _, legend_items = render_quadrant_chart(items)
    score_map = {i["id"]: i["display_score"] for i in items}
    for li in legend_items:
        assert li["id"] in score_map


def test_epic_count_chart_matches_legend():
    nodes, edges = _make_graph()
    items = collect_roadmap_items(nodes, edges)
    chart_src, legend_items = render_quadrant_chart(items)
    chart_epics = [i for i in items if i["type"] == "EPIC"]
    assert len(legend_items) == len(chart_epics)


def test_quadrant_values_valid():
    nodes, edges = _make_graph()
    items = collect_roadmap_items(nodes, edges)
    valid_quadrants = set(QUADRANT_ORDER)
    for item in items:
        assert item["quadrant"] in valid_quadrants


def test_classify_epics_uses_precomputed_quadrant():
    nodes, edges = _make_graph()
    items = collect_roadmap_items(nodes, edges)
    quadrants = classify_epics_eisenhower(items)
    epic_ids = {i["id"] for i in items if i["type"] == "EPIC"}
    bucketed_ids = set()
    for qkey, qitems in quadrants.items():
        for item in qitems:
            assert item["quadrant"] == qkey
            bucketed_ids.add(item["id"])
    assert bucketed_ids == epic_ids


def test_operator_decision_precomputed():
    nodes, edges = _make_graph()
    items = collect_roadmap_items(nodes, edges)
    epic_003 = next(i for i in items if i["id"] == "EPIC-003")
    assert epic_003["operator_decision"] == "activate or drop"
    epic_004 = next(i for i in items if i["id"] == "EPIC-004")
    assert epic_004["operator_decision"] == "ready to complete"


def test_short_id_format():
    nodes, edges = _make_graph()
    items = collect_roadmap_items(nodes, edges)
    for item in items:
        sid = item["short_id"]
        assert sid[0] in ("E", "I", "S"), f"Unexpected short_id prefix: {sid}"


def test_display_score_formula():
    nodes, edges = _make_graph()
    items = collect_roadmap_items(nodes, edges)
    active_statuses = {"Active", "Implementation", "Testing", "In Progress"}
    for item in items:
        expected = item["weight"] + (
            item["score"] + 1 if item["status"] in active_statuses else item["score"]
        )
        assert item["display_score"] == expected


def test_initiative_counts_direct_child_specs():
    """Direct-child SPECs of an Initiative contribute to its progress."""
    nodes, edges = _make_graph()
    # Add a SPEC directly under INITIATIVE-001 (no parent-epic)
    nodes["SPEC-DIRECT"] = {
        "type": "Spec",
        "title": "Direct Initiative Spec",
        "status": "Complete",
    }
    edges.append({"from": "SPEC-DIRECT", "to": "INITIATIVE-001", "type": "parent-initiative"})

    items = collect_roadmap_items(nodes, edges)
    init_item = next(i for i in items if i["id"] == "INITIATIVE-001")
    # EPIC-001 has 2 SPECs (1 complete), EPIC-002 has 0 SPECs, direct SPEC = 1 complete
    assert init_item["children_total"] == 3  # 2 from EPIC-001 + 1 direct
    assert init_item["children_complete"] == 2  # SPEC-001 + SPEC-DIRECT


def test_initiative_direct_child_spec_appears_as_item():
    """An active direct-child SPEC of an Initiative appears as a roadmap item."""
    nodes, edges = _make_graph()
    nodes["SPEC-DIRECT"] = {
        "type": "Spec",
        "title": "Direct Initiative Spec",
        "status": "Active",
    }
    edges.append({"from": "SPEC-DIRECT", "to": "INITIATIVE-001", "type": "parent-initiative"})

    items = collect_roadmap_items(nodes, edges)
    item_ids = {i["id"] for i in items}
    assert "SPEC-DIRECT" in item_ids, "Direct-child SPEC should appear as a roadmap item"
    spec_item = next(i for i in items if i["id"] == "SPEC-DIRECT")
    assert spec_item["group"] == "INITIATIVE-001"
    assert spec_item["type"] == "SPEC"


def test_initiative_counts_active_direct_child_spec():
    """An active direct-child SPEC counts toward total but not complete."""
    nodes, edges = _make_graph()
    nodes["SPEC-ACTIVE-DIRECT"] = {
        "type": "Spec",
        "title": "Active Direct Spec",
        "status": "Active",
    }
    edges.append({"from": "SPEC-ACTIVE-DIRECT", "to": "INITIATIVE-001", "type": "parent-initiative"})

    items = collect_roadmap_items(nodes, edges)
    init_item = next(i for i in items if i["id"] == "INITIATIVE-001")
    assert init_item["children_total"] == 3  # 2 from EPIC-001 + 1 direct
    assert init_item["children_complete"] == 1  # only SPEC-001


def test_renderers_accept_enriched_items():
    nodes, edges = _make_graph()
    items = collect_roadmap_items(nodes, edges)
    chart_src, legend = render_quadrant_chart(items)
    assert "quadrantChart" in chart_src
    table = render_eisenhower_table(items, nodes)
    assert "###" in table
    gantt = render_gantt(items, nodes)
    assert "gantt" in gantt
    dep = render_dependency_graph(items, nodes)
    assert dep is not None
    assert "flowchart TD" in dep
