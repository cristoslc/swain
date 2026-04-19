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
    """Scanner detects new worktrees → ProjectBridge auto-creates sessions."""

    @pytest.mark.asyncio
    async def test_trunk_session_created_on_first_poll(self):
        events: list[Event] = []
        scanner = WorktreeScanner("/tmp/swain", run_git=lambda d: TRUNK_PORCELAIN)
        registry = SessionRegistry("/tmp/swain")
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            bridge = ProjectBridge(
                project="swain",
                project_dir="/tmp/swain",
                on_event=events.append,
                scanner=scanner,
                registry=registry,
            )
            diff = WorktreeDiff(added=[WorktreeInfo(path="/tmp/swain", branch="trunk")])
            bridge._on_worktree_diff(diff)
            await asyncio.sleep(0)

        assert "trunk" in bridge._branch_to_session
        assert len(bridge.sessions) == 1
        sess = list(bridge.sessions.values())[0]
        assert sess.origin == "trunk"

    @pytest.mark.asyncio
    async def test_feature_branch_session_created(self):
        scanner = WorktreeScanner("/tmp/swain", run_git=lambda d: WITH_FEATURE)
        registry = SessionRegistry("/tmp/swain")
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            bridge = ProjectBridge(
                project="swain",
                project_dir="/tmp/swain",
                scanner=scanner,
                registry=registry,
            )
            diff = WorktreeDiff(
                added=[
                    WorktreeInfo(path="/tmp/swain", branch="trunk"),
                    WorktreeInfo(
                        path="/tmp/swain/.worktrees/feat/foo", branch="feat/foo"
                    ),
                ]
            )
            bridge._on_worktree_diff(diff)
            await asyncio.sleep(0)

        assert "trunk" in bridge._branch_to_session
        assert "feat/foo" in bridge._branch_to_session
        assert len(bridge.sessions) == 2

    @pytest.mark.asyncio
    async def test_duplicate_worktree_no_double_session(self):
        scanner = WorktreeScanner("/tmp/swain", run_git=lambda d: TRUNK_PORCELAIN)
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            bridge = ProjectBridge(
                project="swain",
                project_dir="/tmp/swain",
                scanner=scanner,
            )
            diff1 = WorktreeDiff(
                added=[WorktreeInfo(path="/tmp/swain", branch="trunk")]
            )
            bridge._on_worktree_diff(diff1)
            await asyncio.sleep(0)
            diff2 = WorktreeDiff(
                added=[WorktreeInfo(path="/tmp/swain", branch="trunk")]
            )
            bridge._on_worktree_diff(diff2)
            await asyncio.sleep(0)

        assert len(bridge.sessions) == 1


