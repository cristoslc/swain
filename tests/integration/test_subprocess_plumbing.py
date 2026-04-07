"""Subprocess plumbing tests — verify NDJSON flows through real pipes.

These tests spawn actual plugin subprocesses (not mocks) and verify
that messages flow correctly through stdin/stdout pipes. This is the
layer between "the code logic works" (tested in test_control_flows.py)
and "the live system works" (manual Zulip testing).

Scenarios covered:

  PluginProcess pipe I/O:
    - Receives ConfigMessage on stdin, reads stdout response
    - write() delivers NDJSON to subprocess stdin
    - stderr is captured separately from stdout

  Project bridge subprocess:
    - Starts, reads config, stays alive
    - Receives a control_message Command without crashing

  Chat plugin poll → emit → stdout:
    - _poll_zulip + _emit in a subprocess writes commands to stdout
    - Kernel reads them via PluginProcess._read_stdout
"""
from __future__ import annotations

import asyncio
import json
import sys

import pytest

from untethered.protocol import (
    Event, Command, ConfigMessage,
    encode_message, decode_message,
)
from untethered.kernel import PluginProcess


# ---------------------------------------------------------------------------
# Scenario: PluginProcess starts, receives config, reads/writes NDJSON
# ---------------------------------------------------------------------------

class TestPluginProcessPlumbing:
    """PluginProcess correctly wires stdin/stdout/stderr pipes."""

    async def test_plugin_receives_config_and_echoes_stdout(self):
        """Spawn a minimal Python subprocess that reads config from stdin
        and echoes a command back on stdout. Verifies the pipe works."""
        received: list = []

        # Inline Python script that acts as a minimal plugin:
        # - Reads config from stdin line 0
        # - Writes a command to stdout
        # - Exits
        script = (
            "import sys, json\n"
            "line = sys.stdin.readline()\n"
            "cfg = json.loads(line)\n"
            "# Echo back a command to prove we got the config\n"
            "cmd = json.dumps({"
            "'type': 'control_message', "
            "'bridge': cfg.get('config', {}).get('project', 'test'), "
            "'session_id': None, "
            "'timestamp': 0, "
            "'payload': {'text': 'got config'}"
            "}) + '\\n'\n"
            "sys.stdout.write(cmd)\n"
            "sys.stdout.flush()\n"
        )

        plugin = PluginProcess(
            name="test-echo",
            cmd=[sys.executable, "-c", script],
            plugin_type="test",
            config={"project": "swain"},
            on_message=received.append,
        )
        await plugin.start()

        # Wait for the subprocess to write its response
        await asyncio.sleep(0.5)

        assert len(received) == 1
        assert received[0].type == "control_message"
        assert received[0].payload["text"] == "got config"

        await plugin.stop()

    async def test_plugin_write_delivers_to_stdin(self):
        """PluginProcess.write() sends NDJSON to the subprocess stdin."""
        received_on_stdout: list = []

        # Script: reads config, then reads one more line, echoes it back
        script = (
            "import sys, json\n"
            "config = sys.stdin.readline()\n"  # line 0: config
            "line = sys.stdin.readline()\n"     # line 1: command from kernel
            "if line:\n"
            "    data = json.loads(line)\n"
            "    # Echo the command type back as an event\n"
            "    event = json.dumps({"
            "'type': 'text_output', "
            "'bridge': 'swain', "
            "'session_id': 'sess-1', "
            "'timestamp': 0, "
            "'payload': {'content': 'received: ' + data.get('type', '?')}"
            "}) + '\\n'\n"
            "    sys.stdout.write(event)\n"
            "    sys.stdout.flush()\n"
        )

        plugin = PluginProcess(
            name="test-relay",
            cmd=[sys.executable, "-c", script],
            plugin_type="test",
            config={"project": "swain"},
            on_message=received_on_stdout.append,
        )
        await plugin.start()

        # Send a command to the plugin
        cmd = Command.control_message(bridge="swain", text="hello")
        await plugin.write(cmd)

        await asyncio.sleep(0.5)

        assert len(received_on_stdout) == 1
        assert received_on_stdout[0].type == "text_output"
        assert "received: control_message" in received_on_stdout[0].payload["content"]

        await plugin.stop()

    async def test_plugin_stderr_logged(self):
        """Plugin stderr is captured by the kernel (not mixed with stdout)."""
        received: list = []

        script = (
            "import sys\n"
            "config = sys.stdin.readline()\n"
            "sys.stderr.write('diagnostic: plugin started\\n')\n"
            "sys.stderr.flush()\n"
            "# Wait a moment so kernel can read stderr\n"
            "import time; time.sleep(0.2)\n"
        )

        plugin = PluginProcess(
            name="test-stderr",
            cmd=[sys.executable, "-c", script],
            plugin_type="test",
            config={},
            on_message=received.append,
        )
        await plugin.start()
        await asyncio.sleep(0.5)

        # No messages on stdout (stderr is separate)
        assert len(received) == 0

        await plugin.stop()


