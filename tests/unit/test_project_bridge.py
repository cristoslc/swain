"""RED tests for the project bridge kernel — session orchestrator for one project."""
import asyncio
from unittest.mock import AsyncMock, MagicMock

from swain_helm.protocol import Event, Command
from swain_helm.bridges.project import ProjectBridge, SessionState


class TestSessionLifecycle:
    def test_initial_state_is_empty(self):
        bridge = ProjectBridge(project="swain")
        assert bridge.sessions == {}

    def test_start_session_creates_session(self):
        bridge = ProjectBridge(project="swain")
        cmd = Command.start_session(bridge="swain", runtime="claude", prompt="hello")
        bridge.handle_command(cmd)
        assert len(bridge.sessions) == 1
        sess = list(bridge.sessions.values())[0]
        assert sess.state == SessionState.SPAWNING
        assert sess.runtime == "claude"

    def test_session_transitions_to_active_on_spawned_event(self):
        bridge = ProjectBridge(project="swain")
        cmd = Command.start_session(bridge="swain", runtime="claude")
        bridge.handle_command(cmd)
        sess_id = list(bridge.sessions.keys())[0]

        event = Event.session_spawned(
            bridge="swain", session_id=sess_id, runtime="claude",
        )
        bridge.handle_runtime_event(event)
        assert bridge.sessions[sess_id].state == SessionState.ACTIVE

    def test_session_dies(self):
        bridge = ProjectBridge(project="swain")
        cmd = Command.start_session(bridge="swain", runtime="claude")
        bridge.handle_command(cmd)
        sess_id = list(bridge.sessions.keys())[0]

        event = Event.session_died(
            bridge="swain", session_id=sess_id, reason="exited cleanly",
        )
        bridge.handle_runtime_event(event)
        assert bridge.sessions[sess_id].state == SessionState.DEAD

    def test_cancel_command_marks_session_dead(self):
        bridge = ProjectBridge(project="swain")
        cmd = Command.start_session(bridge="swain", runtime="claude")
        bridge.handle_command(cmd)
        sess_id = list(bridge.sessions.keys())[0]

        cancel = Command.cancel(bridge="swain", session_id=sess_id)
        bridge.handle_command(cancel)
        assert bridge.sessions[sess_id].state == SessionState.DEAD


class TestEventForwarding:
    def test_runtime_events_forwarded_to_on_event(self):
        received = []
        bridge = ProjectBridge(project="swain", on_event=received.append)
        cmd = Command.start_session(bridge="swain", runtime="claude")
        bridge.handle_command(cmd)
        sess_id = list(bridge.sessions.keys())[0]

        event = Event.text_output(bridge="swain", session_id=sess_id, content="hi")
        bridge.handle_runtime_event(event)
        assert len(received) >= 1
        text_events = [e for e in received if e.type == "text_output"]
        assert len(text_events) == 1

    def test_approval_event_sets_waiting_state(self):
        bridge = ProjectBridge(project="swain")
        cmd = Command.start_session(bridge="swain", runtime="claude")
        bridge.handle_command(cmd)
        sess_id = list(bridge.sessions.keys())[0]

        # Mark as active first
        bridge.handle_runtime_event(
            Event.session_spawned(bridge="swain", session_id=sess_id, runtime="claude")
        )

        event = Event.approval_needed(
            bridge="swain", session_id=sess_id,
            tool_name="Bash", description="Run: ls", call_id="call-1",
        )
        bridge.handle_runtime_event(event)
        assert bridge.sessions[sess_id].state == SessionState.WAITING_APPROVAL


class TestSessionRegistry:
    def test_get_session_by_id(self):
        bridge = ProjectBridge(project="swain")
        cmd = Command.start_session(bridge="swain", runtime="claude")
        bridge.handle_command(cmd)
        sess_id = list(bridge.sessions.keys())[0]
        assert bridge.get_session(sess_id) is not None

    def test_get_nonexistent_session_returns_none(self):
        bridge = ProjectBridge(project="swain")
        assert bridge.get_session("nonexistent") is None

    def test_list_active_sessions(self):
        bridge = ProjectBridge(project="swain")
        # Start two sessions
        bridge.handle_command(Command.start_session(bridge="swain", runtime="claude"))
        bridge.handle_command(Command.start_session(bridge="swain", runtime="opencode"))
        # Mark first as active
        sess_ids = list(bridge.sessions.keys())
        bridge.handle_runtime_event(
            Event.session_spawned(bridge="swain", session_id=sess_ids[0], runtime="claude")
        )
        active = bridge.active_sessions()
        assert len(active) == 1
        assert active[0].session_id == sess_ids[0]
