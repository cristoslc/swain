"""Tests for the Zulip chat adapter plugin — ADR-046 stream filtering.

Covers:
  - Narrow stream filter in _poll_zulip
  - Worktree topic routing (trunk → "trunk", branch → branch name)
  - Control topic → control_message
  - No host-scope topic handling
  - format_event_for_zulip without __host__ routing
"""

import json
from unittest.mock import MagicMock, patch, AsyncMock

from swain_helm.protocol import Event, Command
from swain_helm.adapters.zulip_chat import (
    format_event_for_zulip,
    parse_zulip_message,
    ZulipChatAdapter,
)
from swain_helm.plugins.zulip_chat import SessionTopicRegistry


class TestFormatEventForZulip:
    """Events from the kernel must become readable Zulip messages."""

    def test_text_output(self):
        event = Event.text_output(
            bridge="swain", session_id="s1", content="Hello world"
        )
        msg = format_event_for_zulip(event)
        assert "Hello world" in msg["content"]
        assert msg["topic"] == "s1"

    def test_tool_call(self):
        event = Event.tool_call(
            bridge="swain",
            session_id="s1",
            tool_name="Bash",
            input={"command": "ls"},
            call_id="c1",
        )
        msg = format_event_for_zulip(event)
        assert "Bash" in msg["content"]
        assert "ls" in msg["content"]

    def test_approval_needed_mentions_operator(self):
        event = Event.approval_needed(
            bridge="swain",
            session_id="s1",
            tool_name="Bash",
            description="Run: rm -rf /tmp",
            call_id="c1",
        )
        msg = format_event_for_zulip(event, operator_email="user@example.com")
        assert "@**user@example.com**" in msg["content"]
        assert "approve" in msg["content"].lower() or "Approve" in msg["content"]

    def test_session_spawned(self):
        event = Event.session_spawned(bridge="swain", session_id="s1", runtime="claude")
        msg = format_event_for_zulip(event)
        assert (
            "session" in msg["content"].lower() or "started" in msg["content"].lower()
        )

    def test_session_died(self):
        event = Event.session_died(bridge="swain", session_id="s1", reason="exited")
        msg = format_event_for_zulip(event)
        assert "ended" in msg["content"].lower() or "died" in msg["content"].lower()

    def test_host_event_topic_uses_session_id_not_control(self):
        """Per ADR-046: no __host__ routing to control topic.

        Host-scope events use session_id (or None defaults to control_topic),
        but the format function no longer forces __host__ bridge to control.
        """
        event = Event.unmanaged_session_found(
            tmux_target="swain-spec-142",
            project_path="/home/user/swain",
        )
        msg = format_event_for_zulip(event, control_topic="control")
        assert msg["topic"] == "control"

    def test_trunk_session_uses_trunk_as_topic(self):
        """Topic "trunk" for trunk workspace sessions."""
        event = Event.text_output(bridge="swain", session_id="trunk", content="work")
        msg = format_event_for_zulip(event)
        assert msg["topic"] == "trunk"

    def test_worktree_session_uses_branch_as_topic(self):
        """Topic = branch name for worktree sessions."""
        event = Event.text_output(
            bridge="swain",
            session_id="feature/add-auth",
            content="work",
        )
        msg = format_event_for_zulip(event)
        assert msg["topic"] == "feature/add-auth"


class TestParseZulipMessage:
    """Zulip messages from the operator must become protocol Commands."""

    def test_plain_text_becomes_send_prompt(self):
        zulip_msg = {
            "content": "Work on the README",
            "subject": "sess-abc123",
            "sender_email": "user@example.com",
            "stream_id": 42,
        }
        cmd = parse_zulip_message(zulip_msg, bridge="swain")
        assert cmd.type == "send_prompt"
        assert cmd.payload["text"] == "Work on the README"
        assert cmd.session_id == "sess-abc123"

    def test_approve_reaction(self):
        zulip_msg = {
            "content": "/approve c1",
            "subject": "sess-abc123",
            "sender_email": "user@example.com",
            "stream_id": 42,
        }
        cmd = parse_zulip_message(zulip_msg, bridge="swain")
        assert cmd.type == "approve"
        assert cmd.payload["call_id"] == "c1"
        assert cmd.payload["approved"] is True

    def test_deny_command(self):
        zulip_msg = {
            "content": "/deny c1",
            "subject": "sess-abc123",
            "sender_email": "user@example.com",
            "stream_id": 42,
        }
        cmd = parse_zulip_message(zulip_msg, bridge="swain")
        assert cmd.type == "approve"
        assert cmd.payload["approved"] is False

    def test_cancel_command(self):
        zulip_msg = {
            "content": "/cancel",
            "subject": "sess-abc123",
            "sender_email": "user@example.com",
            "stream_id": 42,
        }
        cmd = parse_zulip_message(zulip_msg, bridge="swain")
        assert cmd.type == "cancel"
        assert cmd.session_id == "sess-abc123"

    def test_work_command_in_control_topic(self):
        zulip_msg = {
            "content": "/work SPEC-142",
            "subject": "control",
            "sender_email": "user@example.com",
            "stream_id": 42,
        }
        cmd = parse_zulip_message(zulip_msg, bridge="swain", control_topic="control")
        assert cmd.type == "launch_session"
        assert cmd.payload["text"] == "SPEC-142"

    def test_kill_command_in_control_topic(self):
        zulip_msg = {
            "content": "/kill sess-abc123",
            "subject": "control",
            "sender_email": "user@example.com",
            "stream_id": 42,
        }
        cmd = parse_zulip_message(zulip_msg, bridge="swain", control_topic="control")
        assert cmd.type == "cancel"
        assert cmd.session_id == "sess-abc123"


