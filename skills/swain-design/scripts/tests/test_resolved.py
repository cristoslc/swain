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


class TestIsResolvedWithTrack:
    """Test is_resolved with explicit track= parameter (SPEC-038)."""

    def test_standing_active_is_resolved(self):
        """Standing-track Active artifacts are resolved."""
        assert is_resolved("SPEC", "Active", track="standing") is True

    def test_standing_proposed_not_resolved(self):
        """Standing-track Proposed is not yet resolved."""
        assert is_resolved("SPEC", "Proposed", track="standing") is False

    def test_implementable_active_not_resolved(self):
        """Implementable-track Active artifacts are NOT resolved."""
        assert is_resolved("SPEC", "Active", track="implementable") is False

    def test_implementable_complete_is_resolved(self):
        """Implementable-track Complete is resolved."""
        assert is_resolved("SPEC", "Complete", track="implementable") is True

    def test_container_active_not_resolved(self):
        """Container-track Active artifacts are NOT resolved."""
        assert is_resolved("EPIC", "Active", track="container") is False

    def test_container_complete_is_resolved(self):
        """Container-track Complete is resolved."""
        assert is_resolved("EPIC", "Complete", track="container") is True

    def test_standing_complete_terminal_is_resolved(self):
        """Terminal statuses are resolved for any track, including standing."""
        assert is_resolved("ADR", "Complete", track="standing") is True

    def test_abandoned_is_resolved_for_any_track(self):
        """Abandoned is a universal terminal — resolved regardless of track."""
        assert is_resolved("SPEC", "Abandoned", track="implementable") is True
        assert is_resolved("ADR", "Abandoned", track="standing") is True
        assert is_resolved("EPIC", "Abandoned", track="container") is True

    def test_track_none_falls_back_to_type_inference(self):
        """track=None triggers type-based inference (backward compat)."""
        # VISION is in _STANDING_TYPES, so Active should resolve
        assert is_resolved("VISION", "Active", track=None) is True
        # SPEC is implementable by inference, so Active should NOT resolve
        assert is_resolved("SPEC", "Active", track=None) is False


def test_initiative_container_track():
    """INITIATIVE uses container track — resolved only at terminal statuses."""
    assert not is_resolved("INITIATIVE", "Proposed")
    assert not is_resolved("INITIATIVE", "Active")
    assert is_resolved("INITIATIVE", "Complete")
    assert is_resolved("INITIATIVE", "Abandoned")
    assert is_resolved("INITIATIVE", "Superseded")


def test_initiative_with_track_field():
    """INITIATIVE with explicit track=container works correctly."""
    assert not is_resolved("INITIATIVE", "Active", track="container")
    assert is_resolved("INITIATIVE", "Complete", track="container")
