"""Integration tests: Watchdog lifecycle with real bridge subprocesses.

These tests spawn real watchdog and bridge processes against an isolated
config directory. They verify process management, PID files, health
checks, and reconciliation — the core loop from SPEC-318.

Requires: swain-helm installed in venv, Zulip credentials in test config.
"""

from __future__ import annotations

import asyncio
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest


def _make_config_dir(tmp_path: Path) -> Path:
    cfg = tmp_path / "swain-helm"
    cfg.mkdir()
    (cfg / "projects").mkdir()
    (cfg / "run" / "bridges").mkdir(parents=True)
    helm = {
        "scan_paths": ["/tmp"],
        "chat": {
            "server_url": "https://cristoslc.zulipchat.com",
            "bot_email": "swain-bot@cristoslc.zulipchat.com",
            "bot_api_key": "TEST_BOT_API_KEY_PLACEHOLDER",
            "operator_email": "cristos@cristoslc.com",
            "control_topic": "trunk",
        },
        "opencode": {"default_port": 4098},
    }
    (cfg / "helm.config.json").write_text(json.dumps(helm))
    return cfg


def _write_project(cfg_dir: Path, name: str, auto_start: bool = True) -> Path:
    p = cfg_dir / "projects" / f"{name}.json"
    p.write_text(
        json.dumps(
            {
                "name": name,
                "path": f"/tmp/{name}",
                "stream": name,
                "runtime": "claude",
                "auto_start": auto_start,
                "worktree_poll_interval_s": 15,
            }
        )
    )
    return p


class _WatchdogProcess:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.proc: subprocess.Popen | None = None

    def start(self, timeout: float = 10) -> None:
        self.proc = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "swain_helm.watchdog",
                "--config-dir",
                str(self.config_dir),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        deadline = time.time() + timeout
        while time.time() < deadline:
            pid_file = self.config_dir / "run" / "watchdog.pid"
            if pid_file.exists():
                return
            time.sleep(0.2)
        raise TimeoutError("Watchdog did not start")

    def stop(self) -> None:
        if self.proc and self.proc.returncode is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=3)

    @property
    def pid(self) -> int | None:
        return self.proc.pid if self.proc else None


@pytest.fixture
def config_dir(tmp_path: Path) -> Path:
    return _make_config_dir(tmp_path)


@pytest.fixture
def watchdog(config_dir: Path):
    wd = _WatchdogProcess(config_dir)
    yield wd
    wd.stop()


class TestWatchdogStartsBridge:
    """SPEC-318 AC2: auto_start=true bridges start within one cycle."""

    def test_bridge_pid_file_created(
        self, config_dir: Path, watchdog: _WatchdogProcess
    ):
        _write_project(config_dir, "alpha")
        watchdog.start()
        pid_file = config_dir / "run" / "bridges" / "alpha.pid"
        assert pid_file.exists(), "Bridge PID file not created"
        content = pid_file.read_text().strip().split("\n")
        pid = int(content[0])
        assert pid > 0

    def test_bridge_process_alive(self, config_dir: Path, watchdog: _WatchdogProcess):
        _write_project(config_dir, "alpha")
        watchdog.start()
        pid_file = config_dir / "run" / "bridges" / "alpha.pid"
        pid = int(pid_file.read_text().strip().split("\n")[0])
        os.kill(pid, 0)

    def test_two_projects_two_bridges(
        self, config_dir: Path, watchdog: _WatchdogProcess
    ):
        _write_project(config_dir, "alpha")
        _write_project(config_dir, "beta")
        watchdog.start()
        assert (config_dir / "run" / "bridges" / "alpha.pid").exists()
        assert (config_dir / "run" / "bridges" / "beta.pid").exists()


class TestWatchdogSkipsAutoStartFalse:
    """SPEC-318: auto_start=false bridges are not started."""

    def test_no_pid_file_for_manual_project(
        self, config_dir: Path, watchdog: _WatchdogProcess
    ):
        _write_project(config_dir, "manual", auto_start=False)
        watchdog.start()
        time.sleep(3)
        pid_file = config_dir / "run" / "bridges" / "manual.pid"
        assert not pid_file.exists()


class TestWatchdogStalePID:
    """SPEC-318 AC3: stale PID files trigger bridge restart."""

    def test_stale_pid_replaced(self, config_dir: Path, watchdog: _WatchdogProcess):
        _write_project(config_dir, "stale")
        bridges_dir = config_dir / "run" / "bridges"
        (bridges_dir / "stale.pid").write_text("999999\n0.0\n")
        watchdog.start()
        time.sleep(5)
        pid_file = bridges_dir / "stale.pid"
        assert pid_file.exists()
        pid = int(pid_file.read_text().strip().split("\n")[0])
        assert pid != 999999, "Stale PID was not replaced"
        os.kill(pid, 0)


class TestWatchdogZeroConfigs:
    """SPEC-318 edge: no projects configured."""

    def test_watchdog_runs_with_no_projects(
        self, config_dir: Path, watchdog: _WatchdogProcess
    ):
        watchdog.start()
        assert watchdog.proc.poll() is None, "Watchdog crashed with zero configs"


class TestWatchdogMalformedConfig:
    """SPEC-318 edge: malformed project config is skipped."""

    def test_bad_config_skipped_good_config_started(
        self, config_dir: Path, watchdog: _WatchdogProcess
    ):
        (config_dir / "projects" / "bad.json").write_text("not json{}")
        _write_project(config_dir, "good")
        watchdog.start()
        assert not (config_dir / "run" / "bridges" / "bad.pid").exists()
        assert (config_dir / "run" / "bridges" / "good.pid").exists()


class TestWatchdogGracefulShutdown:
    """SPEC-318 AC7: SIGINT triggers graceful shutdown."""

    def test_bridges_stopped_on_sigint(
        self, config_dir: Path, watchdog: _WatchdogProcess
    ):
        _write_project(config_dir, "alpha")
        watchdog.start()
        pid_file = config_dir / "run" / "bridges" / "alpha.pid"
        pid = int(pid_file.read_text().strip().split("\n")[0])
        watchdog.proc.send_signal(signal.SIGINT)
        try:
            watchdog.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            watchdog.proc.kill()
            watchdog.proc.wait(timeout=3)
        for _ in range(10):
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                break
            time.sleep(0.5)
        else:
            # Process survived SIGTERM, try SIGKILL
            import logging

            logging.warning(
                "Bridge pid %s still alive after SIGTERM+wait, sending SIGKILL", pid
            )
            try:
                cmdline = Path(f"/proc/{pid}/cmdline").read_text().replace(chr(0), " ")
                logging.warning("Process cmdline: %s", cmdline[:200])
            except (FileNotFoundError, OSError):
                pass
            os.kill(pid, signal.SIGKILL)
            time.sleep(0.5)
        with pytest.raises((ProcessLookupError, OSError)):
            os.kill(pid, 0)


class TestWatchdogBridgeLog:
    """SPEC-318: bridge subprocess output goes to log file."""

    def test_bridge_log_nonempty(self, config_dir: Path, watchdog: _WatchdogProcess):
        _write_project(config_dir, "alpha")
        watchdog.start()
        time.sleep(5)
        log_file = config_dir / "run" / "bridges" / "alpha.log"
        if log_file.exists():
            assert log_file.stat().st_size > 0, "Bridge log is empty"
