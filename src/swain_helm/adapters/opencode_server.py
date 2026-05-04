"""OpenCode Server runtime adapter (SPEC-292).

Connects to an opencode serve process managed by the watchdog.
Uses prompt_async for non-blocking message sending and SSE for
streaming responses. The operator can attach via
`opencode attach http://127.0.0.1:<port>`.
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from typing import Any, Callable
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

from swain_helm.protocol import (
    Event,
    Command,
    ConfigMessage,
    encode_message,
)

log = logging.getLogger(__name__)


class SSEClient:
    """Minimal SSE client using stdlib http.client for streaming.

    Connects to GET /event and yields parsed event dicts.
    Reconnects automatically on connection loss.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self._running = False
        self._reconnect_delay = 1.0
        self._max_reconnect_delay = 30.0

    async def listen(self, on_event: Callable[[dict], None]) -> None:
        """Connect to GET /event and call on_event for each parsed SSE event.

        Runs until stop() is called. Reconnects on connection errors
        with exponential backoff.
        """
        import http.client
        from urllib.parse import urlparse

        self._running = True
        parsed = urlparse(self.base_url)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or 80

        while self._running:
            try:
                conn = http.client.HTTPConnection(host, port, timeout=30)
                conn.request("GET", "/event", headers={"Accept": "text/event-stream"})
                resp = conn.getresponse()

                if resp.status != 200:
                    log.warning(
                        "SSE endpoint returned %d, reconnecting...", resp.status
                    )
                    conn.close()
                    await asyncio.sleep(self._reconnect_delay)
                    self._reconnect_delay = min(
                        self._reconnect_delay * 2, self._max_reconnect_delay
                    )
                    continue

                self._reconnect_delay = 1.0
                event_type = ""
                data_buf = ""

                while self._running:
                    try:
                        line = await asyncio.get_running_loop().run_in_executor(
                            None, resp.readline
                        )
                    except Exception:
                        break
                    if not line:
                        break

                    line_str = line.decode("utf-8", errors="replace")

                    if line_str.startswith("event:"):
                        event_type = line_str[6:].strip()
                    elif line_str.startswith("data:"):
                        data_buf += line_str[5:].strip() + "\n"
                    elif line_str.strip() == "":
                        if data_buf.strip():
                            try:
                                payload = json.loads(data_buf.strip())
                                on_event(
                                    {
                                        "type": event_type or payload.get("type", ""),
                                        "data": payload,
                                    }
                                )
                            except json.JSONDecodeError:
                                on_event(
                                    {
                                        "type": event_type,
                                        "data": {"raw": data_buf.strip()},
                                    }
                                )
                        event_type = ""
                        data_buf = ""

                conn.close()
            except (OSError, http.client.HTTPException) as exc:
                if not self._running:
                    break
                log.warning("SSE connection error: %s, reconnecting...", exc)
                await asyncio.sleep(self._reconnect_delay)
                self._reconnect_delay = min(
                    self._reconnect_delay * 2, self._max_reconnect_delay
                )

    def stop(self) -> None:
        self._running = False


