"""Tests for security_gate.py — SPEC-064 Post-Implementation Security Gate.

TDD RED phase: tests for diff-only security gate trigger and finding-to-ticket filing.

Covers:
- swa-kvf5: Diff-only security gate trigger (should_run_gate, get_changed_files, run_gate)
- swa-1qiw: Finding-to-ticket filing (file_finding_as_ticket, linking, tag correctness)
"""

from __future__ import annotations

import os
import subprocess
import sys
from unittest.mock import MagicMock, patch, call

import pytest

# Add the scanner scripts to the path
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "skills",
        "swain-security-check",
        "scripts",
    ),
)

from security_gate import (
    should_run_gate,
    get_changed_files,
    run_gate,
    file_finding_as_ticket,
)


# ---------------------------------------------------------------------------
# swa-kvf5: Tests for should_run_gate
# ---------------------------------------------------------------------------

class TestShouldRunGate:
    """should_run_gate uses threat_surface to decide if gate should trigger."""

    def test_security_sensitive_title_triggers_gate(self):
        """Task with auth keyword in title should trigger gate."""
        assert should_run_gate(
            task_title="Add JWT token validation middleware",
            task_tags=[],
            spec_criteria="",
        ) is True

    def test_security_tag_triggers_gate(self):
        """Task with 'security' tag should trigger gate."""
        assert should_run_gate(
            task_title="Update README formatting",
            task_tags=["security"],
            spec_criteria="",
        ) is True

    def test_auth_tag_triggers_gate(self):
        """Task with 'auth' tag should trigger gate."""
        assert should_run_gate(
            task_title="Refactor module",
            task_tags=["auth"],
            spec_criteria="",
        ) is True

    def test_crypto_tag_triggers_gate(self):
        """Task with 'crypto' tag should trigger gate."""
        assert should_run_gate(
            task_title="Update library",
            task_tags=["crypto"],
            spec_criteria="",
        ) is True

    def test_spec_criteria_triggers_gate(self):
        """SPEC criteria mentioning encryption should trigger gate."""
        assert should_run_gate(
            task_title="Store user data",
            task_tags=[],
            spec_criteria="All PII must be encrypted at rest",
        ) is True

    def test_non_security_task_skips_gate(self):
        """Non-security task should not trigger gate."""
        assert should_run_gate(
            task_title="Fix button alignment on dashboard",
            task_tags=["frontend"],
            spec_criteria="Button should be centered",
        ) is False

    def test_empty_inputs_skips_gate(self):
        """Empty inputs should not trigger gate."""
        assert should_run_gate(
            task_title="",
            task_tags=[],
            spec_criteria="",
        ) is False

    def test_none_tags_handled(self):
        """None tags should not crash."""
        assert should_run_gate(
            task_title="Fix CSS alignment",
            task_tags=None,
            spec_criteria="",
        ) is False

    def test_password_keyword_triggers_gate(self):
        """Password keyword in title triggers gate."""
        assert should_run_gate(
            task_title="Implement password reset endpoint",
            task_tags=[],
            spec_criteria="",
        ) is True

    def test_sanitize_in_criteria_triggers_gate(self):
        """Sanitize in SPEC criteria triggers gate."""
        assert should_run_gate(
            task_title="Implement form handler",
            task_tags=[],
            spec_criteria="Must sanitize user input before storing",
        ) is True


# ---------------------------------------------------------------------------
# swa-kvf5: Tests for get_changed_files
# ---------------------------------------------------------------------------

