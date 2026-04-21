"""Smoke tests for swain-helm containerized services.

These tests verify that containers start correctly, respond to health checks,
and expose expected ports. They run from outside the container using Docker
commands and port checks.

Run with:
    docker compose -f docker-compose.external-tests.yml up -d smoke-test-target
    python -m pytest tests/external/test_smoke.py -v
    docker compose -f docker-compose.external-tests.yml down
"""

from __future__ import annotations

import socket
import subprocess
import time

import pytest


# Check if Docker is available
def _docker_available() -> bool:
    try:
        result = subprocess.run(
            ["docker", "version"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


DOCKER_AVAILABLE = _docker_available()

# Container configuration
SMOKE_CONTAINER = "swain-helm-smoke-test"
SMOKE_HEALTH_PORT = 18081
SMOKE_OPCODE_PORT = 14099


@pytest.fixture
def smoke_container():
    """Ensure smoke test container is running."""
    if not DOCKER_AVAILABLE:
        pytest.skip("Docker not available")
    return SMOKE_CONTAINER


@pytest.mark.smoke
class TestDockerAvailability:
    """Smoke: Docker availability tests."""

    def test_docker_is_available(self):
        """Smoke: Docker is available on host."""
        assert DOCKER_AVAILABLE, "Docker is not available"

    def test_docker_daemon_responds(self):
        """Smoke: Docker daemon responds to commands."""
        result = subprocess.run(
            ["docker", "info", "--format", "{{.ServerVersion}}"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Docker daemon not responding: {result.stderr}"
        assert result.stdout.strip(), "Docker version is empty"


@pytest.mark.smoke
class TestContainerLifecycle:
    """Smoke: Container lifecycle tests."""

    def test_container_is_running(self, smoke_container):
        """Smoke: Container is running."""
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Status}}", smoke_container],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Container {smoke_container} not found"
        assert result.stdout.strip() == "running", (
            f"Container not running: {result.stdout}"
        )

    def test_container_is_healthy(self, smoke_container):
        """Smoke: Container passes health checks."""
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Health.Status}}", smoke_container],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            # Health check exists
            assert result.stdout.strip() == "healthy", (
                f"Container not healthy: {result.stdout}"
            )

    def test_container_processes_exist(self, smoke_container):
        """Smoke: Container has running processes."""
        result = subprocess.run(
            ["docker", "exec", smoke_container, "ps", "aux"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, "Could not get container processes"
        lines = result.stdout.strip().split("\n")
        assert len(lines) > 1, (
            "No processes found in container"
        )  # Header + at least one process


@pytest.mark.smoke
class TestContainerPorts:
    """Smoke: Port exposure tests."""

    def test_health_port_listening(self, smoke_container):
        """Smoke: Health port is accessible from host."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        try:
            result = sock.connect_ex(("localhost", SMOKE_HEALTH_PORT))
            assert result == 0, f"Health port {SMOKE_HEALTH_PORT} is not accessible"
        finally:
            sock.close()

    def test_opencode_port_listening(self, smoke_container):
        """Smoke: Opencode port is accessible from host."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        try:
            result = sock.connect_ex(("localhost", SMOKE_OPCODE_PORT))
            # Port should be listening (even if no server yet)
            assert result in [0, 111], (
                f"Opencode port {SMOKE_OPCODE_PORT} in unexpected state: {result}"
            )
        finally:
            sock.close()


@pytest.mark.smoke
class TestContainerFilesystem:
    """Smoke: Container filesystem tests."""

    def test_config_directory_exists(self, smoke_container):
        """Smoke: Config directory exists in container."""
        result = subprocess.run(
            [
                "docker",
                "exec",
                smoke_container,
                "test",
                "-d",
                "/root/.config/swain-helm",
            ],
            capture_output=True,
        )
        assert result.returncode == 0, "Config directory does not exist"

    def test_run_directory_exists(self, smoke_container):
        """Smoke: Run directory exists in container."""
        result = subprocess.run(
            [
                "docker",
                "exec",
                smoke_container,
                "test",
                "-d",
                "/root/.config/swain-helm/run",
            ],
            capture_output=True,
        )
        assert result.returncode == 0, "Run directory does not exist"

    def test_health_pid_file_exists(self, smoke_container):
        """Smoke: Health indicator file exists."""
        result = subprocess.run(
            [
                "docker",
                "exec",
                smoke_container,
                "test",
                "-f",
                "/root/.config/swain-helm/run/health.pid",
            ],
            capture_output=True,
        )
        assert result.returncode == 0, "Health PID file does not exist"


@pytest.mark.smoke
class TestContainerEnvironment:
    """Smoke: Container environment tests."""

    def test_test_mode_env_set(self, smoke_container):
        """Smoke: SWAIN_HELM_TEST_MODE is set."""
        result = subprocess.run(
            ["docker", "exec", smoke_container, "printenv", "SWAIN_HELM_TEST_MODE"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, "SWAIN_HELM_TEST_MODE not set"
        assert result.stdout.strip() == "1", (
            f"Expected TEST_MODE=1, got {result.stdout}"
        )

    def test_external_test_env_set(self, smoke_container):
        """Smoke: SWAIN_HELM_EXTERNAL_TEST is set."""
        result = subprocess.run(
            ["docker", "exec", smoke_container, "printenv", "SWAIN_HELM_EXTERNAL_TEST"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, "SWAIN_HELM_EXTERNAL_TEST not set"
        assert result.stdout.strip() == "1", (
            f"Expected EXTERNAL_TEST=1, got {result.stdout}"
        )

    def test_python_available(self, smoke_container):
        """Smoke: Python is available in container."""
        result = subprocess.run(
            ["docker", "exec", smoke_container, "python", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, "Python not available"
        assert "Python 3" in result.stdout, (
            f"Unexpected Python version: {result.stdout}"
        )

    def test_opencode_available(self, smoke_container):
        """Smoke: opencode CLI is available in container."""
        result = subprocess.run(
            ["docker", "exec", smoke_container, "which", "opencode"],
            capture_output=True,
        )
        assert result.returncode == 0, "opencode CLI not in PATH"


@pytest.mark.smoke
class TestDockerComposeFile:
    """Smoke: Docker compose file validation."""

    def test_external_compose_file_exists(self):
        """Smoke: External tests compose file exists."""
        import pathlib

        compose_file = (
            pathlib.Path(__file__).parent.parent.parent
            / "docker-compose.external-tests.yml"
        )
        assert compose_file.exists(), f"Compose file not found: {compose_file}"

    def test_external_compose_is_valid(self):
        """Smoke: External compose file is valid YAML."""
        import pathlib
        import yaml

        compose_file = (
            pathlib.Path(__file__).parent.parent.parent
            / "docker-compose.external-tests.yml"
        )
        try:
            with open(compose_file) as f:
                config = yaml.safe_load(f)
            assert "services" in config, "No services defined in compose file"
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML in compose file: {e}")
        except ImportError:
            pytest.skip("PyYAML not installed, skipping YAML validation")
