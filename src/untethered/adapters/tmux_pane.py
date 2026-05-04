"""Tmux pane runtime adapter.

Runs the runtime in a tmux session. Streams output via pipe-pane to a log
file, tailed by an async reader. Sends input via tmux send-keys. The
operator can attach locally at any time.

This is the "untethered" model: the runtime is independent of the bridge
process. If the bridge crashes, the runtime keeps running.
"""
from __future__ import annotations

import asyncio
import logging
import os
import re
import subprocess
import tempfile
from typing import Any, Callable

from untethered.protocol import Event, Command

log = logging.getLogger(__name__)

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]|\x1b\].*?\x07|\x1b\[.*?\x1b\\")


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from terminal output."""
    return _ANSI_RE.sub("", text)


class TmuxPaneAdapter:
    """Manages a runtime running in a tmux pane.

    - start(): creates tmux session, runs runtime, sets up pipe-pane
    - send_command(): translates to tmux send-keys
    - stop(): sends Ctrl-C, then kills the session
    - Output streams via pipe-pane → FIFO → asyncio reader
    """

    def __init__(
        self,
        bridge: str,
        session_id: str,
        *,
        project_dir: str | None = None,
        on_event: Callable[[Event], None] | None = None,
    ):
        self.bridge = bridge
        self.session_id = session_id
        self.project_dir = project_dir
        self.on_event = on_event
        self._session_name: str | None = None
        self._fifo_path: str | None = None
        self._reader_task: asyncio.Task | None = None
        self._monitor_task: asyncio.Task | None = None

    async def start(
        self,
        runtime_cmd: list[str] | None = None,
        session_name: str | None = None,
    ) -> None:
        """Create a tmux session, run the runtime, set up pipe-pane."""
        self._session_name = session_name or f"swain-{self.session_id}"
        cmd = runtime_cmd or ["opencode"]

        # Create output file for pipe-pane
        fifo_dir = tempfile.mkdtemp(prefix="untethered-")
        self._fifo_path = os.path.join(fifo_dir, "output.log")
        # Touch the file so tail -f can start immediately
        open(self._fifo_path, "w").close()

        # Create tmux session with the runtime command
        import shlex
        shell_cmd = " ".join(shlex.quote(c) for c in cmd)
        cwd = self.project_dir or os.getcwd()

        result = subprocess.run(
            [
                "tmux", "new-session",
                "-d",  # detached
                "-s", self._session_name,
                "-c", cwd,
                shell_cmd,
            ],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            log.error("Failed to create tmux session %s: %s",
                      self._session_name, result.stderr)
            return

        log.info("Tmux session created: %s (cmd: %s)", self._session_name, shell_cmd)

        # Set up pipe-pane to append output to the log file.
        subprocess.run(
            ["tmux", "pipe-pane", "-t", self._session_name, "-O",
             f"cat >> {self._fifo_path}"],
            capture_output=True,
        )

        # Tail the log file for real-time output streaming.
        self._reader_task = asyncio.create_task(self._tail_output())

        # Monitor for pane exit
        self._monitor_task = asyncio.create_task(self._monitor_pane())

        # Emit session_spawned
        if self.on_event:
            self.on_event(Event.session_spawned(
                bridge=self.bridge, session_id=self.session_id,
                runtime="opencode",
            ))

    async def _tail_output(self) -> None:
        """Tail the pipe-pane output file and emit text_output events."""
        if not self._fifo_path:
            return

        # Use tail -f to stream new lines as they're appended by pipe-pane.
        proc = await asyncio.create_subprocess_exec(
            "tail", "-f", self._fifo_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        self._tail_proc = proc

        try:
            while proc.stdout:
                line = await proc.stdout.readline()
                if not line:
                    break
                raw = line.decode("utf-8", errors="replace").rstrip("\r\n")
                text = strip_ansi(raw)
                if text and self.on_event:
                    self.on_event(Event.text_output(
                        bridge=self.bridge,
                        session_id=self.session_id,
                        content=text,
                    ))
        except asyncio.CancelledError:
            pass
        finally:
            proc.terminate()
            try:
                await asyncio.wait_for(proc.wait(), timeout=2.0)
            except asyncio.TimeoutError:
                proc.kill()

    async def _monitor_pane(self) -> None:
        """Poll for pane exit and emit session_died."""
        while True:
            await asyncio.sleep(1.0)
            if not self._pane_alive():
                log.info("Tmux pane %s exited", self._session_name)
                if self.on_event:
                    self.on_event(Event.session_died(
                        bridge=self.bridge,
                        session_id=self.session_id,
                        reason="pane exited",
                    ))
                break

    def _pane_alive(self) -> bool:
        """Check if the tmux session/pane still exists."""
        if not self._session_name:
            return False
        result = subprocess.run(
            ["tmux", "has-session", "-t", self._session_name],
            capture_output=True,
        )
        return result.returncode == 0

    async def send_command(self, cmd: Command) -> None:
        """Translate a protocol Command to tmux send-keys."""
        if not self._session_name:
            log.warning("Cannot send command — no tmux session")
            return

        if cmd.type == "send_prompt":
            text = cmd.payload.get("text", "")
            subprocess.run(
                ["tmux", "send-keys", "-t", self._session_name, text, "Enter"],
                capture_output=True,
            )

        elif cmd.type == "cancel":
            subprocess.run(
                ["tmux", "send-keys", "-t", self._session_name, "C-c"],
                capture_output=True,
            )

        elif cmd.type == "approve":
            # SPIKE: approval mechanism varies by runtime
            # For now, send "y" + Enter as a naive approval
            subprocess.run(
                ["tmux", "send-keys", "-t", self._session_name, "y", "Enter"],
                capture_output=True,
            )

        else:
            log.warning("Unsupported command for tmux adapter: %s", cmd.type)

    async def stop(self) -> None:
        """Stop the runtime and clean up."""
        if self._reader_task:
            self._reader_task.cancel()
            try:
                await self._reader_task
            except asyncio.CancelledError:
                pass

        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

        if self._session_name:
            # Send Ctrl-C first, give it a moment, then kill
            subprocess.run(
                ["tmux", "send-keys", "-t", self._session_name, "C-c"],
                capture_output=True,
            )
            await asyncio.sleep(0.5)
            subprocess.run(
                ["tmux", "kill-session", "-t", self._session_name],
                capture_output=True,
            )

        # Clean up FIFO
        if self._fifo_path:
            try:
                os.unlink(self._fifo_path)
                os.rmdir(os.path.dirname(self._fifo_path))
            except OSError:
                pass
