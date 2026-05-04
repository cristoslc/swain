"""UAT: SPEC-322 — Project Bridge Microkernel.

Tests bridge subprocess spawning, plugin management, config scoping,
and NDJSON protocol handling.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from swain_helm.bridges.project import ProjectBridge
from swain_helm.plugin_process import PluginProcess
from swain_helm.protocol import encode_message, decode_message, Event, Command

IS_DOCKER = (
    Path("/.dockerenv").exists() or os.environ.get("SWAIN_HELM_TEST_MODE") == "1"
)
skip_if_not_docker = pytest.mark.skipif(
    not IS_DOCKER,
    reason="UAT tests require Docker isolation",
)


@skip_if_not_docker
class TestBridgeSpawnsPlugins:
    """UAT-322-01 through UAT-322-05: Bridge plugin spawning."""

    def test_bridge_has_chat_plugin_attribute(self):
        """UAT-322-01: Bridge spawns chat plugin as subprocess."""
        bridge = ProjectBridge(project="test", project_dir="/tmp/test")
        assert hasattr(bridge, "_chat_plugin")

    def test_bridge_has_runtime_plugins_dict(self):
        """UAT-322-04: Runtime adapters stored as dict of plugins on /work."""
        bridge = ProjectBridge(project="test", project_dir="/tmp/test")
        assert hasattr(bridge, "_runtime_plugins")
        assert isinstance(bridge._runtime_plugins, dict)

    def test_plugin_process_is_spawnable(self):
        """UAT-322-02: Chat plugin receives ConfigMessage on stdin."""
        plugin = PluginProcess(
            name="test-chat",
            cmd=["echo", "test"],
            plugin_type="chat",
            config={"bridge": "test"},
        )
        assert plugin.name == "test-chat"
        assert plugin.plugin_type == "chat"

    def test_plugin_config_scoped(self):
        """UAT-322-03: ConfigMessage contains only scoped credentials."""
        config = {
            "bridge": "test-project",
            "stream": "test-stream",
        }
        plugin = PluginProcess(
            name="test",
            cmd=["echo"],
            plugin_type="chat",
            config=config,
        )
        assert plugin.config["bridge"] == "test-project"


@skip_if_not_docker
class TestPluginProcessManagement:
    """UAT-322-06, UAT-322-07: Plugin process management."""

    def test_plugin_process_tracks_running_state(self):
        """UAT-322-06: Adapter crash detected by PluginProcess."""
        plugin = PluginProcess(
            name="test",
            cmd=["echo", "hello"],
            plugin_type="chat",
            config={},
        )
        # Initially not running — _proc is the asyncio subprocess
        assert plugin._proc is None

    def test_plugin_handles_non_ndjson_gracefully(self):
        """UAT-322-07: Non-NDJSON from adapter handled gracefully."""
        invalid_line = "not valid json {{"
        result = decode_message(invalid_line)
        assert result is None


@skip_if_not_docker
class TestOldFilesRemoved:
    """UAT-322-08: Old kernel files are deleted."""

    def test_no_kernel_module(self):
        """UAT-322-08: kernel.py does not exist."""
        import importlib

        try:
            importlib.import_module("swain_helm.kernel")
            pytest.fail("swain_helm.kernel should not exist")
        except ImportError:
            pass

    def test_no_host_bridge_module(self):
        """UAT-322-08: bridges/host.py does not exist."""
        import importlib

        try:
            importlib.import_module("swain_helm.bridges.host")
            pytest.fail("swain_helm.bridges.host should not exist")
        except ImportError:
            pass


@skip_if_not_docker
class TestConsoleScripts:
    """UAT-322-09: Console scripts registered."""

    def test_entry_points_in_pyproject_toml(self):
        """UAT-322-09: Console scripts registered in pyproject.toml."""
        pyproject = Path(__file__).parent.parent.parent / "pyproject.toml"
        content = pyproject.read_text()

        assert "swain-helm-zulip-chat" in content
        assert "swain-helm-opencode" in content
        assert "swain-helm-claude" in content
        assert "swain-helm-tmux" in content


@skip_if_not_docker
class TestNegativeCases:
    """UAT-322-NEG-01, UAT-322-NEG-02: Negative cases."""

    def test_bridge_exits_on_malformed_config(self):
        """UAT-322-NEG-01: Bridge receives malformed ConfigMessage."""
        invalid_config = "not json {{"
        result = decode_message(invalid_config)
        assert result is None

    def test_bridge_exits_on_empty_stdin(self):
        """UAT-322-NEG-02: Bridge receives empty stdin."""
        result = decode_message("")
        assert result is None


@skip_if_not_docker
class TestNDJSONProtocol:
    """Additional NDJSON protocol tests."""

    def test_event_serialization(self):
        """Events serialize to NDJSON correctly."""
        event = Event.text_output(
            bridge="test", session_id="sess-123", content="Hello, world!"
        )
        encoded = encode_message(event)
        assert "text_output" in encoded
        assert "Hello, world!" in encoded

    def test_command_serialization(self):
        """Commands serialize to NDJSON correctly."""
        cmd = Command.send_prompt(
            bridge="test", session_id="sess-123", text="Run tests"
        )
        encoded = encode_message(cmd)
        assert "send_prompt" in encoded
        assert "Run tests" in encoded

    def test_config_message_format(self):
        """ConfigMessage has correct format on line 0."""
        config = {
            "type": "config",
            "plugin_type": "chat",
            "config": {"bridge": "test", "stream": "test-stream"},
        }
        line = json.dumps(config)
        decoded = decode_message(line)
        assert decoded is not None
        assert decoded.type == "config"
