"""Tests for SPEC-318: Watchdog Core — all 7 acceptance criteria."""

import asyncio
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from swain_helm.watchdog import Watchdog


@pytest.fixture
def config_dir(tmp_path: Path) -> Path:
    return tmp_path / "swain-helm"


@pytest.fixture
def watchdog(config_dir: Path) -> Watchdog:
    return Watchdog(config_dir=config_dir)


def _write_project_config(
    projects_dir: Path, name: str, auto_start: bool = True
) -> None:
    projects_dir.mkdir(parents=True, exist_ok=True)
    cfg = {"auto_start": auto_start, "runtime": "claude"}
    (projects_dir / f"{name}.json").write_text(json.dumps(cfg))


def _write_pid_file(run_dir: Path, name: str, pid: int) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / f"{name}.pid").write_text(str(pid))


class TestAC1ReadsProjectConfigs:
    """AC1: Reads project configs from ~/.config/swain-helm/projects/."""

    def test_reads_valid_config(self, watchdog: Watchdog, config_dir: Path) -> None:
        _write_project_config(config_dir / "projects", "myproj")
        configs = watchdog._read_project_configs()
        assert "myproj" in configs
        assert configs["myproj"]["auto_start"] is True

    def test_skips_auto_start_false(self, watchdog: Watchdog, config_dir: Path) -> None:
        _write_project_config(config_dir / "projects", "manual", auto_start=False)
        configs = watchdog._read_project_configs()
        assert "manual" not in configs

    def test_handles_missing_projects_dir(self, watchdog: Watchdog) -> None:
        configs = watchdog._read_project_configs()
        assert configs == {}

    def test_handles_invalid_json(self, watchdog: Watchdog, config_dir: Path) -> None:
        projects_dir = config_dir / "projects"
        projects_dir.mkdir(parents=True, exist_ok=True)
        (projects_dir / "bad.json").write_text("not json")
        configs = watchdog._read_project_configs()
        assert "bad" not in configs

    def test_auto_start_defaults_to_true(
        self, watchdog: Watchdog, config_dir: Path
    ) -> None:
        projects_dir = config_dir / "projects"
        projects_dir.mkdir(parents=True, exist_ok=True)
        (projects_dir / "nodefault.json").write_text(json.dumps({"runtime": "claude"}))
        configs = watchdog._read_project_configs()
        assert "nodefault" in configs


class TestAC2StartsAutoStartBridges:
    """AC2: For auto_start=true bridges: starts if not running, within one cycle."""

    @pytest.mark.asyncio
    async def test_starts_bridge_not_running(
        self, watchdog: Watchdog, config_dir: Path
    ) -> None:
        _write_project_config(config_dir / "projects", "myproj")
        mock_proc = MagicMock()
        mock_proc.pid = 42
        with patch("swain_helm.watchdog.subprocess.Popen", return_value=mock_proc):
            await watchdog._reconcile()
        assert "myproj" in watchdog._running
        pid_file = config_dir / "run" / "bridges" / "myproj.pid"
        assert pid_file.exists()
        assert pid_file.read_text() == "42"

    @pytest.mark.asyncio
    async def test_does_not_restart_running_bridge(
        self, watchdog: Watchdog, config_dir: Path
    ) -> None:
        _write_project_config(config_dir / "projects", "myproj")
        _write_pid_file(config_dir / "run" / "bridges", "myproj", 99)
        with patch("swain_helm.watchdog.os.kill") as mock_kill:
            with patch("swain_helm.watchdog.subprocess.Popen") as mock_popen:
                await watchdog._reconcile()
                mock_popen.assert_not_called()


class TestAC3HealthCheckRestart:
    """AC3: Health check failure: kill and restart bridge."""

    @pytest.mark.asyncio
    async def test_restarts_unhealthy_bridge(
        self, watchdog: Watchdog, config_dir: Path
    ) -> None:
        _write_project_config(config_dir / "projects", "myproj")
        _write_pid_file(config_dir / "run" / "bridges", "myproj", 99)
        mock_proc = MagicMock()
        mock_proc.pid = 100
        with patch(
            "swain_helm.watchdog.os.kill", side_effect=ProcessLookupError
        ) as mock_kill:
            with patch("swain_helm.watchdog.subprocess.Popen", return_value=mock_proc):
                await watchdog._reconcile()
        pid_file = config_dir / "run" / "bridges" / "myproj.pid"
        assert pid_file.read_text() == "100"


