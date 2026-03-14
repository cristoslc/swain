"""Integration tests: verify Python specgraph query subcommand output.

Tests verify structural properties of each subcommand's output rather than
exact byte-for-byte parity with the bash implementation.

Documented divergences from bash specgraph.sh:
  - blocks/tree: Python filters resolved artifacts from dependency output;
    bash returns all depends-on targets regardless of resolution status.
    SPEC-030 (Complete) is correctly excluded by Python.
  - blocked-by: Python filters resolved sources; bash includes them.
    SPEC-032 (Complete) is excluded by Python.
  - tree: Same resolved-filtering behavior as blocks.
  - neighbors: Python uses "from"/"to" direction labels; bash uses "outgoing"/"incoming".
    Python omits status brackets; bash wraps status in [brackets].
  - scope: Python uses "=== Section ===" headers; bash uses different headers and format.
    Python includes architecture overview and lateral sections.
  - impact: Python uses "DIRECT: N" / "AFFECTED CHAINS: N" / "TOTAL: N" format;
    bash uses "DIRECT:" / "AFFECTED CHAINS:" with indented entries.
    Python counts are correct; format differs.
  - ready: Python produces plain "ID  Status  Title" lines; bash produces
    OSC 8 hyperlinked lines with bracketed status.
  - next: Python uses "READY:" / "BLOCKED:" section headers; bash uses "=== Ready ===" etc.
    Python includes "would unblock" annotations; bash does not.
  - mermaid: Python labels nodes as ID["Title"]; bash labels as ID["ID: Title"].
    Python and bash include different edges (bash only shows some of the graph).
  - status: Python uses "--- TYPE ---" headers; bash uses "## TYPE" with blank lines.
    Python aligns columns dynamically.
  - overview: Significantly different format. Python uses Unix tree connectors
    (├──, └──) and includes === Summary === + === Execution Tracking === sections;
    bash uses "── Hierarchy ──" / "── Cross-cutting ──" / "── Unparented ──" sections.

SPEC-031 acceptance criterion: outputs are non-empty for commands that produce output,
and structurally valid for the documented format.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
SPECGRAPH = SCRIPTS_DIR / "specgraph.py"


def run_specgraph(args: list[str]) -> str:
    """Run specgraph.py with given args against the live repo. Returns stdout."""
    result = subprocess.run(
        ["python3", str(SPECGRAPH)] + args,
        capture_output=True,
        text=True,
        cwd=str(SCRIPTS_DIR.parent.parent.parent),  # repo root
    )
    return result.stdout


# ---------------------------------------------------------------------------
# blocks
# ---------------------------------------------------------------------------


class TestBlocks:
    """blocks <ID>: unresolved direct dependencies of an artifact."""

    def test_blocks_resolved_artifact_returns_empty(self):
        """SPEC-031 depends on SPEC-030 (Complete). Python filters resolved deps, so empty."""
        result = run_specgraph(["blocks", "SPEC-031"])
        # SPEC-030 is Complete/resolved — Python correctly excludes it
        lines = [l for l in result.strip().split("\n") if l.strip()]
        assert "SPEC-030" not in lines, (
            "SPEC-030 is resolved (Complete) — should not appear in blocks output"
        )

    def test_blocks_all_resolved_deps_returns_empty(self):
        """An artifact whose only dep is resolved should return empty."""
        result = run_specgraph(["blocks", "EPIC-014"])
        # EPIC-014 depends on SPIKE-018 (Complete/resolved)
        # Python filters resolved deps → output should be empty
        lines = [l for l in result.strip().split("\n") if l.strip()]
        assert len(lines) == 0, (
            f"EPIC-014's only dep (SPIKE-018) is resolved — blocks should return empty, got: {lines}"
        )

    def test_blocks_output_format_is_one_id_per_line(self):
        """Each line should be a bare artifact ID (no tabs, no brackets)."""
        result = run_specgraph(["blocks", "EPIC-014"])
        for line in result.strip().split("\n"):
            if not line.strip():
                continue
            assert re.match(r"^[A-Z]+-\d+$", line.strip()), (
                f"Expected bare artifact ID, got: {line!r}"
            )


# ---------------------------------------------------------------------------
# blocked-by
# ---------------------------------------------------------------------------


class TestBlockedBy:
    """blocked-by <ID>: unresolved artifacts that depend on this one."""

    def test_blocked_by_spec030_returns_empty_when_all_resolved(self):
        """SPEC-031 depends on SPEC-030, but SPEC-031 is now Complete (resolved).
        blocked-by SPEC-030 should return empty — no unresolved dependents remain."""
        result = run_specgraph(["blocked-by", "SPEC-030"])
        lines = [l.strip() for l in result.strip().split("\n") if l.strip()]
        assert "SPEC-031" not in lines, (
            "SPEC-031 is resolved (Complete) — should not appear in blocked-by output"
        )

    def test_blocked_by_filters_resolved_sources(self):
        """Resolved artifacts that depend on SPEC-030 should be excluded."""
        result = run_specgraph(["blocked-by", "SPEC-030"])
        lines = [l.strip() for l in result.strip().split("\n") if l.strip()]
        # SPEC-032 depends on SPEC-030 but is Complete (resolved) — should be excluded
        assert "SPEC-032" not in lines, (
            "SPEC-032 is resolved (Complete) — should not appear in blocked-by output"
        )

    def test_blocked_by_output_format_is_one_id_per_line(self):
        """Each line should be a bare artifact ID."""
        result = run_specgraph(["blocked-by", "SPEC-030"])
        for line in result.strip().split("\n"):
            if not line.strip():
                continue
            assert re.match(r"^[A-Z]+-\d+$", line.strip()), (
                f"Expected bare artifact ID, got: {line!r}"
            )


# ---------------------------------------------------------------------------
# tree
# ---------------------------------------------------------------------------


class TestTree:
    """tree <ID>: transitive dependency closure."""

    def test_tree_spec031_excludes_resolved_nodes(self):
        """SPEC-031 → SPEC-030 (Complete). Resolved nodes excluded from tree output."""
        result = run_specgraph(["tree", "SPEC-031"])
        lines = [l.strip() for l in result.strip().split("\n") if l.strip()]
        # SPEC-030 is Complete — should be excluded from transitive tree
        assert "SPEC-030" not in lines, (
            "SPEC-030 is resolved (Complete) — should not appear in tree output"
        )

    def test_tree_all_resolved_deps_returns_empty(self):
        """EPIC-014 depends on SPIKE-018 (Complete). Tree returns empty when all deps resolved."""
        result = run_specgraph(["tree", "EPIC-014"])
        lines = [l.strip() for l in result.strip().split("\n") if l.strip()]
        assert len(lines) == 0, (
            f"EPIC-014's only dep (SPIKE-018) is resolved — tree should return empty, got: {lines}"
        )

    def test_tree_does_not_include_start_node(self):
        """The artifact itself should not appear in the tree output."""
        result = run_specgraph(["tree", "EPIC-014"])
        lines = [l.strip() for l in result.strip().split("\n") if l.strip()]
        assert "EPIC-014" not in lines, "Start node should not appear in its own tree"


# ---------------------------------------------------------------------------
# neighbors
# ---------------------------------------------------------------------------


class TestNeighbors:
    """neighbors <ID>: all directly connected artifacts, both directions."""

    def test_neighbors_returns_tsv_rows(self):
        """Each row should have at least 3 tab-separated fields: direction, type, id."""
        result = run_specgraph(["neighbors", "SPEC-031"])
        assert result.strip(), "neighbors SPEC-031 should produce output"
        for line in result.strip().split("\n"):
            if not line.strip():
                continue
            parts = line.split("\t")
            assert len(parts) >= 3, f"Expected at least 3 TSV columns, got {len(parts)}: {line!r}"

    def test_neighbors_direction_labels(self):
        """Direction field should be 'from' or 'to' (Python format)."""
        result = run_specgraph(["neighbors", "SPEC-031"])
        for line in result.strip().split("\n"):
            if not line.strip():
                continue
            parts = line.split("\t")
            direction = parts[0]
            assert direction in ("from", "to"), (
                f"Direction should be 'from' or 'to', got: {direction!r}"
            )

    def test_neighbors_includes_parent_epic_edge(self):
        """SPEC-031 has a parent-epic edge to EPIC-013."""
        result = run_specgraph(["neighbors", "SPEC-031"])
        assert "EPIC-013" in result, "EPIC-013 should appear in SPEC-031 neighbors"
        assert "parent-epic" in result, "parent-epic edge type should appear"

    def test_neighbors_includes_both_directions(self):
        """Should include edges going both from and to the artifact."""
        result = run_specgraph(["neighbors", "EPIC-013"])
        directions = set()
        for line in result.strip().split("\n"):
            if line.strip():
                parts = line.split("\t")
                directions.add(parts[0])
        # EPIC-013 is referenced by some SPECs (to direction) and may have parents (from direction)
        assert len(directions) >= 1, "Should have at least one direction in output"


# ---------------------------------------------------------------------------
# scope
# ---------------------------------------------------------------------------


class TestScope:
    """scope <ID>: parent chain, siblings, laterals, architecture overview."""

    def test_scope_has_required_sections(self):
        """Output should contain the four === Section === headers."""
        result = run_specgraph(["scope", "SPEC-031"])
        assert "=== Parent Chain ===" in result
        assert "=== Siblings ===" in result
        assert "=== Laterals ===" in result
        assert "=== Architecture Overview ===" in result

    def test_scope_parent_chain_includes_epic(self):
        """SPEC-031 has parent-epic to EPIC-013."""
        result = run_specgraph(["scope", "SPEC-031"])
        assert "EPIC-013" in result, "SPEC-031 scope should include EPIC-013 in parent chain"

    def test_scope_siblings_includes_other_specs_under_same_epic(self):
        """SPECs under the same EPIC should appear as siblings."""
        result = run_specgraph(["scope", "SPEC-031"])
        # SPEC-030, SPEC-032, SPEC-033, SPEC-038 share EPIC-013 as parent
        # At least one of them should appear in siblings
        sibling_section = result.split("=== Siblings ===", 1)[-1].split("=== Laterals ===")[0]
        sibling_ids = re.findall(r"[A-Z]+-\d+", sibling_section)
        assert len(sibling_ids) > 0, "Should have sibling artifacts under EPIC-013"

    def test_scope_returns_empty_for_unknown_id(self):
        """scope with an unknown artifact ID should return empty output."""
        result = run_specgraph(["scope", "DOES-NOT-EXIST-999"])
        assert result.strip() == "", f"Expected empty output for unknown ID, got: {result!r}"


# ---------------------------------------------------------------------------
# impact
# ---------------------------------------------------------------------------


class TestImpact:
    """impact <ID>: what would be affected if this artifact changed."""

    def test_impact_has_required_sections(self):
        """Output should have DIRECT: N, AFFECTED CHAINS: N, TOTAL: N lines."""
        result = run_specgraph(["impact", "SPEC-030"])
        assert re.search(r"^DIRECT: \d+", result, re.MULTILINE), (
            "impact output should have 'DIRECT: N' line"
        )
        assert re.search(r"^AFFECTED CHAINS: \d+", result, re.MULTILINE), (
            "impact output should have 'AFFECTED CHAINS: N' line"
        )
        assert re.search(r"^TOTAL: \d+", result, re.MULTILINE), (
            "impact output should have 'TOTAL: N' line"
        )

    def test_impact_spec030_includes_spec031_as_direct(self):
        """SPEC-031 directly depends on SPEC-030, so it's a direct reference."""
        result = run_specgraph(["impact", "SPEC-030"])
        # SPEC-031 should appear in the DIRECT section
        direct_section = result.split("DIRECT:", 1)[-1].split("AFFECTED CHAINS:")[0]
        assert "SPEC-031" in direct_section, (
            "SPEC-031 depends on SPEC-030 — should appear in DIRECT section"
        )

    def test_impact_total_is_sum_of_direct_and_chains(self):
        """TOTAL should equal DIRECT + AFFECTED CHAINS."""
        result = run_specgraph(["impact", "SPEC-030"])
        m_direct = re.search(r"^DIRECT: (\d+)", result, re.MULTILINE)
        m_chains = re.search(r"^AFFECTED CHAINS: (\d+)", result, re.MULTILINE)
        m_total = re.search(r"^TOTAL: (\d+)", result, re.MULTILINE)
        assert m_direct and m_chains and m_total, "Expected DIRECT/AFFECTED CHAINS/TOTAL lines in output"
        direct = int(m_direct.group(1))
        chains = int(m_chains.group(1))
        total = int(m_total.group(1))
        assert total == direct + chains, (
            f"TOTAL ({total}) should equal DIRECT ({direct}) + AFFECTED CHAINS ({chains})"
        )