# ---------------------------------------------------------------------------
# Scenario: Real project bridge subprocess
# ---------------------------------------------------------------------------

class TestProjectBridgeSubprocess:
    """Spawn the actual project bridge plugin and verify NDJSON flow."""

    async def test_project_bridge_starts_and_logs(self):
        """The real project_bridge plugin starts, reads config, logs to stderr."""
        received: list = []

        plugin = PluginProcess(
            name="project:test",
            cmd=[sys.executable, "-m", "untethered.plugins.project_bridge"],
            plugin_type="project",
            config={"project": "test-project", "project_dir": "/tmp"},
            on_message=received.append,
        )
        await plugin.start()

        # Give it time to process config
        await asyncio.sleep(0.5)

        # Should be alive (not crashed)
        assert plugin._proc is not None
        assert plugin._proc.returncode is None

        await plugin.stop()

    async def test_project_bridge_routes_control_message(self):
        """Send a control_message to the project bridge and verify it processes it.

        The bridge will try to spawn a ClaudeCodeAdapter which will fail
        (claude not available in test), but the command should be received
        and logged without crashing the bridge.
        """
        received: list = []

        plugin = PluginProcess(
            name="project:test",
            cmd=[sys.executable, "-m", "untethered.plugins.project_bridge"],
            plugin_type="project",
            config={"project": "test-project", "project_dir": "/tmp"},
            on_message=received.append,
        )
        await plugin.start()
        await asyncio.sleep(0.3)

        # Send a control_message command
        cmd = Command.control_message(bridge="test-project", text="what's up?")
        await plugin.write(cmd)

        # Wait for processing
        await asyncio.sleep(1.0)

        # Bridge should still be alive (didn't crash on the command)
        assert plugin._proc is not None
        assert plugin._proc.returncode is None

        await plugin.stop()


# ---------------------------------------------------------------------------
# Scenario: Chat plugin poll → _emit → stdout pipe
# ---------------------------------------------------------------------------

class TestChatPluginPollEmit:
    """Verify _poll_zulip + _emit writes commands through a real stdout pipe.

    Spawns a subprocess that runs _poll_zulip with a mock Zulip client,
    so we test the real pipe behavior without hitting Zulip.
    """

    async def test_poll_emits_command_to_stdout_pipe(self):
        """_poll_zulip receives a message event and _emit writes a Command
        to stdout, which the parent process reads via the pipe."""
        received: list = []

        # Python script that simulates the chat plugin's poll loop:
        # - Creates a mock Zulip client with one message event
        # - Runs _poll_zulip with _emit writing to real stdout
        # - The parent reads the Command from the pipe
        script = '''
import asyncio, sys
from unittest.mock import MagicMock

from untethered.plugins.zulip_chat import _poll_zulip, _emit, SessionTopicRegistry

def make_client():
    client = MagicMock()
    client.email = "bot@zulip.com"
    msg = {
        "type": "stream",
        "sender_email": "user123@example.com",
        "display_recipient": "swain",
        "subject": "control",
        "content": "what specs are ready?",
    }
    def call_on_each_message(callback):
        callback(msg)
        sys.exit(0)
    client.call_on_each_message.side_effect = call_on_each_message
    return client

async def main():
    loop = asyncio.get_running_loop()
    client = make_client()
    registry = SessionTopicRegistry()
    try:
        await _poll_zulip(
            client, {"swain": "swain"}, "control", _emit, registry, loop,
        )
    except SystemExit:
        pass

asyncio.run(main())
'''

        plugin = PluginProcess(
            name="test-chat-poll",
            cmd=[sys.executable, "-c", script],
            plugin_type="test",
            config={},  # Not used — script doesn't read config
            on_message=received.append,
        )

        # Start the subprocess — but PluginProcess sends a ConfigMessage
        # on stdin line 0 which the script doesn't read. We need to handle
        # this by making the script read and discard it.
        # Actually, PluginProcess.start() writes config then starts readers.
        # The script doesn't read stdin, but that's OK — the pipe buffer
        # holds the config line and the script just ignores it.
        await plugin.start()

        # Wait for the script to process the mock event and emit a command
        await asyncio.sleep(1.0)

        # The poll should have parsed the operator message and emitted
        # a control_message command via _emit (stdout)
        assert len(received) >= 1, f"Expected command on stdout, got {len(received)} messages"
        cmd = received[0]
        assert cmd.type == "control_message"
        assert cmd.payload["text"] == "what specs are ready?"

        await plugin.stop()

        await plugin.stop()
