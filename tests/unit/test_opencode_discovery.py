import asyncio
import json
import logging
import base64
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from swain_helm.opencode_discovery import (
    DEFAULT_PORT,
    OPENCODE_CONFIG_PATH,
    DiscoveryScanner,
    OpenCodeInstance,
)


def _make_scanner(config=None, tmp_path=None):
    config = config or {}
    run_dir = tmp_path or Path("/tmp/fake-swain-helm-run")
    return DiscoveryScanner(config, run_dir=run_dir)


def _mock_urlopen_health(port, healthy=True, status=200, need_auth=False):
    """Return a mock context manager for urlopen that simulates health responses."""

    class FakeResponse:
        def __init__(self):
            self.status = status
            self._data = json.dumps({"healthy": healthy}).encode()

        def read(self):
            return self._data

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

    class FakeAuthResponse:
        def __init__(self):
            self.status = status if need_auth else 200
            self._data = json.dumps({"healthy": True}).encode()

        def read(self):
            return self._data

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

    return FakeResponse()


class TestDefaultPort:
    def test_reads_default_port_from_config(self, tmp_path):
        scanner = _make_scanner({"default_port": 5000}, tmp_path / "run")
        assert scanner.get_default_port() == 5000

    def test_reads_port_from_opencode_config(self, tmp_path):
        oc_dir = tmp_path / "opencode"
        oc_dir.mkdir()
        oc_config = oc_dir / "opencode.json"
        oc_config.write_text(json.dumps({"server": {"port": 4321}}))

        scanner = _make_scanner({}, tmp_path / "run")
        with patch.object(
            DiscoveryScanner,
            "__init__",
            lambda self, *a, **kw: None,
        ):
            scanner.config = {}
            scanner.run_dir = tmp_path / "run"
            scanner.instances_file = scanner.run_dir / "opencode-instances.json"
            scanner._instances = {}
        with patch("swain_helm.opencode_discovery.OPENCODE_CONFIG_PATH", oc_config):
            assert scanner.get_default_port() == 4321

    def test_fallback_to_4096(self, tmp_path):
        scanner = _make_scanner({}, tmp_path / "run")
        with patch(
            "swain_helm.opencode_discovery.OPENCODE_CONFIG_PATH", Path("/nonexistent")
        ):
            assert scanner.get_default_port() == DEFAULT_PORT


class TestCandidatePorts:
    def test_includes_config_ports(self, tmp_path):
        config = {"ports": {"5000": {"username": "u", "password": "p"}}}
        scanner = _make_scanner(config, tmp_path / "run")
        ports = scanner.get_candidate_ports()
        assert 5000 in ports

    def test_includes_previously_seen_ports(self, tmp_path):
        run_dir = tmp_path / "run"
        run_dir.mkdir()
        state = {"instances": [{"port": 6000, "pid": None, "started_by_bridge": False}]}
        (run_dir / "opencode-instances.json").write_text(json.dumps(state))

        scanner = _make_scanner({}, run_dir)
        ports = scanner.get_candidate_ports()
        assert 6000 in ports

    def test_includes_default_port(self, tmp_path):
        scanner = _make_scanner({"default_port": 7000}, tmp_path / "run")
        ports = scanner.get_candidate_ports()
        assert 7000 in ports

    def test_deduplicates(self, tmp_path):
        config = {
            "default_port": 5000,
            "ports": {"5000": {"username": "u", "password": "p"}},
        }
        scanner = _make_scanner(config, tmp_path / "run")
        ports = scanner.get_candidate_ports()
        assert ports.count(5000) == 1


class TestAuthTestOnlyWithMatchingCredentials:
    def test_auth_test_called_for_port_with_credentials(self, tmp_path):
        config = {
            "ports": {
                "5000": {"username": "user", "password": "pass"},
            }
        }
        scanner = _make_scanner(config, tmp_path / "run")

        call_log = []

        def fake_urlopen(req, timeout=5):
            call_log.append(req.full_url)
            resp = MagicMock()
            resp.status = 200
            resp.read.return_value = json.dumps({"healthy": True}).encode()
            resp.__enter__ = lambda s: s
            resp.__exit__ = MagicMock(return_value=False)
            return resp

        with patch("swain_helm.opencode_discovery.urlopen", fake_urlopen):
            result = scanner.auth_test(5000)
        assert result is True
        assert len(call_log) == 1

    def test_auth_test_returns_false_for_port_without_credentials(self, tmp_path):
        scanner = _make_scanner({}, tmp_path / "run")
        result = scanner.auth_test(5000)
        assert result is False

    def test_scan_does_not_auth_test_port_without_credentials(self, tmp_path, caplog):
        config = {}
        scanner = _make_scanner(config, tmp_path / "run")

        auth_test_calls = []

        original_auth_test = scanner.auth_test

        def tracking_auth_test(port):
            auth_test_calls.append(port)
            return original_auth_test(port)

        scanner.auth_test = tracking_auth_test

        def fake_health(port):
            return True

        with patch.object(scanner, "health_check", fake_health):
            with patch(
                "swain_helm.opencode_discovery.OPENCODE_CONFIG_PATH",
                Path("/nonexistent"),
            ):
                scanner.scan()

        assert len(auth_test_calls) == 0


