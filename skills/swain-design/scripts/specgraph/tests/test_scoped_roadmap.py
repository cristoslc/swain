"""Tests for scoped roadmap generation (SPEC-143)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from specgraph.roadmap import _compute_descendants, _get_children


def _make_scoped_graph():
    """Graph with Vision -> Initiative -> Epic -> Spec hierarchy."""
    nodes = {
        "VISION-001": {"type": "Vision", "title": "Core Platform", "status": "Active", "priority_weight": "high", "file": "docs/vision/Active/(VISION-001)-Core/v.md", "brief_description": ""},
        "INITIATIVE-001": {"type": "Initiative", "title": "Auth System", "status": "Active", "file": "docs/initiative/Active/(INITIATIVE-001)-Auth/i.md", "brief_description": "Harden authentication"},
        "INITIATIVE-002": {"type": "Initiative", "title": "Observability", "status": "Active", "file": "docs/initiative/Active/(INITIATIVE-002)-Obs/i.md", "brief_description": ""},
        "EPIC-001": {"type": "Epic", "title": "Login Flow", "status": "Active", "file": "docs/epic/Active/(EPIC-001)-Login/e.md"},
        "EPIC-002": {"type": "Epic", "title": "SSO", "status": "Active", "file": "docs/epic/Active/(EPIC-002)-SSO/e.md"},
        "SPEC-001": {"type": "Spec", "title": "Login API", "status": "Complete", "file": "docs/spec/Complete/(SPEC-001)-Login-API/s.md"},
        "SPEC-002": {"type": "Spec", "title": "Login UI", "status": "Active", "file": "docs/spec/Active/(SPEC-002)-Login-UI/s.md"},
        "SPEC-DIRECT": {"type": "Spec", "title": "Direct Spec", "status": "Active", "file": "docs/spec/Active/(SPEC-003)-Direct/s.md"},
    }
    edges = [
        {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
        {"from": "INITIATIVE-002", "to": "VISION-001", "type": "parent-vision"},
        {"from": "EPIC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "EPIC-002", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "SPEC-001", "to": "EPIC-001", "type": "parent-epic"},
        {"from": "SPEC-002", "to": "EPIC-001", "type": "parent-epic"},
        {"from": "SPEC-DIRECT", "to": "INITIATIVE-001", "type": "parent-initiative"},
    ]
    return nodes, edges


def test_compute_descendants_vision():
    nodes, edges = _make_scoped_graph()
    desc = _compute_descendants("VISION-001", edges)
    assert "INITIATIVE-001" in desc
    assert "INITIATIVE-002" in desc
    assert "EPIC-001" in desc
    assert "EPIC-002" in desc
    assert "SPEC-001" in desc
    assert "SPEC-002" in desc
    assert "SPEC-DIRECT" in desc
    assert "VISION-001" in desc


def test_compute_descendants_initiative():
    nodes, edges = _make_scoped_graph()
    desc = _compute_descendants("INITIATIVE-001", edges)
    assert "EPIC-001" in desc
    assert "EPIC-002" in desc
    assert "SPEC-001" in desc
    assert "SPEC-DIRECT" in desc
    assert "INITIATIVE-001" in desc
    assert "INITIATIVE-002" not in desc
    assert "VISION-001" not in desc
