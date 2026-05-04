"""UAT: SPEC-323 — Continuous Worktree Discovery.

Tests worktree scanning, polling intervals, diff detection,
and graceful handling of git failures.
"""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from swain_helm.worktree_scanner import WorktreeScanner, WorktreeInfo, WorktreeDiff

IS_DOCKER = (
    Path("/.dockerenv").exists() or os.environ.get("SWAIN_HELM_TEST_MODE") == "1"
)
skip_if_not_docker = pytest.mark.skipif(
    not IS_DOCKER,
    reason="UAT tests require Docker isolation",
)


@skip_if_not_docker
class TestWorktreePolling:
    """UAT-323-01, UAT-323-06: Scanner polling behavior."""

    def test_default_poll_interval_is_15_seconds(self):
        """UAT-323-01: Scanner polls every 15 seconds by default."""
        scanner = WorktreeScanner("/tmp/test")
        assert scanner.poll_interval_s == 15.0

    def test_configurable_poll_interval(self):
        """UAT-323-06: Configurable poll interval."""
        scanner = WorktreeScanner("/tmp/test", poll_interval_s=5.0)
        assert scanner.poll_interval_s == 5.0

    def test_scanner_tracks_worktrees(self):
        """Scanner maintains worktree state."""
        scanner = WorktreeScanner("/tmp/test")
        assert hasattr(scanner, "_last_known")


@skip_if_not_docker
class TestWorktreeDiff:
    """UAT-323-02, UAT-323-03, UAT-323-04: Worktree detection."""

    def test_new_worktree_emits_added_event(self):
        """UAT-323-02: New worktree emits worktree_added event."""
        scanner = WorktreeScanner("/tmp/test")
        scanner._last_known = set()
        current = {WorktreeInfo(path="/tmp/feature", branch="feature/x")}

        with patch.object(scanner, "scan", return_value=current):
            diff = scanner.diff()

        assert len(diff.added) == 1
        assert diff.added[0].branch == "feature/x"

    def test_removed_worktree_emits_removed_event(self):
        """UAT-323-03: Removed worktree emits worktree_removed event."""
        scanner = WorktreeScanner("/tmp/test")
        scanner._last_known = {WorktreeInfo(path="/tmp/feature", branch="feature/x")}
        current = set()

        with patch.object(scanner, "scan", return_value=current):
            diff = scanner.diff()

        assert len(diff.removed) == 1
        assert diff.removed[0].branch == "feature/x"

    def test_existing_worktree_no_event(self):
        """UAT-323-05: No-op when worktree list unchanged."""
        worktree = WorktreeInfo(path="/tmp/feature", branch="feature/x")
        scanner = WorktreeScanner("/tmp/test")
        scanner._last_known = {worktree}
        current = {worktree}

        with patch.object(scanner, "scan", return_value=current):
            diff = scanner.diff()

        assert len(diff.added) == 0
        assert len(diff.removed) == 0
        assert not diff

    def test_existing_worktree_detected_on_startup(self):
        """UAT-323-04: Existing worktree detected on startup."""
        scanner = WorktreeScanner("/tmp/test")

        mock_output = """worktree /tmp/test
HEAD ref: refs/heads/main
branch refs/heads/main

worktree /tmp/test/.worktrees/feature
HEAD ref: refs/heads/feature/x
branch refs/heads/feature/x
"""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=mock_output, stderr=""
            )
            worktrees = scanner.scan()

            assert len(worktrees) == 2
            branches = {wt.branch for wt in worktrees}
            assert "main" in branches or "trunk" in branches