class TestWorktreeDrivenSessionRemoval:
    """Scanner detects removed worktrees → ProjectBridge cleans up sessions."""

    @pytest.mark.asyncio
    async def test_removed_worktree_aborts_session(self):
        scanner = WorktreeScanner("/tmp/swain", run_git=lambda d: WITH_FEATURE)
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            with patch.object(PluginProcess, "stop", new_callable=AsyncMock):
                bridge = ProjectBridge(
                    project="swain",
                    project_dir="/tmp/swain",
                    scanner=scanner,
                )
                bridge._on_worktree_diff(
                    WorktreeDiff(
                        added=[
                            WorktreeInfo(path="/tmp/swain", branch="trunk"),
                            WorktreeInfo(
                                path="/tmp/swain/.worktrees/feat/foo", branch="feat/foo"
                            ),
                        ]
                    )
                )
                await asyncio.sleep(0)
                assert len(bridge.sessions) == 2

                bridge._on_worktree_diff(
                    WorktreeDiff(
                        removed=[
                            WorktreeInfo(
                                path="/tmp/swain/.worktrees/feat/foo", branch="feat/foo"
                            ),
                        ]
                    )
                )
                await asyncio.sleep(0)

        assert "feat/foo" not in bridge._branch_to_session
        sess_id = None
        for sid, s in bridge.sessions.items():
            if s.origin == "feat/foo":
                sess_id = sid
        assert sess_id is not None
        assert bridge.sessions[sess_id].state == SessionState.DEAD


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
    """Session state is persisted to the registry when scanner creates/removes sessions."""

    @pytest.mark.asyncio
    async def test_session_creation_writes_to_registry(self, tmp_path):
        scanner = WorktreeScanner(str(tmp_path), run_git=lambda d: TRUNK_PORCELAIN)
        registry = SessionRegistry(str(tmp_path))
        registry.read()
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            bridge = ProjectBridge(
                project="swain",
                project_dir=str(tmp_path),
                scanner=scanner,
                registry=registry,
            )
            bridge._on_worktree_diff(
                WorktreeDiff(
                    added=[
                        WorktreeInfo(path=str(tmp_path), branch="trunk"),
                    ]
                )
            )
            await asyncio.sleep(0)

        entry = registry.get_entry("trunk")
        assert entry is not None
        assert entry["state"] == "spawning"
        assert entry["topic"] == "trunk"
        assert "opencode_session_id" in entry

    @pytest.mark.asyncio
    async def test_session_removal_marks_dead_in_registry(self, tmp_path):
        scanner = WorktreeScanner(str(tmp_path), run_git=lambda d: WITH_FEATURE)
        registry = SessionRegistry(str(tmp_path))
        registry.read()
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            with patch.object(PluginProcess, "stop", new_callable=AsyncMock):
                bridge = ProjectBridge(
                    project="swain",
                    project_dir=str(tmp_path),
                    scanner=scanner,
                    registry=registry,
                )
                bridge._on_worktree_diff(
                    WorktreeDiff(
                        added=[
                            WorktreeInfo(path=str(tmp_path), branch="trunk"),
                            WorktreeInfo(
                                path=str(tmp_path) + "/.worktrees/feat", branch="feat/x"
                            ),
                        ]
                    )
                )
                await asyncio.sleep(0)

                bridge._on_worktree_diff(
                    WorktreeDiff(
                        removed=[
                            WorktreeInfo(
                                path=str(tmp_path) + "/.worktrees/feat", branch="feat/x"
                            ),
                        ]
                    )
                )
                await asyncio.sleep(0)

        entry = registry.get_entry("feat/x")
        assert entry is not None
        assert entry["state"] == "dead"

    @pytest.mark.asyncio
    async def test_registry_survives_bridge_restart(self, tmp_path):
        """Registry data persists after bridge is torn down and re-read."""
        scanner1 = WorktreeScanner(str(tmp_path), run_git=lambda d: TRUNK_PORCELAIN)
        registry1 = SessionRegistry(str(tmp_path))
        registry1.read()
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            bridge1 = ProjectBridge(
                project="swain",
                project_dir=str(tmp_path),
                scanner=scanner1,
                registry=registry1,
            )
            bridge1._on_worktree_diff(
                WorktreeDiff(
                    added=[
                        WorktreeInfo(path=str(tmp_path), branch="trunk"),
                    ]
                )
            )
            await asyncio.sleep(0)

        registry2 = SessionRegistry(str(tmp_path))
        data = registry2.read()
        assert "trunk" in data
        assert data["trunk"]["state"] == "spawning"


class TestScannerDiffIntegration:
    """The scanner's diff() method correctly feeds _on_worktree_diff."""

    @pytest.mark.asyncio
    async def test_scan_diff_creates_and_removes_sessions(self):
        call_count = 0
        outputs = [WITH_FEATURE, TRUNK_PORCELAIN]

        def git(d):
            nonlocal call_count
            out = outputs[min(call_count, len(outputs) - 1)]
            call_count += 1
            return out

        scanner = WorktreeScanner("/tmp/swain", run_git=git)
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            with patch.object(PluginProcess, "stop", new_callable=AsyncMock):
                bridge = ProjectBridge(
                    project="swain",
                    project_dir="/tmp/swain",
                    scanner=scanner,
                )
                diff1 = scanner.diff()
                bridge._on_worktree_diff(diff1)
                await asyncio.sleep(0)
                assert len(bridge.sessions) == 2

                diff2 = scanner.diff()
                bridge._on_worktree_diff(diff2)
                await asyncio.sleep(0)

        assert "feat/foo" not in bridge._branch_to_session
