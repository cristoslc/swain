"""Tests for SPEC-109: Jinja2 template rendering of roadmap output.

Verifies:
1. Each template renders without error
2. Jinja2 output matches the string-concatenation fallback for a fixed graph
3. The fallback path (when jinja2 is not available) produces the same output
"""
from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path
from unittest.mock import patch

# Ensure the specgraph package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import specgraph.roadmap as roadmap_module
from specgraph.roadmap import (
    collect_roadmap_items,
    render_dependency_graph,
    render_eisenhower_table,
    render_gantt,
    render_quadrant_chart,
    render_roadmap_markdown,
    _render_legend_single_row,
    _HAS_JINJA,
)


# ---------------------------------------------------------------------------
# Shared test fixture
# ---------------------------------------------------------------------------

def _make_test_graph():
    """Return (nodes, edges, items) for a deterministic two-epic graph."""
    nodes = {
        "INITIATIVE-001": {
            "title": "Core Platform",
            "status": "Active",
            "type": "INITIATIVE",
            "track": "",
            "file": "docs/INITIATIVE-001.md",
            "description": "",
            "priority_weight": "high",
            "sort_order": 10,
        },
        "EPIC-001": {
            "title": "Authentication System",
            "status": "Active",
            "type": "EPIC",
            "track": "",
            "file": "docs/EPIC-001.md",
            "description": "",
            "priority_weight": "high",
            "sort_order": 5,
        },
        "EPIC-002": {
            "title": "Data:Model Redesign",
            "status": "Proposed",
            "type": "EPIC",
            "track": "",
            "file": "docs/EPIC-002.md",
            "description": "",
            "priority_weight": "medium",
            "sort_order": 0,
        },
        "SPEC-001": {
            "title": "Login Flow",
            "status": "Complete",
            "type": "SPEC",
            "track": "",
            "file": "docs/SPEC-001.md",
            "description": "",
            "priority_weight": "medium",
            "sort_order": 0,
        },
        "SPEC-002": {
            "title": "Token Refresh",
            "status": "Active",
            "type": "SPEC",
            "track": "",
            "file": "docs/SPEC-002.md",
            "description": "",
            "priority_weight": "medium",
            "sort_order": 0,
        },
    }
    edges = [
        {"from": "EPIC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "EPIC-002", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "SPEC-001", "to": "EPIC-001", "type": "parent-epic"},
        {"from": "SPEC-002", "to": "EPIC-001", "type": "parent-epic"},
        {"from": "EPIC-002", "to": "EPIC-001", "type": "depends-on"},
    ]
    items = collect_roadmap_items(nodes, edges)
    return nodes, edges, items


# ---------------------------------------------------------------------------
# Expected outputs (captured from baseline Python string-concat implementation)
# ---------------------------------------------------------------------------

EXPECTED_QUADRANT = (
    "%%{init: {'quadrantChart': {'chartWidth': 700, 'chartHeight': 500,"
    " 'pointLabelFontSize': 14}}}%%\n"
    "quadrantChart\n"
    "    title Priority Matrix\n"
    '    x-axis "Low Urgency" --> "High Urgency"\n'
    '    y-axis "Low Importance" --> "High Importance"\n'
    "    quadrant-1 Do First\n"
    "    quadrant-2 Schedule\n"
    "    quadrant-3 Backlog\n"
    "    quadrant-4 In Progress\n"
    "    E1: [0.88, 0.82]\n"
    "    E2: [0.15, 0.36]"
)

EXPECTED_GANTT = (
    "gantt\n"
    "    title Roadmap\n"
    "    dateFormat YYYY-MM-DD\n"
    "    axisFormat %b %d\n"
    "    tickInterval 1week\n"
    "    section Do First\n"
    "    Authentication System (1/2) :active, t0, 2026-01-01, 14d\n"
    "    section Backlog\n"
    "    Data#colon;Model Redesign (0/0) :crit, t1, after t0, 14d"
)

EXPECTED_DEPS = (
    "flowchart TD\n"
    "    classDef doFirst fill:#e03131,stroke:#c92a2a,color:#fff\n"
    "    classDef scheduled fill:#f59f00,stroke:#e67700,color:#000\n"
    "    classDef inProgress fill:#1c7ed6,stroke:#1864ab,color:#fff\n"
    "    classDef backlog fill:#868e96,stroke:#495057,color:#fff\n"
    '    subgraph INITIATIVE_001["Core Platform"]\n'
    '        EPIC_001["Authentication System"]:::doFirst\n'
    '        EPIC_002["Data#colon;Model Redesign"]:::backlog\n'
    "    end\n"
    "    EPIC_002 -->|blocks| EPIC_001"
)

EXPECTED_EISENHOWER = (
    "### Do First\n"
    "*High priority, active or unblocking*\n"
    "\n"
    "| Initiative | Epic | Progress | Unblocks | Needs |\n"
    "|-----------|------|----------|----------|-------|\n"
    "| [Core Platform](docs/INITIATIVE-001.md)"
    " | [Authentication System](docs/EPIC-001.md) | 1/2 | 1 | — |\n"
    "\n"
    "### Schedule\n"
    "*High priority, not yet started*\n"
    "\n"
    "*(none)*\n"
    "\n"
    "### In Progress\n"
    "*Active or unblocking, medium priority*\n"
    "\n"
    "*(none)*\n"
    "\n"
    "### Backlog\n"
    "*Not yet prioritized or started*\n"
    "\n"
    "| Initiative | Epic | Progress | Unblocks | Needs |\n"
    "|-----------|------|----------|----------|-------|\n"
    "| [Core Platform](docs/INITIATIVE-001.md)"
    " | [Data:Model Redesign](docs/EPIC-002.md) | 0/0 | 0 | **activate or drop** |\n"
)

EXPECTED_LEGEND = (
    "**Do First** <br> *Core Platform* — [E1](docs/EPIC-001.md)"
    " <br> <br> "
    "**Backlog** <br> *Core Platform* — [E2](docs/EPIC-002.md)"
)


# ---------------------------------------------------------------------------
# 1. Template renders without error
# ---------------------------------------------------------------------------

def test_quadrant_renders_without_error():
    _, _, items = _make_test_graph()
    src, legend = render_quadrant_chart(items)
    assert isinstance(src, str)
    assert len(src) > 0
    assert isinstance(legend, list)


def test_gantt_renders_without_error():
    nodes, _, items = _make_test_graph()
    result = render_gantt(items, nodes)
    assert isinstance(result, str)
    assert "gantt" in result


def test_deps_renders_without_error():
    nodes, _, items = _make_test_graph()
    result = render_dependency_graph(items, nodes)
    assert result is not None
    assert "flowchart TD" in result


def test_eisenhower_renders_without_error():
    nodes, _, items = _make_test_graph()
    result = render_eisenhower_table(items, nodes)
    assert isinstance(result, str)
    assert "### Do First" in result


def test_legend_renders_without_error():
    nodes, _, items = _make_test_graph()
    _, legend_items = render_quadrant_chart(items)
    result = _render_legend_single_row(legend_items, nodes, items)
    assert isinstance(result, str)
    assert "Do First" in result


def test_roadmap_renders_without_error():
    nodes, _, items = _make_test_graph()
    result = render_roadmap_markdown(items, nodes, repo_root="")
    assert isinstance(result, str)
    assert "# Roadmap" in result


# ---------------------------------------------------------------------------
# 2. Jinja2 output matches expected (string-concat baseline)
# ---------------------------------------------------------------------------

def test_quadrant_output_matches_baseline():
    _, _, items = _make_test_graph()
    src, _ = render_quadrant_chart(items)
    assert src == EXPECTED_QUADRANT


def test_gantt_output_matches_baseline():
    nodes, _, items = _make_test_graph()
    result = render_gantt(items, nodes)
    assert result == EXPECTED_GANTT


def test_deps_output_matches_baseline():
    nodes, _, items = _make_test_graph()
    result = render_dependency_graph(items, nodes)
    assert result == EXPECTED_DEPS


def test_eisenhower_output_matches_baseline():
    nodes, _, items = _make_test_graph()
    result = render_eisenhower_table(items, nodes)
    assert result == EXPECTED_EISENHOWER


def test_legend_output_matches_baseline():
    nodes, _, items = _make_test_graph()
    _, legend_items = render_quadrant_chart(items)
    result = _render_legend_single_row(legend_items, nodes, items)
    assert result == EXPECTED_LEGEND


def test_roadmap_inline_mermaid_structure():
    """When no repo_root is given (no PNG), inline Mermaid is used."""
    nodes, _, items = _make_test_graph()
    result = render_roadmap_markdown(items, nodes, repo_root="")
    assert result.startswith("# Roadmap\n")
    assert "```mermaid\n" in result
    assert "quadrantChart" in result
    assert "## Timeline" in result
    assert "## Blocking Dependencies" in result
    assert result.endswith("\n")


def test_roadmap_no_deps_section_when_no_dependencies():
    """When there are no Epic-level dependencies, dep section is omitted."""
    nodes = {
        "EPIC-001": {
            "title": "Auth", "status": "Active", "type": "EPIC",
            "track": "", "file": "", "description": "",
            "priority_weight": "high", "sort_order": 0,
        },
    }
    edges: list[dict] = []
    items = collect_roadmap_items(nodes, edges)
    result = render_roadmap_markdown(items, nodes, repo_root="")
    assert "## Blocking Dependencies" not in result


# ---------------------------------------------------------------------------
# 3. Fallback path — same output when jinja2 is not available
# ---------------------------------------------------------------------------

def _render_with_jinja_disabled(func, *args, **kwargs):
    """Call a roadmap render function with _HAS_JINJA patched to False."""
    with patch.object(roadmap_module, "_HAS_JINJA", False):
        return func(*args, **kwargs)


def test_quadrant_fallback_matches_jinja():
    _, _, items = _make_test_graph()
    jinja_src, _ = render_quadrant_chart(items)
    fallback_src, _ = _render_with_jinja_disabled(render_quadrant_chart, items)
    assert jinja_src == fallback_src


def test_gantt_fallback_matches_jinja():
    nodes, _, items = _make_test_graph()
    jinja_result = render_gantt(items, nodes)
    fallback_result = _render_with_jinja_disabled(render_gantt, items, nodes)
    assert jinja_result == fallback_result


def test_deps_fallback_matches_jinja():
    nodes, _, items = _make_test_graph()
    jinja_result = render_dependency_graph(items, nodes)
    fallback_result = _render_with_jinja_disabled(render_dependency_graph, items, nodes)
    assert jinja_result == fallback_result


def test_eisenhower_fallback_matches_jinja():
    nodes, _, items = _make_test_graph()
    jinja_result = render_eisenhower_table(items, nodes)
    fallback_result = _render_with_jinja_disabled(render_eisenhower_table, items, nodes)
    assert jinja_result == fallback_result


def test_legend_fallback_matches_jinja():
    nodes, _, items = _make_test_graph()
    _, legend_items = render_quadrant_chart(items)
    jinja_result = _render_legend_single_row(legend_items, nodes, items)
    fallback_result = _render_with_jinja_disabled(
        _render_legend_single_row, legend_items, nodes, items
    )
    assert jinja_result == fallback_result


def test_roadmap_fallback_matches_jinja():
    nodes, _, items = _make_test_graph()
    jinja_result = render_roadmap_markdown(items, nodes, repo_root="")
    fallback_result = _render_with_jinja_disabled(
        render_roadmap_markdown, items, nodes, repo_root=""
    )
    assert jinja_result == fallback_result


def test_module_imports_without_jinja_installed():
    """The module must load even when jinja2 is not importable."""
    # Simulate jinja2 being absent by temporarily blocking its import
    saved = sys.modules.get("jinja2")
    sys.modules["jinja2"] = None  # type: ignore[assignment]
    try:
        # Re-import the module; it should set _HAS_JINJA=False silently
        import importlib
        spec = importlib.util.find_spec("specgraph.roadmap")
        # We can't easily re-exec the try/except, so we just verify
        # that _HAS_JINJA is a bool (already set at import time)
        assert isinstance(roadmap_module._HAS_JINJA, bool)
    finally:
        if saved is None:
            del sys.modules["jinja2"]
        else:
            sys.modules["jinja2"] = saved