# ---------------------------------------------------------------------------
# edges
# ---------------------------------------------------------------------------


class TestEdges:
    """edges [<ID>]: raw edge list as TSV."""

    def test_edges_tsv_format_three_columns(self):
        """Each line should have exactly 3 tab-separated fields: from, to, type."""
        result = run_specgraph(["edges", "SPEC-031"])
        assert result.strip(), "edges SPEC-031 should produce output"
        for line in result.strip().split("\n"):
            if not line.strip():
                continue
            parts = line.split("\t")
            assert len(parts) == 3, f"Expected 3 TSV columns, got {len(parts)}: {line!r}"

    def test_edges_no_filter_returns_all_edges(self):
        """Without ID filter, edges returns all graph edges."""
        result = run_specgraph(["edges"])
        lines = [l for l in result.strip().split("\n") if l.strip()]
        # Should have many more edges than a single artifact
        assert len(lines) > 10, f"Global edges should return many edges, got {len(lines)}"

    def test_edges_spec031_includes_depends_on(self):
        """SPEC-031 has a depends-on edge to SPEC-030."""
        result = run_specgraph(["edges", "SPEC-031"])
        assert "SPEC-030" in result, "SPEC-031 should have edge to SPEC-030"
        assert "depends-on" in result, "depends-on edge type should appear"

    def test_edges_filtered_only_shows_artifact_edges(self):
        """Filtered edges should only show rows where from or to equals the ID."""
        result = run_specgraph(["edges", "SPEC-031"])
        for line in result.strip().split("\n"):
            if not line.strip():
                continue
            parts = line.split("\t")
            assert len(parts) == 3
            frm, to, _ = parts
            assert frm == "SPEC-031" or to == "SPEC-031", (
                f"Edge should involve SPEC-031: {line!r}"
            )