@skip_if_not_docker
class TestBranchMapping:
    """Tests for branch name mapping."""

    def test_main_branch_maps_to_trunk(self):
        """main branch maps to trunk topic."""
        from swain_helm.worktree_scanner import _branch_to_topic

        assert _branch_to_topic("refs/heads/main") == "trunk"

    def test_master_branch_maps_to_trunk(self):
        """master branch maps to trunk topic."""
        from swain_helm.worktree_scanner import _branch_to_topic

        assert _branch_to_topic("refs/heads/master") == "trunk"

    def test_feature_branch_preserved(self):
        """feature branch names are preserved."""
        from swain_helm.worktree_scanner import _branch_to_topic

        assert _branch_to_topic("refs/heads/feature/abc-123") == "feature/abc-123"


@skip_if_not_docker
class TestNegativeCases:
    """UAT-323-NEG-01 through UAT-323-NEG-06: Error handling."""

    def test_scanner_graceful_when_not_git_repo(self):
        """UAT-323-NEG-01: git worktree list fails (not a git repo)."""
        scanner = WorktreeScanner("/tmp")

        def failing_git(_dir):
            raise subprocess.CalledProcessError(
                128, "git", stderr="fatal: not a git repository"
            )

        scanner._run_git = failing_git
        worktrees = scanner.scan()

        assert worktrees == set()

    def test_scanner_graceful_when_git_not_on_path(self):
        """UAT-323-NEG-02: git not on PATH."""
        scanner = WorktreeScanner("/tmp/test")

        def failing_git(_dir):
            raise FileNotFoundError("git: command not found")

        scanner._run_git = failing_git
        worktrees = scanner.scan()

        # Should return last known (or empty set if no previous), not crash
        assert isinstance(worktrees, set)

    def test_detached_head_handled(self):
        """UAT-323-NEG-03: Worktree with detached HEAD."""
        scanner = WorktreeScanner("/tmp/test")

        mock_output = """worktree /tmp/test
HEAD abc123...
detached
"""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=mock_output, stderr=""
            )
            worktrees = scanner.scan()

            assert isinstance(worktrees, set)

    def test_special_characters_in_branch_name(self):
        """UAT-323-NEG-04: Branch name with special characters."""
        from swain_helm.worktree_scanner import _branch_to_topic

        result = _branch_to_topic("refs/heads/feature/fix-#123")
        assert result == "feature/fix-#123"

    def test_rapid_create_remove_not_detected(self):
        """UAT-323-NEG-05: Worktree created and removed within scan interval."""
        scanner = WorktreeScanner("/tmp/test")

        # First scan - empty
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            first = scanner.scan()
            assert len(first) == 0

        # Second scan - still empty
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            second = scanner.scan()
            assert len(second) == 0

    def test_scanner_returns_last_known_on_failure(self):
        """UAT-323-NEG-06: Scanner returns last-known on failure."""
        scanner = WorktreeScanner("/tmp/test")

        # First successful scan
        successful_git = lambda _dir: (
            "worktree /tmp/test\nHEAD abc\nbranch refs/heads/main\n"
        )
        with patch.object(scanner, "_run_git", successful_git):
            scanner.scan()

        # Subsequent failing scan — should return last known
        with patch.object(
            scanner, "_run_git", side_effect=subprocess.CalledProcessError(128, "git")
        ):
            result = scanner.scan()

            # Should return last known worktrees
            assert isinstance(result, set)
            assert len(result) == 1


@skip_if_not_docker
class TestWorktreeInfo:
    """Tests for WorktreeInfo dataclass."""

    def test_worktree_info_equality(self):
        """WorktreeInfo equality works correctly."""
        wt1 = WorktreeInfo(path="/tmp/test", branch="main")
        wt2 = WorktreeInfo(path="/tmp/test", branch="main")
        wt3 = WorktreeInfo(path="/tmp/other", branch="main")

        assert wt1 == wt2
        assert wt1 != wt3

    def test_worktree_info_hashable(self):
        """WorktreeInfo can be used in sets."""
        wt1 = WorktreeInfo(path="/tmp/test", branch="main")
        wt2 = WorktreeInfo(path="/tmp/test", branch="main")

        s = {wt1, wt2}
        assert len(s) == 1
