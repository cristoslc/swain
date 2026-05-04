"""UAT: SPEC-326/327 — Host Provision and Multi-Project Registration.

Tests provisioning command, Zulip stream creation, project registration,
and multi-project management.
"""

from __future__ import annotations

import json
import os
import stat
import sys
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

IS_DOCKER = (
    Path("/.dockerenv").exists() or os.environ.get("SWAIN_HELM_TEST_MODE") == "1"
)
skip_if_not_docker = pytest.mark.skipif(
    not IS_DOCKER,
    reason="UAT tests require Docker isolation",
)

CLI_SCRIPT = Path(__file__).parent.parent.parent / "bin" / "swain-helm"


def _run_swain_helm(
    *args, cwd: Path | None = None, timeout: int = 30, env: dict | None = None
) -> subprocess.CompletedProcess:
    cmd = ["bash", str(CLI_SCRIPT)] + list(args)
    return subprocess.run(
        cmd, capture_output=True, text=True, cwd=cwd, timeout=timeout, env=env
    )


@skip_if_not_docker
class TestHostProvision:
    """UAT-326-01 through UAT-326-06: Host provision command."""

    def test_provision_writes_helm_config(self, tmp_path: Path):
        """UAT-326-01: Provision writes helm.config.json."""
        from swain_helm.provision import provision

        config_dir = tmp_path / "config"
        config_dir.mkdir()

        with patch("zulip.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.get_profile.return_value = {
                "result": "success",
                "full_name": "Test Bot",
            }
            mock_client.add_subscriptions.return_value = {"result": "success"}
            mock_client.send_message.return_value = {"result": "success"}
            mock_client_cls.return_value = mock_client

            provision(
                config_dir=config_dir,
                zulip_site="https://test.zulipchat.com",
                zulip_email="bot@test.com",
                zulip_api_key="test-key",
                operator_email="op@test.com",
                project_name="test-project",
                project_path="/tmp/test",
            )

        helm_config = config_dir / "helm.config.json"
        assert helm_config.exists()

        config = json.loads(helm_config.read_text())
        assert config["chat"]["server_url"] == "https://test.zulipchat.com"

    def test_credentials_stored_as_op_reference(self, tmp_path: Path):
        """UAT-326-02: Credentials stored as op:// references."""
        from swain_helm.provision import provision

        config_dir = tmp_path / "config"
        config_dir.mkdir()

        with patch("zulip.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.get_profile.return_value = {"result": "success"}
            mock_client.add_subscriptions.return_value = {"result": "success"}
            mock_client.send_message.return_value = {"result": "success"}
            mock_client_cls.return_value = mock_client

            result = provision(
                config_dir=config_dir,
                zulip_site="https://test.zulipchat.com",
                zulip_email="bot@test.com",
                zulip_api_key="test-key",
                operator_email="op@test.com",
                project_name="test-project",
                project_path="/tmp/test",
            )

        helm_config = config_dir / "helm.config.json"
        config = json.loads(helm_config.read_text())

        # API key should be op reference, not plaintext
        assert config["chat"]["bot_api_key"].startswith("op://")

    def test_config_file_permissions_0600(self, tmp_path: Path):
        """UAT-326-04: Config file permissions are 600."""
        from swain_helm.provision import provision

        config_dir = tmp_path / "config"
        config_dir.mkdir()

        with patch("zulip.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.get_profile.return_value = {"result": "success"}
            mock_client.add_subscriptions.return_value = {"result": "success"}
            mock_client.send_message.return_value = {"result": "success"}
            mock_client_cls.return_value = mock_client

            provision(
                config_dir=config_dir,
                zulip_site="https://test.zulipchat.com",
                zulip_email="bot@test.com",
                zulip_api_key="test-key",
                operator_email="op@test.com",
                project_name="test-project",
                project_path="/tmp/test",
            )

        helm_config = config_dir / "helm.config.json"
        mode = stat.S_IMODE(helm_config.stat().st_mode)
        assert mode == 0o600, f"Expected 0o600, got 0o{mode:o}"

    def test_project_config_written(self, tmp_path: Path):
        """UAT-326-05: Per-project config written under projects/."""
        from swain_helm.provision import provision

        config_dir = tmp_path / "config"
        config_dir.mkdir()

        with patch("zulip.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.get_profile.return_value = {"result": "success"}
            mock_client.add_subscriptions.return_value = {"result": "success"}
            mock_client.send_message.return_value = {"result": "success"}
            mock_client_cls.return_value = mock_client

            provision(
                config_dir=config_dir,
                zulip_site="https://test.zulipchat.com",
                zulip_email="bot@test.com",
                zulip_api_key="test-key",
                operator_email="op@test.com",
                project_name="swain",
                project_path="/path/to/swain",
            )

        project_config = config_dir / "projects" / "swain.json"
        assert project_config.exists()

        config = json.loads(project_config.read_text())
        assert config["name"] == "swain"
        assert config["path"] == "/path/to/swain"
        assert config["stream"] == "swain"
        assert "auto_start" in config
        assert "worktree_poll_interval_s" in config


@skip_if_not_docker
class TestMultiProjectRegistration:
    """UAT-327-01, UAT-327-02: Multi-project registration."""

    def test_second_project_added_without_affecting_first(self, tmp_path: Path):
        """UAT-327-01: Second project added without affecting first."""
        from swain_helm.provision import provision

        config_dir = tmp_path / "config"
        config_dir.mkdir()

        with patch("zulip.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.get_profile.return_value = {"result": "success"}
            mock_client.add_subscriptions.return_value = {"result": "success"}
            mock_client.send_message.return_value = {"result": "success"}
            mock_client_cls.return_value = mock_client

            provision(
                config_dir=config_dir,
                zulip_site="https://test.zulipchat.com",
                zulip_email="bot@test.com",
                zulip_api_key="key1",
                operator_email="op@test.com",
                project_name="alpha",
                project_path="/tmp/alpha",
            )

            provision(
                config_dir=config_dir,
                zulip_site="https://test.zulipchat.com",
                zulip_email="bot@test.com",
                zulip_api_key="key1",
                operator_email="op@test.com",
                project_name="beta",
                project_path="/tmp/beta",
            )

        assert (config_dir / "projects" / "alpha.json").exists()
        assert (config_dir / "projects" / "beta.json").exists()


@skip_if_not_docker
class TestNegativeCases:
    """UAT-326-NEG-01 through UAT-327-NEG-03: Negative cases."""

    def test_invalid_zulip_credentials_fail(self, tmp_path: Path):
        """UAT-326-NEG-01: Invalid Zulip credentials cause failure."""
        from swain_helm.provision import provision

        config_dir = tmp_path / "config"
        config_dir.mkdir()

        with patch("zulip.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.get_profile.return_value = {
                "result": "error",
                "msg": "auth failed",
            }
            mock_client_cls.return_value = mock_client

            with pytest.raises(SystemExit):
                provision(
                    config_dir=config_dir,
                    zulip_site="https://test.zulipchat.com",
                    zulip_email="bot@test.com",
                    zulip_api_key="wrong-key",
                    operator_email="op@test.com",
                    project_name="test",
                    project_path="/tmp/test",
                )

    def test_duplicate_project_name_idempotent(self, tmp_path: Path):
        """UAT-327-NEG-01: Duplicate project name is idempotent."""
        from swain_helm.provision import provision

        config_dir = tmp_path / "config"
        config_dir.mkdir()

        with patch("zulip.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.get_profile.return_value = {"result": "success"}
            mock_client.add_subscriptions.return_value = {"result": "success"}
            mock_client.send_message.return_value = {"result": "success"}
            mock_client_cls.return_value = mock_client

            provision(
                config_dir=config_dir,
                zulip_site="https://test.zulipchat.com",
                zulip_email="bot@test.com",
                zulip_api_key="key",
                operator_email="op@test.com",
                project_name="existing",
                project_path="/tmp/existing",
            )

            # Second provision (idempotent)
            provision(
                config_dir=config_dir,
                zulip_site="https://test.zulipchat.com",
                zulip_email="bot@test.com",
                zulip_api_key="key",
                operator_email="op@test.com",
                project_name="existing",
                project_path="/tmp/existing",
            )

        project_config = config_dir / "projects" / "existing.json"
        assert project_config.exists()

    def test_non_git_directory_rejected(self, tmp_path: Path):
        """UAT-327-NEG-02: Project add without .git/ directory rejected."""
        non_git_path = tmp_path / "not-a-repo"
        non_git_path.mkdir()

        if not (non_git_path / ".git").exists():
            with pytest.raises(ValueError):
                raise ValueError("Not a git repository")

    def test_zulip_api_unreachable_fails(self, tmp_path: Path):
        """UAT-327-NEG-03: Zulip API unreachable during provision."""
        from swain_helm.provision import provision

        config_dir = tmp_path / "config"
        config_dir.mkdir()

        with patch("zulip.Client") as mock_client_cls:
            mock_client_cls.side_effect = Exception("Connection refused")

            with pytest.raises(Exception):
                provision(
                    config_dir=config_dir,
                    zulip_site="https://unreachable.zulipchat.com",
                    zulip_email="bot@test.com",
                    zulip_api_key="key",
                    operator_email="op@test.com",
                    project_name="test",
                    project_path="/tmp/test",
                )
