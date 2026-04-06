"""BDD integration tests — async Zulip polling and Claude Code adapter wiring.

Scenarios covered:

  Zulip polling:
    - Zulip message routes to the correct project bridge
    - BAD_EVENT_QUEUE_ID triggers re-registration and polling continues
    - Blocking SDK calls run in a thread executor, not on the event loop

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

from untethered.protocol import Event, Command
from untethered.bridges.host import HostBridge
from untethered.bridges.project import ProjectBridge
from untethered.adapters.zulip_chat import ZulipChatAdapter, parse_zulip_message
from untethered.main import _poll_zulip_events, _stream_to_bridge


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


def _make_get_events_response(messages: list[dict], *, last_id: int = 0) -> dict:
    events = [
        {"type": "message", "id": last_id + i + 1, "message": msg}
        for i, msg in enumerate(messages)
    ]
    return {"result": "success", "events": events}


# ---------------------------------------------------------------------------
# Scenario: Zulip message routes to the correct project bridge
# ---------------------------------------------------------------------------

class TestZulipMessageRouting:
    """Given a host bridge with 'swain' registered, Zulip messages reach it."""

    async def test_plain_text_routes_to_project_bridge(self):
        received: list[Command] = []
        host = HostBridge(domain="personal")
        bridge = ProjectBridge(project="swain", on_event=lambda e: None)
        host.register_project("swain", on_command=received.append)

        chat_adapter = ZulipChatAdapter(control_topic="control")
        projects_config = [{"name": "swain", "stream": "swain"}]

        client = MagicMock()
        client.email = "bot@zulip.com"
        client.register.return_value = {
            "result": "success", "queue_id": "q1", "last_event_id": 0,
        }

        call_count = 0

        def get_events(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return _make_get_events_response(
                    [_make_zulip_msg("fix the tests")], last_id=0,
                )
            # Second call: cancel the polling loop
            raise asyncio.CancelledError()

        client.get_events.side_effect = get_events

        with pytest.raises(asyncio.CancelledError):
            await _poll_zulip_events(
                client, chat_adapter, host, projects_config=projects_config,
            )

        assert len(received) == 1
        cmd = received[0]
        assert cmd.type == "send_prompt"
        assert cmd.payload["text"] == "fix the tests"
        assert cmd.bridge == "swain"

    async def test_approve_slash_command_routes_correctly(self):
        received: list[Command] = []
        host = HostBridge(domain="personal")
        host.register_project("swain", on_command=received.append)

        chat_adapter = ZulipChatAdapter(control_topic="control")
        projects_config = [{"name": "swain", "stream": "swain"}]

        client = MagicMock()
        client.email = "bot@zulip.com"
        client.register.return_value = {
            "result": "success", "queue_id": "q1", "last_event_id": 0,
        }

        call_count = 0

        def get_events(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return _make_get_events_response(
                    [_make_zulip_msg("/approve call-123", topic="sess-abc")],
                )
            raise asyncio.CancelledError()

        client.get_events.side_effect = get_events

        with pytest.raises(asyncio.CancelledError):
            await _poll_zulip_events(
                client, chat_adapter, host, projects_config=projects_config,
            )

        assert len(received) == 1
        cmd = received[0]
        assert cmd.type == "approve"
        assert cmd.payload["call_id"] == "call-123"
        assert cmd.payload["approved"] is True

    async def test_bot_own_messages_are_skipped(self):
        received: list[Command] = []
        host = HostBridge(domain="personal")
        host.register_project("swain", on_command=received.append)
        chat_adapter = ZulipChatAdapter(control_topic="control")
        projects_config = [{"name": "swain", "stream": "swain"}]

        client = MagicMock()
        client.email = "bot@zulip.com"
        client.register.return_value = {
            "result": "success", "queue_id": "q1", "last_event_id": 0,
        }

        bot_msg = _make_zulip_msg("I am the bot's own message")
        bot_msg["sender_email"] = "bot@zulip.com"

        call_count = 0

        def get_events(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return _make_get_events_response([bot_msg])
            raise asyncio.CancelledError()

        client.get_events.side_effect = get_events

        with pytest.raises(asyncio.CancelledError):
            await _poll_zulip_events(
                client, chat_adapter, host, projects_config=projects_config,
            )

        assert len(received) == 0


# ---------------------------------------------------------------------------
# Scenario: BAD_EVENT_QUEUE_ID triggers re-registration
# ---------------------------------------------------------------------------

class TestZulipQueueReregistration:
    """When get_events returns BAD_EVENT_QUEUE_ID, polling re-registers and continues."""

    async def test_reregisters_on_bad_queue_id(self):
        received: list[Command] = []
        host = HostBridge(domain="personal")
        host.register_project("swain", on_command=received.append)
        chat_adapter = ZulipChatAdapter(control_topic="control")
        projects_config = [{"name": "swain", "stream": "swain"}]

        client = MagicMock()
        client.email = "bot@zulip.com"

        register_calls: list[str] = []

        def register(**kwargs):
            register_calls.append("register")
            return {"result": "success", "queue_id": f"q{len(register_calls)}", "last_event_id": 0}

        client.register.side_effect = register

        call_count = 0

        def get_events(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First call: queue expired
                return {"result": "error", "code": "BAD_EVENT_QUEUE_ID"}
            if call_count == 2:
                # After re-registration: deliver a message
                return _make_get_events_response(
                    [_make_zulip_msg("hello after re-register")]
                )
            raise asyncio.CancelledError()

        client.get_events.side_effect = get_events

        with pytest.raises(asyncio.CancelledError):
            await _poll_zulip_events(
                client, chat_adapter, host, projects_config=projects_config,
            )

        assert len(register_calls) == 2  # initial + re-register
        assert len(received) == 1
        assert received[0].payload["text"] == "hello after re-register"


# ---------------------------------------------------------------------------
# Scenario: Blocking SDK calls run in executor
# ---------------------------------------------------------------------------

class TestZulipBlockingCallsAreOffloaded:
    """register() and get_events() must not run on the event loop thread."""

    async def test_get_events_runs_in_executor(self):
        """Verify run_in_executor is used: the event loop stays responsive
        while get_events blocks in a worker thread."""
        import threading

        loop = asyncio.get_running_loop()
        barrier = asyncio.Event()
        executor_ran = threading.Event()

        host = HostBridge(domain="personal")
        chat_adapter = ZulipChatAdapter(control_topic="control")
        projects_config: list[dict] = []

        client = MagicMock()
        client.email = "bot@zulip.com"
        client.register.return_value = {
            "result": "success", "queue_id": "q1", "last_event_id": 0,
        }

        call_count = 0

        def get_events(**_kw):
            nonlocal call_count
            call_count += 1
            # Signal from worker thread using the captured loop reference
            loop.call_soon_threadsafe(barrier.set)
            executor_ran.set()
            import time
            time.sleep(0.02)  # simulate blocking HTTP
            # Return empty events so polling loops back
            return {"result": "success", "events": []}

        client.get_events.side_effect = get_events

        poll_task = asyncio.create_task(
            _poll_zulip_events(
                client, chat_adapter, host, projects_config=projects_config,
            )
        )

        # Event loop must stay responsive while get_events blocks in executor
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
        with patch("untethered.bridges.project.ClaudeCodeAdapter") as MockAdapter:
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
            mock_instance.start.assert_awaited_once_with(prompt="hello")

    async def test_send_prompt_forwards_to_adapter(self):
        with patch("untethered.bridges.project.ClaudeCodeAdapter") as MockAdapter:
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
        with patch("untethered.bridges.project.ClaudeCodeAdapter") as MockAdapter:
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
        with patch("untethered.bridges.project.ClaudeCodeAdapter") as MockAdapter:
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
        with caplog.at_level(logging.WARNING, logger="untethered.bridges.project"):
            bridge.handle_command(
                Command.send_prompt(bridge="swain", session_id="nonexistent", text="hello")
            )
        assert "unknown session" in caplog.text.lower()


# ---------------------------------------------------------------------------
# Smoke test — all components start without error
# ---------------------------------------------------------------------------

class TestSmoke:
    """Minimal wiring test — nothing crashes on import or instantiation."""

    def test_imports_succeed(self):
        from untethered.protocol import Event, Command
        from untethered.bridges.host import HostBridge
        from untethered.bridges.project import ProjectBridge
        from untethered.adapters.zulip_chat import ZulipChatAdapter
        from untethered.adapters.claude_code import ClaudeCodeAdapter

    def test_full_pipeline_instantiates(self):
        host = HostBridge(domain="personal")
        project = ProjectBridge(project="swain", project_dir="/tmp/swain")
        chat = ZulipChatAdapter(control_topic="control")

        host.register_project("swain", on_command=project.handle_command)
        host.on_chat_event = lambda e: chat.post_event(e)

        assert "swain" in host.projects

    async def test_event_flows_host_to_chat(self):
        """Runtime event reaches the chat adapter callback."""
        delivered: list[Event] = []
        host = HostBridge(domain="personal", on_chat_event=delivered.append)
        project = ProjectBridge(project="swain", on_event=host.route_project_event)

        host.register_project("swain", on_command=project.handle_command)

        # Simulate an event from a runtime adapter
        event = Event.text_output(bridge="swain", session_id="s1", content="Hello!")
        project.handle_runtime_event(event)

        assert len(delivered) == 1
        assert delivered[0].type == "text_output"
        assert delivered[0].payload["content"] == "Hello!"
