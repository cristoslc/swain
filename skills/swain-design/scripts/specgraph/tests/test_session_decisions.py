"""Tests for JSONL session decision log (SPEC-118).

Validates append_decision_record() and read_decision_records().
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from specgraph.session_decisions import append_decision_record, read_decision_records


def test_append_creates_file(tmp_path):
    """First append creates the JSONL file."""
    append_decision_record(
        repo_root=str(tmp_path),
        artifact="SPEC-001",
        action="approved",
        commit="abc1234",
        session_id="2026-03-22T00:00:00Z",
    )
    logfile = tmp_path / ".agents" / "session-decisions.jsonl"
    assert logfile.exists()
    entries = [json.loads(line) for line in logfile.read_text().strip().split("\n")]
    assert len(entries) == 1
    assert entries[0]["artifact"] == "SPEC-001"
    assert entries[0]["action"] == "approved"
    assert entries[0]["commit"] == "abc1234"


def test_append_accumulates(tmp_path):
    """Multiple appends accumulate in the same file."""
    for i in range(3):
        append_decision_record(
            repo_root=str(tmp_path),
            artifact=f"SPEC-{i:03d}",
            action="approved",
            commit=f"hash{i}",
        )
    logfile = tmp_path / ".agents" / "session-decisions.jsonl"
    entries = [json.loads(line) for line in logfile.read_text().strip().split("\n")]
    assert len(entries) == 3


def test_read_returns_all_entries(tmp_path):
    """read_decision_records returns all entries."""
    for i in range(2):
        append_decision_record(
            repo_root=str(tmp_path),
            artifact=f"SPEC-{i:03d}",
            action="activated",
            commit=f"hash{i}",
        )
    records = read_decision_records(str(tmp_path))
    assert len(records) == 2
    assert records[0]["artifact"] == "SPEC-000"
    assert records[1]["artifact"] == "SPEC-001"


def test_read_empty_when_no_file(tmp_path):
    """read_decision_records returns empty list when no file exists."""
    records = read_decision_records(str(tmp_path))
    assert records == []


def test_read_skips_malformed_lines(tmp_path):
    """Malformed JSONL lines are skipped, not exceptions."""
    logfile = tmp_path / ".agents" / "session-decisions.jsonl"
    logfile.parent.mkdir(parents=True)
    logfile.write_text(
        '{"artifact": "SPEC-001", "action": "approved"}\n'
        'not valid json\n'
        '{"artifact": "SPEC-002", "action": "dropped"}\n'
    )
    records = read_decision_records(str(tmp_path))
    assert len(records) == 2


def test_entry_has_timestamp(tmp_path):
    """Each entry should have an auto-generated timestamp."""
    append_decision_record(
        repo_root=str(tmp_path),
        artifact="SPEC-001",
        action="approved",
        commit="abc1234",
    )
    records = read_decision_records(str(tmp_path))
    assert "timestamp" in records[0]
    assert len(records[0]["timestamp"]) > 0


def test_session_id_stored(tmp_path):
    """Session ID is stored when provided."""
    append_decision_record(
        repo_root=str(tmp_path),
        artifact="SPEC-001",
        action="approved",
        commit="abc1234",
        session_id="session-2026-03-22",
    )
    records = read_decision_records(str(tmp_path))
    assert records[0]["session"] == "session-2026-03-22"


def test_filter_by_session(tmp_path):
    """read_decision_records can filter by session_id."""
    append_decision_record(str(tmp_path), "SPEC-001", "approved", "h1", session_id="s1")
    append_decision_record(str(tmp_path), "SPEC-002", "dropped", "h2", session_id="s2")
    append_decision_record(str(tmp_path), "SPEC-003", "approved", "h3", session_id="s1")
    records = read_decision_records(str(tmp_path), session_id="s1")
    assert len(records) == 2
    assert all(r["session"] == "s1" for r in records)