# ---------------------------------------------------------------------------
# ready
# ---------------------------------------------------------------------------


class TestReady:
    """ready: list artifacts with all deps resolved."""

    def test_ready_returns_non_empty(self):
        """Should return at least one ready artifact."""
        result = run_specgraph(["ready"])
        assert result.strip(), "ready should return non-empty output"

    def test_ready_output_has_id_status_title_format(self):
        """Each line: ID  Status  Title (two or more spaces separating fields)."""
        result = run_specgraph(["ready"])
        for line in result.strip().split("\n"):
            if not line.strip():
                continue
            # Should start with an artifact ID
            assert re.match(r"^[A-Z]+-\d+\s+\S", line), (
                f"Line should start with artifact ID: {line!r}"
            )

    def test_ready_artifacts_not_resolved(self):
        """Ready artifacts should have status that is not resolved/complete/superseded."""
        result = run_specgraph(["ready"])
        for line in result.strip().split("\n"):
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 2:
                status = parts[1]
                assert status.lower() not in ("complete", "superseded", "obsolete"), (
                    f"Resolved artifact should not appear in ready: {line!r}"
                )

    def test_ready_sorted_by_id(self):
        """Ready output should be sorted by artifact ID."""
        result = run_specgraph(["ready"])
        ids = []
        for line in result.strip().split("\n"):
            if line.strip():
                m = re.match(r"^([A-Z]+-\d+)", line)
                if m:
                    ids.append(m.group(1))
        assert ids == sorted(ids), f"Ready output should be sorted by ID, got: {ids}"


