"""Tests for specgraph body cross-reference scanner."""

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from specgraph.xref import scan_body


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