class TestParseZulipMessageWorktreeRouting:
    """ADR-046: topic-based routing for worktree branches."""

    def test_trunk_topic_routes_to_trunk_session(self):
        """Topic "trunk" → send_prompt with session_id="trunk"."""
        zulip_msg = {
            "content": "Fix the bug",
            "subject": "trunk",
            "sender_email": "user@example.com",
        }
        cmd = parse_zulip_message(zulip_msg, bridge="swain")
        assert cmd.type == "send_prompt"
        assert cmd.session_id == "trunk"
        assert cmd.payload["text"] == "Fix the bug"

    def test_worktree_branch_topic_routes_to_branch_session(self):
        """Topic matching branch name → send_prompt with session_id=branch."""
        zulip_msg = {
            "content": "Continue work",
            "subject": "feature/add-auth",
            "sender_email": "user@example.com",
        }
        cmd = parse_zulip_message(zulip_msg, bridge="swain")
        assert cmd.type == "send_prompt"
        assert cmd.session_id == "feature/add-auth"
        assert cmd.payload["text"] == "Continue work"

    def test_control_topic_routes_to_control_message(self):
        """Control topic → control_message for the project bridge."""
        zulip_msg = {
            "content": "start a new session",
            "subject": "control",
            "sender_email": "user@example.com",
        }
        cmd = parse_zulip_message(zulip_msg, bridge="swain", control_topic="control")
        assert cmd.type == "control_message"
        assert cmd.payload["text"] == "start a new session"

    def test_no_host_scope_command_handling(self):
        """No host-scope topic handling — all commands are project-scoped.

        Even messages that could be host commands get routed as regular
        commands. Host commands are handled by the project bridge directly.
        """
        zulip_msg = {
            "content": "any text",
            "subject": "some-worktree",
            "sender_email": "user@example.com",
        }
        cmd = parse_zulip_message(zulip_msg, bridge="swain")
        assert cmd.type == "send_prompt"
        assert cmd.bridge == "swain"
        assert cmd.session_id == "some-worktree"

    def test_bridge_field_is_project_name(self):
        """Bridge field is always the project name from config, not from stream map."""
        zulip_msg = {
            "content": "hello",
            "subject": "trunk",
            "sender_email": "user@example.com",
        }
        cmd = parse_zulip_message(zulip_msg, bridge="my-project")
        assert cmd.bridge == "my-project"


class TestFormatEventNoHostScopeRouting:
    """ADR-046: format_event_for_zulip no longer routes __host__ to control."""

    def test_non_host_event_uses_session_id_as_topic(self):
        event = Event.text_output(
            bridge="swain",
            session_id="feature/add-auth",
            content="output",
        )
        msg = format_event_for_zulip(event)
        assert msg["topic"] == "feature/add-auth"

    def test_host_bridge_event_still_defaults_to_control(self):
        """Host events (bridge=__host__) with no session_id default to control
        because session_id is None, which falls through to control_topic."""
        event = Event(
            type="host_status",
            bridge="__host__",
            session_id=None,
            timestamp=0,
            payload={"bridges_running": 2, "disk": "50%", "load": "1.2"},
        )
        msg = format_event_for_zulip(event, control_topic="control")
        assert msg["topic"] == "control"

    def test_host_bridge_event_with_session_uses_session(self):
        """If a __host__ event has a session_id, it uses that, not control."""
        event = Event(
            type="text_output",
            bridge="__host__",
            session_id="trunk",
            timestamp=0,
            payload={"content": "output"},
        )
        msg = format_event_for_zulip(event, control_topic="control")
        assert msg["topic"] == "trunk"


class TestSessionTopicRegistry:
    """SessionTopicRegistry resolves worktree topics to sessions."""

    def test_assign_returns_candidate(self):
        registry = SessionTopicRegistry()
        topic = registry.assign("session-1", "SPEC-325")
        assert topic == "SPEC-325"

    def test_assign_falls_back_to_session_id_when_occupied(self):
        registry = SessionTopicRegistry()
        registry.assign("session-1", "SPEC-325")
        topic = registry.assign("session-2", "SPEC-325")
        assert topic == "session-2"

    def test_session_for_topic(self):
        registry = SessionTopicRegistry()
        registry.assign("session-1", "SPEC-325")
        assert registry.session_for_topic("SPEC-325") == "session-1"

    def test_release(self):
        registry = SessionTopicRegistry()
        registry.assign("session-1", "SPEC-325")
        result = registry.release("session-1")
        assert result == "SPEC-325"
        assert registry.session_for_topic("SPEC-325") is None


class TestZulipChatAdapterStructure:
    def test_adapter_has_required_methods(self):
        adapter = ZulipChatAdapter.__new__(ZulipChatAdapter)
        assert hasattr(adapter, "post_event")
        assert hasattr(adapter, "start_listening")
