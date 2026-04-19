"""Process manager that reconciles desired state against running bridges."""

import asyncio
import json
import logging
import os
import signal
import subprocess
import sys
from pathlib import Path

log = logging.getLogger("swain_helm.watchdog")

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "swain-helm"
RECONCILIATION_INTERVAL = 30


class Watchdog:
    """Process manager that reconciles desired state against running bridges."""

    def __init__(self, config_dir: Path | None = None) -> None:
        self.config_dir = config_dir or DEFAULT_CONFIG_DIR
        self.projects_dir = self.config_dir / "projects"
        self.run_dir = self.config_dir / "run" / "bridges"
        self.watchdog_pid_path = self.config_dir / "run" / "watchdog.pid"
        self._running: dict[str, subprocess.Popen] = {}
        self._shutdown_event = asyncio.Event()

    async def run(self, *, foreground: bool = True) -> None:
        """Main loop: reconcile every 30s until shutdown."""
        self.run_dir.mkdir(parents=True, exist_ok=True)
        if foreground:
            self._write_watchdog_pid()
            loop = asyncio.get_running_loop()
            loop.add_signal_handler(signal.SIGINT, self._request_shutdown)
            loop.add_signal_handler(signal.SIGTERM, self._request_shutdown)
        try:
            while not self._shutdown_event.is_set():
                await self._reconcile()
                try:
                    await asyncio.wait_for(
                        self._shutdown_event.wait(),
                        timeout=RECONCILIATION_INTERVAL,
                    )
                except asyncio.TimeoutError:
                    pass
        finally:
            await self._shutdown()

    async def _reconcile(self) -> None:
        """Read configs, start missing bridges, stop removed ones."""
        desired = self._read_project_configs()
        running = self._get_running_bridges()
        for name in desired:
            if name not in running:
                await self._start_bridge(name, desired[name])
            elif not self._is_healthy(name):
                log.warning("Bridge %s failed health check, restarting", name)
                await self._stop_bridge(name)
                await self._start_bridge(name, desired[name])
        for name in list(running):
            if name not in desired:
                await self._stop_bridge(name)

    def _read_project_configs(self) -> dict[str, dict]:
        """Read all project configs from projects/ directory."""
        configs: dict[str, dict] = {}
        if not self.projects_dir.exists():
            return configs
        for path in self.projects_dir.glob("*.json"):
            try:
                with open(path) as f:
                    cfg = json.load(f)
                if cfg.get("auto_start", True):
                    configs[path.stem] = cfg
            except (json.JSONDecodeError, OSError) as e:
                log.error("Failed to read config %s: %s", path, e)
        return configs

    def _get_running_bridges(self) -> set[str]:
        """Check PID files to determine which bridges are running."""
        running: set[str] = set()
        if not self.run_dir.exists():
            return running
        for pid_file in self.run_dir.glob("*.pid"):
            name = pid_file.stem
            try:
                pid = int(pid_file.read_text().strip())
                os.kill(pid, 0)
                running.add(name)
            except (ProcessLookupError, ValueError, OSError):
                pid_file.unlink(missing_ok=True)
        return running

    def _is_healthy(self, name: str) -> bool:
        """Check if a bridge process is still alive."""
        pid_file = self.run_dir / f"{name}.pid"
        if not pid_file.exists():
            return False
        try:
            pid = int(pid_file.read_text().strip())
            os.kill(pid, 0)
            return True
        except (ProcessLookupError, ValueError, OSError):
            return False

    async def _start_bridge(self, name: str, config: dict) -> None:
        """Start a project bridge subprocess."""
        cmd = [sys.executable, "-m", "swain_helm.bridges.project", "--project", name]
        log.info("Starting bridge: %s", name)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            pid_file = self.run_dir / f"{name}.pid"
            pid_file.write_text(str(proc.pid))
            self._running[name] = proc
            log.info("Bridge %s started (pid %s)", name, proc.pid)
        except Exception as e:
            log.error("Failed to start bridge %s: %s", name, e)

    async def _stop_bridge(self, name: str) -> None:
        """Stop a running bridge."""
        proc = self._running.pop(name, None)
        if proc:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
            log.info("Bridge %s stopped", name)
        pid_file = self.run_dir / f"{name}.pid"
        pid_file.unlink(missing_ok=True)

    async def _shutdown(self) -> None:
        """Gracefully shut down all bridges."""
        log.info("Watchdog shutting down...")
        for name in list(self._running):
            await self._stop_bridge(name)
        if self.watchdog_pid_path.exists():
            self.watchdog_pid_path.unlink()

    def _write_watchdog_pid(self) -> None:
        """Write the watchdog PID file."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        (self.config_dir / "run").mkdir(parents=True, exist_ok=True)
        self.watchdog_pid_path.write_text(str(os.getpid()))

    def _request_shutdown(self) -> None:
        """Signal handler: request graceful shutdown."""
        log.info("Shutdown requested")
        self._shutdown_event.set()

    def stop_bridge(self, name: str) -> None:
        """Stop a specific bridge (called from CLI)."""
        pid_file = self.run_dir / f"{name}.pid"
        if pid_file.exists():
            try:
                pid = int(pid_file.read_text().strip())
                os.kill(pid, signal.SIGTERM)
                pid_file.unlink()
                log.info("Bridge %s stopped by CLI", name)
            except (ProcessLookupError, ValueError, OSError) as e:
                log.warning("Failed to stop bridge %s: %s", name, e)
                pid_file.unlink(missing_ok=True)


def daemonize(config_dir: Path | None = None) -> None:
    """Fork to background and write watchdog.pid."""
    pid = os.fork()
    if pid > 0:
        os._exit(0)
    os.setsid()
    pid2 = os.fork()
    if pid2 > 0:
        os._exit(0)
    wd_config_dir = config_dir or DEFAULT_CONFIG_DIR
    pid_path = wd_config_dir / "run" / "watchdog.pid"
    pid_path.parent.mkdir(parents=True, exist_ok=True)
    pid_path.write_text(str(os.getpid()))
    log_path = "/tmp/swain-helm.log"
    sys.stdout.flush()
    sys.stderr.flush()
    log_file = open(log_path, "a")
    os.dup2(log_file.fileno(), sys.stdout.fileno())
    os.dup2(log_file.fileno(), sys.stderr.fileno())
    watchdog = Watchdog(config_dir=wd_config_dir)
    asyncio.run(watchdog.run(foreground=False))
