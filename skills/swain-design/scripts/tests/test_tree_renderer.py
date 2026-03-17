"""Tests for VisionTree renderer."""
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from specgraph.tree_renderer import render_vision_tree, render_breadcrumb


def _make_nodes(**overrides):
    """Helper to create a minimal node set."""
    base = {
        "VISION-001": {"status": "Active", "type": "VISION", "track": "standing",
                       "title": "Swain", "priority_weight": "high",
                       "file": "", "description": ""},
        "INITIATIVE-001": {"status": "Active", "type": "INITIATIVE", "track": "container",
                           "title": "Operator Awareness",
                           "file": "", "description": ""},
        "EPIC-001": {"status": "Active", "type": "EPIC", "track": "container",
                     "title": "Chart Hierarchy",
                     "file": "", "description": ""},
        "SPEC-001": {"status": "Active", "type": "SPEC", "track": "implementable",
                     "title": "Tree Renderer",
                     "file": "", "description": ""},
        "SPEC-002": {"status": "Active", "type": "SPEC", "track": "implementable",
                     "title": "CLI Entry Point",
                     "file": "", "description": ""},
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
            nodes=set(nodes.keys()),
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
            nodes=set(nodes.keys()),
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
                         "title": "Orphan Epic",
                         "file": "", "description": ""},
        })
        edges = _make_edges()
        lines = render_vision_tree(
            nodes=set(nodes.keys()),
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
        assert "VISION-001" not in output

    def test_show_ids(self):
        """With show_ids=True, IDs appear alongside titles."""
        nodes = _make_nodes()
        edges = _make_edges()
        lines = render_vision_tree(
            nodes={"VISION-001", "INITIATIVE-001", "EPIC-001"},
            all_nodes=nodes,
            edges=edges,
            depth=2,
            show_ids=True,
        )
        output = "\n".join(lines)
        assert "VISION-001" in output
        assert "Swain" in output

    def test_legend_at_bottom(self):
        """Legend line appears at the bottom of output."""
        nodes = _make_nodes()
        edges = _make_edges()
        lines = render_vision_tree(
            nodes={"VISION-001"},
            all_nodes=nodes,
            edges=edges,
            depth=2,
        )
        last_line = lines[-1].lower()
        assert "ready" in last_line or "blocked" in last_line

    def test_flattening_when_intermediate_missing(self):
        """Spec directly under Initiative (no Epic) should flatten."""
        nodes = {
            "VISION-001": {"status": "Active", "type": "VISION", "track": "standing",
                           "title": "Swain", "file": "", "description": ""},
            "INITIATIVE-001": {"status": "Active", "type": "INITIATIVE", "track": "container",
                               "title": "Awareness", "file": "", "description": ""},
            "SPEC-001": {"status": "Active", "type": "SPEC", "track": "implementable",
                         "title": "Direct Spec", "file": "", "description": ""},
        }
        edges = [
            {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
            {"from": "SPEC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
        ]
        lines = render_vision_tree(
            nodes=set(nodes.keys()),
            all_nodes=nodes,
            edges=edges,
            depth=4,
        )
        output = "\n".join(lines)
        assert "Direct Spec" in output

    def test_sort_key(self):
        """Custom sort_key orders siblings."""
        nodes = {
            "VISION-001": {"status": "Active", "type": "VISION", "track": "standing",
                           "title": "Swain", "file": "", "description": ""},
            "EPIC-001": {"status": "Active", "type": "EPIC", "track": "container",
                         "title": "Zebra Epic", "file": "", "description": ""},
            "EPIC-002": {"status": "Active", "type": "EPIC", "track": "container",
                         "title": "Alpha Epic", "file": "", "description": ""},
        }
        edges = [
            {"from": "EPIC-001", "to": "VISION-001", "type": "parent-vision"},
            {"from": "EPIC-002", "to": "VISION-001", "type": "parent-vision"},
        ]
        lines = render_vision_tree(
            nodes=set(nodes.keys()),
            all_nodes=nodes,
            edges=edges,
            depth=2,
        )
        output = "\n".join(lines)
        alpha_pos = output.index("Alpha Epic")
        zebra_pos = output.index("Zebra Epic")
        assert alpha_pos < zebra_pos

    def test_phase_filter(self):
        """Phase filter excludes artifacts not in the specified phases."""
        nodes = _make_nodes(**{
            "SPEC-003": {"status": "Complete", "type": "SPEC", "track": "implementable",
                         "title": "Done Spec", "file": "", "description": ""},
        })
        edges = _make_edges() + [
            {"from": "SPEC-003", "to": "EPIC-001", "type": "parent-epic"},
        ]
        lines = render_vision_tree(
            nodes=set(nodes.keys()),
            all_nodes=nodes,
            edges=edges,
            depth=4,
            phase_filter={"Active"},
        )
        output = "\n".join(lines)
        assert "Done Spec" not in output
        assert "Tree Renderer" in output

    def test_elbow_connectors(self):
        """Output uses proper elbow connectors."""
        nodes = _make_nodes()
        edges = _make_edges()
        lines = render_vision_tree(
            nodes=set(nodes.keys()),
            all_nodes=nodes,
            edges=edges,
            depth=2,
        )
        output = "\n".join(lines)
        assert "\u251c\u2500\u2500" in output or "\u2514\u2500\u2500" in output


class TestRenderBreadcrumb:
    def test_full_chain(self):
        """Breadcrumb shows full ancestry."""
        nodes = _make_nodes()
        edges = _make_edges()
        result = render_breadcrumb("SPEC-001", nodes, edges)
        assert result == "Swain > Operator Awareness > Chart Hierarchy > Tree Renderer"

    def test_vision_only(self):
        """Vision has no parent — breadcrumb is just its title."""
        nodes = _make_nodes()
        edges = _make_edges()
        result = render_breadcrumb("VISION-001", nodes, edges)
        assert result == "Swain"

    def test_orphan(self):
        """Orphan artifact shows just its own title."""
        nodes = _make_nodes(**{
            "EPIC-099": {"status": "Active", "type": "EPIC", "track": "container",
                         "title": "Orphan", "file": "", "description": ""},
        })
        edges = _make_edges()
        result = render_breadcrumb("EPIC-099", nodes, edges)
        assert result == "Orphan"
