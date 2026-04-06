"""BDD integration tests — control topic flows (DESIGN-025 / SPEC-291).

Scenarios covered:

  Control-topic plain text (query flow):
    - Plain text in control topic becomes a control_message command
    - control_message spawns a lightweight session with origin=control
    - Events from control-origin sessions post to control topic (no thread)
    - session_died for control-origin sessions is silent (no noise)

  Control-topic /work (launcher flow):
    - /work in control topic becomes a launch_session command
    - launch_session spawns bin/swain --non-interactive --format ndjson
    - Launcher info/question output posts to control topic
    - Operator follow-up text relays as answer to launcher stdin
    - Launcher ready signal promotes session (session_promoted event)
    - session_promoted creates a dedicated Zulip thread
    - After promotion, events post to the dedicated thread

  End-to-end message routing:
    - Zulip operator message → chat plugin → kernel → project bridge
    - Project bridge event → kernel → chat plugin → Zulip post
"""
from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch, call

import pytest

from untethered.protocol import Event, Command, ConfigMessage, encode_message, decode_message
from untethered.bridges.project import ProjectBridge, SessionState, LauncherProcess
from untethered.adapters.zulip_chat import parse_zulip_message, format_event_for_zulip
from untethered.plugins.zulip_chat import _poll_zulip, _relay_events, SessionTopicRegistry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_zulip_msg(content: str, stream: str = "swain", topic: str = "control") -> dict:
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


def _make_poll_client(responses: list) -> MagicMock:
    client = MagicMock()
    client.email = "bot@zulip.com"
    client.register.return_value = {
        "result": "success", "queue_id": "q1", "last_event_id": 0,
    }
    it = iter(responses)

    def get_events(**_kw):
        try:
            return next(it)
        except StopIteration:
            raise asyncio.CancelledError()

    client.get_events.side_effect = get_events
    return client


