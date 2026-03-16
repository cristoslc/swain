---
id: swa-t4c9
status: closed
deps: [swa-e49a]
links: []
created: 2026-03-16T03:44:32Z
type: task
priority: 1
assignee: cristos
parent: swa-1zpe
tags: [spec:SPEC-052]
---
# Task 2: VisionTree renderer — core tree building

**Files:**
- Create: `skills/swain-design/scripts/specgraph/tree_renderer.py`
- Test: `skills/swain-design/scripts/tests/test_tree_renderer.py`

- [ ] **Step 1: Write failing test for basic vision-rooted tree**

Create `skills/swain-design/scripts/tests/test_tree_renderer.py`:

```python
"""Tests for VisionTree renderer."""
import pytest
from specgraph.tree_renderer import render_vision_tree


def _make_nodes(**overrides):
    """Helper to create a minimal node set with a VISION > INITIATIVE > EPIC hierarchy."""
    base = {
        "VISION-001": {"status": "Active", "type": "VISION", "track": "standing",
                       "title": "Swain", "priority_weight": "high"},
        "INITIATIVE-001": {"status": "Active", "type": "INITIATIVE", "track": "container",
                           "title": "Operator Awareness"},
        "EPIC-001": {"status": "Active", "type": "EPIC", "track": "container",
                     "title": "Chart Hierarchy"},
        "SPEC-001": {"status": "Active", "type": "SPEC", "track": "implementable",
                     "title": "Tree Renderer"},
        "SPEC-002": {"status": "Active", "type": "SPEC", "track": "implementable",
                     "title": "CLI Entry Point"},
    }
    base.update(overrides)
    return base


def _make_edges():
    return [
        {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
        {"from": "EPIC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "SPEC-001", "to": "EPIC-001", "type": "parent-epic"},
        {"from": "SPEC-002", "to": "EPIC-001", "type": "parent-epic"},
    ]


class TestRenderVisionTree:
    def test_basic_tree_depth_2(self):
        """At depth 2, epics are leaf nodes with child counts."""
        nodes = _make_nodes()
        edges = _make_edges()
        lines = render_vision_tree(
            nodes={"SPEC-001", "SPEC-002", "EPIC-001", "INITIATIVE-001", "VISION-001"},
            all_nodes=nodes,
            edges=edges,
            depth=2,
        )
        output = "\n".join(lines)
        assert "Swain" in output
        assert "Operator Awareness" in output
        assert "Chart Hierarchy" in output
        assert "2 specs" in output
        # At depth 2, individual specs should NOT appear
        assert "Tree Renderer" not in output
        assert "CLI Entry Point" not in output

    def test_basic_tree_depth_4(self):
        """At depth 4, individual specs appear."""
        nodes = _make_nodes()
        edges = _make_edges()
        lines = render_vision_tree(
            nodes={"SPEC-001", "SPEC-002", "EPIC-001", "INITIATIVE-001", "VISION-001"},
            all_nodes=nodes,
            edges=edges,
            depth=4,
        )
        output = "\n".join(lines)
        assert "Tree Renderer" in output
        assert "CLI Entry Point" in output

    def test_unanchored_section(self):
        """Artifacts without Vision ancestry appear in Unanchored section."""
        nodes = _make_nodes(**{
            "EPIC-099": {"status": "Active", "type": "EPIC", "track": "container",
                         "title": "Orphan Epic"},
        })
        edges = _make_edges()
        lines = render_vision_tree(
            nodes={"EPIC-099", "VISION-001", "INITIATIVE-001", "EPIC-001"},
            all_nodes=nodes,
            edges=edges,
            depth=2,
        )
        output = "\n".join(lines)
        assert "Unanchored" in output
        assert "Orphan Epic" in output

    def test_titles_are_primary_labels(self):
        """Titles should appear, IDs should NOT appear by default."""
        nodes = _make_nodes()
        edges = _make_edges()
        lines = render_vision_tree(
            nodes={"VISION-001", "INITIATIVE-001", "EPIC-001"},
            all_nodes=nodes,
            edges=edges,
            depth=2,
        )
        output = "\n".join(lines)
        assert "Swain" in output
        # IDs should be hidden by default
        assert "VISION-001" not in output

    def t...


## Notes

**2026-03-16T03:48:56Z**

Complete: tree_renderer.py + 13 tests passing
