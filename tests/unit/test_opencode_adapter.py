"""Unit tests for OpenCodeServerAdapter SSE event handling.

Tests reasoning/thinking detection, duplicate turn_ended suppression,
and text delta accumulation without requiring a real opencode server.
"""

from __future__ import annotations

import pytest

from swain_helm.adapters.opencode_server import OpenCodeServerAdapter
from swain_helm.protocol import Event


def _make_adapter(events: list[Event] | None = None) -> OpenCodeServerAdapter:
    if events is None:
        events = []
    return OpenCodeServerAdapter(
        bridge="swain",
        session_id="sess-test",
        base_url="http://127.0.0.1:0",
        on_event=events.append,
    )


def _sse(event_type: str, properties: dict) -> dict:
    """Build an SSE event dict in the format _on_sse_event expects."""
    return {"type": event_type, "data": {"properties": properties}}


class TestReasoningDetection:
    """OpenCode sends 'reasoning' as the field/type for extended thinking."""

    def test_part_updated_with_reasoning_type_emits_thinking_output(self):
        events: list[Event] = []
        adapter = _make_adapter(events)
        adapter._oc_session_id = "ses_test"

        adapter._on_sse_event(
            _sse(
                "message.part.updated",
                {
                    "sessionID": "ses_test",
                    "part": {
                        "id": "prt_1",
                        "type": "reasoning",
                        "thinking": "Let me think about this...",
                    },
                },
            )
        )

        assert len(events) == 1
        assert events[0].type == "thinking_output"
        assert "Let me think about this" in events[0].payload["content"]

    def test_delta_with_field_reasoning_emits_thinking_output(self):
        events: list[Event] = []
        adapter = _make_adapter(events)
        adapter._oc_session_id = "ses_test"

        adapter._on_sse_event(
            _sse(
                "message.part.delta",
                {
                    "sessionID": "ses_test",
                    "partID": "prt_reason_1",
                    "field": "reasoning",
                    "delta": "Hmm, ",
                },
            )
        )
        adapter._on_sse_event(
            _sse(
                "message.part.delta",
                {
                    "sessionID": "ses_test",
                    "partID": "prt_reason_1",
                    "field": "reasoning",
                    "delta": "let me think...",
                },
            )
        )

        thinking_events = [e for e in events if e.type == "thinking_output"]
        assert len(thinking_events) == 2
        assert "Hmm, " in thinking_events[0].payload["content"]
        assert "let me think..." in thinking_events[1].payload["content"]

    def test_text_delta_from_reasoning_part_preserves_type(self):
        """OpenCode sends field=text on deltas even for reasoning parts.

        The first part.updated establishes the part type as 'reasoning',
        then subsequent deltas come with field=text but should still be
        classified as thinking because _part_types stores the original type.
        """
        events: list[Event] = []
        adapter = _make_adapter(events)
        adapter._oc_session_id = "ses_test"

        adapter._on_sse_event(
            _sse(
                "message.part.updated",
                {
                    "sessionID": "ses_test",
                    "part": {
                        "id": "prt_r2",
                        "type": "reasoning",
                    },
                },
            )
        )

        adapter._on_sse_event(
            _sse(
                "message.part.delta",
                {
                    "sessionID": "ses_test",
                    "partID": "prt_r2",
                    "field": "text",
                    "delta": "reasoning content here",
                },
            )
        )

        text_events = [e for e in events if e.type == "text_output"]
        thinking_events = [e for e in events if e.type == "thinking_output"]
        assert len(text_events) == 0
        assert len(thinking_events) == 1
        assert "reasoning content here" in thinking_events[0].payload["content"]

    def test_thinking_type_also_emits_thinking_output(self):
        """Both 'thinking' and 'reasoning' part types map to thinking_output."""
        events: list[Event] = []
        adapter = _make_adapter(events)
        adapter._oc_session_id = "ses_test"

        adapter._on_sse_event(
            _sse(
                "message.part.updated",
                {
                    "sessionID": "ses_test",
                    "part": {
                        "id": "prt_t1",
                        "type": "thinking",
                        "thinking": "hmm",
                    },
                },
            )
        )

        assert len(events) == 1
        assert events[0].type == "thinking_output"