_STREAM_MAP = {"swain": "swain"}


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
    """ProjectBridge handles control_message by spawning a lightweight session."""

    async def test_control_message_spawns_session_with_origin_control(self):
        with patch("untethered.bridges.project.ClaudeCodeAdapter") as MockAdapter:
            mock_instance = AsyncMock()
            MockAdapter.return_value = mock_instance

            bridge = ProjectBridge(project="swain", project_dir="/tmp/swain")
            cmd = Command.control_message(bridge="swain", text="what specs are ready?")
            bridge.handle_command(cmd)
            await asyncio.sleep(0)

            # Session created with origin=control
            assert len(bridge.sessions) == 1
            session = list(bridge.sessions.values())[0]
            assert session.origin == "control"

            # Adapter spawned with the text as prompt
            MockAdapter.assert_called_once()
            mock_instance.start.assert_awaited_once()
            start_kwargs = mock_instance.start.call_args.kwargs
            assert start_kwargs["prompt"] == "what specs are ready?"

    async def test_control_origin_events_tagged_with_origin(self):
        """Events from control-origin sessions carry origin=control in payload."""
        delivered: list[Event] = []
        bridge = ProjectBridge(project="swain", on_event=delivered.append)

        with patch("untethered.bridges.project.ClaudeCodeAdapter") as MockAdapter:
            mock_instance = AsyncMock()
            MockAdapter.return_value = mock_instance
            bridge.handle_command(
                Command.control_message(bridge="swain", text="status?")
            )
            await asyncio.sleep(0)

        sid = list(bridge.sessions.keys())[0]
        event = Event.text_output(bridge="swain", session_id=sid, content="All good")
        bridge.handle_runtime_event(event)

        assert len(delivered) == 1
        assert delivered[0].payload["origin"] == "control"


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

        event = Event.text_output(bridge="swain", session_id="sess-abc", content="3 specs ready")
        event.payload["origin"] = "control"
        event_line = encode_message(event)

        # Simulate stdin with one event then EOF
        lines = iter([event_line, ""])

        with patch("sys.stdin") as mock_stdin:
            mock_stdin.readline = lambda: next(lines)

            # Run _relay_events — it will read one event then exit on empty line
            await _relay_events(
                client, {"swain": "swain"}, "op@example.com", "control",
                registry, loop,
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

        event = Event.session_spawned(bridge="swain", session_id="sess-abc", runtime="claude")
        event.payload["origin"] = "control"
        event_line = encode_message(event)

        lines = iter([event_line, ""])

        with patch("sys.stdin") as mock_stdin:
            mock_stdin.readline = lambda: next(lines)
            await _relay_events(
                client, {"swain": "swain"}, None, "control", registry, loop,
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
                client, {"swain": "swain"}, None, "control", registry, loop,
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
            bridge="swain", session_id="sess-abc",
            artifact="SPEC-142",
        )
        event_line = encode_message(event)

        lines = iter([event_line, ""])

        with patch("sys.stdin") as mock_stdin:
            mock_stdin.readline = lambda: next(lines)
            await _relay_events(
                client, {"swain": "swain"}, "op@example.com", "control",
                registry, loop,
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
            bridge="swain", session_id="sess-abc", artifact="SPEC-142",
        )
        text_out = Event.text_output(
            bridge="swain", session_id="sess-abc", content="Working on it...",
        )
        lines = iter([encode_message(promoted), encode_message(text_out), ""])

        with patch("sys.stdin") as mock_stdin:
            mock_stdin.readline = lambda: next(lines)
            await _relay_events(
                client, {"swain": "swain"}, None, "control", registry, loop,
            )

        # 2 from promotion + 1 text output = 3
        assert client.send_message.call_count == 3
        last_call = client.send_message.call_args_list[-1][0][0]
        assert last_call["topic"] == "SPEC-142"
        assert "Working on it" in last_call["content"]


# ---------------------------------------------------------------------------
# Scenario: /work triggers launcher, follow-up relays as answer
# ---------------------------------------------------------------------------

class TestLaunchSessionBridge:
    """ProjectBridge handles launch_session by spawning the launcher."""

    async def test_launch_session_creates_interviewing_session(self):
        with patch("untethered.bridges.project.LauncherProcess") as MockLauncher:
            mock_instance = AsyncMock()
            MockLauncher.return_value = mock_instance

            bridge = ProjectBridge(project="swain", project_dir="/tmp/swain")
            cmd = Command.launch_session(bridge="swain", text="fix login")
            bridge.handle_command(cmd)
            await asyncio.sleep(0)

            assert len(bridge.sessions) == 1
            session = list(bridge.sessions.values())[0]
            assert session.origin == "control"
            assert session.state == SessionState.INTERVIEWING

            MockLauncher.assert_called_once()
            mock_instance.start.assert_awaited_once()

    async def test_followup_control_message_relays_to_launcher(self):
        """Second control_message while interviewing relays as answer."""
        with patch("untethered.bridges.project.LauncherProcess") as MockLauncher:
            mock_instance = AsyncMock()
            MockLauncher.return_value = mock_instance

            bridge = ProjectBridge(project="swain", project_dir="/tmp/swain")

            # First: /work starts the interview
            bridge.handle_command(Command.launch_session(bridge="swain", text="fix it"))
            await asyncio.sleep(0)

            # Second: plain text while interviewing → relay as answer
            bridge.handle_command(
                Command.control_message(bridge="swain", text="resume")
            )
            await asyncio.sleep(0)

            mock_instance.send_answer.assert_awaited_once_with("resume")

    async def test_launcher_ready_promotes_session(self):
        """When launcher emits ready, session is promoted and runtime spawned."""
        delivered: list[Event] = []

        with patch("untethered.bridges.project.LauncherProcess") as MockLauncher:
            mock_instance = AsyncMock()
            MockLauncher.return_value = mock_instance

            with patch("untethered.bridges.project.ClaudeCodeAdapter") as MockAdapter:
                adapter_instance = AsyncMock()
                MockAdapter.return_value = adapter_instance

                bridge = ProjectBridge(
                    project="swain", project_dir="/tmp/swain",
                    on_event=delivered.append,
                )

                # Start the interview
                bridge.handle_command(Command.launch_session(bridge="swain", text="fix login"))
                await asyncio.sleep(0)

                sid = list(bridge.sessions.keys())[0]

                # Simulate launcher emitting ready
                on_output = MockLauncher.call_args.kwargs["on_output"]
                on_output("ready", {
                    "purpose": "fix login",
                    "worktree": "/tmp/swain/worktrees/fix-login",
                    "runtime": "claude",
                    "prompt": "/swain-session Session purpose: fix login",
                })
                await asyncio.sleep(0)

                # Session promoted event should be emitted
                promoted_events = [e for e in delivered if e.type == "session_promoted"]
                assert len(promoted_events) == 1
                assert promoted_events[0].payload["artifact"] == "fix login"

                # Session should no longer be control-origin
                session = bridge.sessions[sid]
                assert session.origin is None
                assert session.state == SessionState.SPAWNING

                # Runtime adapter should be spawned in the launcher's worktree
                MockAdapter.assert_called_once()
                assert MockAdapter.call_args.kwargs["project_dir"] == "/tmp/swain/worktrees/fix-login"
                adapter_instance.start.assert_awaited_once()

    async def test_launcher_info_relays_to_control(self):
        """Launcher info messages become text_output events with origin=control."""
        delivered: list[Event] = []

        with patch("untethered.bridges.project.LauncherProcess") as MockLauncher:
            mock_instance = AsyncMock()
            MockLauncher.return_value = mock_instance

            bridge = ProjectBridge(
                project="swain", project_dir="/tmp/swain",
                on_event=delivered.append,
            )

            bridge.handle_command(Command.launch_session(bridge="swain", text="status"))
            await asyncio.sleep(0)

            on_output = MockLauncher.call_args.kwargs["on_output"]
            on_output("info", {"text": "Previous session detected."})

            assert len(delivered) == 1
            assert delivered[0].type == "text_output"
            assert delivered[0].payload["content"] == "Previous session detected."
            assert delivered[0].payload["origin"] == "control"

    async def test_launcher_question_relays_with_options(self):
        """Launcher question messages show options in the text."""
        delivered: list[Event] = []

        with patch("untethered.bridges.project.LauncherProcess") as MockLauncher:
            mock_instance = AsyncMock()
            MockLauncher.return_value = mock_instance

            bridge = ProjectBridge(
                project="swain", project_dir="/tmp/swain",
                on_event=delivered.append,
            )

            bridge.handle_command(Command.launch_session(bridge="swain", text="work"))
            await asyncio.sleep(0)

            on_output = MockLauncher.call_args.kwargs["on_output"]
            on_output("question", {
                "text": "Resume or fresh?",
                "options": ["resume", "fresh"],
            })

            assert len(delivered) == 1
            assert "Resume or fresh?" in delivered[0].payload["content"]
            assert "resume/fresh" in delivered[0].payload["content"]


# ---------------------------------------------------------------------------
# Scenario: Full Zulip poll → command routing
# ---------------------------------------------------------------------------

class TestZulipPollControlRouting:
    """_poll_zulip correctly routes control-topic messages as control_message."""

    async def test_control_topic_plain_text_emits_control_message(self):
        received: list[Command] = []
        client = _make_poll_client([
            _make_get_events_response([_make_zulip_msg("what's next?", topic="control")]),
        ])
        registry = SessionTopicRegistry()
        loop = asyncio.get_running_loop()

        with pytest.raises(asyncio.CancelledError):
            await _poll_zulip(client, _STREAM_MAP, "control", received.append, registry, loop)

        assert len(received) == 1
        assert received[0].type == "control_message"
        assert received[0].payload["text"] == "what's next?"

    async def test_control_topic_work_command_emits_launch_session(self):
        received: list[Command] = []
        client = _make_poll_client([
            _make_get_events_response([_make_zulip_msg("/work SPEC-142", topic="control")]),
        ])
        registry = SessionTopicRegistry()
        loop = asyncio.get_running_loop()

        with pytest.raises(asyncio.CancelledError):
            await _poll_zulip(client, _STREAM_MAP, "control", received.append, registry, loop)

        assert len(received) == 1
        assert received[0].type == "launch_session"
        assert received[0].payload["text"] == "SPEC-142"

    async def test_session_topic_plain_text_emits_send_prompt(self):
        received: list[Command] = []
        registry = SessionTopicRegistry()
        # Register a session so topic resolution works
        registry.assign("sess-abc", "SPEC-142")

        client = _make_poll_client([
            _make_get_events_response([_make_zulip_msg("keep going", topic="SPEC-142")]),
        ])
        loop = asyncio.get_running_loop()

        with pytest.raises(asyncio.CancelledError):
            await _poll_zulip(client, _STREAM_MAP, "control", received.append, registry, loop)

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
            bridge="swain", session_id="sess-abc",
            artifact="SPEC-142", topic="SPEC-142",
        )
        line = encode_message(event)
        restored = decode_message(line)
        assert isinstance(restored, Event)
        assert restored.type == "session_promoted"
        assert restored.payload["artifact"] == "SPEC-142"


# ---------------------------------------------------------------------------
# Scenario: bin/swain NDJSON mode (subprocess test)
# ---------------------------------------------------------------------------

class TestLauncherNdjsonMode:
    """bin/swain --format ndjson produces structured NDJSON output."""

    async def test_launcher_emits_ready_with_fresh_flag(self):
        """--fresh skips interview, goes straight to ready."""
        import subprocess
        result = subprocess.run(
            ["bash", "bin/swain", "--format", "ndjson", "--fresh", "--trunk"],
            input="",
            capture_output=True,
            text=True,
            timeout=10,
        )
        lines = [l for l in result.stdout.strip().split("\n") if l]
        # Should have at least a ready message
        ready_lines = [json.loads(l) for l in lines if '"ready"' in l]
        assert len(ready_lines) >= 1
        ready = ready_lines[0]
        assert ready["type"] == "ready"
        assert "runtime" in ready
        assert "worktree" in ready
