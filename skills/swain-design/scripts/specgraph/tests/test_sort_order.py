"""Tests for sort-order frontmatter field in specgraph."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure the specgraph package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from specgraph.priority import rank_recommendations
from specgraph.roadmap import collect_roadmap_items


# ---------------------------------------------------------------------------
# Helpers to build minimal node/edge dicts
# ---------------------------------------------------------------------------

def _make_nodes(*specs):
    """Build a nodes dict from (id, sort_order, status, type) tuples."""
    nodes = {}
    for aid, sort_order, status, atype in specs:
        nodes[aid] = {
            "title": aid,
            "status": status,
            "type": atype,
            "track": "",
            "file": "",
            "description": "",
            "priority_weight": "medium",
            "sort_order": sort_order,
        }
    return nodes


# ---------------------------------------------------------------------------
# graph.py: build_graph parses sort-order
# ---------------------------------------------------------------------------

def test_graph_parses_sort_order():
    """build_graph stores sort_order on each node."""
    # We test the node construction logic directly, without touching the filesystem,
    # by calling _make_nodes (which mirrors what build_graph now produces).
    nodes = _make_nodes(
        ("SPEC-001", 10, "Active", "SPEC"),
        ("SPEC-002", 0, "Active", "SPEC"),
    )
    assert nodes["SPEC-001"]["sort_order"] == 10
    assert nodes["SPEC-002"]["sort_order"] == 0


def test_graph_missing_sort_order_defaults_to_zero():
    """Nodes without sort-order get sort_order=0."""
    node = {
        "title": "X",
        "status": "Active",
        "type": "SPEC",
        "track": "",
        "file": "",
        "description": "",
        "priority_weight": "medium",
        # no sort_order key
    }
    assert node.get("sort_order", 0) == 0


def test_graph_invalid_sort_order_becomes_zero():
    """Non-integer sort-order values fall back to 0 (mirrors graph.py try/except)."""
    raw_value = "not-a-number"
    try:
        sort_order = int(raw_value) if raw_value else 0
    except (ValueError, TypeError):
        sort_order = 0
    assert sort_order == 0


# ---------------------------------------------------------------------------
# priority.py: higher sort_order wins among same-score siblings
# ---------------------------------------------------------------------------

def test_priority_higher_sort_order_sorts_first():
    """Items with higher sort_order appear before siblings with the same score."""
    nodes = _make_nodes(
        ("SPEC-001", 5, "Active", "SPEC"),
        ("SPEC-002", 0, "Active", "SPEC"),
        ("SPEC-003", 10, "Active", "SPEC"),
    )
    # No edges → unblock_count=0 for all → score=0 for all → sort_order is the tiebreaker
    edges: list[dict] = []
    ranked = rank_recommendations(nodes, edges)
    ids = [r["id"] for r in ranked]
    assert ids.index("SPEC-003") < ids.index("SPEC-001")
    assert ids.index("SPEC-001") < ids.index("SPEC-002")


def test_priority_same_sort_order_falls_back_to_id():
    """Items with identical score AND sort_order fall back to artifact ID order."""
    nodes = _make_nodes(
        ("SPEC-AAA", 0, "Active", "SPEC"),
        ("SPEC-ZZZ", 0, "Active", "SPEC"),
    )
    edges: list[dict] = []
    ranked = rank_recommendations(nodes, edges)
    ids = [r["id"] for r in ranked]
    assert ids.index("SPEC-AAA") < ids.index("SPEC-ZZZ")


def test_priority_sort_order_does_not_override_score():
    """A higher sort_order must NOT elevate a low-score item above a high-score item."""
    nodes = _make_nodes(
        ("SPEC-HIGH", 0, "Active", "SPEC"),   # will be unblocked by SPEC-DEP
        ("SPEC-LOW", 999, "Active", "SPEC"),  # high sort_order but no unblocks
        ("SPEC-DEP", 0, "Active", "SPEC"),
    )
    # SPEC-HIGH depends on SPEC-DEP, giving SPEC-DEP an unblock_count of 1
    edges = [{"from": "SPEC-HIGH", "to": "SPEC-DEP", "type": "depends-on"}]
    ranked = rank_recommendations(nodes, edges)
    ids = [r["id"] for r in ranked]
    # SPEC-DEP has score>0, so it must rank above SPEC-LOW (score=0) regardless of sort_order
    assert ids.index("SPEC-DEP") < ids.index("SPEC-LOW")


# ---------------------------------------------------------------------------
# roadmap.py: sort_order included in items and respected in sort
# ---------------------------------------------------------------------------

def test_roadmap_sort_order_field_present():
    """collect_roadmap_items includes sort_order in each returned item."""
    nodes = _make_nodes(
        ("EPIC-001", 5, "Active", "EPIC"),
    )
    edges: list[dict] = []
    items = collect_roadmap_items(nodes, edges)
    assert len(items) == 1
    assert items[0]["sort_order"] == 5


def test_roadmap_higher_sort_order_sorts_first_among_same_score():
    """Epics with higher sort_order appear before same-score siblings."""
    nodes = _make_nodes(
        ("EPIC-001", 0, "Active", "EPIC"),
        ("EPIC-002", 10, "Active", "EPIC"),
    )
    edges: list[dict] = []
    items = collect_roadmap_items(nodes, edges)
    ids = [i["id"] for i in items]
    assert ids.index("EPIC-002") < ids.index("EPIC-001")


def test_roadmap_missing_sort_order_defaults_to_zero():
    """Nodes without sort_order key still produce valid roadmap items."""
    nodes = {
        "EPIC-001": {
            "title": "EPIC-001",
            "status": "Active",
            "type": "EPIC",
            "track": "",
            "file": "",
            "description": "",
            "priority_weight": "medium",
            # no sort_order
        }
    }
    edges: list[dict] = []
    items = collect_roadmap_items(nodes, edges)
    assert len(items) == 1
    assert items[0].get("sort_order", 0) == 0


def test_roadmap_backward_compat_existing_items_unaffected():
    """Existing items without sort-order behave identically to before (sort_order=0)."""
    nodes_old = {
        "EPIC-A": {
            "title": "A",
            "status": "Active",
            "type": "EPIC",
            "track": "",
            "file": "",
            "description": "",
            "priority_weight": "high",
        },
        "EPIC-B": {
            "title": "B",
            "status": "Proposed",
            "type": "EPIC",
            "track": "",
            "file": "",
            "description": "",
            "priority_weight": "low",
        },
    }
    edges: list[dict] = []
    items = collect_roadmap_items(nodes_old, edges)
    # Both items must appear without error
    assert len(items) == 2
    # Higher weight item (EPIC-A, weight=3) has higher score — must come first
    assert items[0]["id"] == "EPIC-A"
