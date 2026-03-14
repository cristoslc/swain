"""Tests for specgraph blocks/blocked-by/tree/edges query functions."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from specgraph.queries import blocks, blocked_by, tree, edges_cmd, neighbors, scope, impact, mermaid_cmd, status_cmd, ready, next_cmd, overview


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


# ---------------------------------------------------------------------------
# Fixtures for scope/impact tests
# ---------------------------------------------------------------------------

# Richer graph: VISION → EPIC → SPEC hierarchy + laterals
SCOPE_NODES = {
    "VISION-001": {"title": "Vision 1", "status": "Active", "type": "VISION", "file": "docs/vision/VISION-001.md", "description": ""},
    "EPIC-010": {"title": "Epic 10", "status": "Active", "type": "EPIC", "file": "docs/epic/EPIC-010.md", "description": ""},
    "EPIC-011": {"title": "Epic 11", "status": "Active", "type": "EPIC", "file": "docs/epic/EPIC-011.md", "description": ""},
    "SPEC-010": {"title": "Spec 10", "status": "In Progress", "type": "SPEC", "file": "docs/spec/SPEC-010.md", "description": ""},
    "SPEC-011": {"title": "Spec 11", "status": "Ready", "type": "SPEC", "file": "docs/spec/SPEC-011.md", "description": ""},
    "SPEC-012": {"title": "Spec 12", "status": "Draft", "type": "SPEC", "file": "docs/spec/SPEC-012.md", "description": ""},
    "ADR-010": {"title": "ADR 10", "status": "Active", "type": "ADR", "file": "docs/adr/ADR-010.md", "description": ""},
}

SCOPE_EDGES = [
    # EPIC-010 is child of VISION-001
    {"from": "EPIC-010", "to": "VISION-001", "type": "parent-vision"},
    # EPIC-011 is also child of VISION-001 (sibling of EPIC-010)
    {"from": "EPIC-011", "to": "VISION-001", "type": "parent-vision"},
    # SPEC-010 is child of EPIC-010
    {"from": "SPEC-010", "to": "EPIC-010", "type": "parent-epic"},
    # SPEC-011 is also child of EPIC-010 (sibling of SPEC-010)
    {"from": "SPEC-011", "to": "EPIC-010", "type": "parent-epic"},
    # SPEC-012 is child of EPIC-011 (different epic, not sibling of SPEC-010)
    {"from": "SPEC-012", "to": "EPIC-011", "type": "parent-epic"},
    # Lateral: SPEC-010 linked-artifact to ADR-010
    {"from": "SPEC-010", "to": "ADR-010", "type": "linked-artifact"},
    # Lateral: SPEC-010 validates SPEC-012
    {"from": "SPEC-010", "to": "SPEC-012", "type": "validates"},
]


# ---------------------------------------------------------------------------
# TestScope
# ---------------------------------------------------------------------------


class TestScope:
    """Test scope() — parent chain, siblings, laterals."""

    def test_scope_unknown_artifact_returns_empty(self):
        """scope(UNKNOWN-999) returns empty string."""
        result = scope("UNKNOWN-999", SCOPE_NODES, SCOPE_EDGES)
        assert result == ""

    def test_scope_parent_chain_direct_parent(self):
        """scope(SPEC-010) parent chain includes EPIC-010."""
        result = scope("SPEC-010", SCOPE_NODES, SCOPE_EDGES)
        assert "EPIC-010" in result

    def test_scope_parent_chain_grandparent(self):
        """scope(SPEC-010) parent chain includes VISION-001 (grandparent via EPIC-010)."""
        result = scope("SPEC-010", SCOPE_NODES, SCOPE_EDGES)
        assert "VISION-001" in result

    def test_scope_parent_chain_section_header(self):
        """scope output includes '=== Parent Chain ===' header."""
        result = scope("SPEC-010", SCOPE_NODES, SCOPE_EDGES)
        assert "=== Parent Chain ===" in result

    def test_scope_siblings_includes_sibling_spec(self):
        """scope(SPEC-010) siblings includes SPEC-011 (shares EPIC-010 parent)."""
        result = scope("SPEC-010", SCOPE_NODES, SCOPE_EDGES)
        assert "SPEC-011" in result

    def test_scope_siblings_excludes_self(self):
        """scope(SPEC-010) siblings does NOT include SPEC-010 itself."""
        result = scope("SPEC-010", SCOPE_NODES, SCOPE_EDGES)
        # Find siblings section specifically
        lines = result.split("\n")
        in_siblings = False
        sibling_ids = []
        for line in lines:
            if "=== Siblings ===" in line:
                in_siblings = True
                continue
            if in_siblings and line.startswith("==="):
                break
            if in_siblings and line.strip():
                sibling_ids.append(line.strip())
        assert "SPEC-010" not in sibling_ids

    def test_scope_siblings_excludes_different_parent(self):
        """scope(SPEC-010) siblings does NOT include SPEC-012 (different parent EPIC-011)."""
        result = scope("SPEC-010", SCOPE_NODES, SCOPE_EDGES)
        lines = result.split("\n")
        in_siblings = False
        sibling_ids = []
        for line in lines:
            if "=== Siblings ===" in line:
                in_siblings = True
                continue
            if in_siblings and line.startswith("==="):
                break
            if in_siblings and line.strip():
                sibling_ids.append(line.strip())
        assert "SPEC-012" not in sibling_ids

    def test_scope_siblings_section_header(self):
        """scope output includes '=== Siblings ===' header."""
        result = scope("SPEC-010", SCOPE_NODES, SCOPE_EDGES)
        assert "=== Siblings ===" in result

    def test_scope_laterals_includes_linked_artifact(self):
        """scope(SPEC-010) laterals includes ADR-010 (linked-artifact edge)."""
        result = scope("SPEC-010", SCOPE_NODES, SCOPE_EDGES)
        assert "ADR-010" in result

    def test_scope_laterals_includes_validates(self):
        """scope(SPEC-010) laterals includes SPEC-012 (validates edge)."""
        result = scope("SPEC-010", SCOPE_NODES, SCOPE_EDGES)
        assert "SPEC-012" in result

    def test_scope_laterals_section_header(self):
        """scope output includes '=== Laterals ===' header."""
        result = scope("SPEC-010", SCOPE_NODES, SCOPE_EDGES)
        assert "=== Laterals ===" in result

    def test_scope_no_parent_shows_empty_parent_chain(self):
        """scope(VISION-001) has no parent chain entries."""
        result = scope("VISION-001", SCOPE_NODES, SCOPE_EDGES)
        lines = result.split("\n")
        in_chain = False
        chain_ids = []
        for line in lines:
            if "=== Parent Chain ===" in line:
                in_chain = True
                continue
            if in_chain and line.startswith("==="):
                break
            if in_chain and line.strip():
                chain_ids.append(line.strip())
        assert chain_ids == []

    def test_scope_architecture_overview_section_header(self):
        """scope output includes '=== Architecture Overview ===' header."""
        result = scope("SPEC-010", SCOPE_NODES, SCOPE_EDGES)
        assert "=== Architecture Overview ===" in result

    def test_scope_parent_chain_epic_only(self):
        """scope(EPIC-010) parent chain includes VISION-001 only."""
        result = scope("EPIC-010", SCOPE_NODES, SCOPE_EDGES)
        lines = result.split("\n")
        in_chain = False
        chain_ids = []
        for line in lines:
            if "=== Parent Chain ===" in line:
                in_chain = True
                continue
            if in_chain and line.startswith("==="):
                break
            if in_chain and line.strip():
                chain_ids.append(line.strip())
        assert "VISION-001" in chain_ids
        assert "EPIC-010" not in chain_ids


# ---------------------------------------------------------------------------
# TestImpact
# ---------------------------------------------------------------------------


class TestImpact:
    """Test impact() — direct refs and transitive chain walking."""

    def test_impact_unknown_artifact_shows_zero_direct(self):
        """impact(UNKNOWN-999) shows DIRECT: 0."""
        result = impact("UNKNOWN-999", SCOPE_NODES, SCOPE_EDGES)
        assert "DIRECT: 0" in result

    def test_impact_direct_refs(self):
        """impact(EPIC-010) shows SPEC-010 and SPEC-011 as direct references."""
        result = impact("EPIC-010", SCOPE_NODES, SCOPE_EDGES)
        assert "SPEC-010" in result
        assert "SPEC-011" in result

    def test_impact_direct_count(self):
        """impact(EPIC-010) DIRECT count is 2 (SPEC-010 and SPEC-011)."""
        result = impact("EPIC-010", SCOPE_NODES, SCOPE_EDGES)
        lines = result.split("\n")
        direct_line = next((l for l in lines if l.startswith("DIRECT:")), "")
        assert direct_line == "DIRECT: 2"

    def test_impact_affected_chains_section(self):
        """impact output includes 'AFFECTED CHAINS:' section."""
        result = impact("VISION-001", SCOPE_NODES, SCOPE_EDGES)
        assert "AFFECTED CHAINS:" in result

    def test_impact_total_section(self):
        """impact output includes 'TOTAL:' section."""
        result = impact("EPIC-010", SCOPE_NODES, SCOPE_EDGES)
        assert "TOTAL:" in result

    def test_impact_vision_direct_is_epics(self):
        """impact(VISION-001) direct refs are EPIC-010 and EPIC-011."""
        result = impact("VISION-001", SCOPE_NODES, SCOPE_EDGES)
        assert "EPIC-010" in result
        assert "EPIC-011" in result
        lines = result.split("\n")
        direct_line = next((l for l in lines if l.startswith("DIRECT:")), "")
        assert direct_line == "DIRECT: 2"

    def test_impact_vision_affected_chains_include_specs(self):
        """impact(VISION-001) affected chains includes SPEC-010, SPEC-011, SPEC-012."""
        result = impact("VISION-001", SCOPE_NODES, SCOPE_EDGES)
        assert "SPEC-010" in result
        assert "SPEC-011" in result
        assert "SPEC-012" in result

    def test_impact_total_count_vision(self):
        """impact(VISION-001) TOTAL includes direct + chain artifacts."""
        result = impact("VISION-001", SCOPE_NODES, SCOPE_EDGES)
        lines = result.split("\n")
        total_line = next((l for l in lines if l.startswith("TOTAL:")), "")
        # 2 direct (EPIC-010, EPIC-011) + 3 chain (SPEC-010, SPEC-011, SPEC-012) = 5
        assert total_line == "TOTAL: 5"

    def test_impact_leaf_node_no_direct(self):
        """impact(ADR-010) DIRECT is 1 (SPEC-010 linked-artifact edge to ADR-010)."""
        result = impact("ADR-010", SCOPE_NODES, SCOPE_EDGES)
        lines = result.split("\n")
        direct_line = next((l for l in lines if l.startswith("DIRECT:")), "")
        # SPEC-010 has a linked-artifact edge to ADR-010 → counts as direct
        assert direct_line == "DIRECT: 1"


# ---------------------------------------------------------------------------
# Fixtures for mermaid/status tests
# ---------------------------------------------------------------------------

MERMAID_NODES = {
    "SPEC-001": {"title": "Spec One", "status": "In Progress", "type": "SPEC", "file": "docs/spec/SPEC-001.md", "description": ""},
    "SPEC-002": {"title": 'Spec "Quoted"', "status": "Ready", "type": "SPEC", "file": "docs/spec/SPEC-002.md", "description": ""},
    "EPIC-001": {"title": "Epic One", "status": "Active", "type": "EPIC", "file": "docs/epic/EPIC-001.md", "description": ""},
    "EPIC-002": {"title": "Epic Done", "status": "Complete", "type": "EPIC", "file": "docs/epic/EPIC-002.md", "description": ""},
    "ADR-001": {"title": "ADR Active", "status": "Active", "type": "ADR", "file": "docs/adr/ADR-001.md", "description": ""},
    "SPIKE-001": {"title": "", "status": "In Progress", "type": "SPIKE", "file": "docs/spike/SPIKE-001.md", "description": ""},
}

MERMAID_EDGES = [
    {"from": "SPEC-001", "to": "EPIC-001", "type": "depends-on"},
    {"from": "SPEC-002", "to": "EPIC-001", "type": "parent-epic"},
    {"from": "EPIC-001", "to": "EPIC-002", "type": "depends-on"},
    {"from": "SPEC-001", "to": "SPEC-002", "type": "linked-artifacts"},
    {"from": "SPEC-001", "to": "ADR-001", "type": "validates"},
]


# ---------------------------------------------------------------------------
# TestMermaid
# ---------------------------------------------------------------------------


class TestMermaid:
    """Test mermaid_cmd() — Mermaid graph TD diagram generation."""

    def test_mermaid_starts_with_graph_td(self):
        """mermaid_cmd output starts with 'graph TD'."""
        result = mermaid_cmd(MERMAID_NODES, MERMAID_EDGES)
        assert result.startswith("graph TD")

    def test_mermaid_includes_node_definitions(self):
        """mermaid_cmd includes node definitions for visible nodes."""
        result = mermaid_cmd(MERMAID_NODES, MERMAID_EDGES)
        # SPEC-001 is unresolved — should appear
        assert "SPEC-001" in result

    def test_mermaid_excludes_resolved_nodes_by_default(self):
        """mermaid_cmd excludes resolved nodes by default (show_all=False)."""
        result = mermaid_cmd(MERMAID_NODES, MERMAID_EDGES)
        # EPIC-002 is Complete (resolved), ADR-001 is ADR Active (resolved)
        # They should not appear as node definitions
        lines = result.split("\n")
        node_def_lines = [l for l in lines if "[" in l and "]" in l and "-->" not in l]
        node_ids_defined = []
        for line in node_def_lines:
            # e.g. SPEC-001["Spec One"]
            node_id = line.strip().split("[")[0]
            node_ids_defined.append(node_id)
        assert "EPIC-002" not in node_ids_defined
        assert "ADR-001" not in node_ids_defined

    def test_mermaid_show_all_includes_resolved_nodes(self):
        """mermaid_cmd with show_all=True includes resolved nodes."""
        result = mermaid_cmd(MERMAID_NODES, MERMAID_EDGES, show_all=True)
        assert "EPIC-002" in result
        assert "ADR-001" in result

    def test_mermaid_node_label_uses_title(self):
        """mermaid_cmd node label uses title when available."""
        result = mermaid_cmd(MERMAID_NODES, MERMAID_EDGES)
        assert 'SPEC-001["Spec One"]' in result

    def test_mermaid_node_label_uses_id_when_no_title(self):
        """mermaid_cmd node label uses artifact ID when title is empty."""
        result = mermaid_cmd(MERMAID_NODES, MERMAID_EDGES)
        # SPIKE-001 has empty title
        assert 'SPIKE-001["SPIKE-001"]' in result

    def test_mermaid_escapes_double_quotes_in_title(self):
        """mermaid_cmd escapes double quotes in titles with #quot;."""
        result = mermaid_cmd(MERMAID_NODES, MERMAID_EDGES)
        # SPEC-002 title has double quotes: Spec "Quoted"
        assert '#quot;' in result

    def test_mermaid_includes_depends_on_edges(self):
        """mermaid_cmd includes depends-on edges between visible nodes."""
        result = mermaid_cmd(MERMAID_NODES, MERMAID_EDGES)
        # SPEC-001 --> EPIC-001 (depends-on, both unresolved)
        assert "SPEC-001 --> EPIC-001" in result

    def test_mermaid_includes_parent_epic_edges(self):
        """mermaid_cmd includes parent-epic edges between visible nodes."""
        result = mermaid_cmd(MERMAID_NODES, MERMAID_EDGES)
        # SPEC-002 --> EPIC-001 (parent-epic, both unresolved)
        assert "SPEC-002 --> EPIC-001" in result

    def test_mermaid_excludes_edges_to_resolved_nodes(self):
        """mermaid_cmd excludes edges where either endpoint is resolved (show_all=False)."""
        result = mermaid_cmd(MERMAID_NODES, MERMAID_EDGES)
        # EPIC-001 --> EPIC-002 (depends-on), but EPIC-002 is resolved
        assert "EPIC-001 --> EPIC-002" not in result

    def test_mermaid_excludes_lateral_edges_by_default(self):
        """mermaid_cmd excludes linked-artifacts/validates edges when all_edges=False."""
        result = mermaid_cmd(MERMAID_NODES, MERMAID_EDGES)
        # SPEC-001 --> SPEC-002 (linked-artifacts) should NOT appear
        # Note: we check for edge specifically, not just "SPEC-002" appearing as a node
        lines = result.split("\n")
        edge_lines = [l for l in lines if "-->" in l]
        assert not any("SPEC-001 --> SPEC-002" in l for l in edge_lines)

    def test_mermaid_all_edges_includes_lateral_edges(self):
        """mermaid_cmd with all_edges=True includes linked-artifacts/validates edges."""
        result = mermaid_cmd(MERMAID_NODES, MERMAID_EDGES, all_edges=True)
        lines = result.split("\n")
        edge_lines = [l for l in lines if "-->" in l]
        assert any("SPEC-001 --> SPEC-002" in l for l in edge_lines)

    def test_mermaid_all_edges_excludes_edges_to_resolved_when_show_all_false(self):
        """mermaid_cmd all_edges=True still excludes edges to resolved when show_all=False."""
        result = mermaid_cmd(MERMAID_NODES, MERMAID_EDGES, all_edges=True)
        # SPEC-001 --> ADR-001 (validates), ADR-001 is resolved (ADR Active)
        lines = result.split("\n")
        edge_lines = [l for l in lines if "-->" in l]
        assert not any("ADR-001" in l for l in edge_lines)

    def test_mermaid_all_edges_show_all_includes_edges_to_resolved(self):
        """mermaid_cmd all_edges=True, show_all=True includes edges involving resolved nodes."""
        result = mermaid_cmd(MERMAID_NODES, MERMAID_EDGES, show_all=True, all_edges=True)
        lines = result.split("\n")
        edge_lines = [l for l in lines if "-->" in l]
        assert any("ADR-001" in l for l in edge_lines)

    def test_mermaid_output_is_deterministic(self):
        """mermaid_cmd produces the same output on repeated calls."""
        result1 = mermaid_cmd(MERMAID_NODES, MERMAID_EDGES)
        result2 = mermaid_cmd(MERMAID_NODES, MERMAID_EDGES)
        assert result1 == result2

    def test_mermaid_empty_graph(self):
        """mermaid_cmd on empty graph returns just 'graph TD'."""
        result = mermaid_cmd({}, [])
        assert result.strip() == "graph TD"


