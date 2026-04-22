"""Shared fixtures for swain-helm integration tests that spawn real processes.

Process-interactive tests MUST be run inside Docker (docker-compose.test.yml)
to avoid interfering with the host's opencode server or Zulip connection.

External Testing Mode:
---------------------
Set SWAIN_HELM_EXTERNAL_TEST=1 to run tests against containerized services
instead of spawning local processes. This requires the external test containers
to be running (see docker-compose.external-tests.yml).

Quick start for external testing:
    docker compose -f docker-compose.external-tests.yml up -d uat-test-target
    SWAIN_HELM_EXTERNAL_TEST=1 pytest tests/uat/ -v
    docker compose -f docker-compose.external-tests.yml down
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest


# Check if we're in external test mode (testing containers from outside)
EXTERNAL_TEST_MODE = os.environ.get("SWAIN_HELM_EXTERNAL_TEST") == "1"

# Container configuration for external testing
CONTAINER_CONFIG = {
    "smoke": {
        "name": "swain-helm-smoke-test",
        "service": "smoke-test-target",
        "ports": {"health": 18081, "opencode": 14099},
    },
    "uat": {
        "name": "swain-helm-uat-test",
        "service": "uat-test-target",
        "ports": {"health": 18082, "opencode": 14100},
    },
    "e2e": {
        "name": "swain-helm-e2e-test",
        "service": "e2e-test-target",
        "ports": {"health": 18083, "opencode": 14101},
    },
}


def _docker(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a docker command."""
    cmd = ["docker", *args]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if check and result.returncode != 0:
        raise RuntimeError(f"Docker command failed: {' '.join(cmd)}\n{result.stderr}")
    return result


def _docker_compose(compose_file: Path, *args: str) -> subprocess.CompletedProcess:
    """Run docker compose command."""
    cmd = ["docker", "compose", "-f", str(compose_file), *args]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return result


