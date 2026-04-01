"""Tests for specgraph body cross-reference scanner."""

import argparse
import io
import sys
import unittest.mock
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from specgraph.xref import collect_frontmatter_ids, compute_discrepancies, compute_xref, scan_body, check_reciprocal_edges


class TestScanBodyBasic:
    """Test basic artifact ID extraction from body text."""

    def test_extracts_known_ids(self):
        """Body containing known artifact IDs returns those IDs."""
        body = "EPIC-005 depends on SPIKE-007 for its implementation."
        known = {"EPIC-005", "SPIKE-007", "SPEC-010"}
        result = scan_body(body, known, self_id="SPEC-001")
        assert result == {"EPIC-005", "SPIKE-007"}

    def test_empty_body_returns_empty_set(self):
        """Empty body text yields no cross-references."""
        result = scan_body("", known_ids={"SPEC-001", "EPIC-005"}, self_id="SPEC-010")
        assert result == set()

    def test_body_with_no_artifact_patterns_returns_empty_set(self):
        """Body with no TYPE-NNN patterns yields no cross-references."""
        body = "This is plain prose with no artifact identifiers whatsoever."
        result = scan_body(body, known_ids={"SPEC-001", "EPIC-005"}, self_id="SPEC-010")
        assert result == set()


class TestScanBodySelfExclusion:
    """Test that self_id is excluded from results."""

    def test_self_id_excluded(self):
        """The artifact's own ID mentioned in its body is not returned."""
        body = "SPEC-010 references EPIC-005 here."
        known = {"SPEC-010", "EPIC-005"}
        result = scan_body(body, known, self_id="SPEC-010")
        assert "SPEC-010" not in result
        assert "EPIC-005" in result


class TestScanBodyNonArtifactFiltering:
    """Test that non-artifact TYPE-NNN patterns are filtered out."""

    def test_technical_codes_excluded(self):
        """Patterns like UTF-8, SHA-256, HTTP-302 are not in known_ids so are excluded."""
        body = "Encoding is UTF-8, hash is SHA-256, response code HTTP-302."
        known = {"SPEC-001", "EPIC-005"}
        result = scan_body(body, known, self_id="SPEC-001")
        assert result == set()

    def test_unknown_id_filtered(self):
        """An artifact-style ID not present in known_ids is excluded."""
        body = "See SPEC-999 for details."
        known = {"SPEC-001", "EPIC-005"}
        result = scan_body(body, known, self_id="SPEC-001")
        assert "SPEC-999" not in result
        assert result == set()


class TestScanBodyCodeBlocks:
    """Test that IDs inside code spans are still detected (text-level scan)."""

    def test_id_in_backtick_code_span_detected(self):
        """Body scan is text-level; IDs inside backticks are still found."""
        body = "See `SPEC-010` for the interface definition."
        known = {"SPEC-010", "EPIC-005"}
        result = scan_body(body, known, self_id="SPEC-001")
        assert "SPEC-010" in result


class TestScanBodyDeduplication:
    """Test that repeated IDs appear only once in the result."""

    def test_duplicate_ids_deduplicated(self):
        """Same ID mentioned three times appears once in the result set."""
        body = "EPIC-005 is key. See also EPIC-005 and EPIC-005 again."
        known = {"EPIC-005", "SPEC-001"}
        result = scan_body(body, known, self_id="SPEC-001")
        assert result == {"EPIC-005"}


class TestScanBodyMixed:
    """Integration-style tests mixing multiple scenarios."""

    def test_mixed_known_unknown_self(self):
        """Known IDs extracted, unknown filtered, self excluded."""
        body = (
            "This spec (SPEC-010) implements EPIC-005 and references SPEC-999. "
            "The encoding is UTF-8 and the spike is SPIKE-007."
        )
        known = {"SPEC-010", "EPIC-005", "SPIKE-007"}
        result = scan_body(body, known, self_id="SPEC-010")
        assert result == {"EPIC-005", "SPIKE-007"}
        assert "SPEC-010" not in result
        assert "SPEC-999" not in result


