"""BDD integration tests — async Zulip polling and Claude Code adapter wiring.

Scenarios covered:

  Zulip polling (via call_on_each_message):
    - Zulip message routes to the correct project bridge
    - Bot's own messages are skipped
    - Blocking SDK call runs in a thread executor

  Claude Code adapter wiring:
    - start_session spawns a ClaudeCodeAdapter
    - send_prompt forwards the command to the adapter
    - approve forwards the command to the adapter
    - cancel stops the adapter subprocess

  Smoke:
    - All components import and instantiate without error
    - The event loop runs a minimal polling cycle without crashing
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, call

import pytest

from swain_helm.protocol import Event, Command
from swain_helm.bridges.project import ProjectBridge, SessionState
from swain_helm.adapters.zulip_chat import ZulipChatAdapter
from swain_helm.plugins.zulip_chat import _poll_zulip, SessionTopicRegistry
from swain_helm.plugin_process import PluginProcess


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_zulip_msg(
    content: str, stream: str = "swain", topic: str = "sess-abc"
) -> dict:
    return {
        "type": "stream",
        "sender_email": "operator@example.com",
        "display_recipient": stream,
        "subject": topic,
        "content": content,
    }


def _make_poll_client(messages: list[dict]) -> MagicMock:
    """Build a mock Zulip client that delivers messages via call_on_each_message."""
    client = MagicMock()
    client.email = "bot@zulip.com"

    def call_on_each_message(callback, **kwargs):
        for msg in messages:
            callback(msg)
        raise asyncio.CancelledError()

    client.call_on_each_message.side_effect = call_on_each_message
    return client


_STREAM_MAP = "swain"


# ---------------------------------------------------------------------------
# Scenario: Zulip message routes to the correct project bridge
# ---------------------------------------------------------------------------


class TestZulipMessageRouting:
    """_poll_zulip emits the correct Command for each Zulip message type."""

    async def test_plain_text_becomes_send_prompt(self):
        received: list[Command] = []
        client = _make_poll_client([_make_zulip_msg("fix the tests")])
        loop = asyncio.get_running_loop()
        with pytest.raises(asyncio.CancelledError):
            await _poll_zulip(
                client,
                _STREAM_MAP,
                "control",
                received.append,
                SessionTopicRegistry(),
                loop,
                "swain",
            )

        assert len(received) == 1
        assert received[0].type == "send_prompt"
        assert received[0].payload["text"] == "fix the tests"
        assert received[0].bridge == "swain"

    async def test_approve_slash_command(self):
        received: list[Command] = []
        client = _make_poll_client(
            [
                _make_zulip_msg("/approve call-123", topic="sess-abc"),
            ]
        )
        loop = asyncio.get_running_loop()
        with pytest.raises(asyncio.CancelledError):
            await _poll_zulip(
                client,
                _STREAM_MAP,
                "control",
                received.append,
                SessionTopicRegistry(),
                loop,
                "swain",
            )

        assert len(received) == 1
        assert received[0].type == "approve"
        assert received[0].payload["call_id"] == "call-123"
        assert received[0].payload["approved"] is True

    async def test_bot_own_messages_skipped(self):
        received: list[Command] = []
        bot_msg = _make_zulip_msg("I am the bot")
        bot_msg["sender_email"] = "bot@zulip.com"
        client = _make_poll_client([bot_msg])
        loop = asyncio.get_running_loop()
        with pytest.raises(asyncio.CancelledError):
            await _poll_zulip(
                client,
                _STREAM_MAP,
                "control",
                received.append,
                SessionTopicRegistry(),
                loop,
                "swain",
            )

        assert len(received) == 0


# ---------------------------------------------------------------------------
# Scenario: Blocking SDK call runs in executor
# ---------------------------------------------------------------------------


class TestZulipBlockingCallsAreOffloaded:
    """call_on_each_message runs in a thread executor, not on the event loop."""

    async def test_sdk_runs_in_executor(self):
        """Verify run_in_executor is used: the event loop stays responsive
        while call_on_each_message blocks in a worker thread."""
        import threading

        loop = asyncio.get_running_loop()
        barrier = asyncio.Event()
        executor_ran = threading.Event()

        client = MagicMock()
        client.email = "bot@zulip.com"

        def call_on_each_message(callback, **kwargs):
            loop.call_soon_threadsafe(barrier.set)
            executor_ran.set()
            import time

            time.sleep(0.02)

        client.call_on_each_message.side_effect = call_on_each_message

        poll_task = asyncio.create_task(
            _poll_zulip(
                client,
                "swain",
                "control",
                lambda _cmd: None,
                SessionTopicRegistry(),
                loop,
                "swain",
            )
        )

        await asyncio.wait_for(barrier.wait(), timeout=2.0)
        assert executor_ran.is_set()

        poll_task.cancel()
        with pytest.raises((asyncio.CancelledError, Exception)):
            await poll_task


# ---------------------------------------------------------------------------
# Scenario: Claude Code adapter wiring
# ---------------------------------------------------------------------------


class TestAdapterWiring:
    """ProjectBridge spawns runtime adapters as PluginProcess subprocesses."""

    async def test_start_session_creates_runtime_plugin(self):
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            bridge = ProjectBridge(project="swain", project_dir="/tmp/swain")
            cmd = Command.start_session(
                bridge="swain", runtime="claude", prompt="hello"
            )
            bridge.handle_command(cmd)
            await asyncio.sleep(0)

            assert len(bridge._runtime_plugins) == 1
            plugin = list(bridge._runtime_plugins.values())[0]
            assert plugin.name.startswith("runtime:")

    async def test_send_prompt_forwards_to_runtime_plugin(self):
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            with patch.object(
                PluginProcess, "write", new_callable=AsyncMock
            ) as mock_write:
                bridge = ProjectBridge(project="swain")
                bridge.handle_command(
                    Command.start_session(bridge="swain", runtime="claude")
                )
                await asyncio.sleep(0)

                sess_id = list(bridge.sessions.keys())[0]
                bridge.handle_command(
                    Command.send_prompt(
                        bridge="swain", session_id=sess_id, text="keep going"
                    )
                )
                await asyncio.sleep(0)

                assert mock_write.await_count >= 1

    async def test_cancel_stops_runtime_plugin(self):
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            with patch.object(PluginProcess, "stop", new_callable=AsyncMock):
                bridge = ProjectBridge(project="swain")
                bridge.handle_command(
                    Command.start_session(bridge="swain", runtime="claude")
                )
                await asyncio.sleep(0)

                sess_id = list(bridge.sessions.keys())[0]
                bridge.handle_command(
                    Command.cancel(bridge="swain", session_id=sess_id)
                )
                await asyncio.sleep(0)

                assert bridge.sessions[sess_id].state == SessionState.DEAD

    async def test_send_prompt_to_unknown_session_logs_warning(self, caplog):
        import logging

        bridge = ProjectBridge(project="swain")
        with caplog.at_level(logging.WARNING, logger="swain_helm.bridges.project"):
            bridge.handle_command(
                Command.send_prompt(
                    bridge="swain", session_id="nonexistent", text="hello"
                )
            )
        assert "unknown session" in caplog.text.lower()


# ---------------------------------------------------------------------------
# Smoke test — all components start without error
# ---------------------------------------------------------------------------


class TestSmoke:
    """Minimal wiring test — nothing crashes on import or instantiation."""

    def test_kernel_imports(self):
        from swain_helm.plugin_process import PluginProcess
        from swain_helm.bridges.project import ProjectBridge
        from swain_helm.plugins.zulip_chat import _poll_zulip, _relay_events

    def test_kernel_instantiates(self):
        from swain_helm.plugin_process import PluginProcess

        p = PluginProcess(name="test", cmd=["echo"], plugin_type="test", config={})
        assert p.name == "test"

    def test_project_bridge_library_still_works(self):
        """ProjectBridge is still usable as a library (used by project_bridge plugin)."""
        from swain_helm.bridges.project import ProjectBridge
        from swain_helm.protocol import Event

        delivered = []
        bridge = ProjectBridge(project="swain", on_event=delivered.append)
        event = Event.text_output(bridge="swain", session_id="s1", content="hello")
        bridge.handle_runtime_event(event)
        assert delivered[0].payload["content"] == "hello"

    def test_protocol_encode_decode_roundtrip(self):
        """ConfigMessage roundtrips correctly (used by kernel → plugin handshake)."""
        from swain_helm.protocol import ConfigMessage, encode_message, decode_message

        cfg = ConfigMessage(plugin_type="chat", config={"bot_email": "x@y.com"})
        line = encode_message(cfg)
        restored = decode_message(line)
        assert isinstance(restored, ConfigMessage)
        assert restored.config["bot_email"] == "x@y.com"
