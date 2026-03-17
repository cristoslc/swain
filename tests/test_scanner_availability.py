"""Tests for scanner availability detection (SPEC-059).

Tests cover:
- PATH-based binary detection for gitleaks, osv-scanner, trivy
- Semgrep detection with uv-run fallback
- OS detection and install command generation
- Aggregate availability reporting
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add the scripts directory to the path so we can import the module
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "skills" / "swain-security-check" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from scanner_availability import (
    ScannerResult,
    check_scanner,
    check_semgrep,
    check_all_scanners,
    detect_os,
    get_install_command,
)


# ---------------------------------------------------------------------------
# Tests for PATH-based scanner detection (gitleaks, osv-scanner, trivy)
# ---------------------------------------------------------------------------


class TestScannerResult:
    """ScannerResult dataclass has the right shape."""

    def test_available_result(self):
        result = ScannerResult(name="gitleaks", available=True, path="/usr/local/bin/gitleaks")
        assert result.name == "gitleaks"
        assert result.available is True
        assert result.path == "/usr/local/bin/gitleaks"
        assert result.install_hint is None

    def test_unavailable_result_with_hint(self):
        result = ScannerResult(
            name="gitleaks",
            available=False,
            path=None,
            install_hint="brew install gitleaks",
        )
        assert result.available is False
        assert result.path is None
        assert result.install_hint == "brew install gitleaks"


class TestCheckScanner:
    """check_scanner() detects binary presence via PATH."""

    def test_scanner_found_in_path(self):
        with patch("shutil.which", return_value="/usr/local/bin/gitleaks"):
            result = check_scanner("gitleaks")
        assert result.available is True
        assert result.name == "gitleaks"
        assert result.path == "/usr/local/bin/gitleaks"

    def test_scanner_not_found_in_path(self):
        with patch("shutil.which", return_value=None):
            result = check_scanner("gitleaks")
        assert result.available is False
        assert result.name == "gitleaks"
        assert result.path is None
        assert result.install_hint is not None

    def test_osv_scanner_found(self):
        with patch("shutil.which", return_value="/usr/local/bin/osv-scanner"):
            result = check_scanner("osv-scanner")
        assert result.available is True
        assert result.name == "osv-scanner"

    def test_osv_scanner_not_found(self):
        with patch("shutil.which", return_value=None):
            result = check_scanner("osv-scanner")
        assert result.available is False
        assert result.install_hint is not None

    def test_trivy_found(self):
        with patch("shutil.which", return_value="/usr/local/bin/trivy"):
            result = check_scanner("trivy")
        assert result.available is True

    def test_trivy_not_found(self):
        with patch("shutil.which", return_value=None):
            result = check_scanner("trivy")
        assert result.available is False
        assert result.install_hint is not None


class TestDetectOS:
    """detect_os() returns darwin or linux."""

    def test_darwin(self):
        with patch("platform.system", return_value="Darwin"):
            assert detect_os() == "darwin"

    def test_linux(self):
        with patch("platform.system", return_value="Linux"):
            assert detect_os() == "linux"

    def test_unknown_falls_back(self):
        with patch("platform.system", return_value="Windows"):
            # Should return something (not crash), even on unsupported OS
            result = detect_os()
            assert isinstance(result, str)


class TestGetInstallCommand:
    """get_install_command() returns OS-appropriate install instructions."""

    def test_gitleaks_darwin(self):
        cmd = get_install_command("gitleaks", "darwin")
        assert "brew install gitleaks" in cmd

    def test_gitleaks_linux(self):
        cmd = get_install_command("gitleaks", "linux")
        # Linux can use apt or cargo
        assert "gitleaks" in cmd

    def test_osv_scanner_darwin(self):
        cmd = get_install_command("osv-scanner", "darwin")
        assert "brew install osv-scanner" in cmd

    def test_osv_scanner_linux(self):
        cmd = get_install_command("osv-scanner", "linux")
        assert "osv-scanner" in cmd

    def test_trivy_darwin(self):
        cmd = get_install_command("trivy", "darwin")
        assert "brew install trivy" in cmd

    def test_trivy_linux(self):
        cmd = get_install_command("trivy", "linux")
        assert "trivy" in cmd

    def test_semgrep_darwin(self):
        cmd = get_install_command("semgrep", "darwin")
        assert "uv" in cmd or "semgrep" in cmd

    def test_semgrep_linux(self):
        cmd = get_install_command("semgrep", "linux")
        assert "uv" in cmd or "semgrep" in cmd


# ---------------------------------------------------------------------------
# Tests for semgrep uv-run fallback (task 2)
# ---------------------------------------------------------------------------


class TestCheckSemgrep:
    """check_semgrep() detects semgrep in PATH, falls back to uv-run."""

    def test_semgrep_found_in_path(self):
        """When semgrep is directly in PATH, return available with path."""
        with patch("shutil.which", return_value="/usr/local/bin/semgrep"):
            result = check_semgrep()
        assert result.available is True
        assert result.name == "semgrep"
        assert result.path == "/usr/local/bin/semgrep"

    def test_semgrep_not_in_path_uv_available(self):
        """When semgrep is NOT in PATH but uv IS, return available via uv fallback."""
        def mock_which(name):
            if name == "semgrep":
                return None
            if name == "uv":
                return "/usr/local/bin/uv"
            return None

        with patch("shutil.which", side_effect=mock_which):
            result = check_semgrep()
        assert result.available is True
        assert result.name == "semgrep"
        # Path should indicate the uv-run fallback mechanism
        assert "uv" in (result.path or "")

    def test_semgrep_not_in_path_uv_not_available(self):
        """When neither semgrep nor uv is in PATH, return unavailable with install hint."""
        with patch("shutil.which", return_value=None):
            result = check_semgrep()
        assert result.available is False
        assert result.name == "semgrep"
        assert result.install_hint is not None
        # Hint should mention uv as the recommended install method
        assert "uv" in result.install_hint

    def test_semgrep_fallback_does_not_execute(self):
        """uv-run fallback detection must NOT actually execute semgrep (no network)."""
        # We only check for uv binary presence, we don't run it
        def mock_which(name):
            if name == "uv":
                return "/usr/local/bin/uv"
            return None

        with patch("shutil.which", side_effect=mock_which):
            with patch("subprocess.run") as mock_run:
                result = check_semgrep()
                # subprocess.run should NOT be called — detection is passive
                mock_run.assert_not_called()
        assert result.available is True


class TestCheckAllScanners:
    """check_all_scanners() returns results for all four scanners."""

    def test_returns_all_scanners(self):
        with patch("shutil.which", return_value=None):
            with patch("scanner_availability.check_semgrep") as mock_semgrep:
                mock_semgrep.return_value = ScannerResult(
                    name="semgrep", available=False, install_hint="uv run --with semgrep semgrep"
                )
                results = check_all_scanners()
        names = [r.name for r in results]
        assert "gitleaks" in names
        assert "osv-scanner" in names
        assert "trivy" in names
        assert "semgrep" in names
        assert len(results) == 4

    def test_all_available(self):
        def mock_which(name):
            return f"/usr/local/bin/{name}"

        with patch("shutil.which", side_effect=mock_which):
            with patch("scanner_availability.check_semgrep") as mock_semgrep:
                mock_semgrep.return_value = ScannerResult(
                    name="semgrep", available=True, path="/usr/local/bin/semgrep"
                )
                results = check_all_scanners()
        assert all(r.available for r in results)

    def test_none_available(self):
        with patch("shutil.which", return_value=None):
            with patch("scanner_availability.check_semgrep") as mock_semgrep:
                mock_semgrep.return_value = ScannerResult(
                    name="semgrep", available=False, install_hint="uv run --with semgrep semgrep"
                )
                results = check_all_scanners()
        assert not any(r.available for r in results)
        assert all(r.install_hint is not None for r in results)


class TestPerformanceBound:
    """Availability checks must complete in < 1 second with no network."""

    def test_check_all_under_one_second(self):
        import time

        with patch("shutil.which", return_value=None):
            with patch("scanner_availability.check_semgrep") as mock_semgrep:
                mock_semgrep.return_value = ScannerResult(
                    name="semgrep", available=False, install_hint="hint"
                )
                start = time.monotonic()
                check_all_scanners()
                elapsed = time.monotonic() - start
        assert elapsed < 1.0, f"check_all_scanners took {elapsed:.3f}s (must be < 1s)"