class TestAC4ConfigRemovedStopsBridge:
    """AC4: Config removed: bridge stopped on next cycle."""

    @pytest.mark.asyncio
    async def test_stops_bridge_when_config_removed(
        self, watchdog: Watchdog, config_dir: Path
    ) -> None:
        mock_proc = MagicMock()
        mock_proc.pid = 50
        watchdog._running["orphan"] = mock_proc
        _write_pid_file(config_dir / "run" / "bridges", "orphan", 50)
        with patch("swain_helm.watchdog.os.kill"):
            await watchdog._reconcile()
        assert "orphan" not in watchdog._running
        mock_proc.terminate.assert_called_once()
        assert not (config_dir / "run" / "bridges" / "orphan.pid").exists()


class TestAC5PidFilesAtCorrectPath:
    """AC5: PID files at ~/.config/swain-helm/run/bridges/<name>.pid."""

    @pytest.mark.asyncio
    async def test_pid_file_written_on_start(
        self, watchdog: Watchdog, config_dir: Path
    ) -> None:
        _write_project_config(config_dir / "projects", "alpha")
        mock_proc = MagicMock()
        mock_proc.pid = 1234
        with patch("swain_helm.watchdog.subprocess.Popen", return_value=mock_proc):
            await watchdog._start_bridge("alpha", {"auto_start": True})
        expected = config_dir / "run" / "bridges" / "alpha.pid"
        assert expected.exists()
        assert expected.read_text() == "1234"

    @pytest.mark.asyncio
    async def test_pid_file_removed_on_stop(
        self, watchdog: Watchdog, config_dir: Path
    ) -> None:
        _write_pid_file(config_dir / "run" / "bridges", "beta", 5678)
        mock_proc = MagicMock()
        watchdog._running["beta"] = mock_proc
        await watchdog._stop_bridge("beta")
        assert not (config_dir / "run" / "bridges" / "beta.pid").exists()


class TestAC6DaemonModeWritesWatchdogPid:
    """AC6: Daemon mode writes ~/.config/swain-helm/run/watchdog.pid."""

    def test_foreground_mode_writes_watchdog_pid(
        self, watchdog: Watchdog, config_dir: Path
    ) -> None:
        with patch("swain_helm.watchdog.os.getpid", return_value=9999):
            watchdog._write_watchdog_pid()
        pid_path = config_dir / "run" / "watchdog.pid"
        assert pid_path.exists()
        assert pid_path.read_text() == "9999"


class TestAC7GracefulShutdown:
    """AC7: Ctrl-C triggers graceful shutdown of all bridges."""

    @pytest.mark.asyncio
    async def test_shutdown_stops_all_bridges(
        self, watchdog: Watchdog, config_dir: Path
    ) -> None:
        proc_a = MagicMock()
        proc_b = MagicMock()
        watchdog._running = {"alpha": proc_a, "beta": proc_b}
        _write_pid_file(config_dir / "run" / "bridges", "alpha", 10)
        _write_pid_file(config_dir / "run" / "bridges", "beta", 20)
        watchdog_pid = config_dir / "run" / "watchdog.pid"
        watchdog_pid.parent.mkdir(parents=True, exist_ok=True)
        watchdog_pid.write_text(str(1))
        await watchdog._shutdown()
        proc_a.terminate.assert_called_once()
        proc_b.terminate.assert_called_once()
        assert len(watchdog._running) == 0
        assert not (config_dir / "run" / "bridges" / "alpha.pid").exists()
        assert not (config_dir / "run" / "bridges" / "beta.pid").exists()
        assert not watchdog_pid.exists()

    def test_request_shutdown_sets_event(self, watchdog: Watchdog) -> None:
        assert not watchdog._shutdown_event.is_set()
        watchdog._request_shutdown()
        assert watchdog._shutdown_event.is_set()

    @pytest.mark.asyncio
    async def test_full_run_responds_to_shutdown(
        self, watchdog: Watchdog, config_dir: Path
    ) -> None:
        watchdog._shutdown_event.set()
        with patch.object(watchdog, "_write_watchdog_pid"):
            await watchdog.run(foreground=True)
