"""BDD tests — swain-helm runbook validation.

Scenarios covered:

  Runbook validation:
    - RUNBOOK-004 exists and has required sections
"""

from __future__ import annotations

import os

import pytest


class TestRunbookExists:
    """RUNBOOK-004 exists and covers key sections."""

    def test_runbook_file_exists(self):
        path = "docs/runbook/Active/(RUNBOOK-004)-swain-helm-Operations/(RUNBOOK-004)-swain-helm-Operations.md"
        assert os.path.exists(path)

    def test_runbook_has_required_sections(self):
        path = "docs/runbook/Active/(RUNBOOK-004)-swain-helm-Operations/(RUNBOOK-004)-swain-helm-Operations.md"
        with open(path) as f:
            content = f.read()
        assert "## Prerequisites" in content
        assert "## Steps" in content
        assert "## Troubleshooting" in content

    def test_runbook_documents_helm_commands(self):
        path = "docs/runbook/Active/(RUNBOOK-004)-swain-helm-Operations/(RUNBOOK-004)-swain-helm-Operations.md"
        with open(path) as f:
            content = f.read()
        assert "swain-helm" in content
