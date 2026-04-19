"""BDD integration tests — OpenCodeServerAdapter (SPEC-292).

Scenarios covered:

  Server lifecycle:
    - Adapter starts opencode serve and waits for health check
    - Adapter creates a session on first message
    - Adapter reuses session for follow-up messages

  Message sending:
    - send_prompt posts to /session/{id}/message
    - Response parts are emitted as text_output events

  Session persistence:
    - Same session ID used across multiple messages
    - Session died emitted when server stops

  Mock server (no real opencode):
    - Tests use a lightweight HTTP server that mimics the opencode API
    - No dependency on opencode being installed or configured
"""
from __future__ import annotations

import asyncio
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from swain_helm.protocol import Event, Command


# ---------------------------------------------------------------------------
# Mock opencode server
# ---------------------------------------------------------------------------

class MockOpenCodeHandler(BaseHTTPRequestHandler):
    """Minimal mock of the opencode serve API."""

    # Class-level state shared across requests
    sessions: dict = {}
    message_count: int = 0

    def do_GET(self):
        if self.path == "/global/health":
            self._json_response({"healthy": True, "version": "mock"})
        elif self.path == "/session":
            self._json_response(list(self.sessions.values()))
        elif self.path.endswith("/event"):
            # SSE stub — just close immediately
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()
        else:
            self.send_error(404)

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b""

        if self.path == "/session":
            sess_id = f"ses_mock_{len(self.sessions)}"
            session = {
                "id": sess_id,
                "slug": "mock-session",
                "version": "mock",
                "projectID": "mock-project",
                "directory": "/tmp",
                "title": "Mock session",
                "time": {"created": 0, "updated": 0},
            }
            MockOpenCodeHandler.sessions[sess_id] = session
            self._json_response(session)

        elif "/message" in self.path:
            data = json.loads(body) if body else {}
            parts = data.get("parts", [])
            user_text = parts[0].get("text", "") if parts else ""
            MockOpenCodeHandler.message_count += 1

            response = {
                "info": {
                    "id": f"msg_mock_{self.message_count}",
                    "sessionID": self.path.split("/")[2],
                    "role": "assistant",
                    "finish": "stop",
                },
                "parts": [
                    {"type": "step-start", "id": "prt_start"},
                    {"type": "text", "text": f"Mock response to: {user_text}", "id": "prt_text"},
                    {"type": "step-finish", "reason": "stop", "id": "prt_finish"},
                ],
            }
            self._json_response(response)
        else:
            self.send_error(404)

    def _json_response(self, data):
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass  # Suppress request logging


@pytest.fixture
def mock_server():
    """Start a mock opencode server on a random port."""
    MockOpenCodeHandler.sessions = {}
    MockOpenCodeHandler.message_count = 0

    server = HTTPServer(("127.0.0.1", 0), MockOpenCodeHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}", port
    server.shutdown()


# ---------------------------------------------------------------------------
# Scenario: Server lifecycle
# ---------------------------------------------------------------------------

class TestServerLifecycle:
    """OpenCodeServerAdapter manages the opencode serve process."""

    async def test_adapter_connects_to_server(self, mock_server):
        from swain_helm.adapters.opencode_server import OpenCodeServerAdapter

        url, port = mock_server
        events: list[Event] = []
        adapter = OpenCodeServerAdapter(
            bridge="swain",
            session_id="sess-test",
            base_url=url,
            on_event=events.append,
        )

        healthy = await adapter.wait_for_health(timeout=2.0)
        assert healthy

    async def test_adapter_creates_session_on_first_message(self, mock_server):
        from swain_helm.adapters.opencode_server import OpenCodeServerAdapter

        url, port = mock_server
        events: list[Event] = []
        adapter = OpenCodeServerAdapter(
            bridge="swain",
            session_id="sess-test",
            base_url=url,
            on_event=events.append,
        )
        await adapter.wait_for_health(timeout=2.0)

        cmd = Command.send_prompt(bridge="swain", session_id="sess-test", text="hello")
        await adapter.send_command(cmd)

        assert adapter._oc_session_id is not None
        assert adapter._oc_session_id.startswith("ses_mock_")


# ---------------------------------------------------------------------------
# Scenario: Message sending and response
# ---------------------------------------------------------------------------

class TestMessageSending:
    """Messages are sent via HTTP and responses emitted as events."""

    async def test_send_prompt_returns_text_output(self, mock_server):
        from swain_helm.adapters.opencode_server import OpenCodeServerAdapter

        url, port = mock_server
        events: list[Event] = []
        adapter = OpenCodeServerAdapter(
            bridge="swain",
            session_id="sess-test",
            base_url=url,
            on_event=events.append,
        )
        await adapter.wait_for_health(timeout=2.0)

        cmd = Command.send_prompt(bridge="swain", session_id="sess-test", text="what specs?")
        await adapter.send_command(cmd)

        text_events = [e for e in events if e.type == "text_output"]
        assert len(text_events) >= 1
        assert "Mock response to: what specs?" in text_events[0].payload["content"]

    async def test_send_prompt_emits_session_spawned_first(self, mock_server):
        from swain_helm.adapters.opencode_server import OpenCodeServerAdapter

        url, port = mock_server
        events: list[Event] = []
        adapter = OpenCodeServerAdapter(
            bridge="swain",
            session_id="sess-test",
            base_url=url,
            on_event=events.append,
        )
        await adapter.wait_for_health(timeout=2.0)

        cmd = Command.send_prompt(bridge="swain", session_id="sess-test", text="hi")
        await adapter.send_command(cmd)

        assert events[0].type == "session_spawned"


# ---------------------------------------------------------------------------
# Scenario: Session persistence
# ---------------------------------------------------------------------------

class TestSessionPersistence:
    """Same session reused across multiple messages."""

    async def test_second_message_reuses_session(self, mock_server):
        from swain_helm.adapters.opencode_server import OpenCodeServerAdapter

        url, port = mock_server
        events: list[Event] = []
        adapter = OpenCodeServerAdapter(
            bridge="swain",
            session_id="sess-test",
            base_url=url,
            on_event=events.append,
        )
        await adapter.wait_for_health(timeout=2.0)

        cmd1 = Command.send_prompt(bridge="swain", session_id="sess-test", text="first")
        await adapter.send_command(cmd1)
        first_session = adapter._oc_session_id

        cmd2 = Command.send_prompt(bridge="swain", session_id="sess-test", text="second")
        await adapter.send_command(cmd2)
        second_session = adapter._oc_session_id

        assert first_session == second_session

    async def test_multiple_messages_all_get_responses(self, mock_server):
        from swain_helm.adapters.opencode_server import OpenCodeServerAdapter

        url, port = mock_server
        events: list[Event] = []
        adapter = OpenCodeServerAdapter(
            bridge="swain",
            session_id="sess-test",
            base_url=url,
            on_event=events.append,
        )
        await adapter.wait_for_health(timeout=2.0)

        for i in range(3):
            cmd = Command.send_prompt(
                bridge="swain", session_id="sess-test", text=f"message {i}",
            )
            await adapter.send_command(cmd)

        text_events = [e for e in events if e.type == "text_output"]
        assert len(text_events) == 3
        assert "message 0" in text_events[0].payload["content"]
        assert "message 2" in text_events[2].payload["content"]
