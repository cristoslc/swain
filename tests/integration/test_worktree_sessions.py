"""Integration tests for worktree-driven session management.

Tests the wiring of WorktreeScanner + SessionRegistry into ProjectBridge,
covering the full lifecycle: worktree discovery → session creation →
worktree removal → session cleanup → registry persistence.
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from swain_helm.bridges.project import ProjectBridge, SessionState
from swain_helm.plugin_process import PluginProcess
from swain_helm.protocol import Event
from swain_helm.worktree_scanner import WorktreeScanner, WorktreeInfo, WorktreeDiff
from swain_helm.session_registry import SessionRegistry


TRUNK_PORCELAIN = """\
worktree /tmp/swain
branch refs/heads/main

"""

WITH_FEATURE = """\
worktree /tmp/swain
branch refs/heads/main

worktree /tmp/swain/.worktrees/feat/foo
branch refs/heads/feat/foo

"""


class TestWorktreeDrivenSessionCreation:
    """Scanner detects new worktrees → events emitted, registry updated, no auto-spawn.

    Sessions are only created on explicit /work operator command.
    """

    @pytest.mark.asyncio
    async def test_trunk_worktree_emits_event(self):
        events: list[Event] = []
        scanner = WorktreeScanner("/tmp/swain", run_git=lambda d: TRUNK_PORCELAIN)
        registry = SessionRegistry(str(Path("/tmp/swain")))
        bridge = ProjectBridge(
            project="swain",
            project_dir="/tmp/swain",
            on_event=events.append,
            scanner=scanner,
            registry=registry,
        )
        diff = WorktreeDiff(added=[WorktreeInfo(path="/tmp/swain", branch="trunk")])
        bridge._on_worktree_diff(diff)

        assert len(bridge.sessions) == 0, "No sessions auto-spawned"
        wt_events = [e for e in events if e.type == "worktree_added"]
        assert len(wt_events) == 1
        assert wt_events[0].payload["branch_name"] == "trunk"

    @pytest.mark.asyncio
    async def test_feature_branch_emits_event(self):
        events: list[Event] = []
        bridge = ProjectBridge(
            project="swain",
            project_dir="/tmp/swain",
            on_event=events.append,
        )
        diff = WorktreeDiff(
            added=[
                WorktreeInfo(path="/tmp/swain", branch="trunk"),
                WorktreeInfo(path="/tmp/swain/.worktrees/feat/foo", branch="feat/foo"),
            ]
        )
        bridge._on_worktree_diff(diff)

        wt_events = [e for e in events if e.type == "worktree_added"]
        assert len(wt_events) == 2
        assert len(bridge.sessions) == 0

    @pytest.mark.asyncio
    async def test_duplicate_worktree_emits_events_both_times(self):
        events: list[Event] = []
        bridge = ProjectBridge(
            project="swain",
            project_dir="/tmp/swain",
            on_event=events.append,
        )
        diff1 = WorktreeDiff(added=[WorktreeInfo(path="/tmp/swain", branch="trunk")])
        bridge._on_worktree_diff(diff1)
        diff2 = WorktreeDiff(added=[WorktreeInfo(path="/tmp/swain", branch="trunk")])
        bridge._on_worktree_diff(diff2)

        wt_events = [e for e in events if e.type == "worktree_added"]
        assert len(wt_events) == 2


class TestWorktreeDrivenSessionRemoval:
    """Scanner detects removed worktrees → events emitted, registry updated."""

    @pytest.mark.asyncio
    async def test_removed_worktree_emits_event(self):
        events: list[Event] = []
        bridge = ProjectBridge(
            project="swain",
            project_dir="/tmp/swain",
            on_event=events.append,
        )
        bridge._on_worktree_diff(
            WorktreeDiff(added=[WorktreeInfo(path="/tmp/swain", branch="trunk")])
        )
        events.clear()
        bridge._on_worktree_diff(
            WorktreeDiff(removed=[WorktreeInfo(path="/tmp/swain", branch="trunk")])
        )

        wt_events = [e for e in events if e.type == "worktree_removed"]
        assert len(wt_events) == 1


class TestWorktreeEvents:
    """worktree_added and worktree_removed events are emitted."""

    @pytest.mark.asyncio
    async def test_added_emits_worktree_added_event(self):
        events: list[Event] = []
        scanner = WorktreeScanner("/tmp/swain", run_git=lambda d: TRUNK_PORCELAIN)
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            bridge = ProjectBridge(
                project="swain",
                project_dir="/tmp/swain",
                on_event=events.append,
                scanner=scanner,
            )
            bridge._on_worktree_diff(
                WorktreeDiff(
                    added=[
                        WorktreeInfo(path="/tmp/swain", branch="trunk"),
                    ]
                )
            )
            await asyncio.sleep(0)

        wt_events = [e for e in events if e.type == "worktree_added"]
        assert len(wt_events) == 1
        assert wt_events[0].payload["branch_name"] == "trunk"
        assert wt_events[0].payload["worktree_path"] == "/tmp/swain"

    @pytest.mark.asyncio
    async def test_removed_emits_worktree_removed_event(self):
        events: list[Event] = []
        scanner = WorktreeScanner("/tmp/swain", run_git=lambda d: WITH_FEATURE)
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            with patch.object(PluginProcess, "stop", new_callable=AsyncMock):
                bridge = ProjectBridge(
                    project="swain",
                    project_dir="/tmp/swain",
                    on_event=events.append,
                    scanner=scanner,
                )
                bridge._on_worktree_diff(
                    WorktreeDiff(
                        added=[
                            WorktreeInfo(path="/tmp/swain", branch="trunk"),
                        ]
                    )
                )
                await asyncio.sleep(0)
                events.clear()

                bridge._on_worktree_diff(
                    WorktreeDiff(
                        removed=[
                            WorktreeInfo(path="/tmp/swain", branch="trunk"),
                        ]
                    )
                )
                await asyncio.sleep(0)

        wt_events = [e for e in events if e.type == "worktree_removed"]
        assert len(wt_events) == 1


class TestRegistryIntegration:
    """Session state is persisted to the registry when worktree diffs are processed."""

    @pytest.mark.asyncio
    async def test_worktree_diff_writes_to_registry(self, tmp_path):
        registry = SessionRegistry(str(tmp_path))
        registry.read()
        bridge = ProjectBridge(
            project="swain",
            project_dir=str(tmp_path),
            registry=registry,
        )
        bridge._on_worktree_diff(
            WorktreeDiff(added=[WorktreeInfo(path=str(tmp_path), branch="trunk")])
        )

        entry = registry.get_entry("trunk")
        assert entry is not None
        assert entry["state"] == "available"
        assert entry.get("worktree_path") == str(tmp_path)

    @pytest.mark.asyncio
    async def test_worktree_removal_marks_dead_in_registry(self, tmp_path):
        registry = SessionRegistry(str(tmp_path))
        registry.read()
        bridge = ProjectBridge(
            project="swain",
            project_dir=str(tmp_path),
            registry=registry,
        )
        bridge._on_worktree_diff(
            WorktreeDiff(added=[WorktreeInfo(path=str(tmp_path), branch="feat/x")])
        )
        bridge._on_worktree_diff(
            WorktreeDiff(removed=[WorktreeInfo(path=str(tmp_path), branch="feat/x")])
        )

        entry = registry.get_entry("feat/x")
        assert entry is not None
        assert entry["state"] == "dead"

    @pytest.mark.asyncio
    async def test_registry_survives_bridge_restart(self, tmp_path):
        registry1 = SessionRegistry(str(tmp_path))
        registry1.read()
        bridge1 = ProjectBridge(
            project="swain",
            project_dir=str(tmp_path),
            registry=registry1,
        )
        bridge1._on_worktree_diff(
            WorktreeDiff(added=[WorktreeInfo(path=str(tmp_path), branch="trunk")])
        )

        registry2 = SessionRegistry(str(tmp_path))
        data = registry2.read()
        assert "trunk" in data
        assert data["trunk"]["state"] == "available"


class TestScannerDiffIntegration:
    """The scanner's diff() method correctly feeds _on_worktree_diff."""

    @pytest.mark.asyncio
    async def test_scan_diff_emits_added_and_removed_events(self):
        events: list[Event] = []
        call_count = 0
        outputs = [WITH_FEATURE, TRUNK_PORCELAIN]

        def git(d):
            nonlocal call_count
            out = outputs[min(call_count, len(outputs) - 1)]
            call_count += 1
            return out

        scanner = WorktreeScanner("/tmp/swain", run_git=git)
        bridge = ProjectBridge(
            project="swain",
            project_dir="/tmp/swain",
            on_event=events.append,
            scanner=scanner,
        )
        diff1 = scanner.diff()
        bridge._on_worktree_diff(diff1)
        added_events = [e for e in events if e.type == "worktree_added"]
        assert len(added_events) == 2

        events.clear()
        diff2 = scanner.diff()
        bridge._on_worktree_diff(diff2)
        removed_events = [e for e in events if e.type == "worktree_removed"]
        assert len(removed_events) == 1