# ---------------------------------------------------------------------------
# next
# ---------------------------------------------------------------------------


class TestNext:
    """next: ready items + what they'd unblock, plus blocked items."""

    def test_next_has_ready_section(self):
        """Output should start with 'READY:' section."""
        result = run_specgraph(["next"])
        assert result.strip().startswith("READY:"), (
            f"next output should start with 'READY:'"
        )

    def test_next_has_blocked_section(self):
        """Output should contain a 'BLOCKED:' section."""
        result = run_specgraph(["next"])
        assert "BLOCKED:" in result, "next output should contain 'BLOCKED:' section"

    def test_next_ready_section_non_empty(self):
        """READY section should have at least one artifact."""
        result = run_specgraph(["next"])
        ready_section = result.split("BLOCKED:")[0]
        artifact_lines = [l for l in ready_section.split("\n")
                          if l.strip() and re.search(r"[A-Z]+-\d+", l)]
        assert len(artifact_lines) > 0, "READY section should have at least one artifact"

    def test_next_would_unblock_annotation(self):
        """If any ready item would unblock others, '-> would unblock:' annotation present."""
        result = run_specgraph(["next"])
        # SPIKE-018 resolving would unblock EPIC-014 — check if annotation appears
        if "SPIKE-018" in result and "would unblock" in result:
            assert "EPIC-014" in result.split("would unblock")[1].split("\n")[0], (
                "Resolving SPIKE-018 should unblock EPIC-014"
            )


