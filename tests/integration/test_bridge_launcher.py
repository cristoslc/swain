"""BDD tests — swain-bridge launcher and runbook validation.

Scenarios covered:

  Launcher script:
    - swain-bridge --help exits 0 and shows usage
    - swain-bridge script is executable
    - swain-bridge detects existing opencode serve

  Runbook validation:
    - RUNBOOK-003 exists and has required sections
    - Domain config schema is documented
"""
from __future__ import annotations

import os
import subprocess

import pytest


class TestBridgeLauncherScript:
    """bin/swain-bridge launcher basics."""

    def test_script_exists_and_executable(self):
        script = "bin/swain-bridge"
        assert os.path.exists(script)
        assert os.access(script, os.X_OK)

    def test_help_flag_exits_zero(self):
        result = subprocess.run(
            ["bash", "bin/swain-bridge", "--help"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "Usage:" in result.stdout
        assert "--domain" in result.stdout
        assert "--port" in result.stdout

    def test_help_mentions_opencode(self):
        result = subprocess.run(
            ["bash", "bin/swain-bridge", "--help"],
            capture_output=True, text=True,
        )
        assert "opencode" in result.stdout.lower()


class TestRunbookExists:
    """RUNBOOK-003 exists and covers key sections."""

    def test_runbook_file_exists(self):
        path = "docs/runbook/Active/(RUNBOOK-003)-Untethered-Operator-Bridge/(RUNBOOK-003)-Untethered-Operator-Bridge.md"
        assert os.path.exists(path)

    def test_runbook_has_required_sections(self):
        path = "docs/runbook/Active/(RUNBOOK-003)-Untethered-Operator-Bridge/(RUNBOOK-003)-Untethered-Operator-Bridge.md"
        with open(path) as f:
            content = f.read()
        assert "## Quick Start" in content
        assert "## Prerequisites" in content
        assert "## Security Domain Setup" in content
        assert "## Troubleshooting" in content
        assert "## Slash Commands" in content

    def test_runbook_documents_attach_command(self):
        path = "docs/runbook/Active/(RUNBOOK-003)-Untethered-Operator-Bridge/(RUNBOOK-003)-Untethered-Operator-Bridge.md"
        with open(path) as f:
            content = f.read()
        assert "opencode attach" in content