class TestCollectFrontmatterIdsListFields:
    """Test extraction from list-type frontmatter fields."""

    def test_depends_on_artifacts(self):
        """IDs in depends-on-artifacts list are returned."""
        fm = {"depends-on-artifacts": ["SPEC-010", "SPIKE-007"]}
        assert collect_frontmatter_ids(fm) == {"SPEC-010", "SPIKE-007"}

    def test_linked_artifacts(self):
        """IDs in linked-artifacts list are returned."""
        fm = {"linked-artifacts": ["EPIC-003", "SPEC-011"]}
        assert collect_frontmatter_ids(fm) == {"EPIC-003", "SPEC-011"}

    def test_validates(self):
        """IDs in validates list are returned."""
        fm = {"validates": ["SPEC-020", "SPEC-021"]}
        assert collect_frontmatter_ids(fm) == {"SPEC-020", "SPEC-021"}


class TestCollectFrontmatterIdsAddresses:
    """Test extraction from the addresses field, including sub-path stripping."""

    def test_addresses_strips_sub_path(self):
        """Items in addresses with dot sub-path return only the base ID."""
        fm = {"addresses": ["JOURNEY-001.PP-03", "JOURNEY-002.O-01"]}
        assert collect_frontmatter_ids(fm) == {"JOURNEY-001", "JOURNEY-002"}

    def test_addresses_plain_id(self):
        """Items in addresses without sub-path are returned as-is."""
        fm = {"addresses": ["JOURNEY-003"]}
        assert collect_frontmatter_ids(fm) == {"JOURNEY-003"}


class TestCollectFrontmatterIdsScalarFields:
    """Test extraction from scalar (string) frontmatter fields."""

    def test_parent_epic(self):
        """parent-epic scalar string is returned as a single-element set."""
        fm = {"parent-epic": "EPIC-005"}
        assert collect_frontmatter_ids(fm) == {"EPIC-005"}

    def test_parent_vision(self):
        """parent-vision scalar string is returned."""
        fm = {"parent-vision": "VISION-001"}
        assert collect_frontmatter_ids(fm) == {"VISION-001"}

    def test_superseded_by(self):
        """superseded-by scalar string is returned."""
        fm = {"superseded-by": "SPEC-030"}
        assert collect_frontmatter_ids(fm) == {"SPEC-030"}


class TestCollectFrontmatterIdsExcludedFields:
    """Test that non-artifact fields are ignored."""

    def test_source_issue_excluded(self):
        """source-issue value is not returned."""
        fm = {"source-issue": "github:foo#12"}
        assert collect_frontmatter_ids(fm) == set()

    def test_evidence_pool_excluded(self):
        """evidence-pool value is not returned."""
        fm = {"evidence-pool": "ep-001"}
        assert collect_frontmatter_ids(fm) == set()

    def test_both_excluded_fields_together(self):
        """Both excluded fields together yield an empty set."""
        fm = {"source-issue": "github:foo#12", "evidence-pool": "ep-001"}
        assert collect_frontmatter_ids(fm) == set()


class TestCollectFrontmatterIdsEdgeCases:
    """Test empty, null, and missing values."""

    def test_empty_scalar_skipped(self):
        """Empty string scalar yields no ID."""
        fm = {"parent-epic": ""}
        assert collect_frontmatter_ids(fm) == set()

    def test_empty_list_skipped(self):
        """Empty list yields no IDs."""
        fm = {"depends-on-artifacts": []}
        assert collect_frontmatter_ids(fm) == set()

    def test_null_scalar_skipped(self):
        """None scalar yields no ID."""
        fm = {"parent-epic": None}
        assert collect_frontmatter_ids(fm) == set()

    def test_empty_frontmatter(self):
        """Empty dict yields empty set."""
        assert collect_frontmatter_ids({}) == set()

    def test_mixed_empty_and_populated(self):
        """Empty string and empty list alongside populated field."""
        fm = {
            "parent-epic": "",
            "depends-on-artifacts": [],
            "parent-vision": "VISION-002",
        }
        assert collect_frontmatter_ids(fm) == {"VISION-002"}


