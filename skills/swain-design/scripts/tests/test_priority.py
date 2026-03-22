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

    def test_epic_overrides_initiative_weight(self):
        """Epic with priority-weight overrides its parent initiative's weight."""
        nodes = {
            "VISION-001": {"title": "V1", "status": "Active", "type": "VISION",
                           "priority_weight": "high", "file": "", "description": ""},
            "INITIATIVE-001": {"title": "I1", "status": "Active", "type": "INITIATIVE",
                               "priority_weight": "medium", "file": "", "description": ""},
            "EPIC-001": {"title": "E1", "status": "Active", "type": "EPIC",
                         "priority_weight": "low", "file": "", "description": ""},
            "SPEC-001": {"title": "S1", "status": "Proposed", "type": "SPEC",
                         "priority_weight": "", "file": "", "description": ""},
        }
        edges = [
            {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
            {"from": "EPIC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
            {"from": "SPEC-001", "to": "EPIC-001", "type": "parent-epic"},
        ]
        # SPEC inherits from EPIC's override (low=1), not INITIATIVE (medium=2)
        assert resolve_vision_weight("SPEC-001", nodes, edges) == 1

    def test_epic_without_weight_inherits_from_initiative(self):
        """Epic without priority-weight inherits from parent initiative."""
        nodes = {
            "VISION-001": {"title": "V1", "status": "Active", "type": "VISION",
                           "priority_weight": "high", "file": "", "description": ""},
            "INITIATIVE-001": {"title": "I1", "status": "Active", "type": "INITIATIVE",
                               "priority_weight": "medium", "file": "", "description": ""},
            "EPIC-001": {"title": "E1", "status": "Active", "type": "EPIC",
                         "priority_weight": "", "file": "", "description": ""},
            "SPEC-001": {"title": "S1", "status": "Proposed", "type": "SPEC",
                         "priority_weight": "", "file": "", "description": ""},
        }
        edges = [
            {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
            {"from": "EPIC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
            {"from": "SPEC-001", "to": "EPIC-001", "type": "parent-epic"},
        ]
        # SPEC inherits from INITIATIVE (medium=2) since EPIC has no weight
        assert resolve_vision_weight("SPEC-001", nodes, edges) == 2

    def test_spec_overrides_epic_weight(self):
        """SPEC with priority-weight overrides its parent Epic's weight."""
        nodes = {
            "VISION-001": {"title": "V1", "status": "Active", "type": "VISION",
                           "priority_weight": "high", "file": "", "description": ""},
            "EPIC-001": {"title": "E1", "status": "Active", "type": "EPIC",
                         "priority_weight": "high", "file": "", "description": ""},
            "SPEC-001": {"title": "S1", "status": "Ready", "type": "SPEC",
                         "priority_weight": "low", "file": "", "description": ""},
        }
        edges = [
            {"from": "EPIC-001", "to": "VISION-001", "type": "parent-vision"},
            {"from": "SPEC-001", "to": "EPIC-001", "type": "parent-epic"},
        ]
        # SPEC has own weight low=1, overrides Epic's high=3
        assert resolve_vision_weight("SPEC-001", nodes, edges) == 1

    def test_spec_without_weight_still_inherits(self):
        """SPEC with no priority-weight still inherits from parent chain (no regression)."""
        assert resolve_vision_weight("SPEC-001", self.NODES, self.EDGES) == 3


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


class TestRecommendationScoring:
    """Test the score = unblock_count × vision_weight ranking."""

    NODES = {
        "VISION-001": {"title": "V1", "status": "Active", "type": "VISION", "priority_weight": "high", "file": "", "description": ""},
        "VISION-002": {"title": "V2", "status": "Active", "type": "VISION", "priority_weight": "low", "file": "", "description": ""},
        "INITIATIVE-001": {"title": "I1", "status": "Active", "type": "INITIATIVE", "priority_weight": "", "file": "", "description": ""},
        "INITIATIVE-002": {"title": "I2", "status": "Active", "type": "INITIATIVE", "priority_weight": "", "file": "", "description": ""},
        "EPIC-001": {"title": "E1", "status": "Proposed", "type": "EPIC", "priority_weight": "", "file": "", "description": ""},
        "EPIC-002": {"title": "E2", "status": "Proposed", "type": "EPIC", "priority_weight": "", "file": "", "description": ""},
        "SPEC-010": {"title": "SP10", "status": "Proposed", "type": "SPEC", "priority_weight": "", "file": "", "description": ""},
        "SPEC-011": {"title": "SP11", "status": "Proposed", "type": "SPEC", "priority_weight": "", "file": "", "description": ""},
        "SPEC-012": {"title": "SP12", "status": "Proposed", "type": "SPEC", "priority_weight": "", "file": "", "description": ""},
    }

    EDGES = [
        {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
        {"from": "INITIATIVE-002", "to": "VISION-002", "type": "parent-vision"},
        {"from": "EPIC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "EPIC-002", "to": "INITIATIVE-002", "type": "parent-initiative"},
        # EPIC-002 (low vision) unblocks 3 specs
        {"from": "SPEC-010", "to": "EPIC-002", "type": "depends-on"},
        {"from": "SPEC-011", "to": "EPIC-002", "type": "depends-on"},
        {"from": "SPEC-012", "to": "EPIC-002", "type": "depends-on"},
    ]

    def test_unblock_count_times_weight_determines_rank(self):
        from specgraph.priority import rank_recommendations
        ranked = rank_recommendations(self.NODES, self.EDGES)
        # EPIC-001: 0 unblocks × 3 (high) = 0. EPIC-002: 3 unblocks × 1 (low) = 3
        # Score 3 > 0 so EPIC-002 ranks first despite lower vision weight
        assert ranked[0]["id"] == "EPIC-002"

    def test_ranking_is_deterministic(self):
        from specgraph.priority import rank_recommendations
        ranked1 = rank_recommendations(self.NODES, self.EDGES)
        ranked2 = rank_recommendations(self.NODES, self.EDGES)
        assert [r["id"] for r in ranked1] == [r["id"] for r in ranked2]

    def test_focus_vision_filters_results(self):
        from specgraph.priority import rank_recommendations
        ranked = rank_recommendations(self.NODES, self.EDGES, focus_vision="VISION-001")
        vision_ids = {r["vision_id"] for r in ranked}
        assert "VISION-002" not in vision_ids

    def test_each_item_has_required_fields(self):
        from specgraph.priority import rank_recommendations
        ranked = rank_recommendations(self.NODES, self.EDGES)
        for item in ranked:
            assert "id" in item
            assert "score" in item
            assert "unblock_count" in item
            assert "vision_weight" in item
            assert "vision_id" in item
            assert "is_decision" in item
            assert "type" in item
