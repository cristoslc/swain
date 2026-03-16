"""Tests for attention tracking module."""

import sys
from pathlib import Path
from datetime import datetime, timezone

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from specgraph.attention import parse_git_log_entry, attribute_to_vision, compute_attention


class TestParseGitLogEntry:
    """Test parsing git log --name-only output."""

    def test_extracts_artifact_id_from_path(self):
        path = "docs/epic/Active/(EPIC-001)-Title/(EPIC-001)-Title.md"
        result = parse_git_log_entry(path)
        assert result == "EPIC-001"

    def test_extracts_spec_id(self):
        path = "docs/spec/Complete/(SPEC-042)-MOTD-Fix/(SPEC-042)-MOTD-Fix.md"
        result = parse_git_log_entry(path)
        assert result == "SPEC-042"

    def test_extracts_initiative_id(self):
        path = "docs/initiative/Active/(INITIATIVE-001)-Security/(INITIATIVE-001)-Security.md"
        result = parse_git_log_entry(path)
        assert result == "INITIATIVE-001"

    def test_returns_none_for_non_artifact(self):
        path = "skills/swain-status/scripts/swain-status.sh"
        result = parse_git_log_entry(path)
        assert result is None

    def test_returns_none_for_readme(self):
        path = "docs/epic/README.md"
        result = parse_git_log_entry(path)
        assert result is None


class TestAttributeToVision:
    """Test vision attribution via parent chain."""

    NODES = {
        "VISION-001": {"type": "VISION"},
        "INITIATIVE-001": {"type": "INITIATIVE"},
        "EPIC-001": {"type": "EPIC"},
        "SPEC-001": {"type": "SPEC"},
    }

    EDGES = [
        {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
        {"from": "EPIC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "SPEC-001", "to": "EPIC-001", "type": "parent-epic"},
    ]

    def test_spec_attributed_to_vision(self):
        result = attribute_to_vision("SPEC-001", self.NODES, self.EDGES)
        assert result == "VISION-001"

    def test_orphan_returns_unaligned(self):
        result = attribute_to_vision("ORPHAN-001", self.NODES, self.EDGES)
        assert result == "_unaligned"


class TestComputeAttention:
    """Test the full attention computation from structured log data."""

    def test_aggregates_by_vision(self):
        log_entries = [
            ("SPEC-001", datetime(2026, 3, 1, tzinfo=timezone.utc)),
            ("SPEC-001", datetime(2026, 3, 5, tzinfo=timezone.utc)),
            ("EPIC-002", datetime(2026, 3, 10, tzinfo=timezone.utc)),
        ]
        nodes = {
            "VISION-001": {"type": "VISION"},
            "INITIATIVE-001": {"type": "INITIATIVE"},
            "SPEC-001": {"type": "SPEC"},
            "EPIC-002": {"type": "EPIC"},
        }
        edges = [
            {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
            {"from": "SPEC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
        ]
        result = compute_attention(log_entries, nodes, edges)
        assert result["VISION-001"]["transitions"] == 2
        assert result["_unaligned"]["transitions"] == 1  # EPIC-002 is orphan