class ExternalContainerHelper:
    """Helper for interacting with external test containers."""

    def __init__(self, target: str, compose_file: Path | None = None):
        self.target = target
        self.config = CONTAINER_CONFIG.get(target, CONTAINER_CONFIG["uat"])
        self.container_name = self.config["name"]
        self._ports = self.config["ports"]
        self._compose_file = compose_file or self._find_compose_file()

    def _find_compose_file(self) -> Path:
        """Find the external tests compose file."""
        # Look relative to test file
        test_dir = Path(__file__).parent.parent
        return test_dir / "docker-compose.external-tests.yml"

    @property
    def health_port(self) -> int:
        return self._ports["health"]

    @property
    def opencode_port(self) -> int:
        return self._ports["opencode"]

    def is_running(self) -> bool:
        """Check if the container is running."""
        try:
            result = _docker(
                "inspect", "-f", "{{.State.Status}}", self.container_name, check=False
            )
            return result.returncode == 0 and result.stdout.strip() == "running"
        except Exception:
            return False

    def is_healthy(self) -> bool:
        """Check container health status."""
        try:
            result = _docker(
                "inspect",
                "-f",
                "{{.State.Health.Status}}",
                self.container_name,
                check=False,
            )
            return result.returncode == 0 and result.stdout.strip() == "healthy"
        except Exception:
            return False

    def start(self) -> None:
        """Start the container via compose."""
        _docker_compose(self._compose_file, "up", "-d", self.config["service"])

    def stop(self) -> None:
        """Stop the container."""
        _docker_compose(self._compose_file, "stop", self.config["service"])

    def restart(self) -> None:
        """Restart the container."""
        _docker_compose(self._compose_file, "restart", self.config["service"])

    def wait_for_healthy(self, timeout: float = 30.0) -> bool:
        """Wait for container to become healthy."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.is_healthy():
                return True
            time.sleep(0.5)
        return False

    def exec(
        self, command: list[str], check: bool = True
    ) -> subprocess.CompletedProcess:
        """Execute a command inside the container."""
        return _docker("exec", self.container_name, *command, check=check)

    def read_file(self, path: str) -> str | None:
        """Read a file from inside the container."""
        try:
            result = self.exec(["cat", path], check=False)
            if result.returncode == 0:
                return result.stdout
            return None
        except Exception:
            return None

    def write_file(self, path: str, content: str) -> bool:
        """Write a file inside the container."""
        try:
            escaped = content.replace("'", "'\"'\"'")
            result = self.exec(
                ["sh", "-c", f"printf '%s' '{escaped}' > {path}"],
                check=False,
            )
            return result.returncode == 0
        except Exception:
            return False

    def pid_file_exists(self, path: str) -> bool:
        """Check if a PID file exists in the container."""
        try:
            result = self.exec(["test", "-f", path], check=False)
            return result.returncode == 0
        except Exception:
            return False

    def get_processes(self) -> list[dict[str, Any]]:
        """Get list of running processes in the container."""
        try:
            result = self.exec(["ps", "aux"], check=False)
            if result.returncode != 0:
                return []
            lines = result.stdout.strip().split("\n")
            processes = []
            for line in lines[1:]:  # Skip header
                parts = line.split()
                if len(parts) >= 11:
                    processes.append(
                        {
                            "user": parts[0],
                            "pid": parts[1],
                            "cpu": parts[2],
                            "mem": parts[3],
                            "vsz": parts[4],
                            "rss": parts[5],
                            "tty": parts[6],
                            "stat": parts[7],
                            "start": parts[8],
                            "time": parts[9],
                            "command": " ".join(parts[10:]),
                        }
                    )
            return processes
        except Exception:
            return []


class _WatchdogProcess:
    """Wrapper that can control either local or external watchdog."""

    def __init__(
        self, config_dir: Path, external_helper: ExternalContainerHelper | None = None
    ):
        self.config_dir = config_dir
        self.external = external_helper
        self.proc: subprocess.Popen | None = None

    def start(self, timeout: float = 15) -> None:
        if self.external:
            # External mode: ensure container is running
            if not self.external.is_running():
                self.external.start()
            self.external.wait_for_healthy(timeout=timeout)
            return

        # Local mode: spawn process
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
        if self.external:
            # External mode: stop container
            self.external.stop()
            return

        # Local mode: stop process
        if self.proc and self.proc.returncode is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=3)

    @property
    def pid(self) -> int | None:
        if self.external:
            return None  # No local PID in external mode
        return self.proc.pid if self.proc else None


def _make_config_dir(tmp_path: Path, *, port: int = 4098) -> Path:
    cfg = tmp_path / "swain-helm"
    cfg.mkdir()
    (cfg / "projects").mkdir()
    (cfg / "run" / "bridges").mkdir(parents=True)
    helm = {
        "scan_paths": ["/tmp"],
        "chat": {
            "server_url": "https://cristoslc.zulipchat.com",
            "bot_email": "swain-bot@cristoslc.zulipchat.com",
            "bot_api_key": os.environ.get("ZULIP_BOT_API_KEY", "test-key"),
            "operator_email": "cristos@cristoslc.com",
            "control_topic": "trunk",
        },
        "opencode": {"default_port": port},
    }
    (cfg / "helm.config.json").write_text(json.dumps(helm))
    return cfg


def _write_project(cfg_dir: Path, name: str, **overrides) -> Path:
    data = {
        "name": name,
        "path": f"/tmp/{name}",
        "stream": name,
        "runtime": "claude",
        "auto_start": True,
        "worktree_poll_interval_s": 15,
    }
    data.update(overrides)
    p = cfg_dir / "projects" / f"{name}.json"
    p.write_text(json.dumps(data, indent=2))
    return p


@pytest.fixture
def config_dir(tmp_path: Path) -> Path:
    return _make_config_dir(tmp_path)


@pytest.fixture
def config_dir_no_creds(tmp_path: Path) -> Path:
    return _make_config_dir(tmp_path)


@pytest.fixture
def watchdog(config_dir: Path):
    if EXTERNAL_TEST_MODE:
        # In external mode, use container helper
        helper = ExternalContainerHelper("uat")
        wd = _WatchdogProcess(config_dir, external_helper=helper)
    else:
        # Local mode
        wd = _WatchdogProcess(config_dir)
    yield wd
    wd.stop()


@pytest.fixture
def external_helper():
    """Fixture for external container helper (UAT target)."""
    if not EXTERNAL_TEST_MODE:
        pytest.skip("External helper only available in EXTERNAL_TEST_MODE")
    return ExternalContainerHelper("uat")


@pytest.fixture
def write_project():
    return _write_project


IS_DOCKER = (
    Path("/.dockerenv").exists() or os.environ.get("SWAIN_HELM_TEST_MODE") == "1"
)

skip_if_not_docker = pytest.mark.skipif(
    not IS_DOCKER and not EXTERNAL_TEST_MODE,
    reason="Process tests require Docker isolation to avoid interfering with host services",
)

requires_zulip = pytest.mark.skipif(
    not os.environ.get("ZULIP_BOT_API_KEY"),
    reason="Requires ZULIP_BOT_API_KEY environment variable",
)