class TestCollectFrontmatterIdsMixed:
    """Integration-style tests combining multiple field types."""

    def test_multiple_field_types_union(self):
        """IDs from list fields, scalar fields, and addresses are unioned."""
        fm = {
            "depends-on-artifacts": ["SPEC-010", "SPIKE-007"],
            "parent-epic": "EPIC-005",
            "addresses": ["JOURNEY-001.PP-03"],
            "source-issue": "github:foo#12",
        }
        result = collect_frontmatter_ids(fm)
        assert result == {"SPEC-010", "SPIKE-007", "EPIC-005", "JOURNEY-001"}

    def test_deduplication_across_fields(self):
        """Same ID in multiple fields appears only once."""
        fm = {
            "depends-on-artifacts": ["SPEC-010"],
            "linked-artifacts": ["SPEC-010"],
        }
        assert collect_frontmatter_ids(fm) == {"SPEC-010"}


# ---------------------------------------------------------------------------
# swa-ika9 — Discrepancy computation tests
# ---------------------------------------------------------------------------


class TestComputeDiscrepanciesBasic:
    """Test compute_discrepancies returns correct set differences."""

    def test_partial_overlap(self):
        """body_ids={A,B}, frontmatter_ids={B,C} → body_not_in_frontmatter={A}, frontmatter_not_in_body={C}."""
        result = compute_discrepancies({"A", "B"}, {"B", "C"})
        assert result["body_not_in_frontmatter"] == {"A"}
        assert result["frontmatter_not_in_body"] == {"C"}

    def test_perfect_overlap(self):
        """Identical sets → both output sets empty."""
        result = compute_discrepancies({"A", "B"}, {"A", "B"})
        assert result["body_not_in_frontmatter"] == set()
        assert result["frontmatter_not_in_body"] == set()

    def test_empty_body_ids(self):
        """body_ids empty → body_not_in_frontmatter empty, frontmatter_not_in_body=all frontmatter_ids."""
        result = compute_discrepancies(set(), {"B", "C"})
        assert result["body_not_in_frontmatter"] == set()
        assert result["frontmatter_not_in_body"] == {"B", "C"}

    def test_empty_frontmatter_ids(self):
        """frontmatter_ids empty → body_not_in_frontmatter=all body_ids, frontmatter_not_in_body empty."""
        result = compute_discrepancies({"A", "B"}, set())
        assert result["body_not_in_frontmatter"] == {"A", "B"}
        assert result["frontmatter_not_in_body"] == set()

    def test_both_empty(self):
        """Both empty → both output sets empty."""
        result = compute_discrepancies(set(), set())
        assert result["body_not_in_frontmatter"] == set()
        assert result["frontmatter_not_in_body"] == set()


# ---------------------------------------------------------------------------
# swa-htqd — Bidirectional edge enforcement tests
# ---------------------------------------------------------------------------


