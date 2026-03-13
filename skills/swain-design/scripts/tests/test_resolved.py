"""Tests for specgraph resolution logic."""

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from specgraph.resolved import is_resolved, is_status_resolved


class TestIsStatusResolved:
    """Test bare status resolution (type-agnostic)."""

    @pytest.mark.parametrize(
        "status",
        [
            "Complete",
            "Retired",
            "Superseded",
            "Abandoned",
            "Implemented",
            "Adopted",
            "Validated",
            "Archived",
            "Sunset",
            "Deprecated",
            "Verified",
            "Declined",
        ],
    )
    def test_terminal_statuses_are_resolved(self, status):
        assert is_status_resolved(status) is True

    @pytest.mark.parametrize(
        "status",
        ["Proposed", "Active", "Draft", "Ready", "In Progress", "Review", "Planned"],
    )
    def test_non_terminal_statuses_not_resolved(self, status):
        assert is_status_resolved(status) is False


class TestIsResolved:
    """Test type-aware resolution logic."""

    # Standing-track types resolve at Active
    @pytest.mark.parametrize(
        "atype", ["VISION", "JOURNEY", "PERSONA", "ADR", "RUNBOOK", "DESIGN"]
    )
    def test_standing_active_is_resolved(self, atype):
        assert is_resolved(atype, "Active") is True

    @pytest.mark.parametrize(
        "atype", ["VISION", "JOURNEY", "PERSONA", "ADR", "RUNBOOK", "DESIGN"]
    )
    def test_standing_proposed_not_resolved(self, atype):
        assert is_resolved(atype, "Proposed") is False

    # Container types do NOT resolve at Active
    @pytest.mark.parametrize("atype", ["EPIC", "SPIKE"])
    def test_container_active_not_resolved(self, atype):
        assert is_resolved(atype, "Active") is False

    @pytest.mark.parametrize("atype", ["EPIC", "SPIKE"])
    def test_container_complete_is_resolved(self, atype):
        assert is_resolved(atype, "Complete") is True

    # Implementable type (SPEC) requires Complete
    def test_spec_complete_is_resolved(self):
        assert is_resolved("SPEC", "Complete") is True

    def test_spec_in_progress_not_resolved(self):
        assert is_resolved("SPEC", "In Progress") is False

    def test_spec_ready_not_resolved(self):
        assert is_resolved("SPEC", "Ready") is False

    # Universal terminals work for all types
    @pytest.mark.parametrize(
        "atype", ["SPEC", "EPIC", "SPIKE", "ADR", "VISION"]
    )
    def test_abandoned_always_resolved(self, atype):
        assert is_resolved(atype, "Abandoned") is True

    @pytest.mark.parametrize(
        "atype", ["SPEC", "EPIC", "SPIKE", "ADR", "VISION"]
    )
    def test_superseded_always_resolved(self, atype):
        assert is_resolved(atype, "Superseded") is True

    @pytest.mark.parametrize(
        "atype", ["SPEC", "EPIC", "SPIKE", "ADR", "VISION"]
    )
    def test_retired_always_resolved(self, atype):
        assert is_resolved(atype, "Retired") is True
