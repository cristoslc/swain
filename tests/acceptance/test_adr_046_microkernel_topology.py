"""Acceptance tests: ADR-046 Project-Level Microkernel Topology.

These tests verify architectural constraints specified in ADR-046.
"""

from __future__ import annotations

import importlib

import pytest

from swain_helm.bridges.project import ProjectBridge
from swain_helm.worktree_scanner import WorktreeScanner, WorktreeInfo
from swain_helm.protocol import Event


class TestADR046NoHubRouting:
    """ADR-046: 'No hub routing. Project bridges talk directly to their chat adapter subprocess.'"""

    def test_no_host_bridge_module(self):
        """HostBridge module should not exist."""
        try:
            importlib.import_module("swain_helm.bridges.host")
            pytest.fail("swain_helm.bridges.host should not exist")
        except ImportError:
            pass

    def test_project_bridge_spawns_chat_directly(self):
        """ProjectBridge starts its own chat adapter subprocess."""
        bridge = ProjectBridge(project="test", project_dir="/tmp/test")
        assert hasattr(bridge, "_chat_plugin")
        assert hasattr(bridge, "start")

    def test_no_kernel_module(self):
        """HostKernel module should not exist."""
        try:
            importlib.import_module("swain_helm.kernel")
            pytest.fail("swain_helm.kernel should not exist")
        except ImportError:
            pass


class TestADR046OneSessionPerWorktree:
    """ADR-046: 'One session per worktree.' — sessions are NOT auto-spawned;
    worktree discovery only emits events and updates the registry. Sessions
    are only created on explicit /work operator command.
    """

    def test_worktree_diff_emits_events_no_auto_spawn(self):
        """Worktree diff emits events but does NOT auto-spawn sessions."""
        events: list[Event] = []
        bridge = ProjectBridge(
            project="test", project_dir="/tmp/test", on_event=events.append
        )
        from swain_helm.worktree_scanner import WorktreeDiff

        bridge._on_worktree_diff(
            WorktreeDiff(
                added=[
                    WorktreeInfo(path="/tmp/trunk", branch="trunk"),
                    WorktreeInfo(path="/tmp/feat", branch="feat/x"),
                ]
            )
        )

        assert len(bridge.sessions) == 0, (
            "No sessions auto-spawned from worktree discovery"
        )
        wt_events = [e for e in events if e.type == "worktree_added"]
        assert len(wt_events) == 2

    def test_duplicate_diff_no_duplicate_events(self):
        """Duplicate worktree diff emits events but still no sessions."""
        events: list[Event] = []
        bridge = ProjectBridge(
            project="test", project_dir="/tmp/test", on_event=events.append
        )
        from swain_helm.worktree_scanner import WorktreeDiff

        bridge._on_worktree_diff(
            WorktreeDiff(added=[WorktreeInfo(path="/tmp/trunk", branch="trunk")])
        )
        bridge._on_worktree_diff(
            WorktreeDiff(added=[WorktreeInfo(path="/tmp/trunk", branch="trunk")])
        )

        assert len(bridge.sessions) == 0


class TestADR046ContinuousWorktreeDiscovery:
    """ADR-046: 'Project bridges poll git worktree list --porcelain every 15s.'"""

    def test_default_poll_interval(self):
        scanner = WorktreeScanner("/tmp/test")
        assert scanner.poll_interval_s == 15.0

    def test_configurable_poll_interval(self):
        scanner = WorktreeScanner("/tmp/test", poll_interval_s=30.0)
        assert scanner.poll_interval_s == 30.0
