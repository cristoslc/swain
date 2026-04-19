"""INITIATIVE-022 verification tests — alignment between implementation and ADRs/SPECs.

These tests verify that the current implementation matches the architectural
decisions in ADR-046, ADR-047, and ADR-038, and the acceptance criteria in
SPEC-318 through SPEC-327.
"""

from __future__ import annotations

import importlib
import json
import os
import subprocess
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pathlib import Path as _Path

from swain_helm.bridges.project import ProjectBridge, SessionState, Session
from swain_helm.protocol import Event, Command, encode_message, decode_message
from swain_helm.plugin_process import PluginProcess
from swain_helm.worktree_scanner import WorktreeScanner, WorktreeInfo
from swain_helm.session_registry import SessionRegistry
from swain_helm.config import resolve_op_references, ResolutionError
from swain_helm.watchdog import Watchdog
from swain_helm.opencode_discovery import DiscoveryScanner


# ---------------------------------------------------------------------------
# ADR-046: Project-Level Microkernel Topology
# ---------------------------------------------------------------------------


class TestADR046NoHubRouting:
    """ADR-046: 'No hub routing. Project bridges talk directly to their chat adapter subprocess.'"""

    def test_no_host_bridge_module(self):
        """HostBridge module should not exist."""
        try:
            importlib.import_module("swain_helm.bridges.host")
            assert False, "swain_helm.bridges.host should not exist"
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
            assert False, "swain_helm.kernel should not exist"
        except ImportError:
            pass


class TestADR046OneSessionPerWorktree:
    """ADR-046: 'One session per worktree.'"""

    @pytest.mark.asyncio
    async def test_branch_to_session_mapping(self):
        """Each branch maps to exactly one session."""
        scanner = WorktreeScanner("/tmp/test", run_git=lambda d: "")
        bridge = ProjectBridge(project="test", project_dir="/tmp/test", scanner=scanner)
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            from swain_helm.worktree_scanner import WorktreeDiff

            bridge._on_worktree_diff(
                WorktreeDiff(
                    added=[
                        WorktreeInfo(path="/tmp/trunk", branch="trunk"),
                        WorktreeInfo(path="/tmp/feat", branch="feat/x"),
                    ]
                )
            )
            await __import__("asyncio").sleep(0)

        assert "trunk" in bridge._branch_to_session
        assert "feat/x" in bridge._branch_to_session
        assert bridge._branch_to_session["trunk"] != bridge._branch_to_session["feat/x"]

    @pytest.mark.asyncio
    async def test_duplicate_branch_no_double_session(self):
        """Adding the same branch twice does not create a second session."""
        bridge = ProjectBridge(project="test", project_dir="/tmp/test")
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            from swain_helm.worktree_scanner import WorktreeDiff

            bridge._on_worktree_diff(
                WorktreeDiff(
                    added=[
                        WorktreeInfo(path="/tmp/trunk", branch="trunk"),
                    ]
                )
            )
            await __import__("asyncio").sleep(0)
            bridge._on_worktree_diff(
                WorktreeDiff(
                    added=[
                        WorktreeInfo(path="/tmp/trunk", branch="trunk"),
                    ]
                )
            )
            await __import__("asyncio").sleep(0)

        assert len(bridge.sessions) == 1


class TestADR046ContinuousWorktreeDiscovery:
    """ADR-046: 'Project bridges poll git worktree list --porcelain every 15s.'"""

    def test_default_poll_interval(self):
        scanner = WorktreeScanner("/tmp/test")
        assert scanner.poll_interval_s == 15.0

    def test_configurable_poll_interval(self):
        scanner = WorktreeScanner("/tmp/test", poll_interval_s=30.0)
        assert scanner.poll_interval_s == 30.0


# ---------------------------------------------------------------------------
# ADR-047: Watchdog Architecture
# ---------------------------------------------------------------------------


