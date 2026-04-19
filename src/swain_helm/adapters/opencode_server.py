"""OpenCode Server runtime adapter (SPEC-292).

Manages an `opencode serve` process and communicates via HTTP API.
Sessions persist across messages. The operator can attach via
`opencode attach http://127.0.0.1:<port>`.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import socket
import subprocess
from typing import Any, Callable
from urllib.request import urlopen, Request
from urllib.error import URLError


from swain_helm.protocol import Event, Command

log = logging.getLogger(__name__)


class OpenCodeServerAdapter:
    """HTTP client adapter for opencode serve.

    - Spawns a dedicated `opencode serve` process per session in a worktree.
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
        self._server_proc: asyncio.subprocess.Process | None = None
        self._server_log: str | None = None

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

    async def send_command(self, cmd: Command) -> None:
        """Handle a protocol Command by sending it to the opencode server."""
        if cmd.type == "send_prompt":
            text = cmd.payload.get("text", "")
            await self._send_message(text)
        elif cmd.type == "cancel":
            log.info("Cancel not yet implemented for opencode server adapter")
        else:
            log.warning("Unsupported command for opencode server: %s", cmd.type)

    def _find_available_port(self) -> int:
        """Find an available port by binding to 0."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            return s.getsockname()[1]

    async def spawn_server(self, worktree_path: str) -> bool:
        """Spawn a dedicated opencode serve process in the specified worktree."""
        port = self._find_available_port()
        self.base_url = f"http://127.0.0.1:{port}"

        log_file = os.path.join(worktree_path, ".opencode-serve.log")
        self._server_log = log_file

        # Spawn server: port, print logs for stderr capture, and stdout to file
        cmd = ["opencode", "serve", "--port", str(port), "--print-logs"]

        log.info("Spawning opencode server in %s on port %s", worktree_path, port)

        self._server_proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=worktree_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        # Fork stdout to both the log file and potentially the bridge stderr
        # Since we use PIPE for stdout, we need a reader to write to the file
        async def _pipe_stdout():
            if self._server_proc and self._server_proc.stdout:
                with open(log_file, "w") as f:
                    while True:
                        line = await self._server_proc.stdout.readline()
                        if not line:
                            break
                        f.write(line.decode())
                        f.flush()

        asyncio.create_task(_pipe_stdout())

        # Wait for health (with extended timeout for cold start)
        healthy = await self.wait_for_health(timeout=60.0)
        if not healthy:
            log.error("Spawned opencode server failed health check on port %s", port)
            await self.stop()
            return False

        log.info("OpenCode server healthy on port %s", port)

        if self.on_event:
            self.on_event(
                Event.text_output(
                    bridge=self.bridge,
                    session_id=self.session_id,
                    content=f"Operator can attach: `opencode attach {self.base_url}`",
                )
            )

        return True

    async def stop(self) -> None:
        """Clean up and stop the spawned server."""
        if self._server_proc:
            try:
                self._server_proc.terminate()
                await asyncio.wait_for(self._server_proc.wait(), timeout=5.0)
            except (asyncio.TimeoutError, ProcessLookupError):
                self._server_proc.kill()
            self._server_proc = None
        log.info("OpenCode server stopped for session %s", self.session_id)

    async def _send_message(self, text: str) -> None:
        """Create session if needed, send message, emit response events."""
        loop = asyncio.get_running_loop()

        # Create session on first message.
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

            # Emit session_spawned on first use.
            if not self._spawned and self.on_event:
                self._spawned = True
                self.on_event(
                    Event.session_spawned(
                        bridge=self.bridge,
                        session_id=self.session_id,
                        runtime="opencode",
                    )
                )

        # Send the message.
        body = {"parts": [{"type": "text", "text": text}]}
        response = await loop.run_in_executor(
            None,
            lambda: self._post(f"/session/{self._oc_session_id}/message", body),
        )

        if not response:
            log.error("No response from opencode server")
            return

        log.debug("OpenCode response: %s", json.dumps(response))

        # Extract events from response parts.
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
                        )
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
                        )
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
                        )
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
                        )
                    )

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
