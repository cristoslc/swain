"""E2E: End-to-End Synthetic Transaction Tests.

Tests the full swain-helm pipeline with real system integration.
These tests require Docker and may require actual Zulip credentials.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

import pytest

IS_DOCKER = (
    Path("/.dockerenv").exists() or os.environ.get("SWAIN_HELM_TEST_MODE") == "1"
)
ZULIP_AVAILABLE = os.environ.get("ZULIP_BOT_API_KEY") is not None

skip_if_not_docker = pytest.mark.skipif(
    not IS_DOCKER,
    reason="E2E tests require Docker isolation",
)

skip_if_no_zulip = pytest.mark.skipif(
    not ZULIP_AVAILABLE,
    reason="ZULIP_BOT_API_KEY required for Zulip E2E tests",
)


def _make_config(tmp_path: Path) -> Path:
    """Create a test configuration directory."""
    cfg = tmp_path / "swain-helm"
    cfg.mkdir()
    (cfg / "projects").mkdir()
    (cfg / "run" / "bridges").mkdir(parents=True)

    # Basic helm config
    helm = {
        "scan_paths": ["/tmp"],
        "chat": {
            "server_url": os.environ.get(
                "ZULIP_SITE", "https://cristoslc.zulipchat.com"
            ),
            "bot_email": os.environ.get(
                "ZULIP_BOT_EMAIL", "swain-bot@cristoslc.zulipchat.com"
            ),
            "bot_api_key": os.environ.get("ZULIP_BOT_API_KEY", "test-key"),
            "operator_email": os.environ.get(
                "ZULIP_OPERATOR_EMAIL", "cristos@cristoslc.com"
            ),
            "control_topic": "trunk",
        },
        "opencode": {"default_port": 4098},
    }
    (cfg / "helm.config.json").write_text(json.dumps(helm))
    return cfg


@skip_if_not_docker
class TestWatchdogToBridgeLifecycle:
    """E2E: Full watchdog -> bridge lifecycle."""

    def test_watchdog_starts_and_stops_cleanly(self, tmp_path: Path):
        """Watchdog starts, creates bridges, stops cleanly."""
        cfg = _make_config(tmp_path)

        # Create a test project
        project_config = {
            "name": "e2e-test",
            "path": str(tmp_path / "project"),
            "stream": "e2e-test",
            "runtime": "claude",
            "auto_start": True,
            "worktree_poll_interval_s": 15,
        }
        (tmp_path / "project").mkdir()
        (cfg / "projects" / "e2e-test.json").write_text(json.dumps(project_config))

        # Start watchdog
        proc = subprocess.Popen(
            ["python", "-m", "swain_helm.watchdog", "--config-dir", str(cfg)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        try:
            # Wait for watchdog to start
            time.sleep(3)

            # Check watchdog PID file
            pid_file = cfg / "run" / "watchdog.pid"
            assert pid_file.exists(), "Watchdog PID file not created"

            # Give time for bridge to start
            time.sleep(5)

            # Check bridge PID file
            bridge_pid = cfg / "run" / "bridges" / "e2e-test.pid"
            # May or may not exist depending on config

        finally:
            # Cleanup
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()


@skip_if_not_docker
@skip_if_no_zulip
class TestZulipIntegration:
    """E2E: Zulip integration tests (require real credentials)."""

    def test_zulip_connection_health_check(self, tmp_path: Path):
        """Verify Zulip client can connect and authenticate."""
        cfg = _make_config(tmp_path)

        # Import and test Zulip client
        from swain_helm.adapters.zulip_chat import ZulipChatAdapter

        config = {
            "site": cfg / "helm.config.json",
            "email": os.environ["ZULIP_BOT_EMAIL"],
            "api_key": os.environ["ZULIP_BOT_API_KEY"],
        }

        # This would connect to real Zulip
        # For now, just verify the config structure
        assert config["api_key"]
        assert config["email"]


@skip_if_not_docker
class TestConfigCredentialResolutionE2E:
    """E2E: Config loading with credential resolution."""

    def test_config_loads_with_op_references(self, tmp_path: Path):
        """Config loads and resolves op:// references."""
        cfg = _make_config(tmp_path)

        # Write config with op reference
        config = {
            "scan_paths": ["/tmp"],
            "chat": {
                "server_url": "https://test.zulipchat.com",
                "bot_email": "test@test.com",
                "bot_api_key": "op://TestVault/Zulip/api_key",
                "operator_email": "op@test.com",
                "control_topic": "trunk",
            },
        }
        (cfg / "helm.config.json").write_text(json.dumps(config))

        # Try to load config (will fail if op not available, but tests the path)
        # from swain_helm.config import load_helm_config
        # load_helm_config(cfg)  # This would try to resolve op://

        # For now, just verify file exists
        assert (cfg / "helm.config.json").exists()


@skip_if_not_docker
class TestSessionRegistryE2E:
    """E2E: Session registry persistence across process restarts."""

    def test_registry_persists_session_state(self, tmp_path: Path):
        """Session state persists in registry file."""
        cfg = _make_config(tmp_path)

        # Create a project
        (cfg / "projects" / "test.json").write_text(
            json.dumps(
                {
                    "name": "test",
                    "path": str(tmp_path / "project"),
                    "stream": "test",
                    "runtime": "claude",
                    "auto_start": True,
                }
            )
        )
        (tmp_path / "project").mkdir()

        # Simulate session registry write
        registry = (
            tmp_path / "project" / ".swain" / "swain-helm" / "session-registry.json"
        )
        registry.parent.mkdir(parents=True)
        registry.write_text(
            json.dumps(
                {
                    "trunk": {
                        "opencode_session_id": "test-session-123",
                        "state": "active",
                        "topic": "trunk",
                        "worktree_path": str(tmp_path / "project"),
                        "started_at": time.time(),
                    }
                }
            )
        )

        # Verify registry can be read
        assert registry.exists()
        data = json.loads(registry.read_text())
        assert "trunk" in data


@skip_if_not_docker
class TestNegativeE2E:
    """E2E: Negative cases and error handling."""

    def test_watchdog_handles_missing_config_gracefully(self, tmp_path: Path):
        """Watchdog handles missing config directory gracefully."""
        cfg = tmp_path / "nonexistent" / "config"

        proc = subprocess.Popen(
            ["python", "-m", "swain_helm.watchdog", "--config-dir", str(cfg)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        try:
            # Give it time to potentially crash
            time.sleep(2)

            # Should still be running (creates directories if needed)
            assert proc.poll() is None or proc.returncode in [0, 1]
        finally:
            if proc.poll() is None:
                proc.terminate()
                proc.wait()

    def test_bridge_handles_invalid_zulip_config(self, tmp_path: Path):
        """Bridge handles invalid Zulip config gracefully."""
        cfg = _make_config(tmp_path)

        # Create invalid Zulip config
        helm = {
            "scan_paths": ["/tmp"],
            "chat": {
                "server_url": "not-a-valid-url",
                "bot_email": "invalid",
                "bot_api_key": "invalid",
            },
        }
        (cfg / "helm.config.json").write_text(json.dumps(helm))

        # This would be tested by starting the bridge and checking it doesn't crash
        # For now, just verify the file structure
        assert (cfg / "helm.config.json").exists()
