"""BDD integration tests — control topic flows (DESIGN-025 / SPEC-291).

Scenarios covered:

  Control-topic plain text (query flow):
    - Plain text in control topic becomes a control_message command
    - control_message forwards to an existing control-origin session
    - Events from control-origin sessions post to control topic (no thread)
    - session_died for control-origin sessions is silent (no noise)

  Control-topic /work (launcher flow):
    - /work in control topic becomes a launch_session command
    - (Launcher flow superseded by worktree scanner — SPEC-323 — tests skipped)

  End-to-end message routing:
    - Zulip operator message → chat plugin → kernel → project bridge
    - Project bridge event → kernel → chat plugin → Zulip post
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from swain_helm.protocol import (
    Event,
    Command,
    ConfigMessage,
    encode_message,
    decode_message,
)
from swain_helm.bridges.project import ProjectBridge, SessionState
from swain_helm.plugin_process import PluginProcess
from swain_helm.adapters.zulip_chat import parse_zulip_message, format_event_for_zulip
from swain_helm.plugins.zulip_chat import (
    _poll_zulip,
    _relay_events,
    SessionTopicRegistry,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_zulip_msg(
    content: str, stream: str = "swain", topic: str = "control"
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
_STREAM_NAME = "swain"
_BRIDGE = "swain"


# ---------------------------------------------------------------------------
# Scenario: Plain text in control → control_message
# ---------------------------------------------------------------------------


class TestControlMessageParsing:
    """Plain text in the control topic produces a control_message command."""

    def test_plain_text_in_control_becomes_control_message(self):
        msg = _make_zulip_msg("what specs are ready?", topic="control")
        cmd = parse_zulip_message(msg, bridge="swain", control_topic="control")
        assert cmd is not None
        assert cmd.type == "control_message"
        assert cmd.payload["text"] == "what specs are ready?"

    def test_plain_text_in_session_topic_becomes_send_prompt(self):
        msg = _make_zulip_msg("keep going", topic="SPEC-142")
        cmd = parse_zulip_message(msg, bridge="swain", control_topic="control")
        assert cmd is not None
        assert cmd.type == "send_prompt"
        assert cmd.session_id == "SPEC-142"

    def test_work_command_becomes_launch_session(self):
        msg = _make_zulip_msg("/work fix the login bug", topic="control")
        cmd = parse_zulip_message(msg, bridge="swain", control_topic="control")
        assert cmd is not None
        assert cmd.type == "launch_session"
        assert cmd.payload["text"] == "fix the login bug"

    def test_session_command_becomes_launch_session(self):
        msg = _make_zulip_msg("/session", topic="control")
        cmd = parse_zulip_message(msg, bridge="swain", control_topic="control")
        assert cmd is not None
        assert cmd.type == "launch_session"


# ---------------------------------------------------------------------------
# Scenario: control_message spawns lightweight session
# ---------------------------------------------------------------------------


class TestControlMessageBridge:
    """ProjectBridge handles control_message by forwarding to an existing control-origin session."""

    async def test_control_message_forwards_to_control_origin_session(self):
        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            bridge = ProjectBridge(project="swain", project_dir="/tmp/swain")
            bridge.handle_command(
                Command.start_session(bridge="swain", runtime="opencode")
            )
            await asyncio.sleep(0)

            sid = list(bridge.sessions.keys())[0]
            bridge.sessions[sid].origin = "control"
            bridge.sessions[sid].state = SessionState.ACTIVE

            cmd = Command.control_message(bridge="swain", text="what specs are ready?")
            plugin = bridge._runtime_plugins[sid]
            with patch.object(plugin, "write", new_callable=AsyncMock) as mock_write:
                bridge.handle_command(cmd)
                await asyncio.sleep(0)
                mock_write.assert_awaited_once()

    async def test_control_origin_events_tagged_with_origin(self):
        """Events from control-origin sessions carry origin=control in payload."""
        delivered: list[Event] = []
        bridge = ProjectBridge(project="swain", on_event=delivered.append)

        with patch.object(PluginProcess, "start", new_callable=AsyncMock):
            bridge.handle_command(
                Command.start_session(bridge="swain", runtime="opencode")
            )
            await asyncio.sleep(0)

        sid = list(bridge.sessions.keys())[0]
        bridge.sessions[sid].origin = "control"
        bridge.sessions[sid].state = SessionState.ACTIVE

        event = Event.text_output(bridge="swain", session_id=sid, content="All good")
        bridge.handle_runtime_event(event)

        text_events = [e for e in delivered if e.type == "text_output"]
        assert len(text_events) == 1
        assert text_events[0].payload["origin"] == "control"


# ---------------------------------------------------------------------------
# Scenario: Control-origin events post to control topic (no thread)
# ---------------------------------------------------------------------------


class TestControlOriginRelayEvents:
    """_relay_events routes control-origin events to the control topic."""

    async def test_control_origin_text_posts_to_control_topic(self):
        """Text output from control-origin session goes to control, not a new thread."""
        client = MagicMock()
        client.send_message = MagicMock()
        registry = SessionTopicRegistry()
        loop = asyncio.get_running_loop()
        posted: list[dict] = []

        event = Event.text_output(
            bridge="swain", session_id="sess-abc", content="3 specs ready"
        )
        event.payload["origin"] = "control"
        event_line = encode_message(event)

        # Simulate stdin with one event then EOF
        lines = iter([event_line, ""])

        with patch("sys.stdin") as mock_stdin:
            mock_stdin.readline = lambda: next(lines)

            # Run _relay_events — it will read one event then exit on empty line
            await _relay_events(
                client,
                _STREAM_NAME,
                "op@example.com",
                "control",
                registry,
                loop,
            )

        # Should have posted to control topic, not created a thread
        assert client.send_message.call_count == 1
        call_args = client.send_message.call_args[0][0]
        assert call_args["topic"] == "control"
        assert "3 specs ready" in call_args["content"]

    async def test_control_origin_session_spawned_is_silent(self):
        """session_spawned with origin=control produces no Zulip post."""
        client = MagicMock()
        registry = SessionTopicRegistry()
        loop = asyncio.get_running_loop()

        event = Event.session_spawned(
            bridge="swain", session_id="sess-abc", runtime="claude"
        )
        event.payload["origin"] = "control"
        event_line = encode_message(event)

        lines = iter([event_line, ""])

        with patch("sys.stdin") as mock_stdin:
            mock_stdin.readline = lambda: next(lines)
            await _relay_events(
                client,
                "swain",
                None,
                "control",
                registry,
                loop,
            )

        assert client.send_message.call_count == 0

    async def test_control_origin_session_died_is_silent(self):
        """session_died with origin=control produces no Zulip post."""
        client = MagicMock()
        registry = SessionTopicRegistry()
        loop = asyncio.get_running_loop()

        event = Event.session_died(bridge="swain", session_id="sess-abc", reason="done")
        event.payload["origin"] = "control"
        event_line = encode_message(event)

        lines = iter([event_line, ""])

        with patch("sys.stdin") as mock_stdin:
            mock_stdin.readline = lambda: next(lines)
            await _relay_events(
                client,
                "swain",
                None,
                "control",
                registry,
                loop,
            )

        assert client.send_message.call_count == 0


# ---------------------------------------------------------------------------
# Scenario: session_promoted creates a dedicated thread
# ---------------------------------------------------------------------------


class TestSessionPromotedRelay:
    """session_promoted event creates a Zulip thread and announces in control."""

    async def test_promoted_creates_thread_and_announces(self):
        client = MagicMock()
        registry = SessionTopicRegistry()
        loop = asyncio.get_running_loop()

        event = Event.session_promoted(
            bridge="swain",
            session_id="sess-abc",
            artifact="SPEC-142",
        )
        event_line = encode_message(event)

        lines = iter([event_line, ""])

        with patch("sys.stdin") as mock_stdin:
            mock_stdin.readline = lambda: next(lines)
            await _relay_events(
                client,
                "swain",
                "op@example.com",
                "control",
                registry,
                loop,
            )

        # Two posts: one in the new thread, one announcement in control
        assert client.send_message.call_count == 2

        calls = [c[0][0] for c in client.send_message.call_args_list]
        thread_post = next(c for c in calls if c["topic"] != "control")
        control_post = next(c for c in calls if c["topic"] == "control")

        assert thread_post["topic"] == "SPEC-142"
        assert "Session started" in thread_post["content"]
        assert "SPEC-142" in control_post["content"]

        # Registry should have the assignment
        assert registry.topic_for("sess-abc") == "SPEC-142"

    async def test_post_promotion_events_go_to_thread(self):
        """After promotion, regular events go to the dedicated thread."""
        client = MagicMock()
        registry = SessionTopicRegistry()
        loop = asyncio.get_running_loop()

        promoted = Event.session_promoted(
            bridge="swain",
            session_id="sess-abc",
            artifact="SPEC-142",
        )
        text_out = Event.text_output(
            bridge="swain",
            session_id="sess-abc",
            content="Working on it...",
        )
        lines = iter([encode_message(promoted), encode_message(text_out), ""])

        with patch("sys.stdin") as mock_stdin:
            mock_stdin.readline = lambda: next(lines)
            await _relay_events(
                client,
                "swain",
                None,
                "control",
                registry,
                loop,
            )

        # 2 from promotion + 1 text output = 3
        assert client.send_message.call_count == 3
        last_call = client.send_message.call_args_list[-1][0][0]
        assert last_call["topic"] == "SPEC-142"
        assert "Working on it" in last_call["content"]


# ---------------------------------------------------------------------------
# Scenario: /work triggers launcher, follow-up relays as answer
# ---------------------------------------------------------------------------


@pytest.mark.skip(reason="Launcher flow superseded by worktree scanner (SPEC-323)")
class TestLaunchSessionBridge:
    """ProjectBridge handles launch_session by spawning the launcher."""

    async def test_launch_session_creates_interviewing_session(self):
        pass

    async def test_followup_control_message_relays_to_launcher(self):
        pass

    async def test_launcher_ready_promotes_session(self):
        pass

    async def test_launcher_info_relays_to_control(self):
        pass

    async def test_launcher_question_relays_with_options(self):
        pass


# ---------------------------------------------------------------------------
# Scenario: Full Zulip poll → command routing
# ---------------------------------------------------------------------------


class TestZulipPollControlRouting:
    """_poll_zulip correctly routes control-topic messages as control_message."""

    async def test_control_topic_plain_text_emits_control_message(self):
        received: list[Command] = []
        client = _make_poll_client([_make_zulip_msg("what's next?", topic="control")])
        registry = SessionTopicRegistry()
        loop = asyncio.get_running_loop()

        with pytest.raises(asyncio.CancelledError):
            await _poll_zulip(
                client, _STREAM_MAP, "control", received.append, registry, loop, "swain"
            )

        assert len(received) == 1
        assert received[0].type == "control_message"
        assert received[0].payload["text"] == "what's next?"

    async def test_control_topic_work_command_emits_launch_session(self):
        received: list[Command] = []
        client = _make_poll_client([_make_zulip_msg("/work SPEC-142", topic="control")])
        registry = SessionTopicRegistry()
        loop = asyncio.get_running_loop()

        with pytest.raises(asyncio.CancelledError):
            await _poll_zulip(
                client, _STREAM_MAP, "control", received.append, registry, loop, "swain"
            )

        assert len(received) == 1
        assert received[0].type == "launch_session"
        assert received[0].payload["text"] == "SPEC-142"

    async def test_session_topic_plain_text_emits_send_prompt(self):
        received: list[Command] = []
        registry = SessionTopicRegistry()
        registry.assign("sess-abc", "SPEC-142")

        client = _make_poll_client([_make_zulip_msg("keep going", topic="SPEC-142")])
        loop = asyncio.get_running_loop()

        with pytest.raises(asyncio.CancelledError):
            await _poll_zulip(
                client, _STREAM_MAP, "control", received.append, registry, loop, "swain"
            )

        assert len(received) == 1
        assert received[0].type == "send_prompt"
        assert received[0].session_id == "sess-abc"


# ---------------------------------------------------------------------------
# Scenario: Protocol roundtrip for new types
# ---------------------------------------------------------------------------


class TestProtocolNewTypes:
    """New protocol types encode/decode correctly."""

    def test_control_message_roundtrip(self):
        cmd = Command.control_message(bridge="swain", text="what's up?")
        line = encode_message(cmd)
        restored = decode_message(line)
        assert isinstance(restored, Command)
        assert restored.type == "control_message"
        assert restored.payload["text"] == "what's up?"

    def test_launch_session_roundtrip(self):
        cmd = Command.launch_session(bridge="swain", text="fix login")
        line = encode_message(cmd)
        restored = decode_message(line)
        assert isinstance(restored, Command)
        assert restored.type == "launch_session"
        assert restored.payload["text"] == "fix login"

    def test_session_promoted_roundtrip(self):
        event = Event.session_promoted(
            bridge="swain",
            session_id="sess-abc",
            artifact="SPEC-142",
            topic="SPEC-142",
        )
        line = encode_message(event)
        restored = decode_message(line)
        assert isinstance(restored, Event)
        assert restored.type == "session_promoted"
        assert restored.payload["artifact"] == "SPEC-142"


# ---------------------------------------------------------------------------
# Scenario: Zulip Cloud message format (real-world format)
# ---------------------------------------------------------------------------


class TestZulipCloudMessageFormat:
    """Messages from Zulip Cloud use specific sender_email and HTML content."""

    def test_zulip_cloud_operator_message_parses(self):
        """Zulip Cloud uses user{id}@domain sender emails and HTML content."""
        msg = {
            "type": "stream",
            "sender_email": "user1065126@cristoslc.zulipchat.com",
            "display_recipient": "swain",
            "subject": "control",
            "content": "<p>what specs are ready?</p>",
        }
        cmd = parse_zulip_message(msg, bridge="swain", control_topic="control")
        assert cmd is not None
        assert cmd.type == "control_message"
        # Content includes HTML tags — that's what Zulip sends
        assert "what specs are ready?" in cmd.payload["text"]

    async def test_poll_receives_zulip_cloud_format(self):
        """Full poll cycle with Zulip Cloud message format."""
        received: list[Command] = []
        zulip_msg = {
            "type": "stream",
            "sender_email": "user1065126@cristoslc.zulipchat.com",
            "display_recipient": "swain",
            "subject": "control",
            "content": "<p>What gh issues are left?</p>",
        }
        client = _make_poll_client([zulip_msg])
        registry = SessionTopicRegistry()
        loop = asyncio.get_running_loop()

        with pytest.raises(asyncio.CancelledError):
            await _poll_zulip(
                client, _STREAM_MAP, "control", received.append, registry, loop, "swain"
            )

        assert len(received) == 1
        assert received[0].type == "control_message"


# ---------------------------------------------------------------------------
# Scenario: Full round trip — mock LLM
# ---------------------------------------------------------------------------


class TestFullRoundTripMockLlm:
    """End-to-end: control_message → mock runtime → event back to control."""

    async def test_runtime_event_relay_to_control_via_relay(self):
        """Runtime event from control-origin session posts to control topic via _relay_events."""
        client = MagicMock()
        registry = SessionTopicRegistry()
        loop = asyncio.get_running_loop()

        text_event = Event.text_output(
            bridge="swain",
            session_id="sess-abc",
            content="Here are your specs",
        )
        text_event.payload["origin"] = "control"

        died_event = Event.session_died(
            bridge="swain",
            session_id="sess-abc",
            reason="done",
        )
        died_event.payload["origin"] = "control"

        lines = iter(
            [
                encode_message(text_event),
                encode_message(died_event),
                "",
            ]
        )

        with patch("sys.stdin") as mock_stdin:
            mock_stdin.readline = lambda: next(lines)
            await _relay_events(
                client,
                "swain",
                None,
                "control",
                registry,
                loop,
            )

        assert client.send_message.call_count == 1
        call_args = client.send_message.call_args[0][0]
        assert call_args["topic"] == "control"
        assert "Here are your specs" in call_args["content"]

    async def test_control_origin_session_died_is_silent_via_relay(self):
        """session_died with origin=control via _relay_events produces no Zulip post."""
        client = MagicMock()
        registry = SessionTopicRegistry()
        loop = asyncio.get_running_loop()

        died_event = Event.session_died(
            bridge="swain",
            session_id="sess-abc",
            reason="mock complete",
        )
        died_event.payload["origin"] = "control"

        lines = iter(
            [
                encode_message(died_event),
                "",
            ]
        )

        with patch("sys.stdin") as mock_stdin:
            mock_stdin.readline = lambda: next(lines)
            await _relay_events(
                client,
                "swain",
                None,
                "control",
                registry,
                loop,
            )

        assert client.send_message.call_count == 0


# ---------------------------------------------------------------------------
# Scenario: bin/swain NDJSON mode (subprocess test)
# ---------------------------------------------------------------------------


@pytest.mark.skip(reason="Launcher flow superseded by worktree scanner (SPEC-323)")
class TestLauncherNdjsonMode:
    """bin/swain --format ndjson produces structured NDJSON output."""

    async def test_launcher_emits_ready_with_fresh_flag(self):
        pass
