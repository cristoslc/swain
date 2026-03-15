"""Tests for prioritization scoring functions."""

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from specgraph.priority import resolve_vision_weight, WEIGHT_MAP


class TestVisionWeightResolution:
    """Test resolving the effective vision weight for any artifact."""

    NODES = {
        "VISION-001": {"title": "V1", "status": "Active", "type": "VISION", "priority_weight": "high", "file": "", "description": ""},
        "VISION-002": {"title": "V2", "status": "Active", "type": "VISION", "priority_weight": "", "file": "", "description": ""},
        "INITIATIVE-001": {"title": "I1", "status": "Active", "type": "INITIATIVE", "priority_weight": "", "file": "", "description": ""},
        "INITIATIVE-002": {"title": "I2", "status": "Active", "type": "INITIATIVE", "priority_weight": "low", "file": "", "description": ""},
        "EPIC-001": {"title": "E1", "status": "Active", "type": "EPIC", "priority_weight": "", "file": "", "description": ""},
        "SPEC-001": {"title": "S1", "status": "Ready", "type": "SPEC", "priority_weight": "", "file": "", "description": ""},
    }

    EDGES = [
        {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
        {"from": "INITIATIVE-002", "to": "VISION-001", "type": "parent-vision"},
        {"from": "EPIC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "SPEC-001", "to": "EPIC-001", "type": "parent-epic"},
    ]

    def test_vision_returns_own_weight(self):
        assert resolve_vision_weight("VISION-001", self.NODES, self.EDGES) == 3  # high

    def test_vision_default_medium(self):
        assert resolve_vision_weight("VISION-002", self.NODES, self.EDGES) == 2  # medium default

    def test_initiative_inherits_vision_weight(self):
        assert resolve_vision_weight("INITIATIVE-001", self.NODES, self.EDGES) == 3  # inherits high

    def test_initiative_override(self):
        assert resolve_vision_weight("INITIATIVE-002", self.NODES, self.EDGES) == 1  # overrides to low

    def test_epic_inherits_through_initiative(self):
        assert resolve_vision_weight("EPIC-001", self.NODES, self.EDGES) == 3  # EPIC→INIT→VISION(high)

    def test_spec_inherits_through_chain(self):
        assert resolve_vision_weight("SPEC-001", self.NODES, self.EDGES) == 3  # SPEC→EPIC→INIT→VISION(high)

    def test_orphan_returns_default(self):
        assert resolve_vision_weight("ORPHAN-001", self.NODES, self.EDGES) == 2  # medium default


class TestDecisionDebt:
    """Test decision debt computation per vision."""

    NODES = {
        "VISION-001": {"title": "V1", "status": "Active", "type": "VISION", "priority_weight": "high", "file": "", "description": ""},
        "VISION-002": {"title": "V2", "status": "Active", "type": "VISION", "priority_weight": "medium", "file": "", "description": ""},
        "INITIATIVE-001": {"title": "I1", "status": "Active", "type": "INITIATIVE", "priority_weight": "", "file": "", "description": ""},
        "EPIC-001": {"title": "E1", "status": "Proposed", "type": "EPIC", "priority_weight": "", "file": "", "description": ""},
        "EPIC-002": {"title": "E2", "status": "Proposed", "type": "EPIC", "priority_weight": "", "file": "", "description": ""},
        "SPIKE-001": {"title": "S1", "status": "Proposed", "type": "SPIKE", "priority_weight": "", "file": "", "description": ""},
        "SPEC-001": {"title": "SP1", "status": "Ready", "type": "SPEC", "priority_weight": "", "file": "", "description": ""},
    }

    EDGES = [
        {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
        {"from": "EPIC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "EPIC-002", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "SPIKE-001", "to": "VISION-002", "type": "parent-vision"},
        {"from": "SPEC-001", "to": "EPIC-001", "type": "parent-epic"},
        # EPIC-002 depends on SPIKE-001 (blocked)
        {"from": "EPIC-002", "to": "SPIKE-001", "type": "depends-on"},
    ]

    def test_decision_debt_counts_ready_decision_items_per_vision(self):
        from specgraph.priority import compute_decision_debt
        debt = compute_decision_debt(self.NODES, self.EDGES)
        # VISION-001: EPIC-001 is ready and decision-type (Proposed Epic). SPEC-001 is Ready but NOT decision-type (it's implementation work). EPIC-002 is blocked.
        # VISION-002: SPIKE-001 is ready and decision-type (Proposed Spike)
        assert debt["VISION-001"]["count"] == 1  # Only EPIC-001 (decision-type)
        assert debt["VISION-002"]["count"] == 1  # SPIKE-001

    def test_decision_debt_includes_weighted_unblocks(self):
        from specgraph.priority import compute_decision_debt
        debt = compute_decision_debt(self.NODES, self.EDGES)
        # SPIKE-001 being completed would unblock EPIC-002
        assert debt["VISION-002"]["total_unblocks"] >= 1
