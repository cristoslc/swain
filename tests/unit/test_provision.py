"""Tests for SPEC-326: Host Provision Command and SPEC-327: Multi-Project Registration."""

import json
import stat
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from swain_helm.provision import provision


def _patch_zulip_client(mock_client):
    """Patch zulip.Client — imported inside provision(), not at module level."""
    import zulip

    return patch.object(zulip, "Client", return_value=mock_client)


def _mock_zulip():
    mock = MagicMock()
    mock.get_profile.return_value = {"result": "success", "full_name": "Bot"}
    mock.add_subscriptions.return_value = {"result": "success"}
    mock.send_message.return_value = {"result": "success"}
    return mock


class TestProvisionWritesConfigs:
    """SPEC-326: provision writes both helm.config.json and project config."""

    @pytest.fixture
    def config_dir(self, tmp_path: Path) -> Path:
        return tmp_path / "swain-helm"

    def test_writes_helm_config(self, config_dir: Path) -> None:
        with _patch_zulip_client(_mock_zulip()):
            provision(
                zulip_site="https://test.zulipchat.com",
                zulip_email="bot@test.zulipchat.com",
                zulip_api_key="test-key",
                operator_email="op@test.zulipchat.com",
                project_name="myproj",
                project_path="/home/user/myproj",
                config_dir=config_dir,
            )

        helm = json.loads((config_dir / "helm.config.json").read_text())
        assert helm["chat"]["server_url"] == "https://test.zulipchat.com"
        assert helm["chat"]["bot_api_key"].startswith("op://")
        assert "projects" in helm

    def test_writes_project_config_for_watchdog(self, config_dir: Path) -> None:
        with _patch_zulip_client(_mock_zulip()):
            provision(
                zulip_site="https://test.zulipchat.com",
                zulip_email="bot@test.zulipchat.com",
                zulip_api_key="test-key",
                operator_email="op@test.zulipchat.com",
                project_name="myproj",
                project_path="/home/user/myproj",
                config_dir=config_dir,
            )

        project = json.loads((config_dir / "projects" / "myproj.json").read_text())
        assert project["name"] == "myproj"
        assert project["auto_start"] is True
        assert project["runtime"] == "claude"

    def test_config_file_permissions_0600(self, config_dir: Path) -> None:
        with _patch_zulip_client(_mock_zulip()):
            provision(
                zulip_site="https://test.zulipchat.com",
                zulip_email="bot@test.zulipchat.com",
                zulip_api_key="test-key",
                operator_email="op@test.zulipchat.com",
                project_name="myproj",
                project_path="/home/user/myproj",
                config_dir=config_dir,
            )

        mode = stat.S_IMODE((config_dir / "helm.config.json").stat().st_mode)
        assert mode == 0o600

    def test_api_key_stored_as_op_reference(self, config_dir: Path) -> None:
        with _patch_zulip_client(_mock_zulip()):
            provision(
                zulip_site="https://test.zulipchat.com",
                zulip_email="bot@test.zulipchat.com",
                zulip_api_key="placeholder-not-a-real-key",
                operator_email="op@test.zulipchat.com",
                project_name="myproj",
                project_path="/home/user/myproj",
                config_dir=config_dir,
            )

        raw = (config_dir / "helm.config.json").read_text()
        assert "placeholder-not-a-real-key" not in raw
        helm = json.loads(raw)
        assert (
            helm["chat"]["bot_api_key"] == "op://Private/bot@test.zulipchat.com/api_key"
        )

    def test_stream_defaults_to_project_name_not_worktree_name(
        self, config_dir: Path
    ) -> None:
        """For worktrees, stream = the project (parent of .worktrees), not worktree name.

        This ensures all worktrees for the same project share one Zulip stream,
        differentiated by topic.
        """
        with _patch_zulip_client(_mock_zulip()):
            provision(
                zulip_site="https://test.zulipchat.com",
                zulip_email="bot@test.zulipchat.com",
                zulip_api_key="test-key",
                operator_email="op@test.zulipchat.com",
                project_name="swain",
                project_path="/home/user/swain/.worktrees/epic/epic-initiative-018-swain-helm-implementation",
                config_dir=config_dir,
            )

        project = json.loads(
            (
                config_dir
                / "projects"
                / "epic-initiative-018-swain-helm-implementation.json"
            ).read_text()
        )
        assert project["stream"] == "swain"
        assert project["name"] == "epic-initiative-018-swain-helm-implementation"

    def test_non_worktree_project_uses_basename_as_stream(
        self, config_dir: Path
    ) -> None:
        """Non-worktree projects use their directory name as the stream."""
        with _patch_zulip_client(_mock_zulip()):
            provision(
                zulip_site="https://test.zulipchat.com",
                zulip_email="bot@test.zulipchat.com",
                zulip_api_key="test-key",
                operator_email="op@test.zulipchat.com",
                project_name="myproj",
                project_path="/home/user/myproj",
                config_dir=config_dir,
            )

        project = json.loads((config_dir / "projects" / "myproj.json").read_text())
        assert project["stream"] == "myproj"
        assert project["name"] == "myproj"

    def test_stream_override_escape_hatch(self, config_dir: Path) -> None:
        """--stream overrides the derived stream name."""
        with _patch_zulip_client(_mock_zulip()):
            provision(
                zulip_site="https://test.zulipchat.com",
                zulip_email="bot@test.zulipchat.com",
                zulip_api_key="test-key",
                operator_email="op@test.zulipchat.com",
                project_name="myproj",
                project_path="/home/user/myproj",
                config_dir=config_dir,
                stream_name="custom-stream",
            )

        project = json.loads((config_dir / "projects" / "myproj.json").read_text())
        assert project["stream"] == "custom-stream"
        assert project["name"] == "myproj"

    def test_worktree_project_name_is_worktree_not_project(
        self, config_dir: Path
    ) -> None:
        """The project name in config is the worktree dir, not the repo name."""
        with _patch_zulip_client(_mock_zulip()):
            provision(
                zulip_site="https://test.zulipchat.com",
                zulip_email="bot@test.zulipchat.com",
                zulip_api_key="test-key",
                operator_email="op@test.zulipchat.com",
                project_name="swain",
                project_path="/home/user/swain/.worktrees/feature/add-auth",
                config_dir=config_dir,
            )

        project = json.loads((config_dir / "projects" / "add-auth.json").read_text())
        assert project["name"] == "add-auth"
        assert project["stream"] == "swain"

    def test_zulip_auth_failure_exits(self, config_dir: Path) -> None:
        mock = _mock_zulip()
        mock.get_profile.return_value = {"result": "error", "msg": "Invalid API key"}

        with _patch_zulip_client(mock):
            with pytest.raises(SystemExit):
                provision(
                    zulip_site="https://test.zulipchat.com",
                    zulip_email="bot@test.zulipchat.com",
                    zulip_api_key="bad-key",
                    operator_email="op@test.zulipchat.com",
                    project_name="myproj",
                    project_path="/home/user/myproj",
                    config_dir=config_dir,
                )

    def test_stream_creation_failure_exits(self, config_dir: Path) -> None:
        mock = _mock_zulip()
        mock.add_subscriptions.return_value = {
            "result": "error",
            "msg": "Stream creation failed",
        }

        with _patch_zulip_client(mock):
            with pytest.raises(SystemExit):
                provision(
                    zulip_site="https://test.zulipchat.com",
                    zulip_email="bot@test.zulipchat.com",
                    zulip_api_key="test-key",
                    operator_email="op@test.zulipchat.com",
                    project_name="myproj",
                    project_path="/home/user/myproj",
                    config_dir=config_dir,
                )

    def test_welcome_message_posted_to_trunk_topic(self, config_dir: Path) -> None:
        mock = _mock_zulip()
        with _patch_zulip_client(mock):
            provision(
                zulip_site="https://test.zulipchat.com",
                zulip_email="bot@test.zulipchat.com",
                zulip_api_key="test-key",
                operator_email="op@test.zulipchat.com",
                project_name="myproj",
                project_path="/home/user/myproj",
                config_dir=config_dir,
            )

        mock.send_message.assert_called_once()
        msg = mock.send_message.call_args[0][0]
        assert msg["type"] == "stream"
        assert msg["topic"] == "trunk"
        assert "myproj" in msg["content"]
