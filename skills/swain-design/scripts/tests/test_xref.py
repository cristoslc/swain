"""Tests for specgraph body cross-reference scanner."""

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from specgraph.xref import collect_frontmatter_ids, scan_body


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