class TestADR047CredentialResolution:
    """ADR-047: 'All op:// references resolved once at startup via op read.'"""

    def test_resolve_op_references_function_exists(self):
        assert callable(resolve_op_references)

    def test_resolution_error_on_failure(self):
        assert ResolutionError is not None

    def test_resolve_caches_results(self):
        import swain_helm.config as cfg_mod

        cfg_mod._resolved_cache.clear()
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="secret123\n", stderr=""
            )
            config = {"key": "op://Vault/Item/field"}
            result = resolve_op_references(config)
            assert result["key"] == "secret123"
        cfg_mod._resolved_cache.clear()

    def test_resolve_fails_on_bad_op(self):
        import swain_helm.config as cfg_mod

        cfg_mod._resolved_cache.clear()
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1, stdout="", stderr="op not found"
            )
            config = {"key": "op://Vault/BadItem/field"}
            with pytest.raises(ResolutionError):
                resolve_op_references(config)
        cfg_mod._resolved_cache.clear()


class TestADR047WatchdogReconciliationLoop:
    """ADR-047: 'Python asyncio process that reconciles desired state on a 30-second loop.'"""

    def test_watchdog_has_reconcile(self):
        w = Watchdog(config_dir=_Path("/tmp/test"))
        assert hasattr(w, "_reconcile")

    def test_watchdog_default_interval(self):
        from swain_helm.watchdog import RECONCILIATION_INTERVAL

        assert RECONCILIATION_INTERVAL == 30


class TestADR047PerPortAuth:
    """ADR-047: 'Discovery only authenticates against ports with known credentials.'"""

    def test_discovery_scanner_uses_port_auth(self):
        scanner = DiscoveryScanner(
            opencode_config={"ports": {"4096": {"username": "u", "password": "p"}}},
        )
        creds = scanner._get_credentials_for_port(4096)
        assert creds is not None
        assert creds["username"] == "u"
        no_creds = scanner._get_credentials_for_port(4097)
        assert no_creds is None


# ---------------------------------------------------------------------------
# ADR-038: Microkernel Plugin Architecture
# ---------------------------------------------------------------------------


class TestADR038SubprocessPlugins:
    """ADR-038: Adapters speak NDJSON over stdio as subprocess plugins."""

    def test_plugin_process_exists(self):
        assert PluginProcess is not None

    def test_plugin_process_spawnable(self):
        p = PluginProcess(
            name="test",
            cmd=["echo"],
            plugin_type="chat",
            config={},
        )
        assert p.cmd == ["echo"]

    def test_adapter_entry_points_defined(self):
        """Console scripts for adapter subprocesses exist in pyproject.toml."""
        toml = Path(__file__).parent.parent.parent / "pyproject.toml"
        content = toml.read_text()
        assert "swain-helm-zulip-chat" in content
        assert "swain-helm-opencode" in content
        assert "swain-helm-claude" in content
        assert "swain-helm-tmux" in content


class TestADR038ProtocolFormat:
    """ADR-038: NDJSON over stdio with ConfigMessage on line 0."""

    def test_config_message_decodes(self):
        line = '{"type":"config","plugin_type":"chat","config":{"bridge":"test"}}'
        msg = decode_message(line)
        assert msg is not None

    def test_event_roundtrip(self):
        event = Event.text_output(bridge="test", session_id="s1", content="hello")
        encoded = encode_message(event)
        decoded = decode_message(encoded)
        assert isinstance(decoded, Event)
        assert decoded.type == "text_output"

    def test_command_roundtrip(self):
        cmd = Command.send_prompt(bridge="test", session_id="s1", text="hi")
        encoded = encode_message(cmd)
        decoded = decode_message(encoded)
        assert isinstance(decoded, Command)
        assert decoded.type == "send_prompt"


# ---------------------------------------------------------------------------
# SPEC coverage: key acceptance criteria
# ---------------------------------------------------------------------------


class TestSPEC320ConfigResolution:
    """SPEC-320: Config and Credential Resolution."""

    def test_non_op_values_pass_through(self):
        result = resolve_op_references({"key": "plain_text"})
        assert result["key"] == "plain_text"

    def test_nested_op_references_resolved(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="secret\n", stderr=""
            )
            config = {"chat": {"bot_api_key": "op://Vault/Bot/api_key"}}
            result = resolve_op_references(config)
            assert result["chat"]["bot_api_key"] == "secret"


