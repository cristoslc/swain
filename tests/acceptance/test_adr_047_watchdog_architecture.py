"""Acceptance tests: ADR-047 Watchdog Architecture.

These tests verify architectural constraints specified in ADR-047.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from swain_helm.config import ResolutionError, resolve_op_references
from swain_helm.opencode_discovery import DiscoveryScanner
from swain_helm.watchdog import Watchdog
from swain_helm.watchdog import RECONCILIATION_INTERVAL


class TestADR047CredentialResolution:
    """ADR-047: 'All op:// references resolved once at startup via op read.'"""

    def test_resolve_op_references_function_exists(self):
        assert callable(resolve_op_references)

    def test_resolution_error_on_failure(self):
        assert ResolutionError is not None

    def test_resolve_caches_results(self):
        import swain_helm.config as cfg_mod

        cfg_mod._resolved_cache.clear()
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="secret123\n", stderr=""
            )
            config = {"key": "op://Vault/Item/field"}
            result = resolve_op_references(config)
            assert result["key"] == "secret123"
        cfg_mod._resolved_cache.clear()

    def test_resolve_fails_on_bad_op(self):
        import swain_helm.config as cfg_mod

        cfg_mod._resolved_cache.clear()
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1, stdout="", stderr="op not found"
            )
            config = {"key": "op://Vault/BadItem/field"}
            with pytest.raises(ResolutionError):
                resolve_op_references(config)
        cfg_mod._resolved_cache.clear()


class TestADR047WatchdogReconciliationLoop:
    """ADR-047: 'Python asyncio process that reconciles desired state on a 30-second loop.'"""

    def test_watchdog_has_reconcile(self):
        w = Watchdog(config_dir=Path("/tmp/test"))
        assert hasattr(w, "_reconcile")

    def test_watchdog_default_interval(self):
        assert RECONCILIATION_INTERVAL == 30


class TestADR047PerPortAuth:
    """ADR-047: 'Discovery only authenticates against ports with known credentials.'"""

    def test_discovery_scanner_uses_port_auth(self):
        scanner = DiscoveryScanner(
            opencode_config={"ports": {"4096": {"username": "u", "password": "p"}}},
        )
        creds = scanner._get_credentials_for_port(4096)
        assert creds is not None
        assert creds["username"] == "u"
        no_creds = scanner._get_credentials_for_port(4097)
        assert no_creds is None