class TestUsableInstanceOnAuthSuccess:
    def test_auth_success_returns_usable_instance(self, tmp_path):
        config = {
            "default_port": 5000,
            "ports": {"5000": {"username": "u", "password": "p"}},
        }
        scanner = _make_scanner(config, tmp_path / "run")

        with patch.object(scanner, "health_check", return_value=True):
            with patch.object(scanner, "auth_test", return_value=True):
                with patch(
                    "swain_helm.opencode_discovery.OPENCODE_CONFIG_PATH",
                    Path("/nonexistent"),
                ):
                    usable = scanner.scan()

        assert len(usable) == 1
        assert usable[0].port == 5000
        assert usable[0].auth_valid is True


class TestAuthMismatchOnNoMatchingCredentials:
    def test_healthy_but_no_credentials_marks_auth_mismatch(self, tmp_path, caplog):
        config = {"default_port": 5000}
        scanner = _make_scanner(config, tmp_path / "run")

        with patch.object(scanner, "health_check", return_value=True):
            with patch(
                "swain_helm.opencode_discovery.OPENCODE_CONFIG_PATH",
                Path("/nonexistent"),
            ):
                with caplog.at_level(
                    logging.WARNING, logger="swain_helm.opencode_discovery"
                ):
                    usable = scanner.scan()

        assert len(usable) == 0
        inst = scanner._instances[5000]
        assert inst.auth_tested is False
        assert inst.auth_valid is False

    def test_healthy_with_bad_credentials_logs_warning(self, tmp_path, caplog):
        config = {
            "default_port": 5000,
            "ports": {"5000": {"username": "u", "password": "wrong"}},
        }
        scanner = _make_scanner(config, tmp_path / "run")

        with patch.object(scanner, "health_check", return_value=True):
            with patch.object(scanner, "auth_test", return_value=False):
                with patch(
                    "swain_helm.opencode_discovery.OPENCODE_CONFIG_PATH",
                    Path("/nonexistent"),
                ):
                    with caplog.at_level(
                        logging.WARNING, logger="swain_helm.opencode_discovery"
                    ):
                        usable = scanner.scan()

        assert len(usable) == 0
        inst = scanner._instances[5000]
        assert inst.auth_required is True
        assert inst.auth_tested is True
        assert inst.auth_valid is False


class TestStartIfNeeded:
    @pytest.mark.asyncio
    async def test_starts_new_instance_when_none_usable(self, tmp_path):
        import logging

        config = {"default_port": 4096}
        scanner = _make_scanner(config, tmp_path / "run")

        with patch.object(scanner, "health_check", return_value=False):
            mock_proc = MagicMock()
            mock_proc.pid = 12345

            with patch(
                "swain_helm.opencode_discovery.subprocess.Popen", return_value=mock_proc
            ):
                # Health check returns True on retry
                call_count = {"n": 0}

                def health_flip(port):
                    call_count["n"] += 1
                    return False if call_count["n"] <= 1 else True

                with patch.object(scanner, "health_check", side_effect=health_flip):
                    with patch.object(scanner, "auth_test", return_value=False):
                        with patch(
                            "swain_helm.opencode_discovery.OPENCODE_CONFIG_PATH",
                            Path("/nonexistent"),
                        ):
                            # Override scan to return empty
                            with patch.object(scanner, "scan", return_value=[]):
                                result = await scanner.start_if_needed()

        assert result is not None
        assert result.started_by_bridge is True
        assert result.pid == 12345

    @pytest.mark.asyncio
    async def test_returns_existing_if_usable(self, tmp_path):
        existing = OpenCodeInstance(port=5000, auth_valid=True)
        scanner = _make_scanner({"default_port": 5000}, tmp_path / "run")

        with patch.object(scanner, "scan", return_value=[existing]):
            result = await scanner.start_if_needed()

        assert result is existing


class TestStatePersistence:
    def test_scan_persists_state_to_file(self, tmp_path):
        run_dir = tmp_path / "run"
        config = {
            "default_port": 5000,
            "ports": {"5000": {"username": "u", "password": "p"}},
        }
        scanner = _make_scanner(config, run_dir)

        with patch.object(scanner, "health_check", return_value=True):
            with patch.object(scanner, "auth_test", return_value=True):
                with patch(
                    "swain_helm.opencode_discovery.OPENCODE_CONFIG_PATH",
                    Path("/nonexistent"),
                ):
                    scanner.scan()

        state_file = run_dir / "opencode-instances.json"
        assert state_file.exists()
        data = json.loads(state_file.read_text())
        assert len(data["instances"]) == 1
        assert data["instances"][0]["port"] == 5000

    def test_state_reloaded_on_new_scanner(self, tmp_path):
        run_dir = tmp_path / "run"
        run_dir.mkdir()
        state = {
            "instances": [
                {
                    "port": 6000,
                    "pid": 99,
                    "started_by_bridge": True,
                    "auth_required": True,
                    "auth_tested": True,
                    "auth_valid": True,
                }
            ]
        }
        (run_dir / "opencode-instances.json").write_text(json.dumps(state))

        scanner = _make_scanner({"default_port": 4096}, run_dir)
        ports = scanner.get_candidate_ports()
        assert 6000 in ports
        assert scanner._instances[6000].pid == 99


class TestNeverAuthWithoutCredentials:
    def test_scan_skips_auth_for_port_without_creds(self, tmp_path):
        config = {"default_port": 5000}
        scanner = _make_scanner(config, tmp_path / "run")

        with patch.object(scanner, "health_check", return_value=True):
            with patch(
                "swain_helm.opencode_discovery.OPENCODE_CONFIG_PATH",
                Path("/nonexistent"),
            ):
                usable = scanner.scan()

        assert len(usable) == 0
        inst = scanner._instances[5000]
        assert inst.auth_tested is False
        assert inst.auth_valid is False