class OpenCodeServerAdapter:
    """HTTP client adapter for opencode serve.

    Uses prompt_async + SSE for streaming responses:
    - Sends messages via POST /session/{id}/prompt_async (204, non-blocking)
    - Listens to GET /event for streaming message.part.delta and session.idle
    - Emits text_output events incrementally, turn_ended on session.idle
    - Falls back to synchronous POST /session/{id}/message if SSE is unavailable
    """

    def __init__(
        self,
        bridge: str,
        session_id: str,
        *,
        base_url: str = "http://127.0.0.1:4098",
        origin: str | None = None,
        on_event: Callable[[Event], None] | None = None,
    ):
        self.bridge = bridge
        self.session_id = session_id
        self.base_url = base_url.rstrip("/")
        self.origin = origin
        self.on_event = on_event
        self._oc_session_id: str | None = None
        self._spawned = False
        self._sse_client: SSEClient | None = None
        self._sse_task: asyncio.Task | None = None
        self._text_buffer: dict[str, list[str]] = {}
        self._flushed_up_to: dict[str, int] = {}
        self._part_types: dict[str, str] = {}
        self._user_message_ids: set[str] = set()
        self._turn_timeout: float = 300.0
        self._turn_timer_task: asyncio.Task | None = None
        self._turn_generation: int = 0
        self._turn_ended_generation: int = -1
        self._suppress_idle: bool = False
        self._suppress_events: bool = False

    async def wait_for_health(self, timeout: float = 30.0) -> bool:
        """Poll /global/health until the server is ready."""
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout
        while loop.time() < deadline:
            try:
                data = await loop.run_in_executor(
                    None,
                    lambda: self._get("/global/health"),
                )
                if data and data.get("healthy"):
                    return True
            except Exception:
                pass
            await asyncio.sleep(0.5)
        return False

    async def setup(self) -> None:
        """Start the SSE listener after health check."""
        self._sse_client = SSEClient(self.base_url)
        self._sse_task = asyncio.create_task(
            self._sse_client.listen(self._on_sse_event)
        )
        log.info("SSE listener started for %s", self.base_url)

    async def send_command(self, cmd: Command) -> None:
        """Handle a protocol Command by sending it to the opencode server."""
        if cmd.type == "send_prompt":
            text = cmd.payload.get("text", "")
            await self._send_message(text)
        elif cmd.type == "cancel":
            await self._cancel_session()
        else:
            log.warning("Unsupported command for opencode server: %s", cmd.type)

    async def _send_message(self, text: str) -> None:
        """Create session if needed, send message via prompt_async, SSE handles response."""
        self._suppress_events = False
        self._text_buffer.clear()
        self._flushed_up_to.clear()
        self._turn_ended_generation = -1
        loop = asyncio.get_running_loop()

        if not self._oc_session_id:
            session = await loop.run_in_executor(
                None,
                lambda: self._post("/session", {}),
            )
            if not session or "id" not in session:
                log.error("Failed to create opencode session: %s", session)
                return
            self._oc_session_id = session["id"]
            log.info(
                "OpenCode session created: %s (%s)",
                self._oc_session_id,
                session.get("slug", ""),
            )

            if not self._spawned and self.on_event:
                self._spawned = True
                self.on_event(
                    Event.session_spawned(
                        bridge=self.bridge,
                        session_id=self.session_id,
                        runtime="opencode",
                        origin=self.origin,
                        attach_url=self.base_url,
                    )
                )

        body = {"parts": [{"type": "text", "text": text}]}
        status = await loop.run_in_executor(
            None,
            lambda: self._post_async(
                f"/session/{self._oc_session_id}/prompt_async", body
            ),
        )

        if status == 204:
            log.info("Prompt sent asynchronously to session %s", self._oc_session_id)
            self._start_turn_timer()
        elif status is not None:
            log.warning(
                "prompt_async returned %d, falling back to synchronous send", status
            )
            await self._send_message_sync(text)
        else:
            log.error("Failed to send prompt_async, falling back to synchronous")
            await self._send_message_sync(text)

    async def _send_message_sync(self, text: str) -> None:
        """Fallback: synchronous message send (blocks until response)."""
        if not self._oc_session_id:
            return

        loop = asyncio.get_running_loop()
        body = {"parts": [{"type": "text", "text": text}]}
        response = await loop.run_in_executor(
            None,
            lambda: self._post(f"/session/{self._oc_session_id}/message", body),
        )

        if not response:
            log.error("No response from opencode server (sync fallback)")
            return

        self._emit_parts_from_response(response)

        if self.on_event:
            self.on_event(
                Event.turn_ended(
                    bridge=self.bridge,
                    session_id=self.session_id,
                    origin=self.origin,
                )
            )

    def _emit_parts_from_response(self, response: dict[str, Any]) -> None:
        """Extract and emit events from a synchronous response dict."""
        parts = response.get("parts", [])
        for part in parts:
            part_type = part.get("type")

            if part_type == "text" and part.get("text"):
                if self.on_event:
                    self.on_event(
                        Event.text_output(
                            bridge=self.bridge,
                            session_id=self.session_id,
                            content=part["text"],
                        ),
                    )
            elif part_type == "thinking":
                thinking_text = part.get("thinking", "") or part.get("text", "")
                if thinking_text and self.on_event:
                    self.on_event(
                        Event.thinking_output(
                            bridge=self.bridge,
                            session_id=self.session_id,
                            content=thinking_text,
                        ),
                    )
            elif part_type == "tool_call":
                if self.on_event:
                    self.on_event(
                        Event.tool_call(
                            bridge=self.bridge,
                            session_id=self.session_id,
                            tool_name=part.get("name", ""),
                            input=part.get("input", {}),
                            call_id=part.get("id", ""),
                        ),
                    )
            elif part_type == "tool_result":
                if self.on_event:
                    self.on_event(
                        Event.tool_result(
                            bridge=self.bridge,
                            session_id=self.session_id,
                            call_id=part.get("id", ""),
                            output=part.get("output", ""),
                            success=part.get("success", True),
                        ),
                    )
            elif part_type == "error":
                error = part.get("error", {})
                msg = (
                    error.get("message", str(error))
                    if isinstance(error, dict)
                    else str(error)
                )
                if self.on_event:
                    self.on_event(
                        Event.text_output(
                            bridge=self.bridge,
                            session_id=self.session_id,
                            content=f"Error: {msg}",
                        ),
                    )

    # --- SSE event handlers ---

    def _on_sse_event(self, event: dict) -> None:
        """Handle an SSE event from the opencode server.

        Stale events from a previous turn (after an abort) are silently
        dropped via _suppress_events. The flag is cleared when a new
        prompt is sent via _send_message.
        """
        event_type = event.get("type", "")
        data = event.get("data", {})
        props = data.get("properties", data)

        if self._suppress_events and event_type not in (
            "server.connected",
            "session.created",
        ):
            log.debug("Suppressing stale SSE event after abort: %s", event_type)
            if event_type == "session.idle":
                self._suppress_events = False
                self._suppress_idle = False
                self._cancel_turn_timer()
                self._text_buffer.clear()
                self._flushed_up_to.clear()
            return

        if event_type in (
            "message.part.delta",
            "message.part.updated",
            "session.idle",
            "session.status",
        ):
            log.info(
                "SSE: %s part=%s field=%s delta=%d chars sid=%s",
                event_type,
                props.get("partID", props.get("part", {}).get("id", "")),
                props.get("field", props.get("part", {}).get("type", "")),
                len(props.get("delta", "")),
                props.get("sessionID", ""),
            )

        if event_type == "message.part.delta":
            self._handle_text_delta(props)
        elif event_type == "message.part.updated":
            self._handle_part_updated(props)
        elif event_type == "session.idle":
            self._handle_session_idle(props)
        elif event_type == "session.status":
            self._handle_session_status(props)
        elif event_type == "session.created":
            log.info("SSE: session created: %s", props.get("sessionID"))
        elif event_type == "message.updated":
            info = props.get("info", {})
            msg_id = info.get("id", "")
            msg_role = info.get("role", "")
            if msg_role == "user" and msg_id:
                self._user_message_ids.add(msg_id)
                log.debug("SSE: tracked user message: %s", msg_id)
            else:
                log.debug("SSE: message updated: %s (role=%s)", msg_id, msg_role)
        elif event_type == "permission.asked":
            self._handle_permission_asked(props)
        elif event_type == "session.error":
            log.error("SSE: session error: %s", props)
        elif event_type == "server.connected":
            log.info("SSE: connected to opencode server")
        else:
            log.debug("SSE: unhandled event type: %s", event_type)

    def _is_user_message(self, props: dict) -> bool:
        """Check if an SSE event belongs to a user message (should be suppressed).

        Checks both the top-level messageID (present in message.part.delta events)
        and the nested part.messageID (present in message.part.updated events).
        """
        message_id = props.get("messageID", "")
        if not message_id:
            part = props.get("part", {})
            if isinstance(part, dict):
                message_id = part.get("messageID", "")
        if message_id and message_id in self._user_message_ids:
            return True
        return False

    def _handle_text_delta(self, props: dict) -> None:
        """Accumulate text deltas and emit text_output or thinking_output events.

        Suppresses text from user messages to avoid echoing the operator's
        own input back to the chat.
        """
        session_id = props.get("sessionID", "")
        if self._oc_session_id and session_id != self._oc_session_id:
            return

        if self._is_user_message(props):
            return

        part_id = props.get("partID", "")
        delta = props.get("delta", "")
        if not delta:
            return

        field = props.get("field", "text")
        if part_id not in self._part_types:
            self._part_types[part_id] = field

        if part_id not in self._text_buffer:
            self._text_buffer[part_id] = []
        self._text_buffer[part_id].append(delta)

        flushed = self._flushed_up_to.get(part_id, 0)
        full_text = "".join(self._text_buffer[part_id])
        new_text = full_text[flushed:]
        self._flushed_up_to[part_id] = len(full_text)

        if new_text and self.on_event:
            is_thinking = self._part_types.get(part_id) in ("thinking", "reasoning")
            event_factory = Event.thinking_output if is_thinking else Event.text_output
            self.on_event(
                event_factory(
                    bridge=self.bridge,
                    session_id=self.session_id,
                    content=new_text,
                )
            )

    def _handle_part_updated(self, props: dict) -> None:
        """Handle full part updates (text, tool calls, tool results).

        Suppresses parts from user messages to avoid echoing the operator's
        own input back to the chat.
        """
        session_id = props.get("sessionID", "")
        if self._oc_session_id and session_id != self._oc_session_id:
            return

        if self._is_user_message(props):
            return

        part = props.get("part", props)
        part_type = part.get("type", "")

        if part_type == "text" and part.get("text"):
            flushed = self._flushed_up_to.get(part.get("id", ""), 0)
            full_text = part["text"]
            new_text = full_text[flushed:]
            self._flushed_up_to[part.get("id", "")] = len(full_text)
            if new_text and self.on_event:
                pid = part.get("id", "")
                is_thinking = self._part_types.get(pid) in ("thinking", "reasoning")
                event_factory = (
                    Event.thinking_output if is_thinking else Event.text_output
                )
                self.on_event(
                    event_factory(
                        bridge=self.bridge,
                        session_id=self.session_id,
                        content=new_text,
                    )
                )
        elif part_type in ("thinking", "reasoning"):
            pid = part.get("id", "")
            if pid:
                self._part_types[pid] = part_type
            thinking_text = part.get("thinking", "") or part.get("text", "")
            if thinking_text:
                flushed = self._flushed_up_to.get(part.get("id", ""), 0)
                new_text = thinking_text[flushed:]
                self._flushed_up_to[part.get("id", "")] = len(thinking_text)
                if new_text and self.on_event:
                    self.on_event(
                        Event.thinking_output(
                            bridge=self.bridge,
                            session_id=self.session_id,
                            content=new_text,
                        )
                    )
        elif part_type in ("tool_call", "tool") and part.get("name"):
            if self.on_event:
                self.on_event(
                    Event.tool_call(
                        bridge=self.bridge,
                        session_id=self.session_id,
                        tool_name=part.get("name", ""),
                        input=part.get("input", {}),
                        call_id=part.get("id", ""),
                    )
                )
        elif part_type == "tool_result" or (
            part_type == "tool" and part.get("output") is not None
        ):
            if self.on_event:
                self.on_event(
                    Event.tool_result(
                        bridge=self.bridge,
                        session_id=self.session_id,
                        call_id=part.get("id", ""),
                        output=part.get("output", ""),
                        success=part.get("success", True),
                    )
                )

        part_id = part.get("id", "")
        if part_id in self._text_buffer:
            del self._text_buffer[part_id]
            self._flushed_up_to.pop(part_id, None)
            self._part_types.pop(part_id, None)

    def _handle_session_idle(self, props: dict) -> None:
        """Handle session.idle — emit turn_ended unless suppressed after cancel."""
        session_id = props.get("sessionID", "")
        if self._oc_session_id and session_id != self._oc_session_id:
            return

        if self._suppress_idle:
            log.info(
                "Suppressing stale session.idle after abort for session %s", session_id
            )
            self._suppress_idle = False
            self._cancel_turn_timer()
            self._text_buffer.clear()
            self._flushed_up_to.clear()
            self._part_types.clear()
            self._user_message_ids.clear()
            return

        if self._turn_ended_generation >= self._turn_generation:
            log.debug(
                "Skipping duplicate session.idle for generation %d",
                self._turn_generation,
            )
            self._cancel_turn_timer()
            return

        log.info("Session %s is idle — turn complete", session_id)
        self._turn_ended_generation = self._turn_generation
        self._cancel_turn_timer()
        self._text_buffer.clear()
        self._flushed_up_to.clear()
        self._part_types.clear()
        self._user_message_ids.clear()

        if self.on_event:
            self.on_event(
                Event.turn_ended(
                    bridge=self.bridge,
                    session_id=self.session_id,
                    origin=self.origin,
                )
            )

    def _handle_session_status(self, props: dict) -> None:
        """Handle session.status — emit turn_ended when status is 'idle'."""
        session_id = props.get("sessionID", "")
        if self._oc_session_id and session_id != self._oc_session_id:
            return

        status = props.get("status", {})
        status_type = (
            status.get("type", "") if isinstance(status, dict) else str(status)
        )

        if status_type == "idle":
            if self._turn_ended_generation >= self._turn_generation:
                log.debug(
                    "Skipping duplicate session.status idle for generation %d",
                    self._turn_generation,
                )
                self._cancel_turn_timer()
                return

            log.info("Session %s status=idle — turn complete", session_id)
            self._turn_ended_generation = self._turn_generation
            self._cancel_turn_timer()
            self._text_buffer.clear()
            self._flushed_up_to.clear()
            self._part_types.clear()
            self._user_message_ids.clear()

            if self.on_event:
                self.on_event(
                    Event.turn_ended(
                        bridge=self.bridge,
                        session_id=self.session_id,
                        origin=self.origin,
                    )
                )

    def _start_turn_timer(self) -> None:
        """Start a safety timer that emits turn_ended if SSE doesn't deliver it."""
        self._cancel_turn_timer()
        self._turn_timer_task = asyncio.create_task(self._turn_timeout_expired())

    def _cancel_turn_timer(self) -> None:
        """Cancel the running turn safety timer."""
        if self._turn_timer_task and not self._turn_timer_task.done():
            self._turn_timer_task.cancel()
        self._turn_timer_task = None

    async def _turn_timeout_expired(self) -> None:
        """Emit turn_ended after the safety timeout if SSE never delivered session.idle."""
        try:
            await asyncio.sleep(self._turn_timeout)
            log.warning(
                "Turn timeout (%.0fs) expired for session %s — emitting turn_ended",
                self._turn_timeout,
                self._oc_session_id,
            )
            self._text_buffer.clear()
            self._flushed_up_to.clear()
            self._part_types.clear()
            self._user_message_ids.clear()
            if self.on_event:
                self.on_event(
                    Event.turn_ended(
                        bridge=self.bridge,
                        session_id=self.session_id,
                        origin=self.origin,
                    )
                )
        except asyncio.CancelledError:
            pass

    def _handle_permission_asked(self, props: dict) -> None:
        """Handle permission.asked — emit approval_needed."""
        session_id = props.get("sessionID", "")
        if self._oc_session_id and session_id != self._oc_session_id:
            return

        perm = props.get("permission", props)
        call_id = perm.get("id", "")
        tool_name = perm.get("tool", "")
        description = perm.get("description", "")

        if self.on_event:
            self.on_event(
                Event.approval_needed(
                    bridge=self.bridge,
                    session_id=self.session_id,
                    tool_name=tool_name,
                    description=description,
                    call_id=call_id,
                )
            )

    async def _cancel_session(self) -> None:
        """Abort the current running turn in the session.

        Sends POST /session/{id}/abort to the opencode server, then emits
        turn_ended and clears text buffers so the bridge can send a new
        prompt on the same session.
        """
        if not self._oc_session_id:
            return
        self._turn_generation += 1
        log.info(
            "Aborting session %s (generation %d)",
            self._oc_session_id,
            self._turn_generation,
        )
        loop = asyncio.get_running_loop()
        status = await loop.run_in_executor(
            None,
            lambda: self._post_async(f"/session/{self._oc_session_id}/abort", {}),
        )
        log.info(
            "Abort request sent to session %s (status: %s)", self._oc_session_id, status
        )
        self._cancel_turn_timer()
        self._text_buffer.clear()
        self._flushed_up_to.clear()
        self._part_types.clear()
        self._user_message_ids.clear()
        if self.on_event:
            self.on_event(
                Event.turn_ended(
                    bridge=self.bridge,
                    session_id=self.session_id,
                    origin=self.origin,
                )
            )

    async def stop(self) -> None:
        """Stop the SSE listener and clean up."""
        self._cancel_turn_timer()
        if self._sse_client:
            self._sse_client.stop()
        if self._sse_task and not self._sse_task.done():
            self._sse_task.cancel()
            try:
                await self._sse_task
            except asyncio.CancelledError:
                pass
        log.info("OpenCode adapter stopped")

    # --- HTTP helpers ---

    def _get(self, path: str) -> dict[str, Any] | None:
        """Synchronous GET request."""
        try:
            req = Request(f"{self.base_url}{path}")
            with urlopen(req, timeout=10) as resp:
                return json.loads(resp.read())
        except (URLError, json.JSONDecodeError, OSError) as exc:
            log.debug("GET %s failed: %s", path, exc)
            return None

    def _post(self, path: str, data: dict[str, Any]) -> dict[str, Any] | None:
        """Synchronous POST request, returns parsed JSON response."""
        try:
            body = json.dumps(data).encode()
            req = Request(
                f"{self.base_url}{path}",
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(req, timeout=120) as resp:
                return json.loads(resp.read())
        except (URLError, json.JSONDecodeError, OSError) as exc:
            log.debug("POST %s failed: %s", path, exc)
            return None

    def _post_async(self, path: str, data: dict[str, Any]) -> int | None:
        """Synchronous POST for async endpoints (prompt_async, abort).

        Returns the HTTP status code, or None on connection error.
        """
        try:
            body = json.dumps(data).encode()
            req = Request(
                f"{self.base_url}{path}",
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(req, timeout=10) as resp:
                return resp.status
        except HTTPError as exc:
            return exc.code
        except (URLError, OSError) as exc:
            log.debug("POST async %s failed: %s", path, exc)
            return None


# ---------------------------------------------------------------------------
# Subprocess entry point (ADR-038)
# ---------------------------------------------------------------------------


async def _amain() -> None:
    from swain_helm.adapters import run_adapter

    def factory(config_msg: ConfigMessage, emit: Callable[[Event], None]) -> Any:
        cfg = config_msg.config
        return OpenCodeServerAdapter(
            bridge=cfg.get("bridge", "swain"),
            session_id=cfg.get("session_id", "sess-opencode"),
            base_url=cfg.get("base_url", "http://127.0.0.1:4098"),
            origin=cfg.get("origin"),
            on_event=emit,
        )

    async def setup(adapter: Any, config_msg: ConfigMessage) -> None:
        if not await adapter.wait_for_health(
            timeout=config_msg.config.get("health_timeout", 30.0)
        ):
            log.error("OpenCode server not healthy at %s", adapter.base_url)
            sys.exit(1)
        await adapter.setup()

    await run_adapter(factory, setup=setup)


def main() -> None:
    asyncio.run(_amain())


if __name__ == "__main__":
    main()
