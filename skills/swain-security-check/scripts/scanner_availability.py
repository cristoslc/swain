#!/usr/bin/env python3
"""Scanner availability detection for swain-security-check (SPEC-059).

Detects whether security scanner binaries are available on the system
and generates OS-appropriate install commands when they are missing.

Supported scanners:
- gitleaks: secret detection (PATH check)
- osv-scanner: vulnerability scanning (PATH check)
- trivy: container/IaC scanning (PATH check)
- semgrep: static analysis (PATH check + uv-run fallback)

Design constraints:
- No network calls
- Must complete in < 1 second
- Returns structured results for swain-doctor integration
"""

from __future__ import annotations

import platform
import shutil
from dataclasses import dataclass
from typing import Optional


@dataclass
class ScannerResult:
    """Result of checking a single scanner's availability."""

    name: str
    available: bool
    path: Optional[str] = None
    install_hint: Optional[str] = None


# ---------------------------------------------------------------------------
# OS detection
# ---------------------------------------------------------------------------

def detect_os() -> str:
    """Detect the operating system. Returns 'darwin', 'linux', or the raw system name lowercased."""
    return platform.system().lower()


# ---------------------------------------------------------------------------
# Install command matrix
# ---------------------------------------------------------------------------

_INSTALL_COMMANDS: dict[str, dict[str, str]] = {
    "gitleaks": {
        "darwin": "brew install gitleaks",
        "linux": "apt install gitleaks  # or: cargo install gitleaks",
    },
    "osv-scanner": {
        "darwin": "brew install osv-scanner",
        "linux": "go install github.com/google/osv-scanner/cmd/osv-scanner@latest",
    },
    "trivy": {
        "darwin": "brew install trivy",
        "linux": "apt install trivy",
    },
    "semgrep": {
        "darwin": "uv run --with semgrep semgrep",
        "linux": "uv run --with semgrep semgrep",
    },
}

# Universal cargo fallback for scanners that support it
_CARGO_FALLBACK = {"gitleaks"}


def get_install_command(scanner: str, os_name: str) -> str:
    """Return the install command for a scanner on the given OS.

    Args:
        scanner: Scanner name (gitleaks, osv-scanner, trivy, semgrep).
        os_name: OS identifier from detect_os() (darwin, linux).

    Returns:
        Install command string. Falls back to cargo if available for the scanner,
        or returns a generic hint.
    """
    commands = _INSTALL_COMMANDS.get(scanner, {})
    cmd = commands.get(os_name)
    if cmd:
        return cmd
    # Fallback: cargo if supported, otherwise generic
    if scanner in _CARGO_FALLBACK:
        return f"cargo install {scanner}"
    return f"Install {scanner} — see project documentation"


# ---------------------------------------------------------------------------
# Individual scanner checks
# ---------------------------------------------------------------------------

def check_scanner(name: str) -> ScannerResult:
    """Check if a scanner binary is available in PATH.

    Args:
        name: Binary name to search for (gitleaks, osv-scanner, trivy).

    Returns:
        ScannerResult with availability status and install hint if missing.
    """
    path = shutil.which(name)
    if path:
        return ScannerResult(name=name, available=True, path=path)

    os_name = detect_os()
    hint = get_install_command(name, os_name)
    return ScannerResult(name=name, available=False, install_hint=hint)


def check_semgrep() -> ScannerResult:
    """Check semgrep availability with uv-run fallback.

    Strategy:
    1. Check if semgrep is directly in PATH -> available
    2. Check if uv is in PATH -> available via uv-run fallback
    3. Neither -> unavailable, hint to install uv

    No subprocess calls are made — detection is purely passive (which checks).
    """
    # Direct PATH check
    semgrep_path = shutil.which("semgrep")
    if semgrep_path:
        return ScannerResult(name="semgrep", available=True, path=semgrep_path)

    # uv-run fallback: if uv is available, semgrep can be run via uv
    uv_path = shutil.which("uv")
    if uv_path:
        return ScannerResult(
            name="semgrep",
            available=True,
            path=f"uv run --with semgrep semgrep",
        )

    # Neither available
    os_name = detect_os()
    hint = get_install_command("semgrep", os_name)
    return ScannerResult(
        name="semgrep",
        available=False,
        install_hint=f"uv run --with semgrep semgrep  # or install uv: {hint}",
    )


# ---------------------------------------------------------------------------
# Aggregate check
# ---------------------------------------------------------------------------

# Scanners that use simple PATH checks (not semgrep)
_PATH_SCANNERS = ["gitleaks", "osv-scanner", "trivy"]


def check_all_scanners() -> list[ScannerResult]:
    """Check availability of all security scanners.

    Returns:
        List of ScannerResult for each scanner (gitleaks, osv-scanner, trivy, semgrep).
    """
    results = [check_scanner(name) for name in _PATH_SCANNERS]
    results.append(check_semgrep())
    return results


# ---------------------------------------------------------------------------
# CLI entry point for swain-doctor integration
# ---------------------------------------------------------------------------

def format_report(results: list[ScannerResult]) -> str:
    """Format scanner availability as a human-readable report.

    Returns a multi-line string suitable for swain-doctor output.
    """
    lines = []
    available_count = sum(1 for r in results if r.available)
    total = len(results)

    lines.append(f"Scanner availability: {available_count}/{total} scanners found")

    for r in results:
        if r.available:
            lines.append(f"  [ok] {r.name}: {r.path}")
        else:
            lines.append(f"  [--] {r.name}: not found")
            if r.install_hint:
                lines.append(f"        install: {r.install_hint}")

    return "\n".join(lines)


if __name__ == "__main__":
    results = check_all_scanners()
    print(format_report(results))
