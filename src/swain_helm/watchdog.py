"""Process manager that reconciles desired state against running bridges.

Resolves 1Password op:// references exactly once at startup, then passes
fully-resolved config to bridge subprocesses via NDJSON ConfigMessage on
stdin. Bridges never invoke `op` themselves.
"""

import asyncio
import json
import logging
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from swain_helm.config import load_helm_config, load_project_config
from swain_helm.zombie_cleanup import (
    cleanup_stale_processes,
    cleanup_orphan_subprocesses,
)

log = logging.getLogger("swain_helm.watchdog")

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "swain-helm"
RECONCILIATION_INTERVAL = 30


class Watchdog:
    """Process manager that reconciles desired state against running bridges.

    Owns a single opencode serve process shared by all bridges.
    Bridges create sessions on this server via HTTP; they never
    spawn their own.
    """

    DEFAULT_OPENCODE_PORT = 4098

    def __init__(self, config_dir: Path | None = None) -> None:
        self.config_dir = config_dir or DEFAULT_CONFIG_DIR
        self.projects_dir = self.config_dir / "projects"
        self.run_dir = self.config_dir / "run" / "bridges"
        self.watchdog_pid_path = self.config_dir / "run" / "watchdog.pid"
        self._running: dict[str, subprocess.Popen] = {}
        self._bridge_configs: dict[str, dict] = {}
        self._opencode_proc: subprocess.Popen | None = None
        self._opencode_port: int = self.DEFAULT_OPENCODE_PORT
        self._helm_config: dict | None = None
        self._shutdown_event = asyncio.Event()

    def load_helm_config(self) -> dict:
        """Resolve 1Password refs once at startup and cache the result."""
        if self._helm_config is None:
            config_path = self.config_dir / "helm.config.json"
            if config_path.exists():
                self._helm_config = load_helm_config(str(config_path))
                log.info("Loaded and resolved helm config from %s", config_path)
            else:
                self._helm_config = {}
                log.warning("No helm.config.json found at %s", config_path)
        return self._helm_config

    @property
    def opencode_base_url(self) -> str:
        return f"http://127.0.0.1:{self._opencode_port}"

    def _start_opencode_server(self) -> bool:
        """Start a single opencode serve process owned by the watchdog.

        Uses the first project's directory as cwd so sessions land there.
        """
        helm = self.load_helm_config()
        oc_cfg = helm.get("opencode", {})
        self._opencode_port = oc_cfg.get("default_port", self.DEFAULT_OPENCODE_PORT)

        if self._opencode_proc and self._opencode_proc.poll() is None:
            log.info("OpenCode server already running on port %s", self._opencode_port)
            return True

        project_dir = self._first_project_dir()
        log_path = self.run_dir / "opencode-serve.log"
        self.run_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            "opencode",
            "serve",
            "--port",
            str(self._opencode_port),
            "--hostname",
            "0.0.0.0",
            "--print-logs",
        ]
        log.info("Starting opencode server on port %s", self._opencode_port)

        try:
            log_fd = os.open(
                str(log_path), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600
            )
            self._opencode_proc = subprocess.Popen(
                cmd,
                stdin=subprocess.DEVNULL,
                stdout=log_fd,
                stderr=log_fd,
                cwd=project_dir,
            )
            os.close(log_fd)
        except FileNotFoundError:
            log.error("opencode binary not found — server not started")
            self._opencode_proc = None
            return False

        # Wait for health check
        import json as _json
        from urllib.request import urlopen, Request
        from urllib.error import URLError

        for _ in range(60):
            try:
                req = Request(f"{self.opencode_base_url}/global/health")
                with urlopen(req, timeout=2) as resp:
                    data = _json.loads(resp.read())
                    if data.get("healthy"):
                        log.info(
                            "OpenCode server healthy on port %s", self._opencode_port
                        )
                        return True
            except (URLError, OSError, _json.JSONDecodeError):
                pass
            time.sleep(1)

        log.error("OpenCode server failed health check on port %s", self._opencode_port)
        return False

    def _stop_opencode_server(self) -> None:
        if self._opencode_proc and self._opencode_proc.poll() is None:
            self._opencode_proc.terminate()
            try:
                self._opencode_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._opencode_proc.kill()
            log.info("OpenCode server stopped")

    def _first_project_dir(self) -> str | None:
        """Return the path from the first project config, or None."""
        if not self.projects_dir.exists():
            return None
        for path in self.projects_dir.glob("*.json"):
            try:
                cfg = load_project_config(str(path))
                p = cfg.get("path")
                if p and os.path.isdir(p):
                    return p
            except Exception:
                continue
        return None

    async def run(self, *, foreground: bool = True) -> None:
        """Main loop: start opencode server, then reconcile bridges.

        Per ADR-049, runs startup zombie cleanup first to kill any orphan
        processes from a previous watchdog or bridge instance.
        """
        self.run_dir.mkdir(parents=True, exist_ok=True)

        stale_killed = cleanup_stale_processes(self.run_dir)
        orphan_killed = cleanup_orphan_subprocesses()
        if stale_killed or orphan_killed:
            log.warning(
                "Startup cleanup: killed %d stale and %d orphan processes",
                stale_killed,
                orphan_killed,
            )

        if foreground:
            self._write_watchdog_pid()
            loop = asyncio.get_running_loop()
            loop.add_signal_handler(signal.SIGINT, self._request_shutdown)
            loop.add_signal_handler(signal.SIGTERM, self._request_shutdown)
        self._start_opencode_server()
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
        """Read and resolve all project configs from projects/ directory.

        Merges the resolved helm config (chat credentials, opencode settings)
        into each project config so bridges receive fully-resolved config via
        stdin — no op:// references ever leave this process.
        """
        configs: dict[str, dict] = {}
        if not self.projects_dir.exists():
            return configs
        helm = self.load_helm_config()
        for path in self.projects_dir.glob("*.json"):
            try:
                project_cfg = load_project_config(str(path))
                if not project_cfg.get("auto_start", True):
                    continue
                resolved = {**project_cfg}
                resolved["chat"] = helm.get("chat", {})
                resolved["opencode"] = {
                    **helm.get("opencode", {}),
                    "base_url": self.opencode_base_url,
                }
                configs[path.stem] = resolved
            except Exception as e:
                log.error("Failed to read/resolve config %s: %s", path, e)
        return configs

    def _get_running_bridges(self) -> set[str]:
        """Check PID files and process metadata to determine which bridges are running.

        Validates that the process at the PID is actually a swain-helm bridge
        to guard against PID reuse after system restart.
        """
        running: set[str] = set()
        if not self.run_dir.exists():
            return running
        for pid_file in self.run_dir.glob("*.pid"):
            name = pid_file.stem
            entry = _read_pid_file(pid_file)
            if entry is None:
                pid_file.unlink(missing_ok=True)
                continue
            pid, _recorded_ts = entry
            try:
                os.kill(pid, 0)
                actual_ts = _process_start_time(pid)
                if (
                    actual_ts is not None
                    and _recorded_ts > 0
                    and abs(actual_ts - _recorded_ts) > 1.0
                ):
                    log.warning(
                        "PID %s reused (expected start=%.1f, actual=%.1f), removing stale entry for %s",
                        pid,
                        _recorded_ts,
                        actual_ts,
                        name,
                    )
                    pid_file.unlink(missing_ok=True)
                    continue
                running.add(name)
            except (ProcessLookupError, ValueError, OSError):
                pid_file.unlink(missing_ok=True)
        return running

    def _is_healthy(self, name: str) -> bool:
        """Check if a bridge process is still alive and verify PID reuse protection."""
        pid_file = self.run_dir / f"{name}.pid"
        if not pid_file.exists():
            return False
        entry = _read_pid_file(pid_file)
        if entry is None:
            return False
        pid, _recorded_ts = entry
        try:
            os.kill(pid, 0)
            actual_ts = _process_start_time(pid)
            if (
                actual_ts is not None
                and _recorded_ts > 0
                and abs(actual_ts - _recorded_ts) > 1.0
            ):
                log.warning("PID %s reused for bridge %s, marking unhealthy", pid, name)
                return False
            return True
        except (ProcessLookupError, ValueError, OSError):
            return False

    async def _start_bridge(self, name: str, config: dict) -> None:
        """Start a project bridge subprocess, passing resolved config on stdin."""
        cmd = [sys.executable, "-m", "swain_helm.bridges.project", "--project", name]
        log.info("Starting bridge: %s", name)
        self.run_dir.mkdir(parents=True, exist_ok=True)

        from swain_helm.protocol import encode_message, ConfigMessage

        cfg_msg = ConfigMessage(plugin_type="bridge", config=config)
        cfg_bytes = encode_message(cfg_msg).encode() + b"\n"

        log_path = self.run_dir / f"{name}.log"
        log_fd = os.open(str(log_path), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)

        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=log_fd,
                stderr=log_fd,
                preexec_fn=os.setpgrp,
            )
            os.close(log_fd)
            assert proc.stdin is not None
            proc.stdin.write(cfg_bytes)
            proc.stdin.flush()
            proc.stdin.close()
            pid_file = self.run_dir / f"{name}.pid"
            start_time = _process_start_time(proc.pid)
            pid_file.write_text(f"{proc.pid}\n{start_time or 0.0}\n")
            self._running[name] = proc
            log.info("Bridge %s started (pid %s)", name, proc.pid)
        except Exception as e:
            os.close(log_fd)
            log.error("Failed to start bridge %s: %s", name, e)

    async def _stop_bridge(self, name: str) -> None:
        """Stop a running bridge and its entire process group.

        Per ADR-049, uses process group kill to cascade termination to
        grandchildren (zulip_chat, etc.).
        """
        proc = self._running.pop(name, None)
        if proc:
            pgid = None
            try:
                pgid = os.getpgid(proc.pid)
            except (ProcessLookupError, OSError):
                pass
            if pgid and pgid != os.getpgid(os.getpid()):
                try:
                    os.killpg(pgid, signal.SIGTERM)
                except (ProcessLookupError, OSError):
                    try:
                        proc.terminate()
                    except ProcessLookupError:
                        pass
            else:
                try:
                    proc.terminate()
                except ProcessLookupError:
                    pass
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                if pgid and pgid != os.getpgid(os.getpid()):
                    try:
                        os.killpg(pgid, signal.SIGKILL)
                    except (ProcessLookupError, OSError):
                        pass
                else:
                    proc.kill()
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    pass
            log.info("Bridge %s stopped", name)
        pid_file = self.run_dir / f"{name}.pid"
        pid_file.unlink(missing_ok=True)

    async def _shutdown(self) -> None:
        """Gracefully shut down all bridges and the opencode server."""
        log.info("Watchdog shutting down...")
        for name in list(self._running):
            await self._stop_bridge(name)
        self._stop_opencode_server()
        if self.watchdog_pid_path.exists():
            self.watchdog_pid_path.unlink()

    def _write_watchdog_pid(self) -> None:
        """Write the watchdog PID file with creation timestamp."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        (self.config_dir / "run").mkdir(parents=True, exist_ok=True)
        pid = os.getpid()
        start_ts = _process_start_time(pid) or time.time()
        self.watchdog_pid_path.write_text(f"{pid}\n{start_ts}\n")

    def _request_shutdown(self) -> None:
        """Signal handler: request graceful shutdown."""
        log.info("Shutdown requested")
        self._shutdown_event.set()

    def stop_bridge(self, name: str) -> None:
        """Stop a specific bridge (called from CLI)."""
        pid_file = self.run_dir / f"{name}.pid"
        if pid_file.exists():
            entry = _read_pid_file(pid_file)
            if entry:
                pid, _ = entry
                try:
                    os.kill(pid, signal.SIGTERM)
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
    run_dir = wd_config_dir / "run"
    run_dir.mkdir(parents=True, exist_ok=True)
    pid_path = run_dir / "watchdog.pid"
    pid_path.write_text(str(os.getpid()))
    log_path = run_dir / "watchdog.log"
    sys.stdout.flush()
    sys.stderr.flush()
    log_fd = os.open(str(log_path), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    os.dup2(log_fd, sys.stdout.fileno())
    os.dup2(log_fd, sys.stderr.fileno())
    os.close(log_fd)
    watchdog = Watchdog(config_dir=wd_config_dir)
    asyncio.run(watchdog.run(foreground=False))


def _process_start_time(pid: int) -> float | None:
    """Get the start time of a process as seconds since epoch.

    Uses /proc on Linux, falls back to `ps` on macOS/other Unix.
    Returns None if the PID doesn't exist or the time can't be determined.
    """
    try:
        if sys.platform == "linux":
            clk_tck = os.sysconf("SC_CLK_TCK")
            with open(f"/proc/{pid}/stat") as f:
                stat = f.read()
            fields = stat.split(")")
            starttime = float(fields[-1].split()[19]) / clk_tck
            btime = _boot_time()
            if btime:
                return btime + starttime
            return starttime
        else:
            result = subprocess.run(
                ["ps", "-p", str(pid), "-o", "lstart="],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0 and result.stdout.strip():
                import datetime

                dt = datetime.datetime.strptime(
                    result.stdout.strip(), "%a %b %d %H:%M:%S %Y"
                )
                return dt.timestamp()
        return None
    except (OSError, ValueError, IndexError, subprocess.TimeoutExpired):
        return None


def _boot_time() -> float | None:
    """Get system boot time as seconds since epoch, or None if unavailable."""
    try:
        if sys.platform == "linux":
            with open("/proc/stat") as f:
                for line in f:
                    if line.startswith("btime"):
                        return float(line.split()[1])
    except (OSError, ValueError):
        pass
    return None


def _read_pid_file(pid_file: Path) -> tuple[int, float] | None:
    """Read a PID file that may contain 'pid\\nstart_time' or just 'pid'.

    Returns (pid, recorded_start_time) or None on error.
    """
    try:
        parts = pid_file.read_text().strip().split("\n")
        pid = int(parts[0])
        recorded_start = float(parts[1]) if len(parts) > 1 else 0.0
        return pid, recorded_start
    except (ValueError, OSError):
        return None


def main() -> None:
    """CLI entry point: `python -m swain_helm.watchdog [--daemon]`."""
    import argparse as _argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    parser = _argparse.ArgumentParser(description="swain-helm watchdog")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--config-dir", default=None, help="Config directory")
    parser.add_argument(
        "--test",
        action="store_true",
        help="Skip opencode server health check (for testing only)",
    )
    args = parser.parse_args()

    config_dir = Path(args.config_dir) if args.config_dir else None

    if args.test:

        def _fake_urlopen(req, timeout=None):
            class FakeResp:
                def read(self):
                    return b'{"healthy": true}'

                def __enter__(self):
                    return self

                def __exit__(self, *a):
                    pass

            return FakeResp()

        import urllib.request, urllib.error

        urllib.request.urlopen = _fake_urlopen
        urllib.error.URLError = urllib.error.URLError

    if args.daemon:
        daemonize(config_dir)
    else:
        if os.environ.get("SWAIN_HELM_CONTAINER_MODE") == "1":
            log.info(
                "SWAIN_HELM_CONTAINER_MODE=1 — watchdog is not used in container deployment. "
                "Use python -m swain_helm.bridges.project directly."
            )
            sys.exit(0)
        watchdog = Watchdog(config_dir=config_dir)
        watchdog.load_helm_config()
        asyncio.run(watchdog.run(foreground=True))


if __name__ == "__main__":
    main()
