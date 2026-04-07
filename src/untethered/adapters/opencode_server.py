"""OpenCode Server runtime adapter (SPEC-292).

Manages an `opencode serve` process and communicates via HTTP API.
Sessions persist across messages. The operator can attach via
`opencode attach http://127.0.0.1:<port>`.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Callable
from urllib.request import urlopen, Request
from urllib.error import URLError

from untethered.protocol import Event, Command

log = logging.getLogger(__name__)


class OpenCodeServerAdapter:
    """HTTP client adapter for opencode serve.

    - Creates sessions via POST /session.
    - Sends messages via POST /session/{id}/message.
    - Emits text_output events from response parts.
    - Reuses sessions across messages.
    """

    def __init__(
        self,
        bridge: str,
        session_id: str,
        *,
        base_url: str = "http://127.0.0.1:4097",
        on_event: Callable[[Event], None] | None = None,
    ):
        self.bridge = bridge
        self.session_id = session_id
        self.base_url = base_url.rstrip("/")
        self.on_event = on_event
        self._oc_session_id: str | None = None
        self._spawned = False

    async def wait_for_health(self, timeout: float = 30.0) -> bool:
        """Poll /global/health until the server is ready."""
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout
        while loop.time() < deadline:
            try:
                data = await loop.run_in_executor(
                    None, lambda: self._get("/global/health"),
                )
                if data and data.get("healthy"):
                    return True
            except Exception:
                pass
            await asyncio.sleep(0.5)
        return False

    async def send_command(self, cmd: Command) -> None:
        """Handle a protocol Command by sending it to the opencode server."""
        if cmd.type == "send_prompt":
            text = cmd.payload.get("text", "")
            await self._send_message(text)
        elif cmd.type == "cancel":
            log.info("Cancel not yet implemented for opencode server adapter")
        else:
            log.warning("Unsupported command for opencode server: %s", cmd.type)

    async def stop(self) -> None:
        """Clean up. Does not stop the server — it may be shared."""
        pass

    async def _send_message(self, text: str) -> None:
        """Create session if needed, send message, emit response events."""
        loop = asyncio.get_running_loop()

        # Create session on first message.
        if not self._oc_session_id:
            session = await loop.run_in_executor(
                None, lambda: self._post("/session", {}),
            )
            if not session or "id" not in session:
                log.error("Failed to create opencode session: %s", session)
                return
            self._oc_session_id = session["id"]
            log.info("OpenCode session created: %s (%s)",
                     self._oc_session_id, session.get("slug", ""))

            # Emit session_spawned on first use.
            if not self._spawned and self.on_event:
                self._spawned = True
                self.on_event(Event.session_spawned(
                    bridge=self.bridge,
                    session_id=self.session_id,
                    runtime="opencode",
                ))

        # Send the message.
        body = {"parts": [{"type": "text", "text": text}]}
        response = await loop.run_in_executor(
            None,
            lambda: self._post(f"/session/{self._oc_session_id}/message", body),
        )

        if not response:
            log.error("No response from opencode server")
            return

        # Extract text from response parts.
        parts = response.get("parts", [])
        for part in parts:
            if part.get("type") == "text" and part.get("text"):
                if self.on_event:
                    self.on_event(Event.text_output(
                        bridge=self.bridge,
                        session_id=self.session_id,
                        content=part["text"],
                    ))

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
        """Synchronous POST request."""
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