class TestCheckReciprocalEdgesBasic:
    """Test check_reciprocal_edges returns gaps when linked-artifacts is missing."""

    def test_reciprocal_present_no_gap(self):
        """A depends-on B, B has A in linked-artifacts → no gaps."""
        nodes = {
            "A": {"linked-artifacts": []},
            "B": {"linked-artifacts": ["A"]},
        }
        edges = [{"from": "A", "to": "B", "type": "depends-on"}]
        result = check_reciprocal_edges(nodes, edges)
        assert result == []

    def test_reciprocal_missing_returns_gap(self):
        """A depends-on B, B does NOT have A in linked-artifacts → one gap."""
        nodes = {
            "A": {"linked-artifacts": []},
            "B": {"linked-artifacts": []},
        }
        edges = [{"from": "A", "to": "B", "type": "depends-on"}]
        result = check_reciprocal_edges(nodes, edges)
        assert len(result) == 1
        gap = result[0]
        assert gap["from"] == "A"
        assert gap["to"] == "B"
        assert gap["edge_type"] == "depends-on"
        assert gap["expected_field"] == "linked-artifacts"

    def test_multiple_edges_some_gaps(self):
        """Multiple edges; only the ones missing reciprocals are returned."""
        nodes = {
            "A": {"linked-artifacts": []},
            "B": {"linked-artifacts": ["A"]},
            "C": {"linked-artifacts": []},
        }
        edges = [
            {"from": "A", "to": "B", "type": "depends-on"},
            {"from": "A", "to": "C", "type": "depends-on"},
        ]
        result = check_reciprocal_edges(nodes, edges)
        # A→B has reciprocal; A→C does not
        assert len(result) == 1
        assert result[0]["to"] == "C"

    def test_empty_edges_returns_empty(self):
        """No edges → no gaps."""
        nodes = {"A": {"linked-artifacts": []}}
        result = check_reciprocal_edges(nodes, [])
        assert result == []

    def test_enriched_reciprocal_entries_do_not_raise_and_count_as_backlinks(self):
        """Enriched dict entries should contribute artifact IDs, not crash set handling."""
        nodes = {
            "SPEC-001": {"linked-artifacts": []},
            "EPIC-005": {
                "artifact-refs": [
                    {
                        "artifact": "SPEC-001",
                        "rel": ["documents"],
                        "commit": "abc1234",
                    }
                ]
            },
        }
        edges = [{"from": "SPEC-001", "to": "EPIC-005", "type": "depends-on"}]
        result = check_reciprocal_edges(nodes, edges)
        assert result == []

    def test_orphan_node_missing_from_nodes_dict(self):
        """Node B missing from nodes dict is treated as missing linked-artifacts (gap flagged)."""
        nodes = {
            "A": {"linked-artifacts": []},
            # "B" intentionally absent
        }
        edges = [{"from": "A", "to": "B", "type": "depends-on"}]
        result = check_reciprocal_edges(nodes, edges)
        assert len(result) == 1
        assert result[0]["to"] == "B"


# ---------------------------------------------------------------------------
# swa-zvey — Full xref pipeline tests
# ---------------------------------------------------------------------------


class TestComputeXrefPipeline:
    """Test compute_xref returns only artifacts with at least one discrepancy."""

    def test_one_artifact_with_body_mention_not_in_frontmatter(self):
        """Artifact with body mention missing from frontmatter appears in result; clean artifact omitted."""
        artifacts = [
            {
                "id": "SPEC-001",
                "file": "docs/spec-001.md",
                "body": "See EPIC-005 for context.",
                "frontmatter": {},
            },
            {
                "id": "SPEC-002",
                "file": "docs/spec-002.md",
                "body": "No cross-references here.",
                "frontmatter": {},
            },
        ]
        edges = []
        result = compute_xref(artifacts, edges)
        ids = [entry["artifact"] for entry in result]
        assert "SPEC-001" in ids
        assert "SPEC-002" not in ids

    def test_both_artifacts_clean_returns_empty(self):
        """Two fully consistent artifacts → empty result list."""
        artifacts = [
            {
                "id": "SPEC-010",
                "file": "docs/spec-010.md",
                "body": "SPEC-020 is referenced here.",
                "frontmatter": {"depends-on-artifacts": ["SPEC-020"]},
            },
            {
                "id": "SPEC-020",
                "file": "docs/spec-020.md",
                "body": "No references.",
                "frontmatter": {},
            },
        ]
        edges = []
        result = compute_xref(artifacts, edges)
        assert result == []

    def test_artifact_with_missing_reciprocal_edge(self):
        """Artifact with missing reciprocal edge appears with missing_reciprocal populated."""
        artifacts = [
            {
                "id": "SPEC-001",
                "file": "docs/spec-001.md",
                "body": "",
                "frontmatter": {},
            },
            {
                "id": "EPIC-005",
                "file": "docs/epic-005.md",
                "body": "",
                "frontmatter": {"linked-artifacts": []},
            },
        ]
        edges = [{"from": "SPEC-001", "to": "EPIC-005", "type": "depends-on"}]
        result = compute_xref(artifacts, edges)
        epic_entries = [e for e in result if e["artifact"] == "EPIC-005"]
        assert len(epic_entries) == 1
        assert len(epic_entries[0]["missing_reciprocal"]) >= 1

    def test_all_three_discrepancy_types_in_one_artifact(self):
        """Single artifact with body_not_in_frontmatter, frontmatter_not_in_body, and missing_reciprocal."""
        artifacts = [
            {
                "id": "SPEC-001",
                "file": "docs/spec-001.md",
                "body": "See EPIC-005.",
                "frontmatter": {"depends-on-artifacts": ["SPIKE-007"]},
            },
            {
                "id": "EPIC-005",
                "file": "docs/epic-005.md",
                "body": "",
                "frontmatter": {"linked-artifacts": []},
            },
            {
                "id": "SPIKE-007",
                "file": "docs/spike-007.md",
                "body": "",
                "frontmatter": {},
            },
        ]
        edges = [{"from": "SPEC-001", "to": "EPIC-005", "type": "depends-on"}]
        result = compute_xref(artifacts, edges)
        spec_entries = [e for e in result if e["artifact"] == "SPEC-001"]
        assert len(spec_entries) == 1
        entry = spec_entries[0]
        # body mentions EPIC-005 but frontmatter has SPIKE-007 → both discrepancy sets non-empty
        assert len(entry["body_not_in_frontmatter"]) >= 1
        assert len(entry["frontmatter_not_in_body"]) >= 1

    def test_empty_artifact_list_returns_empty(self):
        """Empty artifact list → empty result."""
        result = compute_xref([], [])
        assert result == []