class TestGetChangedFiles:
    """get_changed_files returns files from git diff --name-only."""

    @patch("security_gate.subprocess.run")
    def test_returns_changed_files(self, mock_run):
        """Should return list of file paths from git diff."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="src/auth/handler.py\nsrc/utils/format.py\n",
        )
        result = get_changed_files()
        assert result == ["src/auth/handler.py", "src/utils/format.py"]
        # Verify git diff --name-only was called
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert "git" in cmd
        assert "diff" in cmd
        assert "--name-only" in cmd

    @patch("security_gate.subprocess.run")
    def test_returns_empty_on_no_changes(self, mock_run):
        """Should return empty list when no files changed."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="",
        )
        result = get_changed_files()
        assert result == []

    @patch("security_gate.subprocess.run")
    def test_returns_empty_on_git_error(self, mock_run):
        """Should return empty list on git failure (not crash)."""
        mock_run.return_value = MagicMock(
            returncode=128,
            stdout="",
        )
        result = get_changed_files()
        assert result == []

    @patch("security_gate.subprocess.run")
    def test_returns_empty_on_subprocess_exception(self, mock_run):
        """Should handle subprocess exceptions gracefully."""
        mock_run.side_effect = OSError("git not found")
        result = get_changed_files()
        assert result == []

    @patch("security_gate.subprocess.run")
    def test_strips_whitespace_from_paths(self, mock_run):
        """Should strip trailing whitespace/newlines from paths."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="  src/auth/handler.py  \n  src/utils/format.py  \n",
        )
        result = get_changed_files()
        assert result == ["src/auth/handler.py", "src/utils/format.py"]

    @patch("security_gate.subprocess.run")
    def test_filters_empty_lines(self, mock_run):
        """Should filter out blank lines from git output."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="src/auth/handler.py\n\n\nsrc/utils/format.py\n\n",
        )
        result = get_changed_files()
        assert result == ["src/auth/handler.py", "src/utils/format.py"]


# ---------------------------------------------------------------------------
# swa-kvf5: Tests for run_gate (integration of trigger + scan)
# ---------------------------------------------------------------------------

class TestRunGateTrigger:
    """run_gate should scan only changed files and only for security tasks."""

    @patch("security_gate.file_finding_as_ticket")
    @patch("security_gate.subprocess.run")
    def test_scans_changed_files_only(self, mock_run, mock_file_ticket):
        """Gate should use context_file_scanner.scan_file on each changed file."""
        # git diff returns two files
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="src/auth/handler.py\nCLAUDE.md\n",
        )
        mock_file_ticket.return_value = None

        with patch("security_gate.scan_file") as mock_scan:
            mock_scan.return_value = []
            run_gate(
                changed_files=["src/auth/handler.py", "CLAUDE.md"],
                originating_task_id="swa-test",
            )
            # scan_file should be called for each changed file
            assert mock_scan.call_count == 2
            mock_scan.assert_any_call("src/auth/handler.py")
            mock_scan.assert_any_call("CLAUDE.md")

    @patch("security_gate.file_finding_as_ticket")
    @patch("security_gate.scan_file")
    def test_returns_filed_ticket_ids(self, mock_scan, mock_file_ticket):
        """Gate should return list of newly created ticket IDs."""
        mock_scan.return_value = [
            {
                "file_path": "CLAUDE.md",
                "line_number": 10,
                "category": "A",
                "severity": "critical",
                "description": "Instruction override detected",
                "matched_pattern": "ignore previous instructions",
            },
        ]
        mock_file_ticket.return_value = "swa-abc1"

        result = run_gate(
            changed_files=["CLAUDE.md"],
            originating_task_id="swa-test",
        )
        assert result == ["swa-abc1"]

    @patch("security_gate.file_finding_as_ticket")
    @patch("security_gate.scan_file")
    def test_returns_empty_list_on_clean_scan(self, mock_scan, mock_file_ticket):
        """Gate should return empty list when no findings."""
        mock_scan.return_value = []

        result = run_gate(
            changed_files=["src/utils/format.py"],
            originating_task_id="swa-test",
        )
        assert result == []
        mock_file_ticket.assert_not_called()

    @patch("security_gate.file_finding_as_ticket")
    @patch("security_gate.scan_file")
    def test_empty_changed_files_returns_empty(self, mock_scan, mock_file_ticket):
        """Gate with no changed files should return empty list."""
        result = run_gate(
            changed_files=[],
            originating_task_id="swa-test",
        )
        assert result == []
        mock_scan.assert_not_called()

    @patch("security_gate.file_finding_as_ticket")
    @patch("security_gate.scan_file")
    def test_multiple_findings_across_files(self, mock_scan, mock_file_ticket):
        """Multiple findings across files should all be filed."""
        mock_scan.side_effect = [
            [  # First file: one finding
                {
                    "file_path": "CLAUDE.md",
                    "line_number": 5,
                    "category": "A",
                    "severity": "critical",
                    "description": "Finding 1",
                    "matched_pattern": "pattern1",
                },
            ],
            [  # Second file: two findings
                {
                    "file_path": "AGENTS.md",
                    "line_number": 10,
                    "category": "B",
                    "severity": "high",
                    "description": "Finding 2",
                    "matched_pattern": "pattern2",
                },
                {
                    "file_path": "AGENTS.md",
                    "line_number": 20,
                    "category": "C",
                    "severity": "medium",
                    "description": "Finding 3",
                    "matched_pattern": "pattern3",
                },
            ],
        ]
        mock_file_ticket.side_effect = ["swa-t1", "swa-t2", "swa-t3"]

        result = run_gate(
            changed_files=["CLAUDE.md", "AGENTS.md"],
            originating_task_id="swa-test",
        )
        assert len(result) == 3
        assert mock_file_ticket.call_count == 3

    @patch("security_gate.file_finding_as_ticket")
    @patch("security_gate.scan_file")
    def test_scan_file_exception_does_not_crash(self, mock_scan, mock_file_ticket):
        """If scanning a file raises an exception, gate should continue."""
        mock_scan.side_effect = [
            OSError("Permission denied"),
            [
                {
                    "file_path": "AGENTS.md",
                    "line_number": 5,
                    "category": "A",
                    "severity": "critical",
                    "description": "Finding",
                    "matched_pattern": "pattern",
                },
            ],
        ]
        mock_file_ticket.return_value = "swa-t1"

        result = run_gate(
            changed_files=["unreadable.md", "AGENTS.md"],
            originating_task_id="swa-test",
        )
        # Should still file the finding from the second file
        assert result == ["swa-t1"]


