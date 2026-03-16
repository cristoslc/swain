---
id: swa-2hqc
status: closed
deps: [swa-t4c9]
links: []
created: 2026-03-16T03:44:32Z
type: task
priority: 1
assignee: cristos
parent: swa-1zpe
tags: [spec:SPEC-052]
---
# Task 3: Lens abstraction and default lens

**Files:**
- Create: `skills/swain-design/scripts/specgraph/lenses.py`
- Test: `skills/swain-design/scripts/tests/test_lenses.py`

- [ ] **Step 1: Write failing test for default lens**

Create `skills/swain-design/scripts/tests/test_lenses.py`:

```python
"""Tests for chart lenses."""
import pytest
from specgraph.lenses import DefaultLens, ReadyLens, RecommendLens, UnanchoredLens


def _make_graph():
    nodes = {
        "VISION-001": {"status": "Active", "type": "VISION", "track": "standing",
                       "title": "Swain", "priority_weight": "high"},
        "INITIATIVE-001": {"status": "Active", "type": "INITIATIVE", "track": "container",
                           "title": "Awareness"},
        "EPIC-001": {"status": "Active", "type": "EPIC", "track": "container",
                     "title": "Chart"},
        "SPEC-001": {"status": "Active", "type": "SPEC", "track": "implementable",
                     "title": "Renderer"},
        "SPEC-002": {"status": "Complete", "type": "SPEC", "track": "implementable",
                     "title": "Done Spec"},
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
        # Alphabetical by title
        assert key_fn("SPEC-001", nodes, edges) < key_fn("VISION-001", nodes, edges)


class TestReadyLens:
    def test_selects_only_ready(self):
        nodes, edges = _make_graph()
        lens = ReadyLens()
        selected = lens.select(nodes, edges)
        # SPEC-001 is ready (no unresolved deps), SPEC-002 is complete
        assert "SPEC-001" in selected
        assert "SPEC-002" not in selected

    def test_default_depth_is_execution(self):
        lens = ReadyLens()
        assert lens.default_depth == 4


class TestUnanchoredLens:
    def test_selects_only_unanchored(self):
        nodes, edges = _make_graph()
        nodes["EPIC-099"] = {"status": "Active", "type": "EPIC", "track": "container",
                             "title": "Orphan"}
        lens = UnanchoredLens()
        selected = lens.select(nodes, edges)
        assert "EPIC-099" in selected
        assert "SPEC-001" not in selected
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd skills/swain-design/scripts && python -m pytest tests/test_lenses.py -v`
Expected: FAIL — module doesn't exist

- [ ] **Step 3: Implement `lenses.py`**

Create `skills/swain-design/scripts/specgraph/lenses.py`:

```python
"""Chart lenses — define node selection, annotation, sort order, and default depth.

Each lens answers a different question about the project hierarchy.
The tree renderer handles display; lenses handle semantics.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable

from specgraph.resolved import is_resolved as _is_resolved_raw
from specgraph.priority import resolve_vision_weight, WEIGHT_MAP, rank_recommendations, compute_decision_debt
from specgraph.tree_renderer import _compute_ready_set, _walk_to_vision, _node_is_resolved


class Lens(ABC):
    """Base class for chart lenses."""

    @property
    @abstractmethod
    def default_depth(self) -> int:
        """Default tree depth (2=strategic, 4=execution)."""
       ...


## Notes

**2026-03-16T03:50:19Z**

Complete: 7 lenses + 15 tests passing
