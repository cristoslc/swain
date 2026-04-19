"""Tests for the ProjectBridge microkernel — subprocess plugin router."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from swain_helm.protocol import Event, Command
from swain_helm.plugin_process import PluginProcess
from swain_helm.bridges.project import ProjectBridge, SessionState, _runtime_cmd


@pytest.fixture
def bridge():
    return ProjectBridge(
        project="swain",
        project_dir="/tmp/swain",
        config={"chat": {"server_url": "https://zulip.example.com"}},
    )


class TestRuntimeCmd:
    def test_opencode(self):
        assert _runtime_cmd("opencode") == ["swain-helm-opencode"]

    def test_claude(self):
        assert _runtime_cmd("claude") == ["swain-helm-claude"]

    def test_default_is_tmux(self):
        assert _runtime_cmd("gemini") == ["swain-helm-tmux"]


class TestStartStop:
    @pytest.mark.asyncio
    async def test_start_spawns_chat_plugin(self, bridge):
        with patch.object(PluginProcess, "start", new_callable=AsyncMock) as mock_start:
            await bridge.start()
            mock_start.assert_awaited_once()
            assert bridge._chat_plugin is not None
            assert bridge._chat_plugin.plugin_type == "chat"
            assert bridge._chat_plugin.config["bridge"] == "swain"

    @pytest.mark.asyncio
    async def test_stop_cleans_up(self, bridge):
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            await bridge.start()
        with patch.object(PluginProcess, "stop", new_callable=AsyncMock) as mock_stop:
            await bridge.stop()
            mock_stop.assert_awaited()


class TestSessionLifecycle:
    def test_initial_state_is_empty(self, bridge):
        assert bridge.sessions == {}

    @pytest.mark.asyncio
    async def test_start_session_spawns_runtime_plugin(self, bridge):
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            bridge.handle_command(
                Command.start_session(bridge="swain", runtime="claude", prompt="hello")
            )
            await asyncio.sleep(0)
        assert len(bridge.sessions) == 1
        sess = list(bridge.sessions.values())[0]
        assert sess.state == SessionState.SPAWNING
        assert sess.runtime == "claude"
        assert sess.session_id in bridge._runtime_plugins

    @pytest.mark.asyncio
    async def test_start_session_uses_correct_cmd(self, bridge):
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            bridge.handle_command(
                Command.start_session(bridge="swain", runtime="opencode")
            )
            await asyncio.sleep(0)
        sess_id = list(bridge.sessions.keys())[0]
        plugin = bridge._runtime_plugins[sess_id]
        assert plugin.cmd == ["swain-helm-opencode"]
        assert plugin.config["bridge"] == "swain"
        assert plugin.config["session_id"] == sess_id

    @pytest.mark.asyncio
    async def test_session_transitions_to_active_on_spawned_event(self, bridge):
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            bridge.handle_command(
                Command.start_session(bridge="swain", runtime="claude")
            )
            await asyncio.sleep(0)
        sess_id = list(bridge.sessions.keys())[0]
        bridge.handle_runtime_event(
            Event.session_spawned(bridge="swain", session_id=sess_id, runtime="claude")
        )
        assert bridge.sessions[sess_id].state == SessionState.ACTIVE

    @pytest.mark.asyncio
    async def test_session_dies(self, bridge):
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            bridge.handle_command(
                Command.start_session(bridge="swain", runtime="claude")
            )
            await asyncio.sleep(0)
        sess_id = list(bridge.sessions.keys())[0]
        bridge.handle_runtime_event(
            Event.session_died(bridge="swain", session_id=sess_id, reason="exited")
        )
        assert bridge.sessions[sess_id].state == SessionState.DEAD

    @pytest.mark.asyncio
    async def test_cancel_marks_dead_and_removes_plugin(self, bridge):
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            bridge.handle_command(
                Command.start_session(bridge="swain", runtime="claude")
            )
            await asyncio.sleep(0)
        sess_id = list(bridge.sessions.keys())[0]
        assert sess_id in bridge._runtime_plugins
        with patch.object(PluginProcess, "stop", new_callable=AsyncMock):
            bridge.handle_command(Command.cancel(bridge="swain", session_id=sess_id))
            await asyncio.sleep(0)
        assert bridge.sessions[sess_id].state == SessionState.DEAD
        assert sess_id not in bridge._runtime_plugins


class TestChatCommandRouting:
    @pytest.mark.asyncio
    async def test_send_prompt_forwards_to_runtime_plugin(self, bridge):
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            bridge.handle_command(
                Command.start_session(bridge="swain", runtime="claude")
            )
            await asyncio.sleep(0)
        sess_id = list(bridge.sessions.keys())[0]
        bridge.sessions[sess_id].state = SessionState.ACTIVE
        cmd = Command.send_prompt(bridge="swain", session_id=sess_id, text="do stuff")
        plugin = bridge._runtime_plugins[sess_id]
        with patch.object(plugin, "write", new_callable=AsyncMock) as mock_write:
            bridge.handle_command(cmd)
            await asyncio.sleep(0)
            mock_write.assert_awaited_once_with(cmd)

    @pytest.mark.asyncio
    async def test_approve_forwards_to_runtime_plugin(self, bridge):
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            bridge.handle_command(
                Command.start_session(bridge="swain", runtime="claude")
            )
            await asyncio.sleep(0)
        sess_id = list(bridge.sessions.keys())[0]
        bridge.sessions[sess_id].state = SessionState.WAITING_APPROVAL
        bridge.sessions[sess_id].pending_approval_call_id = "call-1"
        cmd = Command.approve(
            bridge="swain", session_id=sess_id, call_id="call-1", approved=True
        )
        plugin = bridge._runtime_plugins[sess_id]
        with patch.object(plugin, "write", new_callable=AsyncMock) as mock_write:
            bridge.handle_command(cmd)
            await asyncio.sleep(0)
            mock_write.assert_awaited_once_with(cmd)
        assert bridge.sessions[sess_id].state == SessionState.ACTIVE

    @pytest.mark.asyncio
    async def test_send_prompt_unknown_session_logged(self, bridge):
        cmd = Command.send_prompt(bridge="swain", session_id="nope", text="hi")
        bridge.handle_command(cmd)


class TestRuntimeEventRouting:
    @pytest.mark.asyncio
    async def test_runtime_events_forwarded_to_chat_plugin(self, bridge):
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            await bridge.start()
            bridge.handle_command(
                Command.start_session(bridge="swain", runtime="claude")
            )
            await asyncio.sleep(0)
        sess_id = list(bridge.sessions.keys())[0]
        event = Event.text_output(bridge="swain", session_id=sess_id, content="hi")
        plugin = bridge._runtime_plugins[sess_id]
        with patch.object(
            bridge._chat_plugin, "write", new_callable=AsyncMock
        ) as mock_write:
            plugin.on_message(event)
            await asyncio.sleep(0)
            mock_write.assert_awaited_once_with(event)

    @pytest.mark.asyncio
    async def test_approval_event_sets_waiting_state(self, bridge):
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            bridge.handle_command(
                Command.start_session(bridge="swain", runtime="claude")
            )
            await asyncio.sleep(0)
        sess_id = list(bridge.sessions.keys())[0]
        bridge.sessions[sess_id].state = SessionState.ACTIVE
        event = Event.approval_needed(
            bridge="swain",
            session_id=sess_id,
            tool_name="Bash",
            description="ls",
            call_id="call-1",
        )
        bridge.handle_runtime_event(event)
        assert bridge.sessions[sess_id].state == SessionState.WAITING_APPROVAL


class TestSessionRegistry:
    @pytest.mark.asyncio
    async def test_get_session_by_id(self, bridge):
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            bridge.handle_command(
                Command.start_session(bridge="swain", runtime="claude")
            )
            await asyncio.sleep(0)
        sess_id = list(bridge.sessions.keys())[0]
        assert bridge.get_session(sess_id) is not None

    def test_get_nonexistent_session_returns_none(self, bridge):
        assert bridge.get_session("nonexistent") is None

    @pytest.mark.asyncio
    async def test_list_active_sessions(self, bridge):
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            bridge.handle_command(
                Command.start_session(bridge="swain", runtime="claude")
            )
            bridge.handle_command(
                Command.start_session(bridge="swain", runtime="opencode")
            )
            await asyncio.sleep(0)
        sess_ids = list(bridge.sessions.keys())
        bridge.handle_runtime_event(
            Event.session_spawned(
                bridge="swain", session_id=sess_ids[0], runtime="claude"
            )
        )
        active = bridge.active_sessions()
        assert len(active) == 1
        assert active[0].session_id == sess_ids[0]


class TestControlMessage:
    @pytest.mark.asyncio
    async def test_control_message_forwards_to_existing_control_session(self, bridge):
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            bridge.handle_command(
                Command.start_session(bridge="swain", runtime="opencode")
            )
            await asyncio.sleep(0)
        sess_id = list(bridge.sessions.keys())[0]
        bridge.sessions[sess_id].origin = "control"
        bridge.sessions[sess_id].state = SessionState.ACTIVE
        plugin = bridge._runtime_plugins[sess_id]
        cmd = Command.control_message(bridge="swain", text="hello from control")
        with patch.object(plugin, "write", new_callable=AsyncMock) as mock_write:
            bridge.handle_command(cmd)
            await asyncio.sleep(0)
            mock_write.assert_awaited_once()
