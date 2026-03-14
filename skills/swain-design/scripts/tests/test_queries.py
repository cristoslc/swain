"""Tests for specgraph blocks/blocked-by/tree/edges query functions."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from specgraph.queries import blocks, blocked_by, tree, edges_cmd, neighbors


# ---------------------------------------------------------------------------
# Shared fixture data
# ---------------------------------------------------------------------------

# Node structure: id → {title, status, type, file, description}
NODES = {
    "SPEC-001": {"title": "Spec 1", "status": "In Progress", "type": "SPEC", "file": "docs/spec/SPEC-001.md", "description": ""},
    "SPEC-002": {"title": "Spec 2", "status": "Ready", "type": "SPEC", "file": "docs/spec/SPEC-002.md", "description": ""},
    "SPEC-003": {"title": "Spec 3 (resolved)", "status": "Complete", "type": "SPEC", "file": "docs/spec/SPEC-003.md", "description": ""},
    "EPIC-001": {"title": "Epic 1", "status": "Active", "type": "EPIC", "file": "docs/epic/EPIC-001.md", "description": ""},
    "EPIC-002": {"title": "Epic 2 (resolved)", "status": "Complete", "type": "EPIC", "file": "docs/epic/EPIC-002.md", "description": ""},
    "ADR-001": {"title": "ADR 1 (standing/active)", "status": "Active", "type": "ADR", "file": "docs/adr/ADR-001.md", "description": ""},
    "SPIKE-001": {"title": "Spike 1", "status": "In Progress", "type": "SPIKE", "file": "docs/spike/SPIKE-001.md", "description": ""},
}

# Edge structure: list of {from, to, type}
EDGES = [
    # SPEC-001 depends-on SPEC-002 (SPEC-002 is unresolved → blocks SPEC-001)
    {"from": "SPEC-001", "to": "SPEC-002", "type": "depends-on"},
    # SPEC-001 depends-on SPEC-003 (SPEC-003 is resolved → should NOT appear in blocks)
    {"from": "SPEC-001", "to": "SPEC-003", "type": "depends-on"},
    # SPEC-002 depends-on EPIC-001 (EPIC-001 is unresolved)
    {"from": "SPEC-002", "to": "EPIC-001", "type": "depends-on"},
    # EPIC-001 depends-on EPIC-002 (EPIC-002 is resolved → should NOT appear)
    {"from": "EPIC-001", "to": "EPIC-002", "type": "depends-on"},
    # EPIC-001 depends-on ADR-001 (ADR-001 is Active+standing → resolved, should NOT appear)
    {"from": "EPIC-001", "to": "ADR-001", "type": "depends-on"},
    # Non-depends-on edge (should be ignored by blocks/blocked_by/tree)
    {"from": "SPEC-001", "to": "EPIC-001", "type": "parent-epic"},
]


# ---------------------------------------------------------------------------
# TestBlocksBlockedByTreeEdges
# ---------------------------------------------------------------------------


class TestBlocksBlockedByTreeEdges:
    """Test blocks, blocked_by, tree, and edges_cmd query functions."""

    # --- blocks ---

    def test_blocks_returns_direct_unresolved_deps(self):
        """blocks(SPEC-001) returns SPEC-002 (unresolved depends-on target)."""
        result = blocks("SPEC-001", NODES, EDGES)
        ids = result.strip().split("\n") if result.strip() else []
        assert "SPEC-002" in ids

    def test_blocks_excludes_resolved_deps(self):
        """blocks(SPEC-001) does NOT return SPEC-003 (resolved Complete)."""
        result = blocks("SPEC-001", NODES, EDGES)
        ids = result.strip().split("\n") if result.strip() else []
        assert "SPEC-003" not in ids

    def test_blocks_excludes_standing_active_resolved(self):
        """blocks(EPIC-001) does NOT return ADR-001 (ADR Active = resolved)."""
        result = blocks("EPIC-001", NODES, EDGES)
        ids = result.strip().split("\n") if result.strip() else []
        assert "ADR-001" not in ids

    def test_blocks_ignores_non_depends_on_edges(self):
        """blocks(SPEC-001) ignores parent-epic edge to EPIC-001."""
        result = blocks("SPEC-001", NODES, EDGES)
        ids = result.strip().split("\n") if result.strip() else []
        assert "EPIC-001" not in ids

    def test_blocks_empty_when_no_deps(self):
        """blocks(EPIC-002) returns empty string (no outgoing depends-on edges)."""
        result = blocks("EPIC-002", NODES, EDGES)
        assert result.strip() == ""

    def test_blocks_empty_when_all_deps_resolved(self):
        """blocks(EPIC-001) returns empty (all depends-on targets are resolved)."""
        result = blocks("EPIC-001", NODES, EDGES)
        assert result.strip() == ""

    def test_blocks_unknown_artifact_returns_empty(self):
        """blocks(UNKNOWN-999) returns empty (no such node)."""
        result = blocks("UNKNOWN-999", NODES, EDGES)
        assert result.strip() == ""

    # --- blocked_by ---

    def test_blocked_by_returns_unresolved_sources(self):
        """blocked_by(SPEC-002) returns SPEC-001 (unresolved node that depends on SPEC-002)."""
        result = blocked_by("SPEC-002", NODES, EDGES)
        ids = result.strip().split("\n") if result.strip() else []
        assert "SPEC-001" in ids

    def test_blocked_by_excludes_resolved_sources(self):
        """blocked_by(EPIC-002) does NOT return EPIC-001... wait, EPIC-001 is unresolved.
        So EPIC-001 IS included in blocked_by(EPIC-002)."""
        # EPIC-001 depends-on EPIC-002; EPIC-001 is unresolved → should appear
        result = blocked_by("EPIC-002", NODES, EDGES)
        ids = result.strip().split("\n") if result.strip() else []
        assert "EPIC-001" in ids

    def test_blocked_by_uses_resolved_sources_check(self):
        """blocked_by target filtering: if source is resolved, exclude it.

        Add a resolved source: SPEC-003 (resolved) would-depend-on SPEC-002.
        We inject a test-only edge to verify exclusion.
        """
        extra_edges = list(EDGES) + [
            {"from": "SPEC-003", "to": "SPEC-002", "type": "depends-on"},
        ]
        result = blocked_by("SPEC-002", NODES, extra_edges)
        ids = result.strip().split("\n") if result.strip() else []
        # SPEC-001 (unresolved) should be there
        assert "SPEC-001" in ids
        # SPEC-003 (Complete) should NOT be there
        assert "SPEC-003" not in ids

    def test_blocked_by_ignores_non_depends_on_edges(self):
        """blocked_by(EPIC-001) ignores parent-epic edge from SPEC-001."""
        result = blocked_by("EPIC-001", NODES, EDGES)
        ids = result.strip().split("\n") if result.strip() else []
        # SPEC-001→EPIC-001 is parent-epic, not depends-on → should not appear
        assert "SPEC-001" not in ids

    def test_blocked_by_empty_when_nobody_depends_on_it(self):
        """blocked_by(SPIKE-001) returns empty (nothing depends on SPIKE-001)."""
        result = blocked_by("SPIKE-001", NODES, EDGES)
        assert result.strip() == ""

    def test_blocked_by_unknown_artifact_returns_empty(self):
        """blocked_by(UNKNOWN-999) returns empty."""
        result = blocked_by("UNKNOWN-999", NODES, EDGES)
        assert result.strip() == ""

    # --- tree ---

    def test_tree_returns_transitive_closure(self):
        """tree(SPEC-001) includes SPEC-002 and EPIC-001 (transitive unresolved deps)."""
        result = tree("SPEC-001", NODES, EDGES)
        ids = result.strip().split("\n") if result.strip() else []
        assert "SPEC-002" in ids
        assert "EPIC-001" in ids

    def test_tree_excludes_resolved_nodes(self):
        """tree(SPEC-001) excludes SPEC-003 (resolved) and EPIC-002 and ADR-001 (resolved)."""
        result = tree("SPEC-001", NODES, EDGES)
        ids = result.strip().split("\n") if result.strip() else []
        assert "SPEC-003" not in ids
        assert "EPIC-002" not in ids
        assert "ADR-001" not in ids

    def test_tree_excludes_self(self):
        """tree(SPEC-001) does not include SPEC-001 itself."""
        result = tree("SPEC-001", NODES, EDGES)
        ids = result.strip().split("\n") if result.strip() else []
        assert "SPEC-001" not in ids

    def test_tree_handles_cycle(self):
        """tree with a cycle terminates without infinite loop."""
        cycle_nodes = {
            "A": {"title": "A", "status": "In Progress", "type": "SPEC", "file": "", "description": ""},
            "B": {"title": "B", "status": "In Progress", "type": "SPEC", "file": "", "description": ""},
        }
        cycle_edges = [
            {"from": "A", "to": "B", "type": "depends-on"},
            {"from": "B", "to": "A", "type": "depends-on"},
        ]
        result = tree("A", cycle_nodes, cycle_edges)
        ids = result.strip().split("\n") if result.strip() else []
        # Both A and B are in cycle; B is the dep of A. A itself excluded.
        assert "B" in ids
        assert "A" not in ids

    def test_tree_empty_for_leaf_node(self):
        """tree(EPIC-002) returns empty (no outgoing unresolved depends-on edges)."""
        result = tree("EPIC-002", NODES, EDGES)
        assert result.strip() == ""

    def test_tree_empty_when_all_deps_resolved(self):
        """tree(EPIC-001) returns empty because all its depends-on targets are resolved."""
        result = tree("EPIC-001", NODES, EDGES)
        assert result.strip() == ""

    def test_tree_unknown_artifact_returns_empty(self):
        """tree(UNKNOWN-999) returns empty."""
        result = tree("UNKNOWN-999", NODES, EDGES)
        assert result.strip() == ""

    # --- edges_cmd ---

    def test_edges_cmd_returns_all_edges_when_no_filter(self):
        """edges_cmd(None) returns TSV with all edges."""
        result = edges_cmd(None, NODES, EDGES)
        lines = [l for l in result.strip().split("\n") if l]
        assert len(lines) == len(EDGES)

    def test_edges_cmd_tsv_format(self):
        """Each line is tab-separated: from\\tto\\ttype."""
        result = edges_cmd(None, NODES, EDGES)
        for line in result.strip().split("\n"):
            if line:
                parts = line.split("\t")
                assert len(parts) == 3, f"Expected 3 tab-separated fields, got: {line!r}"

    def test_edges_cmd_filtered_by_artifact_id_from(self):
        """edges_cmd(SPEC-001) includes edges where SPEC-001 is the source."""
        result = edges_cmd("SPEC-001", NODES, EDGES)
        lines = [l for l in result.strip().split("\n") if l]
        for line in lines:
            frm, to, typ = line.split("\t")
            assert frm == "SPEC-001" or to == "SPEC-001", f"Unexpected edge: {line!r}"

    def test_edges_cmd_filtered_includes_to_side(self):
        """edges_cmd(EPIC-001) includes edges where EPIC-001 is the target."""
        result = edges_cmd("EPIC-001", NODES, EDGES)
        lines = [l for l in result.strip().split("\n") if l]
        found_to = any(line.split("\t")[1] == "EPIC-001" for line in lines)
        assert found_to, "Expected at least one edge with EPIC-001 as target"

    def test_edges_cmd_sorted(self):
        """edges_cmd output is sorted by from, then to, then type."""
        result = edges_cmd(None, NODES, EDGES)
        lines = [l for l in result.strip().split("\n") if l]
        tuples = [tuple(l.split("\t")) for l in lines]
        assert tuples == sorted(tuples), "Edges are not sorted"

    def test_edges_cmd_unknown_id_returns_empty(self):
        """edges_cmd(UNKNOWN-999) returns empty string (no matching edges)."""
        result = edges_cmd("UNKNOWN-999", NODES, EDGES)
        assert result.strip() == ""

    def test_edges_cmd_none_empty_graph_returns_empty(self):
        """edges_cmd(None) on empty graph returns empty string."""
        result = edges_cmd(None, {}, [])
        assert result.strip() == ""

    # --- show_links integration (non-TTY) ---

    def test_blocks_show_links_non_tty_no_escapes(self):
        """blocks with show_links=True on non-TTY returns plain IDs."""
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.isatty.return_value = False
            result = blocks("SPEC-001", NODES, EDGES, repo_root="/repo", show_links=True)
        assert "\x1b" not in result
        ids = result.strip().split("\n") if result.strip() else []
        assert "SPEC-002" in ids

    def test_blocked_by_show_links_non_tty_no_escapes(self):
        """blocked_by with show_links=True on non-TTY returns plain IDs."""
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.isatty.return_value = False
            result = blocked_by("SPEC-002", NODES, EDGES, repo_root="/repo", show_links=True)
        assert "\x1b" not in result
        ids = result.strip().split("\n") if result.strip() else []
        assert "SPEC-001" in ids

    def test_tree_show_links_non_tty_no_escapes(self):
        """tree with show_links=True on non-TTY returns plain IDs."""
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.isatty.return_value = False
            result = tree("SPEC-001", NODES, EDGES, repo_root="/repo", show_links=True)
        assert "\x1b" not in result


# ---------------------------------------------------------------------------
# TestNeighbors
# ---------------------------------------------------------------------------


class TestNeighbors:
    """Test neighbors() — TSV of all edges touching an artifact (both directions)."""

    def test_neighbors_from_direction(self):
        """neighbors returns 'from' direction when artifact is the source."""
        result = neighbors("SPEC-001", NODES, EDGES)
        lines = [l for l in result.strip().split("\n") if l]
        directions = {line.split("\t")[0] for line in lines}
        assert "from" in directions

    def test_neighbors_to_direction(self):
        """neighbors returns 'to' direction when artifact is the target."""
        # SPEC-002 is the target of SPEC-001 depends-on, so neighbors(SPEC-002) should
        # show direction='to' for the edge from SPEC-001
        result = neighbors("SPEC-002", NODES, EDGES)
        lines = [l for l in result.strip().split("\n") if l]
        directions = {line.split("\t")[0] for line in lines}
        assert "to" in directions

    def test_neighbors_both_directions(self):
        """neighbors includes both 'from' and 'to' directions for a hub artifact.

        EPIC-001 is:
        - target of SPEC-002 depends-on (direction='to')
        - target of SPEC-001 parent-epic (direction='to')
        - source of EPIC-001 depends-on EPIC-002 (direction='from')
        - source of EPIC-001 depends-on ADR-001 (direction='from')
        So both directions should appear.
        """
        result = neighbors("EPIC-001", NODES, EDGES)
        lines = [l for l in result.strip().split("\n") if l]
        directions = {line.split("\t")[0] for line in lines}
        assert "from" in directions
        assert "to" in directions

    def test_neighbors_includes_status_and_title(self):
        """neighbors includes status and title columns when node is in nodes dict."""
        result = neighbors("SPEC-001", NODES, EDGES)
        lines = [l for l in result.strip().split("\n") if l]
        # Find the row for SPEC-002 (from direction)
        spec002_rows = [l for l in lines if "SPEC-002" in l]
        assert spec002_rows, "Expected row for SPEC-002"
        parts = spec002_rows[0].split("\t")
        # Columns: direction, edge_type, artifact_id, status, title
        assert len(parts) == 5
        assert parts[3] == NODES["SPEC-002"]["status"]
        assert parts[4] == NODES["SPEC-002"]["title"]

    def test_neighbors_empty_when_no_edges_touch_artifact(self):
        """neighbors returns empty string when no edges reference the artifact."""
        result = neighbors("UNKNOWN-999", NODES, EDGES)
        assert result.strip() == ""

    def test_neighbors_tsv_format_column_count(self):
        """Each output line has exactly 5 tab-separated columns."""
        result = neighbors("SPEC-001", NODES, EDGES)
        for line in result.strip().split("\n"):
            if not line:
                continue
            parts = line.split("\t")
            assert len(parts) == 5, f"Expected 5 columns, got: {line!r}"

    def test_neighbors_sorted_by_direction_then_type_then_id(self):
        """neighbors output is sorted by direction, then edge_type, then artifact_id."""
        result = neighbors("EPIC-001", NODES, EDGES)
        lines = [l for l in result.strip().split("\n") if l]
        tuples = [tuple(l.split("\t")[:3]) for l in lines]  # direction, edge_type, artifact_id
        assert tuples == sorted(tuples), f"Output not sorted: {tuples}"

    def test_neighbors_unknown_node_shows_empty_status_title(self):
        """neighbors shows empty status and title for other_id not in nodes dict."""
        extra_edges = list(EDGES) + [
            {"from": "SPEC-001", "to": "UNKNOWN-999", "type": "relates-to"},
        ]
        result = neighbors("SPEC-001", NODES, extra_edges)
        # Use splitlines() to preserve trailing-tab lines without stripping them
        lines = [l for l in result.splitlines() if l.strip()]
        unknown_rows = [l for l in lines if "UNKNOWN-999" in l]
        assert unknown_rows, "Expected row for UNKNOWN-999"
        parts = unknown_rows[0].split("\t")
        assert len(parts) == 5
        assert parts[3] == ""   # status empty
        assert parts[4] == ""   # title empty
