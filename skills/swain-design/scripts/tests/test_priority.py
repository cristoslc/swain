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