# ---------------------------------------------------------------------------
# TestStatus
# ---------------------------------------------------------------------------


class TestStatus:
    """Test status_cmd() — summary table grouped by artifact type."""

    def test_status_groups_by_type(self):
        """status_cmd output groups artifacts by type (SPEC, EPIC, etc.)."""
        result = status_cmd(MERMAID_NODES, MERMAID_EDGES)
        # SPEC section should appear before SPIKE section (alphabetical or by type)
        assert "SPEC" in result
        assert "EPIC" in result

    def test_status_includes_artifact_id(self):
        """status_cmd includes artifact IDs in output."""
        result = status_cmd(MERMAID_NODES, MERMAID_EDGES)
        assert "SPEC-001" in result
        assert "SPEC-002" in result

    def test_status_includes_status_column(self):
        """status_cmd includes status values in output."""
        result = status_cmd(MERMAID_NODES, MERMAID_EDGES)
        assert "In Progress" in result
        assert "Ready" in result

    def test_status_includes_title_column(self):
        """status_cmd includes title values in output."""
        result = status_cmd(MERMAID_NODES, MERMAID_EDGES)
        assert "Spec One" in result

    def test_status_excludes_resolved_by_default(self):
        """status_cmd excludes resolved artifacts by default (show_all=False)."""
        result = status_cmd(MERMAID_NODES, MERMAID_EDGES)
        # EPIC-002 (Complete) and ADR-001 (ADR Active = resolved) should not appear as rows
        lines = result.split("\n")
        data_lines = [l for l in lines if "EPIC-002" in l]
        assert not data_lines, f"EPIC-002 should be excluded but found: {data_lines}"
        adr_lines = [l for l in lines if "ADR-001" in l]
        assert not adr_lines, f"ADR-001 should be excluded but found: {adr_lines}"

    def test_status_show_all_includes_resolved(self):
        """status_cmd with show_all=True includes resolved artifacts."""
        result = status_cmd(MERMAID_NODES, MERMAID_EDGES, show_all=True)
        assert "EPIC-002" in result
        assert "ADR-001" in result

    def test_status_shows_hidden_count_when_resolved_excluded(self):
        """status_cmd indicates how many resolved artifacts were hidden."""
        result = status_cmd(MERMAID_NODES, MERMAID_EDGES)
        # MERMAID_NODES has 2 resolved: EPIC-002 and ADR-001
        assert "hidden" in result.lower() or "resolved" in result.lower()

    def test_status_no_hidden_count_when_show_all(self):
        """status_cmd with show_all=True does not show a hidden count."""
        result = status_cmd(MERMAID_NODES, MERMAID_EDGES, show_all=True)
        assert "hidden" not in result.lower()

    def test_status_sorts_within_group(self):
        """status_cmd sorts artifact IDs within each type group."""
        result = status_cmd(MERMAID_NODES, MERMAID_EDGES, show_all=True)
        lines = result.split("\n")
        # Find SPEC lines
        spec_lines = [l for l in lines if "SPEC-" in l and "-->" not in l]
        spec_ids = []
        for line in spec_lines:
            for part in line.split():
                if part.startswith("SPEC-"):
                    spec_ids.append(part)
                    break
        assert spec_ids == sorted(spec_ids), f"SPEC IDs not sorted: {spec_ids}"

    def test_status_empty_graph_returns_string(self):
        """status_cmd on empty graph returns a string (possibly empty or note)."""
        result = status_cmd({}, [])
        assert isinstance(result, str)

    def test_status_type_headers_present(self):
        """status_cmd output includes type group headers."""
        result = status_cmd(MERMAID_NODES, MERMAID_EDGES)
        # Should have some kind of section header or type label for SPEC
        assert "SPEC" in result