# ---------------------------------------------------------------------------
# swa-1qiw: Tests for file_finding_as_ticket
# ---------------------------------------------------------------------------

class TestFileFindingAsTicket:
    """file_finding_as_ticket creates a tk issue and links it to the originating task."""

    @patch("security_gate.subprocess.run")
    def test_creates_ticket_with_correct_fields(self, mock_run):
        """Should call tk create with correct title, description, tags."""
        # First call: tk create -> returns ticket ID
        # Second call: tk link
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="swa-new1\n"),
            MagicMock(returncode=0, stdout=""),
        ]

        finding = {
            "file_path": "CLAUDE.md",
            "line_number": 10,
            "category": "A",
            "severity": "critical",
            "description": "Instruction override: attempts to nullify prior instructions",
            "matched_pattern": "ignore previous instructions",
            "scanner": "context-file-scanner",
        }
        result = file_finding_as_ticket(finding, "swa-orig")

        assert result == "swa-new1"
        # Verify tk create was called
        create_call = mock_run.call_args_list[0]
        create_cmd = create_call[0][0]
        create_cmd_str = " ".join(create_cmd)
        assert "tk" in create_cmd_str
        assert "create" in create_cmd_str

    @patch("security_gate.subprocess.run")
    def test_ticket_has_security_finding_tag(self, mock_run):
        """Created ticket must have security-finding tag."""
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="swa-new1\n"),
            MagicMock(returncode=0, stdout=""),
        ]

        finding = {
            "file_path": "CLAUDE.md",
            "line_number": 10,
            "category": "A",
            "severity": "critical",
            "description": "Instruction override detected",
            "matched_pattern": "pattern",
        }
        file_finding_as_ticket(finding, "swa-orig")

        create_call = mock_run.call_args_list[0]
        create_cmd = create_call[0][0]
        create_cmd_str = " ".join(create_cmd)
        assert "security-finding" in create_cmd_str

    @patch("security_gate.subprocess.run")
    def test_ticket_linked_to_originating_task(self, mock_run):
        """Created ticket must be linked to originating task via tk link."""
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="swa-new1\n"),
            MagicMock(returncode=0, stdout=""),
        ]

        finding = {
            "file_path": "CLAUDE.md",
            "line_number": 10,
            "category": "A",
            "severity": "critical",
            "description": "Finding",
            "matched_pattern": "pattern",
        }
        file_finding_as_ticket(finding, "swa-orig")

        # Verify tk link was called with correct IDs
        assert mock_run.call_count == 2
        link_call = mock_run.call_args_list[1]
        link_cmd = link_call[0][0]
        link_cmd_str = " ".join(link_cmd)
        assert "tk" in link_cmd_str
        assert "link" in link_cmd_str
        assert "swa-new1" in link_cmd_str
        assert "swa-orig" in link_cmd_str

    @patch("security_gate.subprocess.run")
    def test_ticket_title_includes_file_path(self, mock_run):
        """Ticket title should reference the file where finding was detected."""
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="swa-new1\n"),
            MagicMock(returncode=0, stdout=""),
        ]

        finding = {
            "file_path": "src/auth/handler.py",
            "line_number": 42,
            "category": "A",
            "severity": "critical",
            "description": "Instruction override detected",
            "matched_pattern": "pattern",
        }
        file_finding_as_ticket(finding, "swa-orig")

        create_call = mock_run.call_args_list[0]
        create_cmd = create_call[0][0]
        # Title is typically the first positional arg after "create"
        create_cmd_str = " ".join(create_cmd)
        assert "src/auth/handler.py" in create_cmd_str

    @patch("security_gate.subprocess.run")
    def test_ticket_description_includes_finding_details(self, mock_run):
        """Ticket description should contain finding severity, description, and line."""
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="swa-new1\n"),
            MagicMock(returncode=0, stdout=""),
        ]

        finding = {
            "file_path": "CLAUDE.md",
            "line_number": 10,
            "category": "A",
            "severity": "critical",
            "description": "Instruction override: attempts to nullify prior instructions",
            "matched_pattern": "ignore previous instructions",
            "remediation": "Remove the instruction override pattern",
        }
        file_finding_as_ticket(finding, "swa-orig")

        create_call = mock_run.call_args_list[0]
        create_cmd = create_call[0][0]
        create_cmd_str = " ".join(create_cmd)
        # Description should contain severity and the finding description
        assert "critical" in create_cmd_str.lower()
        assert "Instruction override" in create_cmd_str

    @patch("security_gate.subprocess.run")
    def test_ticket_type_is_bug(self, mock_run):
        """Security findings should be filed as bug type."""
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="swa-new1\n"),
            MagicMock(returncode=0, stdout=""),
        ]

        finding = {
            "file_path": "CLAUDE.md",
            "line_number": 10,
            "category": "A",
            "severity": "critical",
            "description": "Finding",
            "matched_pattern": "pattern",
        }
        file_finding_as_ticket(finding, "swa-orig")

        create_call = mock_run.call_args_list[0]
        create_cmd = create_call[0][0]
        create_cmd_str = " ".join(create_cmd)
        assert "bug" in create_cmd_str

    @patch("security_gate.subprocess.run")
    def test_returns_none_on_create_failure(self, mock_run):
        """Should return None if tk create fails."""
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")

        finding = {
            "file_path": "CLAUDE.md",
            "line_number": 10,
            "category": "A",
            "severity": "critical",
            "description": "Finding",
            "matched_pattern": "pattern",
        }
        result = file_finding_as_ticket(finding, "swa-orig")
        assert result is None

    @patch("security_gate.subprocess.run")
    def test_returns_ticket_id_even_if_link_fails(self, mock_run):
        """Should return ticket ID even if linking fails (best-effort linking)."""
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="swa-new1\n"),
            MagicMock(returncode=1, stdout="", stderr="link error"),
        ]

        finding = {
            "file_path": "CLAUDE.md",
            "line_number": 10,
            "category": "A",
            "severity": "critical",
            "description": "Finding",
            "matched_pattern": "pattern",
        }
        result = file_finding_as_ticket(finding, "swa-orig")
        # Ticket was created successfully, link failed but that's OK
        assert result == "swa-new1"

    @patch("security_gate.subprocess.run")
    def test_handles_subprocess_exception(self, mock_run):
        """Should return None on subprocess exception."""
        mock_run.side_effect = OSError("tk not found")

        finding = {
            "file_path": "CLAUDE.md",
            "line_number": 10,
            "category": "A",
            "severity": "critical",
            "description": "Finding",
            "matched_pattern": "pattern",
        }
        result = file_finding_as_ticket(finding, "swa-orig")
        assert result is None

    @patch("security_gate.subprocess.run")
    def test_priority_maps_from_severity(self, mock_run):
        """Critical severity should map to priority 0, high to 1, etc."""
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="swa-new1\n"),
            MagicMock(returncode=0, stdout=""),
        ]

        finding = {
            "file_path": "CLAUDE.md",
            "line_number": 10,
            "category": "A",
            "severity": "critical",
            "description": "Finding",
            "matched_pattern": "pattern",
        }
        file_finding_as_ticket(finding, "swa-orig")

        create_call = mock_run.call_args_list[0]
        create_cmd = create_call[0][0]
        # Find the -p flag value
        cmd_str = " ".join(create_cmd)
        assert "-p" in create_cmd
        p_idx = create_cmd.index("-p")
        assert create_cmd[p_idx + 1] == "0"  # critical -> priority 0