# ---------------------------------------------------------------------------
# swa-5ckf — xref subcommand tests
# ---------------------------------------------------------------------------


class TestCmdXrefNoData:
    """cmd_xref with empty xref cache outputs nothing meaningful."""

    def test_no_xref_data_outputs_nothing(self):
        """When cache has no xref key or empty list, cmd_xref produces no output."""
        from specgraph.cli import cmd_xref

        cache_data = {"nodes": {}, "edges": [], "xref": []}

        args = argparse.Namespace(json=False)
        with unittest.mock.patch(
            "specgraph.cli._ensure_cache", return_value=cache_data
        ):
            captured = io.StringIO()
            with unittest.mock.patch("sys.stdout", captured):
                cmd_xref(args, Path("/fake/repo"))
        output = captured.getvalue()
        assert "SPEC-" not in output or output.strip() == ""


class TestCmdXrefBodyNotInFrontmatter:
    """cmd_xref with body_not_in_frontmatter data shows Cross-Reference Gaps section."""

    def test_body_not_in_frontmatter_section_shown(self):
        """Output contains 'Cross-Reference Gaps' and the artifact ID."""
        from specgraph.cli import cmd_xref

        xref_data = [
            {
                "artifact": "SPEC-001",
                "file": "docs/spec-001.md",
                "body_not_in_frontmatter": ["EPIC-005"],
                "frontmatter_not_in_body": [],
                "missing_reciprocal": [],
            }
        ]
        cache_data = {"nodes": {}, "edges": [], "xref": xref_data}
        args = argparse.Namespace(json=False)
        with unittest.mock.patch(
            "specgraph.cli._ensure_cache", return_value=cache_data
        ):
            captured = io.StringIO()
            with unittest.mock.patch("sys.stdout", captured):
                cmd_xref(args, Path("/fake/repo"))
        output = captured.getvalue()
        assert "Cross-Reference Gaps" in output
        assert "SPEC-001" in output