# ---------------------------------------------------------------------------
# TestReady
# ---------------------------------------------------------------------------
#
# Ready state analysis for shared NODES/EDGES fixture:
#   SPEC-001: depends-on SPEC-002 (unresolved) → NOT ready
#   SPEC-002: depends-on EPIC-001 (unresolved) → NOT ready
#   SPEC-003: resolved (Complete) → skip
#   EPIC-001: depends-on EPIC-002 (resolved) and ADR-001 (resolved ADR Active) → READY
#   EPIC-002: resolved (Complete) → skip
#   ADR-001: resolved (standing type + Active) → skip
#   SPIKE-001: no depends-on edges → READY
#
# ready_set = {"EPIC-001", "SPIKE-001"}


class TestReady:
    """Test ready() — unresolved nodes whose all depends-on targets are resolved."""

    def test_ready_returns_nodes_with_all_deps_resolved(self):
        """ready() includes EPIC-001 and SPIKE-001 (all deps resolved or no deps)."""
        result = ready(NODES, EDGES)
        assert "EPIC-001" in result
        assert "SPIKE-001" in result

    def test_ready_excludes_nodes_with_unresolved_deps(self):
        """ready() does NOT include SPEC-001 (depends on unresolved SPEC-002)."""
        result = ready(NODES, EDGES)
        lines = result.strip().split("\n") if result.strip() else []
        ids_in_output = [line.split("  ")[0] for line in lines]
        assert "SPEC-001" not in ids_in_output
        assert "SPEC-002" not in ids_in_output

    def test_ready_excludes_resolved_nodes(self):
        """ready() does NOT include SPEC-003, EPIC-002, or ADR-001 (all resolved)."""
        result = ready(NODES, EDGES)
        lines = result.strip().split("\n") if result.strip() else []
        ids_in_output = [line.split("  ")[0] for line in lines]
        assert "SPEC-003" not in ids_in_output
        assert "EPIC-002" not in ids_in_output
        assert "ADR-001" not in ids_in_output

    def test_ready_output_includes_status_and_title(self):
        """ready() output lines contain status and title for EPIC-001."""
        result = ready(NODES, EDGES)
        epic_line = next((l for l in result.split("\n") if l.startswith("EPIC-001")), None)
        assert epic_line is not None, "EPIC-001 not found in ready output"
        assert "Active" in epic_line
        assert "Epic 1" in epic_line

    def test_ready_output_sorted(self):
        """ready() output is sorted alphabetically — EPIC-001 before SPIKE-001."""
        result = ready(NODES, EDGES)
        lines = [l for l in result.strip().split("\n") if l]
        ids = [line.split("  ")[0] for line in lines]
        assert ids == sorted(ids), f"Output not sorted: {ids}"
        # Specifically EPIC-001 before SPIKE-001
        assert ids.index("EPIC-001") < ids.index("SPIKE-001")

    def test_ready_empty_nodes(self):
        """ready() on empty nodes returns empty string."""
        result = ready({}, [])
        assert result == ""

    def test_ready_no_deps_node_is_ready(self):
        """ready() includes SPIKE-001 which has no depends-on edges."""
        result = ready(NODES, EDGES)
        assert "SPIKE-001" in result

    def test_ready_all_resolved_returns_empty(self):
        """ready() returns empty string when all nodes are resolved."""
        resolved_nodes = {
            "SPEC-003": {"title": "Done", "status": "Complete", "type": "SPEC", "file": "", "description": ""},
            "EPIC-002": {"title": "Done Epic", "status": "Complete", "type": "EPIC", "file": "", "description": ""},
        }
        result = ready(resolved_nodes, [])
        assert result == ""