# ---------------------------------------------------------------------------
# swa-1qiw: Tests for run_gate filing integration
# ---------------------------------------------------------------------------

class TestRunGateFiling:
    """run_gate should file findings as tickets and return IDs."""

    @patch("security_gate.file_finding_as_ticket")
    @patch("security_gate.scan_file")
    def test_no_tickets_filed_on_clean_scan(self, mock_scan, mock_file_ticket):
        """No tickets should be filed when scan is clean."""
        mock_scan.return_value = []

        result = run_gate(
            changed_files=["src/utils/format.py"],
            originating_task_id="swa-test",
        )
        assert result == []
        mock_file_ticket.assert_not_called()

    @patch("security_gate.file_finding_as_ticket")
    @patch("security_gate.scan_file")
    def test_skips_none_ticket_ids(self, mock_scan, mock_file_ticket):
        """If filing fails (returns None), that ID should not be in results."""
        mock_scan.return_value = [
            {
                "file_path": "CLAUDE.md",
                "line_number": 10,
                "category": "A",
                "severity": "critical",
                "description": "Finding 1",
                "matched_pattern": "pattern",
            },
            {
                "file_path": "CLAUDE.md",
                "line_number": 20,
                "category": "B",
                "severity": "high",
                "description": "Finding 2",
                "matched_pattern": "pattern2",
            },
        ]
        # First filing succeeds, second fails
        mock_file_ticket.side_effect = ["swa-t1", None]

        result = run_gate(
            changed_files=["CLAUDE.md"],
            originating_task_id="swa-test",
        )
        assert result == ["swa-t1"]

    @patch("security_gate.file_finding_as_ticket")
    @patch("security_gate.scan_file")
    def test_passes_originating_task_to_file_ticket(self, mock_scan, mock_file_ticket):
        """Originating task ID should be passed through to file_finding_as_ticket."""
        mock_scan.return_value = [
            {
                "file_path": "CLAUDE.md",
                "line_number": 10,
                "category": "A",
                "severity": "critical",
                "description": "Finding",
                "matched_pattern": "pattern",
            },
        ]
        mock_file_ticket.return_value = "swa-new1"

        run_gate(
            changed_files=["CLAUDE.md"],
            originating_task_id="swa-orig-123",
        )

        mock_file_ticket.assert_called_once()
        # Second argument should be the originating task ID
        _, task_id = mock_file_ticket.call_args[0]
        assert task_id == "swa-orig-123"