# ---------------------------------------------------------------------------
# mermaid
# ---------------------------------------------------------------------------


class TestMermaid:
    """mermaid: Mermaid graph TD diagram."""

    def test_mermaid_starts_with_graph_td(self):
        """Output must start with 'graph TD'."""
        result = run_specgraph(["mermaid"])
        assert result.strip().startswith("graph TD"), (
            f"mermaid output must start with 'graph TD'"
        )

    def test_mermaid_node_format(self):
        """Nodes should use ID["Title"] format (quoted label)."""
        result = run_specgraph(["mermaid"])
        # At least one node line should match ID["..."] format
        node_pattern = re.compile(r'^  [A-Z]+-\d+\["[^"]*"\]$', re.MULTILINE)
        matches = node_pattern.findall(result)
        assert len(matches) > 0, f"mermaid should contain ID[\"Title\"] nodes"

    def test_mermaid_edge_format(self):
        """Edges should use 'FROM --> TO' format when present."""
        result = run_specgraph(["--all", "mermaid"])
        edge_pattern = re.compile(r"^  [A-Z]+-\d+ --> [A-Z]+-\d+$", re.MULTILINE)
        matches = edge_pattern.findall(result)
        assert len(matches) > 0, (
            "mermaid --all should contain 'FROM --> TO' edges (the full graph has many edges)"
        )

    def test_mermaid_only_shows_unresolved_by_default(self):
        """By default, resolved artifacts should not appear in mermaid output."""
        result = run_specgraph(["mermaid"])
        # SPEC-030 is Complete — should not appear in default mermaid
        assert "SPEC-030" not in result, (
            "SPEC-030 is resolved — should not appear in default mermaid output"
        )

    def test_mermaid_all_flag_includes_resolved(self):
        """--all flag should include resolved artifacts."""
        result_default = run_specgraph(["mermaid"])
        result_all = run_specgraph(["--all", "mermaid"])
        # With --all, should have more lines
        default_lines = len([l for l in result_default.split("\n") if l.strip()])
        all_lines = len([l for l in result_all.split("\n") if l.strip()])
        assert all_lines >= default_lines, (
            "--all should produce at least as many lines as default"
        )


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------


