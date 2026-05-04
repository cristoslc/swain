"""Unit tests for TypingIndicator — the Zulip stream typing notification agent."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, AsyncMock

import pytest

from swain_helm.plugins.zulip_chat import TypingIndicator


class TestTypingIndicatorStart:
    """TypingIndicator.start creates a pulse task and safety timer."""

    async def test_start_creates_active_task(self):
        """start() creates a pulse task for the (stream, topic) key."""
        client = MagicMock()
        loop = asyncio.get_running_loop()
        ti = TypingIndicator(client, loop)

        ti.start("swain", "trunk")

        assert ("swain", "trunk") in ti._active
        task = ti._active[("swain", "trunk")]
        assert isinstance(task, asyncio.Task)
        assert not task.done()

    async def test_start_creates_safety_timer(self):
        """start() creates a safety timer that auto-stops after MAX_DURATION."""
        client = MagicMock()
        loop = asyncio.get_running_loop()
        ti = TypingIndicator(client, loop)

        ti.start("swain", "trunk")

        safety = ti._safety_timers.get(("swain", "trunk"))
        assert safety is not None

    async def test_start_idempotent(self):
        """Calling start twice for the same key does not create duplicate tasks."""
        client = MagicMock()
        loop = asyncio.get_running_loop()
        ti = TypingIndicator(client, loop)

        ti.start("swain", "trunk")
        first_task = ti._active[("swain", "trunk")]

        ti.start("swain", "trunk")
        second_task = ti._active[("swain", "trunk")]

        assert first_task is second_task

    async def test_start_different_keys_independent(self):
        """start() for different (stream, topic) keys creates independent tasks."""
        client = MagicMock()
        loop = asyncio.get_running_loop()
        ti = TypingIndicator(client, loop)

        ti.start("swain", "trunk")
        ti.start("swain", "SPEC-142")

        assert len(ti._active) == 2
        assert ("swain", "trunk") in ti._active
        assert ("swain", "SPEC-142") in ti._active


class TestTypingIndicatorStop:
    """TypingIndicator.stop cancels the pulse task and safety timer."""

    async def test_stop_cancels_pulse_task(self):
        """stop() cancels the pulse task and removes it from _active."""
        client = MagicMock()
        loop = asyncio.get_running_loop()
        ti = TypingIndicator(client, loop)

        ti.start("swain", "trunk")
        task = ti._active[("swain", "trunk")]

        ti.stop("swain", "trunk")
        await asyncio.sleep(0)

        assert ("swain", "trunk") not in ti._active

    async def test_stop_cancels_safety_timer(self):
        """stop() cancels the safety timer and removes it."""
        client = MagicMock()
        loop = asyncio.get_running_loop()
        ti = TypingIndicator(client, loop)

        ti.start("swain", "trunk")
        timer = ti._safety_timers[("swain", "trunk")]

        ti.stop("swain", "trunk")

        assert timer.cancelled()
        assert ("swain", "trunk") not in ti._safety_timers

    async def test_stop_sends_typing_stop(self):
        """stop() calls _send_typing with op='stop'."""
        client = MagicMock()
        client.get_stream_id.return_value = {"stream_id": 42}
        loop = asyncio.get_running_loop()
        ti = TypingIndicator(client, loop)

        ti.start("swain", "trunk")
        ti.stop("swain", "trunk")

        client.set_typing_status.assert_called_once()
        call_kwargs = client.set_typing_status.call_args[0][0]
        assert call_kwargs["op"] == "stop"
        assert call_kwargs["stream_id"] == 42
        assert call_kwargs["topic"] == "trunk"

    async def test_stop_nonexistent_key_sends_stop_anyway(self):
        """stop() with no active key still sends 'stop' to Zulip."""
        client = MagicMock()
        client.get_stream_id.return_value = {"stream_id": 42}
        loop = asyncio.get_running_loop()
        ti = TypingIndicator(client, loop)

        ti.stop("swain", "nonexistent")

        client.set_typing_status.assert_called_once()
        call_kwargs = client.set_typing_status.call_args[0][0]
        assert call_kwargs["op"] == "stop"


class TestTypingIndicatorStopAll:
    """TypingIndicator.stop_all cancels all active pulse tasks."""

    async def test_stop_all_cancels_all_active(self):
        """stop_all() cancels every active pulse task."""
        client = MagicMock()
        loop = asyncio.get_running_loop()
        ti = TypingIndicator(client, loop)

        ti.start("swain", "trunk")
        ti.start("swain", "SPEC-142")

        ti.stop_all()

        for key, task in ti._active.items():
            assert task.cancelled()
        assert len(ti._active) == 0


class TestTypingIndicatorSendTyping:
    """TypingIndicator._send_typing calls Zulip API."""

    async def test_send_typing_calls_get_stream_id_and_set_typing_status(self):
        """_send_typing resolves stream ID then calls set_typing_status."""
        client = MagicMock()
        client.get_stream_id.return_value = {"stream_id": 42}
        loop = asyncio.get_running_loop()
        ti = TypingIndicator(client, loop)

        ti._send_typing("swain", "trunk", "start")

        client.get_stream_id.assert_called_once_with("swain")
        client.set_typing_status.assert_called_once()
        call_kwargs = client.set_typing_status.call_args[0][0]
        assert call_kwargs["op"] == "start"
        assert call_kwargs["stream_id"] == 42
        assert call_kwargs["type"] == "stream"
        assert call_kwargs["topic"] == "trunk"

    async def test_send_typing_swallows_exception(self):
        """_send_typing logs at debug and does not raise on API errors."""
        client = MagicMock()
        client.get_stream_id.side_effect = Exception("network error")
        loop = asyncio.get_running_loop()
        ti = TypingIndicator(client, loop)

        ti._send_typing("swain", "trunk", "start")

        client.set_typing_status.assert_not_called()

    async def test_send_typing_no_stream_id_no_op(self):
        """_send_typing does nothing if get_stream_id returns no stream_id."""
        client = MagicMock()
        client.get_stream_id.return_value = {}
        loop = asyncio.get_running_loop()
        ti = TypingIndicator(client, loop)

        ti._send_typing("swain", "trunk", "start")

        client.set_typing_status.assert_not_called()