class TestDuplicateTurnEnded:
    """Turn-ended should only be emitted once per turn.

    OpenCode sends both session.status (type=idle) and session.idle,
    which would cause duplicate turn_ended events without a guard.
    """

    def test_session_idle_emits_turn_ended(self):
        events: list[Event] = []
        adapter = _make_adapter(events)
        adapter._oc_session_id = "ses_test"

        adapter._on_sse_event(
            _sse(
                "session.idle",
                {
                    "sessionID": "ses_test",
                },
            )
        )

        turn_ended = [e for e in events if e.type == "turn_ended"]
        assert len(turn_ended) == 1

    def test_session_status_idle_emits_turn_ended(self):
        events: list[Event] = []
        adapter = _make_adapter(events)
        adapter._oc_session_id = "ses_test"

        adapter._on_sse_event(
            _sse(
                "session.status",
                {
                    "sessionID": "ses_test",
                    "status": {"type": "idle"},
                },
            )
        )

        turn_ended = [e for e in events if e.type == "turn_ended"]
        assert len(turn_ended) == 1

    def test_no_duplicate_turn_ended_from_idle_and_status(self):
        """Both session.status(idle) and session.idle should only emit one turn_ended."""
        events: list[Event] = []
        adapter = _make_adapter(events)
        adapter._oc_session_id = "ses_test"

        adapter._on_sse_event(
            _sse(
                "session.status",
                {
                    "sessionID": "ses_test",
                    "status": {"type": "idle"},
                },
            )
        )
        adapter._on_sse_event(
            _sse(
                "session.status",
                {
                    "sessionID": "ses_test",
                    "status": {"type": "idle"},
                },
            )
        )
        adapter._on_sse_event(
            _sse(
                "session.idle",
                {
                    "sessionID": "ses_test",
                },
            )
        )

        turn_ended = [e for e in events if e.type == "turn_ended"]
        assert len(turn_ended) == 1, f"Expected 1 turn_ended, got {len(turn_ended)}"

    def test_new_prompt_allows_another_turn_ended(self):
        """After _send_message resets _turn_ended_generation, a new idle can emit turn_ended."""
        events: list[Event] = []
        adapter = _make_adapter(events)
        adapter._oc_session_id = "ses_test"

        adapter._on_sse_event(
            _sse(
                "session.idle",
                {
                    "sessionID": "ses_test",
                },
            )
        )
        assert len([e for e in events if e.type == "turn_ended"]) == 1

        # Simulate a new turn
        adapter._turn_ended_generation = -1
        adapter._on_sse_event(
            _sse(
                "session.idle",
                {
                    "sessionID": "ses_test",
                },
            )
        )
        assert len([e for e in events if e.type == "turn_ended"]) == 2


class TestTextDeltaAccumulation:
    """Text deltas are accumulated and deduplicated against part-updated content."""

    def test_part_updated_skips_already_flushed_content(self):
        events: list[Event] = []
        adapter = _make_adapter(events)
        adapter._oc_session_id = "ses_test"

        adapter._on_sse_event(
            _sse(
                "message.part.delta",
                {
                    "sessionID": "ses_test",
                    "partID": "prt_t1",
                    "field": "text",
                    "delta": "Hello",
                },
            )
        )

        adapter._on_sse_event(
            _sse(
                "message.part.updated",
                {
                    "sessionID": "ses_test",
                    "part": {
                        "id": "prt_t1",
                        "type": "text",
                        "text": "Hello world",
                    },
                },
            )
        )

        text_events = [e for e in events if e.type == "text_output"]
        contents = "".join(e.payload["content"] for e in text_events)
        assert "Hello" in contents
        assert "world" in contents

    def test_reasoning_not_sent_as_text(self):
        events: list[Event] = []
        adapter = _make_adapter(events)
        adapter._oc_session_id = "ses_test"

        adapter._on_sse_event(
            _sse(
                "message.part.updated",
                {
                    "sessionID": "ses_test",
                    "part": {
                        "id": "prt_r1",
                        "type": "reasoning",
                        "thinking": "internal reasoning",
                    },
                },
            )
        )

        text_events = [e for e in events if e.type == "text_output"]
        thinking_events = [e for e in events if e.type == "thinking_output"]
        assert len(text_events) == 0
        assert len(thinking_events) == 1


class TestUserMessageSuppression:
    """Text from user messages should not be echoed back."""

    def test_delta_from_user_message_suppressed(self):
        events: list[Event] = []
        adapter = _make_adapter(events)
        adapter._oc_session_id = "ses_test"
        adapter._user_message_ids.add("msg_user_1")

        adapter._on_sse_event(
            _sse(
                "message.part.delta",
                {
                    "sessionID": "ses_test",
                    "messageID": "msg_user_1",
                    "partID": "prt_u1",
                    "field": "text",
                    "delta": "user typed this",
                },
            )
        )

        assert len(events) == 0

    def test_part_updated_from_user_message_suppressed(self):
        events: list[Event] = []
        adapter = _make_adapter(events)
        adapter._oc_session_id = "ses_test"
        adapter._user_message_ids.add("msg_user_1")

        adapter._on_sse_event(
            _sse(
                "message.part.updated",
                {
                    "sessionID": "ses_test",
                    "messageID": "msg_user_1",
                    "part": {
                        "id": "prt_u1",
                        "type": "text",
                        "text": "user typed this",
                    },
                },
            )
        )

        assert len(events) == 0
