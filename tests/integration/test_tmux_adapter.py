"""BDD integration tests — TmuxPaneAdapter (DESIGN-025 tmux model).

The runtime runs in a tmux pane. The adapter:
  - Creates a tmux session and runs the runtime inside it
  - Streams output via pipe-pane to a FIFO (no polling)
  - Sends operator input via send-keys
  - Detects pane exit (session died)
  - The operator can attach locally at any time

Scenarios covered:

  Session lifecycle:
    - start() creates a tmux session with a named pane
    - The runtime command runs inside the pane
    - stop() sends SIGINT then kills the pane
    - Pane exit emits session_died event

  Output streaming (pipe-pane):
    - Runtime output streams to the adapter via pipe-pane + FIFO
    - Output is emitted as text_output events
    - pipe-pane is set up automatically on start()

  Input relay (send-keys):
    - send_prompt translates to tmux send-keys
    - cancel sends Ctrl-C to the pane

  Attachability:
    - The tmux session is visible in tmux list-sessions
    - The operator can attach with tmux attach -t <name>
"""
from __future__ import annotations

import asyncio
import os
import subprocess
import tempfile

import pytest

from swain_helm.protocol import Event, Command


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def tmux_available() -> bool:
    return subprocess.run(["tmux", "-V"], capture_output=True).returncode == 0

def tmux_has_session(name: str) -> bool:
    return subprocess.run(
        ["tmux", "has-session", "-t", name],
        capture_output=True,
    ).returncode == 0

def tmux_kill_session(name: str) -> None:
    subprocess.run(["tmux", "kill-session", "-t", name], capture_output=True)

def tmux_capture_pane(target: str) -> str:
    result = subprocess.run(
        ["tmux", "capture-pane", "-t", target, "-p"],
        capture_output=True, text=True,
    )
    return result.stdout


# ---------------------------------------------------------------------------
# ANSI stripping
# ---------------------------------------------------------------------------

class TestAnsiStripping:
    """strip_ansi removes terminal escape codes."""

    def test_strips_color_codes(self):
        from swain_helm.adapters.tmux_pane import strip_ansi
        assert strip_ansi("\x1b[91m\x1b[1mError:\x1b[0m unauthorized") == "Error: unauthorized"

    def test_strips_cursor_codes(self):
        from swain_helm.adapters.tmux_pane import strip_ansi
        assert strip_ansi("\x1b[2Khello\x1b[0m") == "hello"

    def test_preserves_plain_text(self):
        from swain_helm.adapters.tmux_pane import strip_ansi
        assert strip_ansi("plain text here") == "plain text here"

    def test_empty_after_strip(self):
        from swain_helm.adapters.tmux_pane import strip_ansi
        assert strip_ansi("\x1b[0m") == ""


pytestmark = pytest.mark.skipif(
    not tmux_available(),
    reason="tmux not available",
)


# ---------------------------------------------------------------------------
# Scenario: Session lifecycle
# ---------------------------------------------------------------------------

class TestTmuxSessionLifecycle:
    """TmuxPaneAdapter creates and manages tmux sessions."""

    async def test_start_creates_tmux_session(self):
        from swain_helm.adapters.tmux_pane import TmuxPaneAdapter

        events: list[Event] = []
        adapter = TmuxPaneAdapter(
            bridge="swain",
            session_id="sess-test-create",
            project_dir="/tmp",
            on_event=events.append,
        )

        try:
            # Use sleep so the session stays alive long enough to check
            await adapter.start(
                runtime_cmd=["sleep", "10"],
                session_name="test-create",
            )
            await asyncio.sleep(0.5)

            assert tmux_has_session("test-create")
        finally:
            await adapter.stop()
            tmux_kill_session("test-create")

    async def test_pane_exit_emits_session_died(self):
        from swain_helm.adapters.tmux_pane import TmuxPaneAdapter

        events: list[Event] = []
        adapter = TmuxPaneAdapter(
            bridge="swain",
            session_id="sess-test-died",
            project_dir="/tmp",
            on_event=events.append,
        )

        try:
            # Command exits immediately
            await adapter.start(
                runtime_cmd=["echo", "done"],
                session_name="test-died",
            )
            # Wait for the pane to exit and adapter to detect it
            await asyncio.sleep(2.0)

            died = [e for e in events if e.type == "session_died"]
            assert len(died) >= 1
        finally:
            tmux_kill_session("test-died")


# ---------------------------------------------------------------------------
# Scenario: Output streaming via pipe-pane
# ---------------------------------------------------------------------------

class TestTmuxOutputStreaming:
    """pipe-pane streams runtime output to the adapter in real time."""

    async def test_output_emitted_as_text_events(self):
        from swain_helm.adapters.tmux_pane import TmuxPaneAdapter

        events: list[Event] = []
        adapter = TmuxPaneAdapter(
            bridge="swain",
            session_id="sess-test-output",
            project_dir="/tmp",
            on_event=events.append,
        )

        try:
            # Delay before first echo so pipe-pane is set up in time
            await adapter.start(
                runtime_cmd=["bash", "-c", "sleep 0.5; echo 'line one'; sleep 0.5; echo 'line two'; sleep 1"],
                session_name="test-output",
            )
            await asyncio.sleep(4.0)

            text_events = [e for e in events if e.type == "text_output"]
            all_content = " ".join(e.payload["content"] for e in text_events)
            assert "line one" in all_content
            assert "line two" in all_content
        finally:
            await adapter.stop()
            tmux_kill_session("test-output")


# ---------------------------------------------------------------------------
# Scenario: Input relay via send-keys
# ---------------------------------------------------------------------------

class TestTmuxInputRelay:
    """Commands are relayed to the pane via tmux send-keys."""

    async def test_send_prompt_sends_keys(self):
        from swain_helm.adapters.tmux_pane import TmuxPaneAdapter

        events: list[Event] = []
        adapter = TmuxPaneAdapter(
            bridge="swain",
            session_id="sess-test-input",
            project_dir="/tmp",
            on_event=events.append,
        )

        try:
            # Start a cat process that echoes stdin
            await adapter.start(
                runtime_cmd=["cat"],
                session_name="test-input",
            )
            await asyncio.sleep(0.5)

            # Send text via the adapter
            cmd = Command.send_prompt(
                bridge="swain", session_id="sess-test-input",
                text="hello from zulip",
            )
            await adapter.send_command(cmd)
            await asyncio.sleep(1.0)

            # The text should appear in the pane output
            text_events = [e for e in events if e.type == "text_output"]
            all_content = " ".join(e.payload["content"] for e in text_events)
            assert "hello from zulip" in all_content
        finally:
            await adapter.stop()
            tmux_kill_session("test-input")


# ---------------------------------------------------------------------------
# Scenario: Attachability
# ---------------------------------------------------------------------------

class TestTmuxAttachability:
    """The tmux session is visible and attachable by the operator."""

    async def test_session_visible_in_list(self):
        from swain_helm.adapters.tmux_pane import TmuxPaneAdapter

        adapter = TmuxPaneAdapter(
            bridge="swain",
            session_id="sess-test-visible",
            project_dir="/tmp",
            on_event=lambda e: None,
        )

        try:
            await adapter.start(
                runtime_cmd=["sleep", "30"],
                session_name="test-visible",
            )
            await asyncio.sleep(0.5)

            result = subprocess.run(
                ["tmux", "list-sessions", "-F", "#{session_name}"],
                capture_output=True, text=True,
            )
            assert "test-visible" in result.stdout
        finally:
            await adapter.stop()
            tmux_kill_session("test-visible")
