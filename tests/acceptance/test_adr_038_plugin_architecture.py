"""Acceptance tests: ADR-038 Microkernel Plugin Architecture.

These tests verify architectural constraints specified in ADR-038.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from swain_helm.plugin_process import PluginProcess
from swain_helm.protocol import encode_message, decode_message, Event, Command


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


class TestADR038ExcisableSoftware:
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