# ---------------------------------------------------------------------------
# TestNext
# ---------------------------------------------------------------------------
#
# next_cmd analysis for shared NODES/EDGES fixture:
#   READY: EPIC-001, SPIKE-001
#   EPIC-001 would unblock SPEC-002 (SPEC-002 depends only on EPIC-001, which is unresolved)
#   SPIKE-001 would unblock nothing
#   BLOCKED: SPEC-001 (needs SPEC-002), SPEC-002 (needs EPIC-001)


class TestNext:
    """Test next_cmd() — ready set + would-unblock + blocked items."""

    def test_next_ready_section_header(self):
        """next_cmd output contains 'READY:' header."""
        result = next_cmd(NODES, EDGES)
        assert "READY:" in result

    def test_next_blocked_section_header(self):
        """next_cmd output contains 'BLOCKED:' header."""
        result = next_cmd(NODES, EDGES)
        assert "BLOCKED:" in result

    def test_next_ready_items_appear(self):
        """next_cmd READY section lists EPIC-001 and SPIKE-001."""
        result = next_cmd(NODES, EDGES)
        # Find content between READY: and BLOCKED:
        ready_section = result.split("BLOCKED:")[0]
        assert "EPIC-001" in ready_section
        assert "SPIKE-001" in ready_section

    def test_next_would_unblock(self):
        """next_cmd shows EPIC-001 would unblock SPEC-002."""
        result = next_cmd(NODES, EDGES)
        # The would-unblock line should appear after EPIC-001 in the READY section
        lines = result.split("\n")
        epic_idx = next(
            (i for i, l in enumerate(lines) if "EPIC-001" in l and "would unblock" not in l),
            None,
        )
        assert epic_idx is not None, "EPIC-001 not found in output"
        # Look within a few lines for the would-unblock annotation
        context = "\n".join(lines[epic_idx:epic_idx + 3])
        assert "would unblock" in context
        assert "SPEC-002" in context

    def test_next_blocked_items_with_needs(self):
        """next_cmd BLOCKED section shows SPEC-002 needs EPIC-001."""
        result = next_cmd(NODES, EDGES)
        blocked_section = result.split("BLOCKED:")[-1]
        assert "SPEC-002" in blocked_section
        # The needs annotation should appear on SPEC-002's line.
        # Each blocked line starts with "  ARTIFACT-ID  ..." — find the line
        # that starts with SPEC-002 (after stripping leading whitespace).
        spec002_line = next(
            (l for l in blocked_section.split("\n") if l.lstrip().startswith("SPEC-002")),
            None,
        )
        assert spec002_line is not None, "SPEC-002 not found in BLOCKED section"
        assert "needs:" in spec002_line
        assert "EPIC-001" in spec002_line

    def test_next_none_placeholder_empty_case(self):
        """next_cmd shows '(none)' in READY section when all nodes are resolved."""
        resolved_nodes = {
            "SPEC-003": {"title": "Done", "status": "Complete", "type": "SPEC", "file": "", "description": ""},
        }
        result = next_cmd(resolved_nodes, [])
        assert "READY:" in result
        assert "(none)" in result

    def test_next_blocked_none_placeholder(self):
        """next_cmd shows '(none)' in BLOCKED section when nothing is blocked."""
        # Only a ready node with no dependents
        simple_nodes = {
            "SPIKE-001": {"title": "Spike 1", "status": "In Progress", "type": "SPIKE", "file": "", "description": ""},
        }
        result = next_cmd(simple_nodes, [])
        blocked_section = result.split("BLOCKED:")[-1]
        assert "(none)" in blocked_section

    def test_next_spec001_in_blocked(self):
        """next_cmd shows SPEC-001 in BLOCKED section (needs SPEC-002)."""
        result = next_cmd(NODES, EDGES)
        blocked_section = result.split("BLOCKED:")[-1]
        spec001_line = next(
            (l for l in blocked_section.split("\n") if "SPEC-001" in l), None
        )
        assert spec001_line is not None
        assert "needs:" in spec001_line
        assert "SPEC-002" in spec001_line


