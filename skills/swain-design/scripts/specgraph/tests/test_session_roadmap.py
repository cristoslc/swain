"""Tests for SESSION-ROADMAP.md generation (SPEC-118).

Validates render_session_roadmap() produces all 7 sections,
filters by focus lane, and uses lightweight evidence pointers.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from specgraph.session_roadmap import render_session_roadmap


def _make_graph():
    """Graph with a focus-lane initiative and items outside it."""
    nodes = {
        "VISION-001": {
            "type": "Vision",
            "title": "Core Platform",
            "status": "Active",
            "priority_weight": "high",
        },
        "INITIATIVE-005": {
            "type": "Initiative",
            "title": "Operator Awareness",
            "status": "Active",
        },
        "INITIATIVE-099": {
            "type": "Initiative",
            "title": "Unrelated Work",
            "status": "Active",
        },
        "EPIC-001": {
            "type": "Epic",
            "title": "Status Dashboard",
            "status": "Active",
        },
        "EPIC-099": {
            "type": "Epic",
            "title": "Unrelated Epic",
            "status": "Proposed",
        },
        "SPEC-001": {
            "type": "Spec",
            "title": "Decision Sections",
            "status": "Active",
        },
        "SPEC-002": {
            "type": "Spec",
            "title": "Recommendation Engine",
            "status": "Proposed",
        },
        "SPEC-099": {
            "type": "Spec",
            "title": "Unrelated Spec",
            "status": "Proposed",
        },
    }
    edges = [
        {"from": "INITIATIVE-005", "to": "VISION-001", "type": "parent-vision"},
        {"from": "INITIATIVE-099", "to": "VISION-001", "type": "parent-vision"},
        {"from": "EPIC-001", "to": "INITIATIVE-005", "type": "parent-initiative"},
        {"from": "EPIC-099", "to": "INITIATIVE-099", "type": "parent-initiative"},
        {"from": "SPEC-001", "to": "EPIC-001", "type": "parent-epic"},
        {"from": "SPEC-002", "to": "EPIC-001", "type": "parent-epic"},
        {"from": "SPEC-099", "to": "EPIC-099", "type": "parent-epic"},
        # SPEC-002 is Proposed with no dependencies — should be in decision set
    ]
    return nodes, edges


# --- Section presence tests ---


def test_all_seven_sections_present():
    """AC2: All 7 sections must be present."""
    nodes, edges = _make_graph()
    md = render_session_roadmap(
        focus_id="INITIATIVE-005",
        nodes=nodes,
        edges=edges,
        repo_root="/tmp/test",
    )
    assert "## Evidence Basis" in md
    assert "## Decision Set" in md
    assert "## Recommended Next" in md
    assert "## Session Goal" in md
    assert "## Progress" in md
    assert "## Decision Records" in md
    assert "## Walk-Away Signal" in md


def test_generates_valid_markdown():
    """AC3: Output should be valid markdown (no broken syntax)."""
    nodes, edges = _make_graph()
    md = render_session_roadmap(
        focus_id="INITIATIVE-005",
        nodes=nodes,
        edges=edges,
        repo_root="/tmp/test",
    )
    # No unclosed fences
    assert md.count("```") % 2 == 0
    # No conflict markers
    assert "<<<<<<" not in md
    assert ">>>>>>" not in md
    # Has a title
    assert md.startswith("# SESSION-ROADMAP")


# --- Focus lane filtering tests ---


def test_decision_set_filtered_to_focus_lane():
    """AC5: Decision set contains only items under the focus initiative."""
    nodes, edges = _make_graph()
    md = render_session_roadmap(
        focus_id="INITIATIVE-005",
        nodes=nodes,
        edges=edges,
        repo_root="/tmp/test",
    )
    decision_section = _extract_section(md, "## Decision Set")
    # SPEC-002 is Proposed under EPIC-001 (child of INITIATIVE-005) — should appear
    assert "SPEC-002" in decision_section
    # SPEC-099 and EPIC-099 are under INITIATIVE-099 — should NOT appear
    assert "SPEC-099" not in decision_section
    assert "EPIC-099" not in decision_section


def test_unrelated_items_excluded():
    """Items outside focus lane should not appear in decision set."""
    nodes, edges = _make_graph()
    md = render_session_roadmap(
        focus_id="INITIATIVE-005",
        nodes=nodes,
        edges=edges,
        repo_root="/tmp/test",
    )
    decision_section = _extract_section(md, "## Decision Set")
    assert "Unrelated" not in decision_section


# --- Evidence basis tests ---


def test_evidence_basis_has_pointers():
    """AC4: Evidence basis uses artifact ID + commit hash pointers."""
    nodes, edges = _make_graph()
    md = render_session_roadmap(
        focus_id="INITIATIVE-005",
        nodes=nodes,
        edges=edges,
        repo_root="/tmp/test",
    )
    evidence = _extract_section(md, "## Evidence Basis")
    assert "INITIATIVE-005" in evidence
    # Should reference focus lane
    assert "Focus" in evidence or "focus" in evidence


# --- Session goal tests ---


def test_session_goal_has_recommendation_and_alternatives():
    """Session goal should propose a recommendation with justification and alternatives."""
    nodes, edges = _make_graph()
    md = render_session_roadmap(
        focus_id="INITIATIVE-005",
        nodes=nodes,
        edges=edges,
        repo_root="/tmp/test",
    )
    goal_section = _extract_section(md, "## Session Goal")
    # Should have a recommended goal
    assert "Recommend" in goal_section or "recommend" in goal_section
    # Should have alternatives
    assert "Alternative" in goal_section or "alternative" in goal_section


# --- Walk-away signal ---


def test_walk_away_signal_present():
    """Walk-away signal should indicate remaining decisions."""
    nodes, edges = _make_graph()
    md = render_session_roadmap(
        focus_id="INITIATIVE-005",
        nodes=nodes,
        edges=edges,
        repo_root="/tmp/test",
    )
    walkaway = _extract_section(md, "## Walk-Away Signal")
    assert len(walkaway.strip()) > 0


# --- Decision records integration ---


def test_decision_records_section_reads_jsonl(tmp_path):
    """Decision records section should render entries from JSONL log."""
    import json
    jsonl = tmp_path / ".agents" / "session-decisions.jsonl"
    jsonl.parent.mkdir(parents=True)
    entry = {
        "session": "2026-03-22T00:00:00Z",
        "artifact": "SPEC-082",
        "action": "approved",
        "commit": "abc1234",
        "timestamp": "2026-03-22T01:00:00Z",
    }
    jsonl.write_text(json.dumps(entry) + "\n")

    nodes, edges = _make_graph()
    md = render_session_roadmap(
        focus_id="INITIATIVE-005",
        nodes=nodes,
        edges=edges,
        repo_root=str(tmp_path),
    )
    records_section = _extract_section(md, "## Decision Records")
    assert "SPEC-082" in records_section
    assert "approved" in records_section


def test_decision_records_empty_when_no_log():
    """Decision records should show empty state when no JSONL exists."""
    nodes, edges = _make_graph()
    md = render_session_roadmap(
        focus_id="INITIATIVE-005",
        nodes=nodes,
        edges=edges,
        repo_root="/tmp/nonexistent-test-path",
    )
    records_section = _extract_section(md, "## Decision Records")
    assert "No decisions recorded" in records_section or len(records_section.strip()) > 0


# --- Helper ---


def _extract_section(md: str, header: str) -> str:
    """Extract the content of a markdown section (between header and next ## or end)."""
    lines = md.split("\n")
    in_section = False
    section_lines = []
    for line in lines:
        if line.strip() == header:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            section_lines.append(line)
    return "\n".join(section_lines)
