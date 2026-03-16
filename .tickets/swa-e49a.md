---
id: swa-e49a
status: closed
deps: []
links: []
created: 2026-03-16T03:44:32Z
type: task
priority: 1
assignee: cristos
parent: swa-1zpe
tags: [spec:SPEC-052]
---
# Task 1: Extend priority-weight to Epics

**Files:**
- Modify: `skills/swain-design/references/epic-definition.md`
- Modify: `skills/swain-design/references/epic-template.md.template`
- Modify: `skills/swain-design/scripts/specgraph/priority.py`
- Test: `skills/swain-design/scripts/tests/test_priority.py`

- [ ] **Step 1: Write the failing test for Epic-level priority override**

Add to `test_priority.py`:

```python
def test_epic_overrides_initiative_weight(self):
    """Epic with priority-weight overrides its parent initiative's weight."""
    nodes = {
        "VISION-001": {"status": "Active", "type": "VISION", "track": "standing",
                       "priority_weight": "high"},
        "INITIATIVE-001": {"status": "Active", "type": "INITIATIVE", "track": "container",
                           "priority_weight": "medium"},
        "EPIC-001": {"status": "Active", "type": "EPIC", "track": "container",
                     "priority_weight": "low"},
        "SPEC-001": {"status": "Proposed", "type": "SPEC", "track": "implementable"},
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
        "VISION-001": {"status": "Active", "type": "VISION", "track": "standing",
                       "priority_weight": "high"},
        "INITIATIVE-001": {"status": "Active", "type": "INITIATIVE", "track": "container",
                           "priority_weight": "medium"},
        "EPIC-001": {"status": "Active", "type": "EPIC", "track": "container"},
        "SPEC-001": {"status": "Proposed", "type": "SPEC", "track": "implementable"},
    }
    edges = [
        {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
        {"from": "EPIC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "SPEC-001", "to": "EPIC-001", "type": "parent-epic"},
    ]
    # SPEC inherits from INITIATIVE (medium=2) since EPIC has no weight
    assert resolve_vision_weight("SPEC-001", nodes, edges) == 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd skills/swain-design/scripts && python -m pytest tests/test_priority.py -v -k "test_epic_overrides or test_epic_without_weight_inherits"`
Expected: FAIL — current `resolve_vision_weight` doesn't check EPIC nodes for `priority_weight`

- [ ] **Step 3: Update `resolve_vision_weight` to include Epic in cascade**

In `skills/swain-design/scripts/specgraph/priority.py`, update the `resolve_vision_weight` function. Currently it checks for `priority_weight` on VISION and INITIATIVE types. Add EPIC to the check:

```python
def resolve_vision_weight(artifact_id, nodes, edges):
    """Walk parent chain and return effective priority weight (int).

    Cascade: Vision -> Initiative (can override) -> Epic (can override) -> Spec (inherits).
    """
    node = nodes.get(artifact_id, {})
    # Check self first (VISION, INITIATIVE, or EPIC with explicit weight)
    pw = node.get("priority_weight")
    if pw and node.get("type") in ("VISION", "INITIATIVE", "EPIC"):
        return WEIGHT_MAP.get(pw, DEFAULT_WEIGHT)

    # Walk parent chain for nearest weight
    chain = _walk_parent_chain(artifact_id, edges)
    for parent_id in chain:
        parent = nodes.get(parent_id, {})
        ppw = parent.get("priority_weight")
        if ppw and parent.get("type") in ("VISION", "INITIATIVE", "EPIC"):
            return WEIGHT_MAP.get(ppw, DEFAULT_WEIGHT)

    return DEFAULT_WEIGHT
```

Note: `_walk_parent_chain` is imported from `queries.py` or duplicated locally. Check the existing import structure — if `priority.py` already ha...


## Notes

**2026-03-16T03:46:31Z**

Complete: priority.py updated, 2 new tests pass, epic definition/template updated