# ---------------------------------------------------------------------------
# TestOverview
# ---------------------------------------------------------------------------

# Hierarchy fixture: VISION-001 → EPIC-001 → [SPEC-010, SPEC-011(done)]
# SPIKE-010 has no parent edge (unparented root)
HIER_NODES = {
    # Use "In Progress" for VISION so it is not resolved (VISION "Active" = resolved in standing types)
    "VISION-001": {"title": "Product Vision", "status": "In Progress", "type": "VISION", "file": "docs/vision/VISION-001.md", "description": ""},
    "EPIC-001": {"title": "Epic 1", "status": "Active", "type": "EPIC", "file": "docs/epic/EPIC-001.md", "description": ""},
    "SPEC-010": {"title": "Spec 10", "status": "In Progress", "type": "SPEC", "file": "docs/spec/SPEC-010.md", "description": ""},
    "SPEC-011": {"title": "Spec 11 (done)", "status": "Complete", "type": "SPEC", "file": "docs/spec/SPEC-011.md", "description": ""},
    "SPIKE-010": {"title": "Orphan Spike", "status": "In Progress", "type": "SPIKE", "file": "docs/spike/SPIKE-010.md", "description": ""},
}
HIER_EDGES = [
    {"from": "EPIC-001", "to": "VISION-001", "type": "parent-vision"},
    {"from": "SPEC-010", "to": "EPIC-001", "type": "parent-epic"},
    {"from": "SPEC-011", "to": "EPIC-001", "type": "parent-epic"},
]


