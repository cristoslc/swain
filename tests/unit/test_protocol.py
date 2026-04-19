"""RED tests for the NDJSON plugin protocol — the published language from DESIGN-024."""
import json
import time

from swain_helm.protocol import (
    Event,
    Command,
    ConfigMessage,
    encode_message,
    decode_message,
    parse_ndjson_line,
)


class TestEventCreation:
    def test_text_output_event(self):
        event = Event.text_output(
            bridge="swain",
            session_id="sess-001",
            content="Hello from the runtime",
        )
        assert event.type == "text_output"
        assert event.bridge == "swain"
        assert event.session_id == "sess-001"
        assert event.payload["content"] == "Hello from the runtime"
        assert isinstance(event.timestamp, int)

    def test_tool_call_event(self):
        event = Event.tool_call(
            bridge="swain",
            session_id="sess-001",
            tool_name="Bash",
            input={"command": "ls"},
            call_id="call-abc",
        )
        assert event.type == "tool_call"
        assert event.payload["tool_name"] == "Bash"
        assert event.payload["call_id"] == "call-abc"

    def test_approval_needed_event(self):
        event = Event.approval_needed(
            bridge="swain",
            session_id="sess-001",
            tool_name="Bash",
            description="Run: rm -rf /tmp/test",
            call_id="call-xyz",
        )
        assert event.type == "approval_needed"
        assert event.payload["description"] == "Run: rm -rf /tmp/test"

    def test_session_spawned_event(self):
        event = Event.session_spawned(
            bridge="swain",
            session_id="sess-001",
            runtime="claude",
        )
        assert event.type == "session_spawned"
        assert event.payload["runtime"] == "claude"

    def test_session_died_event(self):
        event = Event.session_died(
            bridge="swain",
            session_id="sess-001",
            reason="process exited with code 0",
        )
        assert event.type == "session_died"
        assert event.payload["reason"] == "process exited with code 0"

    def test_host_scope_event_has_null_bridge(self):
        event = Event.unmanaged_session_found(
            tmux_target="swain-spec-142",
            runtime_hint="claude",
            project_path="/home/user/swain",
        )
        assert event.type == "unmanaged_session_found"
        assert event.bridge == "__host__"
        assert event.session_id is None


class TestCommandCreation:
    def test_send_prompt_command(self):
        cmd = Command.send_prompt(
            bridge="swain",
            session_id="sess-001",
            text="Work on SPEC-142",
        )
        assert cmd.type == "send_prompt"
        assert cmd.bridge == "swain"
        assert cmd.payload["text"] == "Work on SPEC-142"

    def test_approve_command(self):
        cmd = Command.approve(
            bridge="swain",
            session_id="sess-001",
            call_id="call-xyz",
            approved=True,
        )
        assert cmd.type == "approve"
        assert cmd.payload["approved"] is True

    def test_start_session_command(self):
        cmd = Command.start_session(
            bridge="swain",
            runtime="claude",
            prompt="Work on SPEC-142",
        )
        assert cmd.type == "start_session"
        assert cmd.payload["runtime"] == "claude"
        assert cmd.payload["prompt"] == "Work on SPEC-142"
        assert cmd.session_id is None

    def test_host_scope_command(self):
        cmd = Command.clone_project(
            repo_url="git@github.com:cristoslc/some-repo.git",
        )
        assert cmd.type == "clone_project"
        assert cmd.bridge == "__host__"


class TestSerialization:
    def test_encode_event_to_ndjson(self):
        event = Event.text_output(
            bridge="swain",
            session_id="sess-001",
            content="hello",
        )
        line = encode_message(event)
        assert line.endswith("\n")
        parsed = json.loads(line)
        assert parsed["type"] == "text_output"
        assert parsed["bridge"] == "swain"
        assert parsed["session_id"] == "sess-001"
        assert parsed["payload"]["content"] == "hello"

    def test_decode_ndjson_to_event(self):
        raw = json.dumps({
            "type": "text_output",
            "bridge": "swain",
            "session_id": "sess-001",
            "timestamp": int(time.time() * 1000),
            "payload": {"content": "hello"},
        })
        msg = decode_message(raw)
        assert isinstance(msg, Event)
        assert msg.type == "text_output"

    def test_decode_ndjson_to_command(self):
        raw = json.dumps({
            "type": "send_prompt",
            "bridge": "swain",
            "session_id": "sess-001",
            "timestamp": int(time.time() * 1000),
            "payload": {"text": "hello"},
        })
        msg = decode_message(raw)
        assert isinstance(msg, Command)
        assert msg.type == "send_prompt"

    def test_config_message(self):
        config = ConfigMessage(
            plugin_type="chat",
            config={"server_url": "https://example.zulipchat.com"},
        )
        line = encode_message(config)
        parsed = json.loads(line)
        assert parsed["type"] == "config"
        assert parsed["plugin_type"] == "chat"

    def test_roundtrip(self):
        event = Event.tool_call(
            bridge="rk",
            session_id="sess-002",
            tool_name="Read",
            input={"file_path": "/tmp/test.py"},
            call_id="call-123",
        )
        line = encode_message(event)
        decoded = decode_message(line)
        assert decoded.type == event.type
        assert decoded.bridge == event.bridge
        assert decoded.payload == event.payload

    def test_parse_ndjson_line_ignores_unknown_type(self):
        raw = json.dumps({
            "type": "future_event_type",
            "bridge": "swain",
            "session_id": None,
            "timestamp": int(time.time() * 1000),
            "payload": {"some": "data"},
        })
        msg = parse_ndjson_line(raw)
        assert msg is not None
        assert msg.type == "future_event_type"

    def test_parse_ndjson_line_returns_none_for_malformed(self):
        assert parse_ndjson_line("not json at all") is None
        assert parse_ndjson_line('{"no_type": true}') is None
