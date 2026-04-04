---
title: "Materialize Related Artifacts Symlinks"
artifact: SPEC-249
type: feature
status: Proposed
author: cristos
created: 2026-04-03
last-updated: 2026-04-03
parent-epic: EPIC-058
linked-artifacts:
  - DESIGN-016
artifact-refs: []
depends-on-artifacts:
  - SPEC-248
swain-do: required
---

# Materialize Related Artifacts Symlinks

## Context
Extend `materialize_children()` in `specgraph/materialize.py` to create `_Related/` and `_Depends-On/` symlink directories based on the new projection fields.

## Acceptance Criteria

### _Related/ Directory
- [ ] Create `_Related/` subdirectory inside artifact folder
- [ ] Only create if `linked_artifacts` field is non-empty
- [ ] For each artifact ID in `linked_artifacts`:
  - [ ] Resolve target path from `nodes` dict using `canonical_path`
  - [ ] Create symlink with target folder name: `(ARTIFACT-ID)-Title`
  - [ ] Use relative path from `_Related/` to target folder
- [ ] Skip if target ID not in nodes (broken reference)
- [ ] Skip if target ID equals current artifact (self-reference)

### _Depends-On/ Directory
- [ ] Create `_Depends-On/` subdirectory inside artifact folder
- [ ] Only create if `depends_on_artifacts` field is non-empty
- [ ] For each artifact ID in `depends_on_artifacts`:
  - [ ] Same symlink logic as `_Related/`
- [ ] Skip if target ID not in nodes
- [ ] Skip if target ID equals current artifact

### Symlink Properties
- [ ] Use `os.path.relpath()` for relative targets
- [ ] Target is the artifact's folder (canonical_path), not the .md file
- [ ] Symlink name matches target folder name exactly
- [ ] Handle existing symlinks: skip if correct, replace if stale (SPEC-250)

## Implementation Notes

**Location:** `skills/swain-design/scripts/specgraph/materialize.py`

**New helper function:**
```python
def _materialize_relationship_dir(
    parent_path: Path,
    repo_root: Path,
    dir_name: str,
    artifact_ids: list[str],
    nodes: dict,
    current_artifact_id: str,
) -> set[str]:
    """Create relationship directory symlinks and return created names."""
    if not artifact_ids:
        return set()
    
    rel_dir = parent_path / dir_name
    rel_dir.mkdir(parents=True, exist_ok=True)
    
    created_names: set[str] = set()
    for aid in artifact_ids:
        if aid not in nodes:
            continue  # skip broken reference
        if aid == current_artifact_id:
            continue  # skip self-reference
        
        target_path = repo_root / nodes[aid]["canonical_path"]
        link_name = target_path.name
        link_path = rel_dir / link_name
        
        # Skip if already correct
        if link_path.is_symlink() and link_path.resolve() == target_path.resolve():
            created_names.add(link_name)
            continue
        
        # Remove stale/broken link
        if link_path.is_symlink():
            link_path.unlink()
        elif link_path.exists():
            raise FileExistsError(f"Cannot create link at {link_path}")
        
        relative_target = os.path.relpath(target_path, start=rel_dir)
        link_path.symlink_to(relative_target)
        created_names.add(link_name)
    
    return created_names
```

**Integration into `materialize_children()`:**
```python
def materialize_children(repo_root: Path, projection: list[dict]) -> None:
    paths = {item["artifact"]: item["canonical_path"] for item in projection}
    nodes = {item["artifact"]: item for item in projection}
    
    # ... existing hierarchy logic ...
    
    # NEW: materialize relationship directories
    for item in projection:
        artifact_id = item["artifact"]
        artifact_path = repo_root / item["canonical_path"]
        
        if item.get("linked_artifacts"):
            _materialize_relationship_dir(
                artifact_path, repo_root, "_Related",
                item["linked_artifacts"], nodes, artifact_id
            )
        
        if item.get("depends_on_artifacts"):
            _materialize_relationship_dir(
                artifact_path, repo_root, "_Depends-On",
                item["depends_on_artifacts"], nodes, artifact_id
            )
```

## Edge Cases
- Empty `linked_artifacts`: no `_Related/` directory created
- Empty `depends_on_artifacts`: no `_Depends-On/` directory created
- Mix of valid and broken refs: valid ones processed, broken skips logged
- Target artifact in different lifecycle: symlink still works (path-based)

## Test Plan
- [ ] Artifact with `linked_artifacts`: `_Related/` created with correct symlinks
- [ ] Artifact with `depends_on_artifacts`: `_Depends-On/` created
- [ ] Artifact with both: both directories created
- [ ] Artifact with empty fields: no directories created
- [ ] Broken reference: skipped without error
- [ ] Self-reference: skipped without error
- [ ] Symlink targets correct artifact folder
- [ ] Relative paths resolve correctly
- [ ] Multiple artifacts linked: all appear in directory

## Dependencies
- SPEC-248 (projection schema extension)

## Linked Design Intent
From DESIGN-016:
- **Goal**: Materialize all graph edges
- **Constraint**: Atomic processing, IDs from projection
- **Guarantee**: Skip broken refs, skip self-refs