class TestOverview:
    """Tests for overview() — hierarchy tree view."""

    def test_overview_shows_hierarchy_structure(self):
        """VISION-001 appears as root and EPIC-001 is indented as a child."""
        result = overview(HIER_NODES, HIER_EDGES)
        lines = result.split("\n")
        vision_line = next((l for l in lines if "VISION-001" in l), None)
        epic_line = next((l for l in lines if "EPIC-001" in l), None)
        assert vision_line is not None, "VISION-001 should appear in output"
        assert epic_line is not None, "EPIC-001 should appear in output"
        # EPIC-001 line must come after VISION-001 line
        assert lines.index(epic_line) > lines.index(vision_line)
        # EPIC-001 should be indented (start with whitespace or tree chars)
        assert epic_line[0] in (" ", "\u251c", "\u2514", "\u2502"), (
            f"EPIC-001 line should be indented, got: {repr(epic_line)}"
        )

    def test_overview_hides_resolved_by_default(self):
        """SPEC-011 (Complete) is NOT in output without show_all."""
        result = overview(HIER_NODES, HIER_EDGES, show_all=False)
        assert "SPEC-011" not in result

    def test_overview_shows_resolved_with_all(self):
        """SPEC-011 appears in output with show_all=True."""
        result = overview(HIER_NODES, HIER_EDGES, show_all=True)
        assert "SPEC-011" in result

    def test_overview_unparented_section(self):
        """Artifacts whose parent is resolved/hidden appear in '=== Unparented ===' section.

        SPIKE-010 has a parent-epic edge to EPIC-001, but EPIC-001 is Complete (resolved).
        With show_all=False, EPIC-001 is hidden, so SPIKE-010 appears in Unparented.
        """
        # Build a scenario: SPIKE-010 has a parent that is resolved (Complete)
        resolved_parent_nodes = {
            "EPIC-RESOLVED": {"title": "Done Epic", "status": "Complete", "type": "EPIC", "file": "docs/epic/EPIC-RESOLVED.md", "description": ""},
            "SPEC-010": {"title": "Spec 10", "status": "In Progress", "type": "SPEC", "file": "docs/spec/SPEC-010.md", "description": ""},
        }
        resolved_parent_edges = [
            {"from": "SPEC-010", "to": "EPIC-RESOLVED", "type": "parent-epic"},
        ]
        result = overview(resolved_parent_nodes, resolved_parent_edges, show_all=False)
        assert "=== Unparented ===" in result, f"Expected Unparented section, got:\n{result}"
        unparented_section = result.split("=== Unparented ===")[-1]
        assert "SPEC-010" in unparented_section

    def test_overview_summary_section(self):
        """Output contains '=== Summary ===' with Ready/Blocked/Total counts."""
        result = overview(HIER_NODES, HIER_EDGES)
        assert "=== Summary ===" in result
        summary_section = result.split("=== Summary ===")[-1]
        assert "Ready:" in summary_section
        assert "Blocked:" in summary_section
        assert "Total unresolved:" in summary_section

    def test_overview_status_icons(self):
        """Ready artifacts use the right-arrow icon; no blocked icon used when no deps."""
        # SPEC-010 has no depends-on edges → should be ready (→)
        # SPEC-011 is resolved (only shown with show_all)
        result = overview(HIER_NODES, HIER_EDGES)
        spec010_line = next((l for l in result.split("\n") if "SPEC-010" in l), None)
        assert spec010_line is not None, "SPEC-010 should be in output"
        # The ready icon → should appear
        assert "\u2192" in spec010_line, f"Expected → in SPEC-010 line: {repr(spec010_line)}"

    def test_overview_blocked_shows_deps(self):
        """Blocked artifacts show '[blocked by: ...]' in their line."""
        # Add a depends-on edge so SPEC-010 is blocked by EPIC-001
        extra_edges = list(HIER_EDGES) + [
            {"from": "SPEC-010", "to": "EPIC-001", "type": "depends-on"},
        ]
        result = overview(HIER_NODES, extra_edges)
        spec010_line = next((l for l in result.split("\n") if "SPEC-010" in l), None)
        assert spec010_line is not None, "SPEC-010 should be in output"
        assert "[blocked by:" in spec010_line, (
            f"Expected '[blocked by:' in SPEC-010 line: {repr(spec010_line)}"
        )
        assert "EPIC-001" in spec010_line

    def test_overview_empty_nodes(self):
        """overview() with empty nodes returns minimal output (just summary)."""
        result = overview({}, [])
        assert "=== Summary ===" in result
        assert "Ready: 0" in result
        assert "Blocked: 0" in result
        assert "Total unresolved: 0" in result

    def test_overview_cross_cutting_section(self):
        """Cross-cutting section appears when lateral edges connect visible artifacts."""
        extra_edges = list(HIER_EDGES) + [
            {"from": "SPEC-010", "to": "SPIKE-010", "type": "linked-artifact"},
        ]
        result = overview(HIER_NODES, extra_edges)
        assert "=== Cross-cutting ===" in result
        cross_section = result.split("=== Cross-cutting ===")[-1]
        assert "SPEC-010" in cross_section
        assert "SPIKE-010" in cross_section

    def test_overview_tk_section_present(self):
        """Output always contains '=== Execution Tracking (tk ready) ===' section."""
        result = overview(HIER_NODES, HIER_EDGES)
        assert "=== Execution Tracking (tk ready) ===" in result