class TestCmdXrefMissingReciprocal:
    """cmd_xref with missing_reciprocal data shows Missing Reciprocal Edges section."""

    def test_missing_reciprocal_section_shown(self):
        """Output contains 'Missing Reciprocal Edges' when missing_reciprocal is non-empty."""
        from specgraph.cli import cmd_xref

        xref_data = [
            {
                "artifact": "EPIC-005",
                "file": "docs/epic-005.md",
                "body_not_in_frontmatter": [],
                "frontmatter_not_in_body": [],
                "missing_reciprocal": [
                    {
                        "from": "SPEC-001",
                        "edge_type": "depends-on",
                        "expected_field": "linked-artifacts",
                    }
                ],
            }
        ]
        cache_data = {"nodes": {}, "edges": [], "xref": xref_data}
        args = argparse.Namespace(json=False)
        with unittest.mock.patch(
            "specgraph.cli._ensure_cache", return_value=cache_data
        ):
            captured = io.StringIO()
            with unittest.mock.patch("sys.stdout", captured):
                cmd_xref(args, Path("/fake/repo"))
        output = captured.getvalue()
        assert "Missing Reciprocal Edges" in output


class TestCmdXrefJsonFlag:
    """cmd_xref with --json flag outputs raw JSON array."""

    def test_json_flag_outputs_json_array(self):
        """With json=True, output is parseable JSON and not the human-readable format."""
        import json as json_mod

        from specgraph.cli import cmd_xref

        xref_data = [
            {
                "artifact": "SPEC-001",
                "file": "docs/spec-001.md",
                "body_not_in_frontmatter": ["EPIC-005"],
                "frontmatter_not_in_body": [],
                "missing_reciprocal": [],
            }
        ]
        cache_data = {"nodes": {}, "edges": [], "xref": xref_data}
        args = argparse.Namespace(json=True)
        with unittest.mock.patch(
            "specgraph.cli._ensure_cache", return_value=cache_data
        ):
            captured = io.StringIO()
            with unittest.mock.patch("sys.stdout", captured):
                cmd_xref(args, Path("/fake/repo"))
        output = captured.getvalue()
        parsed = json_mod.loads(output)
        assert isinstance(parsed, list)
        assert "Cross-Reference Gaps" not in output


def test_collect_frontmatter_ids_includes_parent_initiative():
    """parent-initiative scalar is collected by collect_frontmatter_ids."""
    from specgraph.xref import collect_frontmatter_ids
    fm = {"parent-initiative": "INITIATIVE-001"}
    ids = collect_frontmatter_ids(fm)
    assert "INITIATIVE-001" in ids


def test_spec_with_parent_initiative_no_parent_epic_is_valid():
    """A spec can have parent-initiative without parent-epic (small work path)."""
    from specgraph.xref import collect_frontmatter_ids
    fm = {"parent-initiative": "INITIATIVE-001", "title": "Fix bug"}
    ids = collect_frontmatter_ids(fm)
    assert "INITIATIVE-001" in ids
    # No parent-epic — that's fine for small work


class TestCmdXrefMixedResults:
    """cmd_xref with all gap types present shows all three sections."""

    def test_all_three_sections_shown(self):
        """With body, frontmatter, and reciprocal gaps, all three section headers appear."""
        from specgraph.cli import cmd_xref

        xref_data = [
            {
                "artifact": "SPEC-001",
                "file": "docs/spec-001.md",
                "body_not_in_frontmatter": ["EPIC-005"],
                "frontmatter_not_in_body": ["SPIKE-007"],
                "missing_reciprocal": [
                    {
                        "from": "SPEC-002",
                        "edge_type": "depends-on",
                        "expected_field": "linked-artifacts",
                    }
                ],
            }
        ]
        cache_data = {"nodes": {}, "edges": [], "xref": xref_data}
        args = argparse.Namespace(json=False)
        with unittest.mock.patch(
            "specgraph.cli._ensure_cache", return_value=cache_data
        ):
            captured = io.StringIO()
            with unittest.mock.patch("sys.stdout", captured):
                cmd_xref(args, Path("/fake/repo"))
        output = captured.getvalue()
        assert "Cross-Reference Gaps" in output
        assert "Missing Reciprocal Edges" in output
