"""RED tests for the Zulip chat adapter plugin."""
import json
from unittest.mock import MagicMock, patch

from untethered.protocol import Event, Command
from untethered.adapters.zulip_chat import (
    format_event_for_zulip,
    parse_zulip_message,
    ZulipChatAdapter,
)


class TestFormatEventForZulip:
    """Events from the kernel must become readable Zulip messages."""

    def test_text_output(self):
        event = Event.text_output(bridge="swain", session_id="s1", content="Hello world")
        msg = format_event_for_zulip(event)
        assert "Hello world" in msg["content"]
        assert msg["topic"] == "s1"

    def test_tool_call(self):
        event = Event.tool_call(
            bridge="swain", session_id="s1",
            tool_name="Bash", input={"command": "ls"}, call_id="c1",
        )
        msg = format_event_for_zulip(event)
        assert "Bash" in msg["content"]
        assert "ls" in msg["content"]

    def test_approval_needed_mentions_operator(self):
        event = Event.approval_needed(
            bridge="swain", session_id="s1",
            tool_name="Bash", description="Run: rm -rf /tmp", call_id="c1",
        )
        msg = format_event_for_zulip(event, operator_email="user@example.com")
        assert "@**user@example.com**" in msg["content"]
        assert "approve" in msg["content"].lower() or "Approve" in msg["content"]

    def test_session_spawned(self):
        event = Event.session_spawned(bridge="swain", session_id="s1", runtime="claude")
        msg = format_event_for_zulip(event)
        assert "session" in msg["content"].lower() or "started" in msg["content"].lower()

    def test_session_died(self):
        event = Event.session_died(bridge="swain", session_id="s1", reason="exited")
        msg = format_event_for_zulip(event)
        assert "ended" in msg["content"].lower() or "died" in msg["content"].lower()

    def test_host_event_uses_control_topic(self):
        event = Event.unmanaged_session_found(
            tmux_target="swain-spec-142", project_path="/home/user/swain",
        )
        msg = format_event_for_zulip(event, control_topic="control")
        assert msg["topic"] == "control"


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
        assert cmd.type == "start_session"
        assert cmd.payload["runtime"] == "claude"

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


class TestZulipChatAdapterStructure:
    def test_adapter_has_required_methods(self):
        adapter = ZulipChatAdapter.__new__(ZulipChatAdapter)
        assert hasattr(adapter, "post_event")
        assert hasattr(adapter, "start_listening")
