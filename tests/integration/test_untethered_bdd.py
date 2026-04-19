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
from swain_helm.bridges.project import ProjectBridge
from swain_helm.adapters.zulip_chat import ZulipChatAdapter
from swain_helm.plugins.zulip_chat import _poll_zulip, SessionTopicRegistry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_zulip_msg(content: str, stream: str = "swain", topic: str = "sess-abc") -> dict:
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

    def call_on_each_message(callback):
        for msg in messages:
            callback(msg)
        raise asyncio.CancelledError()

    client.call_on_each_message.side_effect = call_on_each_message
    return client


_STREAM_MAP = {"swain": "swain"}


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
            await _poll_zulip(client, _STREAM_MAP, "control", received.append, SessionTopicRegistry(), loop)

        assert len(received) == 1
        assert received[0].type == "send_prompt"
        assert received[0].payload["text"] == "fix the tests"
        assert received[0].bridge == "swain"

    async def test_approve_slash_command(self):
        received: list[Command] = []
        client = _make_poll_client([
            _make_zulip_msg("/approve call-123", topic="sess-abc"),
        ])
        loop = asyncio.get_running_loop()
        with pytest.raises(asyncio.CancelledError):
            await _poll_zulip(client, _STREAM_MAP, "control", received.append, SessionTopicRegistry(), loop)

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
            await _poll_zulip(client, _STREAM_MAP, "control", received.append, SessionTopicRegistry(), loop)

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

        def call_on_each_message(callback):
            loop.call_soon_threadsafe(barrier.set)
            executor_ran.set()
            import time
            time.sleep(0.02)

        client.call_on_each_message.side_effect = call_on_each_message

        poll_task = asyncio.create_task(
            _poll_zulip(client, {}, "control", lambda _cmd: None, SessionTopicRegistry(), loop)
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
    """ProjectBridge spawns and controls ClaudeCodeAdapter instances."""

    async def test_start_session_spawns_adapter(self):
        with patch("swain_helm.bridges.project.TmuxPaneAdapter") as MockAdapter:
            mock_instance = AsyncMock()
            MockAdapter.return_value = mock_instance

            bridge = ProjectBridge(project="swain", project_dir="/tmp/swain")
            cmd = Command.start_session(bridge="swain", runtime="claude", prompt="hello")
            bridge.handle_command(cmd)

            # Drain the scheduled task
            await asyncio.sleep(0)

            MockAdapter.assert_called_once()
            init_kwargs = MockAdapter.call_args.kwargs
            assert init_kwargs["bridge"] == "swain"
            assert init_kwargs["project_dir"] == "/tmp/swain"
            mock_instance.start.assert_awaited_once()
            start_kwargs = mock_instance.start.call_args.kwargs
            assert "runtime_cmd" in start_kwargs
            assert "session_name" in start_kwargs

    async def test_send_prompt_forwards_to_adapter(self):
        with patch("swain_helm.bridges.project.TmuxPaneAdapter") as MockAdapter:
            mock_instance = AsyncMock()
            MockAdapter.return_value = mock_instance

            bridge = ProjectBridge(project="swain")
            bridge.handle_command(
                Command.start_session(bridge="swain", runtime="claude")
            )
            await asyncio.sleep(0)

            sess_id = list(bridge.sessions.keys())[0]
            bridge.handle_command(
                Command.send_prompt(bridge="swain", session_id=sess_id, text="keep going")
            )
            await asyncio.sleep(0)

            assert mock_instance.send_command.await_count == 1
            sent_cmd = mock_instance.send_command.await_args[0][0]
            assert sent_cmd.type == "send_prompt"
            assert sent_cmd.payload["text"] == "keep going"

    async def test_approve_forwards_to_adapter(self):
        with patch("swain_helm.bridges.project.TmuxPaneAdapter") as MockAdapter:
            mock_instance = AsyncMock()
            MockAdapter.return_value = mock_instance

            bridge = ProjectBridge(project="swain")
            bridge.handle_command(
                Command.start_session(bridge="swain", runtime="claude")
            )
            await asyncio.sleep(0)

            sess_id = list(bridge.sessions.keys())[0]
            # Put session in WAITING_APPROVAL state
            bridge.handle_runtime_event(
                Event.session_spawned(bridge="swain", session_id=sess_id, runtime="claude")
            )
            bridge.handle_runtime_event(
                Event.approval_needed(
                    bridge="swain", session_id=sess_id,
                    tool_name="Bash", description="rm -rf /tmp/foo", call_id="c1",
                )
            )

            bridge.handle_command(
                Command.approve(bridge="swain", session_id=sess_id, call_id="c1", approved=True)
            )
            await asyncio.sleep(0)

            assert mock_instance.send_command.await_count == 1
            sent_cmd = mock_instance.send_command.await_args[0][0]
            assert sent_cmd.type == "approve"
            assert sent_cmd.payload["approved"] is True

    async def test_cancel_stops_adapter(self):
        with patch("swain_helm.bridges.project.TmuxPaneAdapter") as MockAdapter:
            mock_instance = AsyncMock()
            MockAdapter.return_value = mock_instance

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

            mock_instance.stop.assert_awaited_once()
            # Adapter removed from registry after cancel
            assert sess_id not in bridge._adapters

    async def test_send_prompt_to_unknown_session_logs_warning(self, caplog):
        import logging
        bridge = ProjectBridge(project="swain")
        with caplog.at_level(logging.WARNING, logger="swain_helm.bridges.project"):
            bridge.handle_command(
                Command.send_prompt(bridge="swain", session_id="nonexistent", text="hello")
            )
        assert "unknown session" in caplog.text.lower()


# ---------------------------------------------------------------------------
# Smoke test — all components start without error
# ---------------------------------------------------------------------------

class TestSmoke:
    """Minimal wiring test — nothing crashes on import or instantiation."""

    def test_kernel_imports(self):
        from swain_helm.kernel import HostKernel, PluginProcess
        from swain_helm.plugins.zulip_chat import _poll_zulip, _relay_events
        from swain_helm.plugins.project_bridge import _amain

    def test_kernel_instantiates(self):
        from swain_helm.kernel import HostKernel
        kernel = HostKernel()
        assert kernel._chat_plugin is None
        assert kernel._project_plugins == {}

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
