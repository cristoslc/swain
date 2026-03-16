"""Tests for chart lenses."""
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from specgraph.lenses import (
    DefaultLens, ReadyLens, RecommendLens, UnanchoredLens,
    DebtLens, StatusLens, AttentionLens, LENSES,
)


def _make_graph():
    nodes = {
        "VISION-001": {"status": "Active", "type": "VISION", "track": "standing",
                       "title": "Swain", "priority_weight": "high",
                       "file": "", "description": ""},
        "INITIATIVE-001": {"status": "Active", "type": "INITIATIVE", "track": "container",
                           "title": "Awareness", "priority_weight": "",
                           "file": "", "description": ""},
        "EPIC-001": {"status": "Active", "type": "EPIC", "track": "container",
                     "title": "Chart", "priority_weight": "",
                     "file": "", "description": ""},
        "SPEC-001": {"status": "Active", "type": "SPEC", "track": "implementable",
                     "title": "Renderer", "priority_weight": "",
                     "file": "", "description": ""},
        "SPEC-002": {"status": "Complete", "type": "SPEC", "track": "implementable",
                     "title": "Done Spec", "priority_weight": "",
                     "file": "", "description": ""},
    }
    edges = [
        {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
        {"from": "EPIC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "SPEC-001", "to": "EPIC-001", "type": "parent-epic"},
        {"from": "SPEC-002", "to": "EPIC-001", "type": "parent-epic"},
    ]
    return nodes, edges


class TestDefaultLens:
    def test_selects_non_terminal(self):
        nodes, edges = _make_graph()
        lens = DefaultLens()
        selected = lens.select(nodes, edges)
        assert "SPEC-001" in selected
        assert "SPEC-002" not in selected  # Complete = terminal

    def test_default_depth_is_strategic(self):
        lens = DefaultLens()
        assert lens.default_depth == 2

    def test_sort_key_is_alphabetical(self):
        nodes, edges = _make_graph()
        lens = DefaultLens()
        key_fn = lens.sort_key
        assert key_fn("SPEC-001", nodes, edges) < key_fn("VISION-001", nodes, edges)


class TestReadyLens:
    def test_selects_only_ready(self):
        nodes, edges = _make_graph()
        lens = ReadyLens()
        selected = lens.select(nodes, edges)
        assert "SPEC-001" in selected
        assert "SPEC-002" not in selected

    def test_default_depth_is_execution(self):
        lens = ReadyLens()
        assert lens.default_depth == 4

    def test_sort_by_unblock_count(self):
        """Artifacts that unblock more work sort first."""
        nodes, edges = _make_graph()
        nodes["SPEC-003"] = {"status": "Active", "type": "SPEC", "track": "implementable",
                             "title": "Blocked Spec", "priority_weight": "",
                             "file": "", "description": ""}
        edges.append({"from": "SPEC-003", "to": "EPIC-001", "type": "parent-epic"})
        # SPEC-003 depends on SPEC-001, so SPEC-001 unblocks 1 thing
        edges.append({"from": "SPEC-003", "to": "SPEC-001", "type": "depends-on"})
        lens = ReadyLens()
        # SPEC-001 unblocks 1 (SPEC-003), EPIC-001 unblocks 0
        key_001 = lens.sort_key("SPEC-001", nodes, edges)
        key_epic = lens.sort_key("EPIC-001", nodes, edges)
        assert key_001 < key_epic  # Higher unblock = lower sort key (first)


class TestRecommendLens:
    def test_selects_ready_items(self):
        nodes, edges = _make_graph()
        lens = RecommendLens()
        selected = lens.select(nodes, edges)
        assert len(selected) > 0
        assert "SPEC-002" not in selected

    def test_annotates_with_score(self):
        nodes, edges = _make_graph()
        lens = RecommendLens()
        lens.select(nodes, edges)
        annotations = lens.annotate(nodes, edges)
        for aid, ann in annotations.items():
            assert "score=" in ann

    def test_default_depth_is_strategic(self):
        lens = RecommendLens()
        assert lens.default_depth == 2


class TestUnanchoredLens:
    def test_selects_only_unanchored(self):
        nodes, edges = _make_graph()
        nodes["EPIC-099"] = {"status": "Active", "type": "EPIC", "track": "container",
                             "title": "Orphan", "priority_weight": "",
                             "file": "", "description": ""}
        lens = UnanchoredLens()
        selected = lens.select(nodes, edges)
        assert "EPIC-099" in selected
        assert "SPEC-001" not in selected


class TestDebtLens:
    def test_selects_decision_type_items(self):
        nodes = {
            "VISION-001": {"status": "Active", "type": "VISION", "track": "standing",
                           "title": "V1", "priority_weight": "high",
                           "file": "", "description": ""},
            "EPIC-001": {"status": "Proposed", "type": "EPIC", "track": "container",
                         "title": "Proposed Epic", "priority_weight": "",
                         "file": "", "description": ""},
            "SPEC-001": {"status": "Active", "type": "SPEC", "track": "implementable",
                         "title": "Active Spec", "priority_weight": "",
                         "file": "", "description": ""},
        }
        edges = [
            {"from": "EPIC-001", "to": "VISION-001", "type": "parent-vision"},
            {"from": "SPEC-001", "to": "EPIC-001", "type": "parent-epic"},
        ]
        lens = DebtLens()
        selected = lens.select(nodes, edges)
        assert "EPIC-001" in selected  # Proposed Epic = decision type
        assert "SPEC-001" not in selected  # Active Spec = not decision type


class TestStatusLens:
    def test_selects_all(self):
        nodes, edges = _make_graph()
        lens = StatusLens()
        selected = lens.select(nodes, edges)
        assert selected == set(nodes.keys())

    def test_annotates_with_status(self):
        nodes, edges = _make_graph()
        lens = StatusLens()
        annotations = lens.annotate(nodes, edges)
        assert annotations["SPEC-001"] == "[Active]"
        assert annotations["SPEC-002"] == "[Complete]"


class TestAttentionLens:
    def test_selects_non_terminal(self):
        nodes, edges = _make_graph()
        lens = AttentionLens()
        selected = lens.select(nodes, edges)
        assert "SPEC-001" in selected
        assert "SPEC-002" not in selected


class TestLensRegistry:
    def test_all_lenses_registered(self):
        assert "default" in LENSES
        assert "ready" in LENSES
        assert "recommend" in LENSES
        assert "attention" in LENSES
        assert "debt" in LENSES
        assert "unanchored" in LENSES
        assert "status" in LENSES
