---
title: "Extend Projection Schema with Relationship Fields"
artifact: SPEC-248
type: feature
status: Proposed
author: cristos
created: 2026-04-03
last-updated: 2026-04-03
parent-epic: EPIC-058
linked-artifacts:
  - DESIGN-016
artifact-refs: []
depends-on-artifacts: []
swain-do: required
---

# Extend Projection Schema with Relationship Fields

## Context
Extend `build_projection()` in `specgraph/graph.py` to include relationship edge IDs so the materializer can create `_Related/` and `_Depends-On/` symlink directories.

## Acceptance Criteria

### Projection Schema Extension
- [ ] Add `linked_artifacts` field: list of artifact IDs from `linked-artifacts` and `artifact-refs` edges
- [ ] Add `depends_on_artifacts` field: list of artifact IDs from `depends-on` edges
- [ ] Both fields are normalized (IDs only, not paths)
- [ ] Both fields are sorted alphabetically for deterministic output
- [ ] Both fields are lists (empty list if no relationships, not null)

### Edge Extraction Logic
- [ ] Extract from edges where `from == artifact_id`
- [ ] `linked_artifacts`: edges with `type in ("linked-artifacts", "artifact-refs")`
- [ ] `depends_on_artifacts`: edges with `type == "depends-on"`
- [ ] Deduplicate: use `set()` then `sorted()` to remove duplicates

### Backward Compatibility
- [ ] Existing projection fields unchanged
- [ ] Existing tests pass without modification
- [ ] New fields are additive, not breaking

## Implementation Notes

**Location:** `skills/swain-design/scripts/specgraph/graph.py`

**Function:** `build_projection(nodes: dict, edges: list) -> list[dict]`

**Extension:**
```python
def build_projection(nodes: dict[str, dict], edges: list[dict]) -> list[dict[str, Any]]:
    projection: list[dict[str, Any]] = []
    for artifact_id in sorted(nodes):
        node = nodes[artifact_id]
        direct_parent = _select_direct_parent(artifact_id, edges)
        
        # ... existing placement logic ...
        
        # NEW: extract relationship IDs from edges
        linked = {
            e["to"] for e in edges
            if e["from"] == artifact_id
            and e["type"] in ("linked-artifacts", "artifact-refs")
            and e["to"] in nodes  # skip broken references
        }
        
        depends = {
            e["to"] for e in edges
            if e["from"] == artifact_id
            and e["type"] == "depends-on"
            and e["to"] in nodes
        }
        
        projection.append({
            "artifact": artifact_id,
            "type": node.get("type", ""),
            "status": node.get("status", ""),
            "canonical_file": node.get("file", ""),
            "canonical_path": _canonical_path(artifact_id, node.get("file", "")),
            "direct_parent": direct_parent,
            "placement_state": placement_state,
            # NEW fields:
            "linked_artifacts": sorted(linked),
            "depends_on_artifacts": sorted(depends),
        })
    return projection
```

## Test Plan
- [ ] Artifact with only `linked-artifacts`: field populated correctly
- [ ] Artifact with only `artifact-refs`: included in `linked_artifacts`
- [ ] Artifact with both `linked-artifacts` and `artifact-refs`: merged and deduplicated
- [ ] Artifact with `depends-on-artifacts`: field populated correctly
- [ ] Artifact with no relationships: both fields are empty lists
- [ ] Broken reference (target not in nodes): excluded from field
- [ ] Self-reference: included in field (materializer handles skip)
- [ ] Projection is deterministic across multiple runs

## Dependencies
- None (foundational spec)

## Linked Design Intent
From DESIGN-016:
- **Goal**: Chart remains sole source of truth
- **Constraint**: Normalized IDs, no new CLI surface
- **Non-goal**: Rendering rel types in projection