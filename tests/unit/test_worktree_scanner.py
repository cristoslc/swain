"""Tests for WorktreeScanner — SPEC-323 continuous worktree discovery."""

import asyncio
from unittest.mock import patch

import pytest

from swain_helm.worktree_scanner import (
    WorktreeScanner,
    WorktreeInfo,
    WorktreeDiff,
    _branch_to_topic,
)


SAMPLE_PORCELAIN = """\
worktree /tmp/swain
branch refs/heads/main

worktree /tmp/swain/.worktrees/feat/foo
branch refs/heads/feat/foo

worktree /tmp/swain/.worktrees/hotfix/bar
branch refs/heads/hotfix/bar
"""

SAMPLE_PORCELAIN_MASTER = """\
worktree /tmp/proj
branch refs/heads/master
"""

SAMPLE_PORCELAIN_DETACHED = """\
worktree /tmp/detached
detached
"""

SAMPLE_PORCELAIN_EMPTY = ""


class TestBranchToTopic:
    def test_main_maps_to_trunk(self):
        assert _branch_to_topic("refs/heads/main") == "trunk"

    def test_master_maps_to_trunk(self):
        assert _branch_to_topic("refs/heads/master") == "trunk"

    def test_feature_branch(self):
        assert _branch_to_topic("refs/heads/feat/foo") == "feat/foo"

    def test_bare_branch_name(self):
        assert _branch_to_topic("my-branch") == "my-branch"


class TestWorktreeInfo:
    def test_equality(self):
        a = WorktreeInfo(path="/tmp/a", branch="trunk")
        b = WorktreeInfo(path="/tmp/a", branch="trunk")
        assert a == b

    def test_inequality(self):
        a = WorktreeInfo(path="/tmp/a", branch="trunk")
        b = WorktreeInfo(path="/tmp/b", branch="trunk")
        assert a != b

    def test_hashable(self):
        s = {WorktreeInfo(path="/tmp/a", branch="trunk")}
        assert len(s) == 1


class TestScan:
    def test_parse_porcelain(self):
        scanner = WorktreeScanner("/tmp/swain", run_git=lambda d: SAMPLE_PORCELAIN)
        result = scanner.scan()
        assert len(result) == 3
        assert WorktreeInfo(path="/tmp/swain", branch="trunk") in result
        assert (
            WorktreeInfo(path="/tmp/swain/.worktrees/feat/foo", branch="feat/foo")
            in result
        )
        assert (
            WorktreeInfo(path="/tmp/swain/.worktrees/hotfix/bar", branch="hotfix/bar")
            in result
        )

    def test_master_branch_maps_to_trunk(self):
        scanner = WorktreeScanner(
            "/tmp/proj", run_git=lambda d: SAMPLE_PORCELAIN_MASTER
        )
        result = scanner.scan()
        assert len(result) == 1
        assert WorktreeInfo(path="/tmp/proj", branch="trunk") in result

    def test_detached_gets_trunk(self):
        scanner = WorktreeScanner(
            "/tmp/detached", run_git=lambda d: SAMPLE_PORCELAIN_DETACHED
        )
        result = scanner.scan()
        assert len(result) == 1
        info = list(result)[0]
        assert info.branch == "trunk"

    def test_empty_output(self):
        scanner = WorktreeScanner(
            "/tmp/empty", run_git=lambda d: SAMPLE_PORCELAIN_EMPTY
        )
        result = scanner.scan()
        assert len(result) == 0

    def test_git_failure_returns_empty(self):
        def fail(d):
            raise RuntimeError("git not found")

        scanner = WorktreeScanner("/tmp/bad", run_git=fail)
        result = scanner.scan()
        assert len(result) == 0


class TestDiff:
    def test_first_diff_returns_all_as_added(self):
        scanner = WorktreeScanner("/tmp/swain", run_git=lambda d: SAMPLE_PORCELAIN)
        diff = scanner.diff()
        assert len(diff.added) == 3
        assert len(diff.removed) == 0

    def test_no_change_empty_diff(self):
        scanner = WorktreeScanner("/tmp/swain", run_git=lambda d: SAMPLE_PORCELAIN)
        scanner.diff()
        diff2 = scanner.diff()
        assert not diff2

    def test_worktree_added(self):
        call_count = 0
        outputs = [
            SAMPLE_PORCELAIN,
            SAMPLE_PORCELAIN + "\nworktree /tmp/new\nbranch refs/heads/new\n\n",
        ]

        def git(d):
            nonlocal call_count
            out = outputs[min(call_count, len(outputs) - 1)]
            call_count += 1
            return out

        scanner = WorktreeScanner("/tmp/swain", run_git=git)
        scanner.diff()
        diff2 = scanner.diff()
        assert len(diff2.added) == 1
        assert diff2.added[0].branch == "new"

    def test_worktree_removed(self):
        call_count = 0
        outputs = [
            SAMPLE_PORCELAIN,
            """worktree /tmp/swain
branch refs/heads/main

""",
        ]

        def git(d):
            nonlocal call_count
            out = outputs[min(call_count, len(outputs) - 1)]
            call_count += 1
            return out

        scanner = WorktreeScanner("/tmp/swain", run_git=git)
        scanner.diff()
        diff2 = scanner.diff()
        assert len(diff2.removed) == 2
        branches = {w.branch for w in diff2.removed}
        assert "feat/foo" in branches
        assert "hotfix/bar" in branches


class TestDiffBool:
    def test_empty_is_falsy(self):
        assert not WorktreeDiff()

    def test_with_added_is_truthy(self):
        assert WorktreeDiff(added=[WorktreeInfo(path="/x", branch="x")])

    def test_with_removed_is_truthy(self):
        assert WorktreeDiff(removed=[WorktreeInfo(path="/x", branch="x")])


class TestBackgroundPolling:
    @pytest.mark.asyncio
    async def test_start_and_stop(self):
        calls = []
        scanner = WorktreeScanner(
            "/tmp/swain", poll_interval_s=0.05, run_git=lambda d: SAMPLE_PORCELAIN
        )
        task = scanner.start_background(lambda d: calls.append(d))
        await asyncio.sleep(0.15)
        scanner.stop_background()
        assert len(calls) >= 1
        assert len(calls[0].added) == 3
