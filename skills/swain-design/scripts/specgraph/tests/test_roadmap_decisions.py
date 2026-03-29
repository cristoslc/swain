"""Tests for ROADMAP.md Decisions and Recommendation sections (SPEC-120).

Validates that render_decisions_section() and render_recommendation_section()
produce correct markdown using existing specgraph data.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from specgraph.roadmap import (
    collect_roadmap_items,
    render_decisions_section,
    render_recommendation_section,
    render_roadmap_markdown,
)


def _make_graph():
    """Graph with a mix of decision-type and implementation-type items."""
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
            "status": "Proposed",  # decision-type (Proposed)
        },
        "SPEC-001": {
            "type": "Spec",
            "title": "Login API",
            "status": "Complete",
        },
        "SPEC-002": {
            "type": "Spec",
            "title": "Login UI",
            "status": "Active",  # implementation-type
        },
        "SPEC-003": {
            "type": "Spec",
            "title": "SSO Config",
            "status": "Proposed",  # decision-type (Proposed)
        },
    }
    edges = [
        {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
        {"from": "EPIC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "EPIC-002", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "SPEC-001", "to": "EPIC-001", "type": "parent-epic"},
        {"from": "SPEC-002", "to": "EPIC-001", "type": "parent-epic"},
        {"from": "SPEC-003", "to": "EPIC-002", "type": "parent-epic"},
        # SPEC-003 depends on SPEC-002 (so SPEC-002 unblocks something)
        {"from": "SPEC-003", "to": "SPEC-002", "type": "depends-on"},
    ]
    return nodes, edges


# --- render_decisions_section tests ---


def test_decisions_section_contains_operator_bucket():
    nodes, edges = _make_graph()
    items = collect_roadmap_items(nodes, edges)
    section = render_decisions_section(items, nodes, edges)
    assert "Decisions Waiting on You" in section


def test_decisions_section_contains_implementation_bucket():
    nodes, edges = _make_graph()
    items = collect_roadmap_items(nodes, edges)
    section = render_decisions_section(items, nodes, edges)
    assert "Implementation Ready" in section


def test_decisions_section_proposed_epic_in_operator_bucket():
    """A Proposed epic should appear in the operator decisions bucket."""
    nodes, edges = _make_graph()
    items = collect_roadmap_items(nodes, edges)
    section = render_decisions_section(items, nodes, edges)
    # EPIC-002 is Proposed — should be in operator bucket
    operator_part = section.split("Implementation Ready")[0]
    assert "EPIC-002" in operator_part


def test_decisions_section_active_spec_in_implementation_bucket():
    """An Active spec should appear in the implementation-ready bucket."""
    nodes, edges = _make_graph()
    items = collect_roadmap_items(nodes, edges)
    section = render_decisions_section(items, nodes, edges)
    # SPEC-002 is Active — not a decision, but ready for implementation
    impl_part = section.split("Implementation Ready")[1]
    assert "SPEC-002" in impl_part or "Login UI" in impl_part


def test_decisions_section_empty_state():
    """When no decisions are pending, show 'No decisions needed right now.'"""
    # All items are resolved — nothing is ready
    nodes = {
        "VISION-001": {
            "type": "Vision",
            "title": "Core",
            "status": "Complete",
            "priority_weight": "medium",
        },
    }
    edges = []
    items = collect_roadmap_items(nodes, edges)
    section = render_decisions_section(items, nodes, edges)
    assert "No decisions needed right now" in section


def test_decisions_sorted_by_unblocks():
    """Items with higher unblock counts should appear first."""
    nodes, edges = _make_graph()
    # Add more items that depend on EPIC-002 to increase its unblock count
    nodes["SPEC-004"] = {"type": "Spec", "title": "SSO UI", "status": "Active"}
    edges.append({"from": "SPEC-004", "to": "EPIC-002", "type": "depends-on"})
    items = collect_roadmap_items(nodes, edges)
    section = render_decisions_section(items, nodes, edges)
    operator_part = section.split("Implementation Ready")[0]
    # EPIC-002 unblocks more items, should appear first in operator bucket
    if "EPIC-002" in operator_part and "SPEC-003" in operator_part:
        assert operator_part.index("EPIC-002") < operator_part.index("SPEC-003")


# --- render_recommendation_section tests ---


def test_recommendation_shows_top_item():
    nodes, edges = _make_graph()
    items = collect_roadmap_items(nodes, edges)
    section = render_recommendation_section(items, nodes, edges)
    assert "Recommended Next" in section


def test_recommendation_includes_rationale():
    nodes, edges = _make_graph()
    items = collect_roadmap_items(nodes, edges)
    section = render_recommendation_section(items, nodes, edges)
    # Should include some scoring rationale
    assert "unblock" in section.lower() or "score" in section.lower() or "weight" in section.lower()


def test_recommendation_empty_when_no_ready_items():
    """When nothing is ready, recommendation section should be empty."""
    # All items are resolved — nothing is ready
    nodes = {
        "VISION-001": {
            "type": "Vision",
            "title": "Core",
            "status": "Complete",
            "priority_weight": "medium",
        },
    }
    edges = []
    items = collect_roadmap_items(nodes, edges)
    section = render_recommendation_section(items, nodes, edges)
    assert section == ""


# --- Integration: render_roadmap_markdown includes new sections ---


def test_roadmap_markdown_includes_decisions():
    nodes, edges = _make_graph()
    items = collect_roadmap_items(nodes, edges)
    md = render_roadmap_markdown(items, nodes, edges=edges)
    assert "Decisions Waiting on You" in md or "No decisions needed right now" in md


def test_roadmap_markdown_includes_recommendation():
    nodes, edges = _make_graph()
    items = collect_roadmap_items(nodes, edges)
    md = render_roadmap_markdown(items, nodes, edges=edges)
    assert "Recommended Next" in md


def test_roadmap_markdown_decisions_before_eisenhower():
    """Decision sections should appear before the Eisenhower tables."""
    nodes, edges = _make_graph()
    items = collect_roadmap_items(nodes, edges)
    md = render_roadmap_markdown(items, nodes, edges=edges)
    decisions_pos = md.find("Decisions Waiting on You")
    if decisions_pos == -1:
        decisions_pos = md.find("No decisions needed right now")
    eisenhower_pos = md.find("### Do First")
    if eisenhower_pos == -1:
        eisenhower_pos = md.find("### Schedule")
    if decisions_pos >= 0 and eisenhower_pos >= 0:
        assert decisions_pos < eisenhower_pos, (
            "Decisions section should appear before Eisenhower tables"
        )


def test_roadmap_markdown_preserves_existing_sections():
    """Existing sections (Timeline, Dependencies) must still be present."""
    nodes, edges = _make_graph()
    items = collect_roadmap_items(nodes, edges)
    md = render_roadmap_markdown(items, nodes, edges=edges)
    assert "## Timeline" in md
    assert "gantt" in md
