"""RED tests for the Claude Code runtime adapter plugin."""
import json
import asyncio

from swain_helm.protocol import Event, Command
from swain_helm.adapters.claude_code import (
    parse_claude_stream_event,
    format_command_for_claude,
    ClaudeCodeAdapter,
)


class TestParseClaudeStreamEvent:
    """Claude Code --output-format stream-json emits these event shapes."""

    def test_system_init(self):
        raw = {"type": "system", "subtype": "init", "session_id": "abc123"}
        event = parse_claude_stream_event(raw, bridge="swain")
        assert event.type == "session_spawned"
        assert event.payload["runtime"] == "claude"
        assert event.session_id == "abc123"

    def test_text_content(self):
        raw = {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": "Hello world"}],
            },
        }
        events = parse_claude_stream_event(raw, bridge="swain", session_id="abc")
        # May return a single event or list — normalize
        if isinstance(events, list):
            text_events = [e for e in events if e.type == "text_output"]
            assert len(text_events) == 1
            assert text_events[0].payload["content"] == "Hello world"
        else:
            assert events.type == "text_output"
            assert events.payload["content"] == "Hello world"

    def test_tool_use(self):
        raw = {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [{
                    "type": "tool_use",
                    "id": "call_123",
                    "name": "Bash",
                    "input": {"command": "ls"},
                }],
            },
        }
        events = parse_claude_stream_event(raw, bridge="swain", session_id="abc")
        if isinstance(events, list):
            tool_events = [e for e in events if e.type == "tool_call"]
            assert len(tool_events) == 1
            assert tool_events[0].payload["tool_name"] == "Bash"
            assert tool_events[0].payload["call_id"] == "call_123"
        else:
            assert events.type == "tool_call"

    def test_tool_result(self):
        raw = {
            "type": "tool",
            "message": {
                "role": "tool",
                "tool_use_id": "call_123",
                "content": "file1.py\nfile2.py",
            },
        }
        event = parse_claude_stream_event(raw, bridge="swain", session_id="abc")
        assert event.type == "tool_result"
        assert event.payload["call_id"] == "call_123"
        assert event.payload["success"] is True

    def test_system_finish(self):
        raw = {"type": "system", "subtype": "result", "session_id": "abc123",
               "result": "success"}
        event = parse_claude_stream_event(raw, bridge="swain", session_id="abc123")
        assert event.type == "session_died"
        assert "success" in event.payload["reason"]


class TestFormatCommandForClaude:
    """Commands must be formatted for Claude Code's --input-format stream-json."""

    def test_send_prompt(self):
        cmd = Command.send_prompt(bridge="swain", session_id="abc", text="hello")
        formatted = format_command_for_claude(cmd)
        parsed = json.loads(formatted)
        assert parsed["type"] == "user"
        assert "hello" in json.dumps(parsed)

    def test_approve_allowed(self):
        cmd = Command.approve(bridge="swain", session_id="abc",
                              call_id="call_123", approved=True)
        formatted = format_command_for_claude(cmd)
        parsed = json.loads(formatted)
        # Claude expects permission responses in a specific format
        assert parsed is not None


class TestClaudeCodeAdapterLifecycle:
    """Integration-style tests using a mock subprocess."""

    def test_adapter_has_required_methods(self):
        adapter = ClaudeCodeAdapter.__new__(ClaudeCodeAdapter)
        assert hasattr(adapter, "start")
        assert hasattr(adapter, "stop")
        assert hasattr(adapter, "send_command")
        assert callable(adapter.start)
        assert callable(adapter.stop)
        assert callable(adapter.send_command)