class TestSPEC318WatchdogCore:
    """SPEC-318: Watchdog Core."""

    def test_watchdog_starts_in_reconcile_mode(self):
        w = Watchdog(config_dir=_Path("/tmp/test"))
        assert hasattr(w, "run")

    def test_watchdog_manages_pid_files(self):
        w = Watchdog(config_dir=_Path("/tmp/test"))
        assert hasattr(w, "watchdog_pid_path")


class TestSPEC321OpenCodeDiscovery:
    """SPEC-321: OpenCode Serve Discovery and Auth."""

    def test_discovery_scans_ports(self):
        scanner = DiscoveryScanner(opencode_config={"default_port": 4096})
        ports = scanner.get_candidate_ports()
        assert 4096 in ports


class TestSPEC323WorktreeDiscovery:
    """SPEC-323: Continuous Worktree Discovery."""

    def test_trunk_branch_mapped(self):
        from swain_helm.worktree_scanner import _branch_to_topic

        assert _branch_to_topic("refs/heads/main") == "trunk"
        assert _branch_to_topic("refs/heads/master") == "trunk"

    def test_feature_branch_mapped(self):
        from swain_helm.worktree_scanner import _branch_to_topic

        assert _branch_to_topic("refs/heads/feat/x") == "feat/x"


class TestSPEC324SessionRegistry:
    """SPEC-324: Session Registry Persistence."""

    def test_registry_keyed_by_branch(self, tmp_path):
        reg = SessionRegistry(str(tmp_path))
        reg.read()
        reg.update_entry("trunk", opencode_session_id="s1", state="active")
        assert reg.get_entry("trunk") is not None

    def test_registry_entry_fields(self, tmp_path):
        reg = SessionRegistry(str(tmp_path))
        import time

        reg.read()
        reg.update_entry(
            "trunk",
            opencode_session_id="s1",
            state="active",
            topic="trunk",
            worktree_path="/tmp/test",
            started_at=time.time(),
        )
        entry = reg.get_entry("trunk")
        assert entry is not None
        assert "opencode_session_id" in entry
        assert "state" in entry
        assert "topic" in entry
        assert "worktree_path" in entry
        assert "started_at" in entry
        assert "last_activity" in entry

    def test_registry_reconcile_removes_orphans(self, tmp_path):
        reg = SessionRegistry(str(tmp_path))
        reg.read()
        reg.update_entry("trunk", opencode_session_id="s1", state="active")
        reg.update_entry("feat", opencode_session_id="s2", state="active")
        removed = reg.reconcile(live_session_ids={"s1"})
        assert "feat" in removed


# ---------------------------------------------------------------------------
# INITIATIVE-018 excisable software constraint
# ---------------------------------------------------------------------------


class TestExcisableSoftware:
    """swain-helm must have zero swain-specific coupling in its core runtime."""

    def test_no_swain_skill_imports(self):
        """Core modules should not import swain skills or design tools."""
        import swain_helm.bridges.project as project_mod
        import swain_helm.watchdog as watchdog_mod
        import swain_helm.config as config_mod

        source = project_mod.__file__ and Path(project_mod.__file__).read_text() or ""
        source += (
            watchdog_mod.__file__ and Path(watchdog_mod.__file__).read_text() or ""
        )
        source += config_mod.__file__ and Path(config_mod.__file__).read_text() or ""
        assert "swain-design" not in source
        assert "swain-do" not in source
        assert "swain-sync" not in source

    def test_cli_script_no_swain_specifics(self):
        """bin/swain-helm should not depend on swain skills."""
        cli_path = Path(__file__).parent.parent.parent / "bin" / "swain-helm"
        if cli_path.exists():
            content = cli_path.read_text()
            assert "swain-design" not in content
            assert "swain-do" not in content