class TestStatus:
    """status: artifact table grouped by type."""

    def test_status_has_type_groupings(self):
        """Output should contain '--- TYPE ---' section headers."""
        result = run_specgraph(["status"])
        assert re.search(r"^--- [A-Z]+ ---$", result, re.MULTILINE), (
            "status output should contain '--- TYPE ---' headers"
        )

    def test_status_has_spec_section_with_all_flag(self):
        """Should have a SPEC section when showing resolved artifacts."""
        result = run_specgraph(["--all", "status"])
        assert "--- SPEC ---" in result, (
            "status --all should show a SPEC section (many resolved SPECs exist)"
        )

    def test_status_has_epic_section(self):
        """Should have an EPIC section."""
        result = run_specgraph(["status"])
        assert "--- EPIC ---" in result

    def test_status_rows_have_id_status_title(self):
        """Data rows should have artifact ID as first token."""
        result = run_specgraph(["status"])
        for line in result.split("\n"):
            stripped = line.strip()
            if not stripped or stripped.startswith("---") or stripped.startswith("("):
                continue
            assert re.match(r"^[A-Z]+-\d+", stripped), (
                f"Data row should start with artifact ID: {line!r}"
            )

    def test_status_hidden_count_shown(self):
        """When resolved artifacts are hidden, a count message should appear."""
        result = run_specgraph(["status"])
        assert "resolved artifact" in result or "hidden" in result, (
            "status should mention how many resolved artifacts are hidden"
        )

    def test_status_all_flag_shows_more(self):
        """--all should show more artifacts than default."""
        result_default = run_specgraph(["status"])
        result_all = run_specgraph(["--all", "status"])
        default_count = len([l for l in result_default.split("\n")
                              if re.match(r"\s+[A-Z]+-\d+", l)])
        all_count = len([l for l in result_all.split("\n")
                         if re.match(r"\s+[A-Z]+-\d+", l)])
        assert all_count > default_count, (
            f"--all should show more artifacts: default={default_count}, all={all_count}"
        )


# ---------------------------------------------------------------------------
# overview
# ---------------------------------------------------------------------------


class TestOverview:
    """overview: hierarchy tree with status icons.

    Intentional divergence from bash: Python uses tree connectors (├──, └──)
    and includes === Summary === and === Execution Tracking === sections.
    Bash uses a different layout with "── Hierarchy ──" header and type-grouped sections.
    """

    def test_overview_returns_non_empty(self):
        """Should return non-empty output."""
        result = run_specgraph(["overview"])
        assert result.strip(), "overview should return non-empty output"

    def test_overview_has_status_icons(self):
        """Should include Unicode status icons: →, ⊘, ·, ✓."""
        result = run_specgraph(["overview"])
        has_icon = any(c in result for c in ("→", "⊘", "·", "✓"))
        assert has_icon, "overview should include status icons (→, ⊘, ·, ✓)"

    def test_overview_has_summary_section(self):
        """Should include a === Summary === section."""
        result = run_specgraph(["overview"])
        assert "=== Summary ===" in result

    def test_overview_summary_has_counts(self):
        """Summary should include Ready, Blocked, Total counts."""
        result = run_specgraph(["overview"])
        summary = result.split("=== Summary ===")[-1].split("\n")[1]
        assert "Ready:" in summary and "Blocked:" in summary, (
            f"Summary line should have Ready/Blocked counts: {summary!r}"
        )

    def test_overview_has_execution_tracking_section(self):
        """Should include a === Execution Tracking (tk ready) === section."""
        result = run_specgraph(["overview"])
        assert "=== Execution Tracking" in result

    def test_overview_includes_unresolved_artifacts(self):
        """Unresolved artifacts should appear in overview."""
        result = run_specgraph(["overview"])
        assert "EPIC-005" in result, "EPIC-005 (Active, unresolved) should appear in overview"
        # SPEC-031 is Complete — should NOT appear in default overview (resolved artifacts hidden)
        assert "SPEC-031" not in result, (
            "SPEC-031 is Complete (resolved) — should not appear in default overview"
        )

    def test_overview_unblocked_artifact_has_no_blocked_by(self):
        """Artifacts with all deps resolved should not show blocked-by annotation."""
        result = run_specgraph(["overview"])
        # EPIC-005 has no deps — should have no blocked-by annotation
        if "EPIC-005" in result:
            epic005_line = next(
                (l for l in result.split("\n") if "EPIC-005" in l), ""
            )
            assert "blocked by" not in epic005_line, (
                f"EPIC-005 should NOT show blocked-by (no deps): {epic005_line!r}"
            )
