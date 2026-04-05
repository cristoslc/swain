---
title: "Cleanup Stale Relationship Symlinks"
artifact: SPEC-250
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
  - SPEC-249
swain-do: required
---

# Cleanup Stale Relationship Symlinks

## Context
When artifacts remove relationship links from frontmatter, the corresponding symlinks in `_Related/` and `_Depends-On/` must be cleaned up during the next `chart build` to avoid stale references.

## Acceptance Criteria

### Stale Symlink Detection
- [ ] Symlink is stale if its target is not in current `linked_artifacts` or `depends_on_artifacts`
- [ ] Only remove symlinks from relationship directories (preserve direct children)
- [ ] Preserve `README.md` files in relationship directories

### Cleanup Logic
- [ ] After creating new symlinks, scan relationship directories for stale entries
- [ ] Remove symlink if its name not in desired set for that directory
- [ ] Only remove symlinks (via `is_symlink()` check), never directories or files
- [ ] Handle empty directories: remove `_Related/` or `_Depends-On/` if empty after cleanup

### Reconciliation Safety
- [ ] Never remove operator-created files (symlink check)
- [ ] Never remove README.md from relationship directories
- [ ] Log removals for debugging

## Implementation Notes

**Location:** `skills/swain-design/scripts/specgraph/materialize.py`

**Cleanup helper:**
```python
def _cleanup_stale_links(rel_dir: Path, desired_names: set[str]) -> None:
    """Remove symlinks not in desired_names set."""
    if not rel_dir.exists():
        return
    
    for entry in rel_dir.iterdir():
        if entry.name == "README.md":
            continue
        if entry.is_symlink() and entry.name not in desired_names:
            entry.unlink()
    
    # Remove directory if empty (except README)
    remaining = [e for e in rel_dir.iterdir() if e.name != "README.md"]
    if not remaining and not any(rel_dir.glob("README.md")):
        rel_dir.rmdir()
```

**Integration into `materialize_children()`:**
```python
def materialize_children(repo_root: Path, projection: list[dict]) -> None:
    # ... existing logic ...
    
    for item in projection:
        artifact_id = item["artifact"]
        artifact_path = repo_root / item["canonical_path"]
        
        # Process linked_artifacts
        if item.get("linked_artifacts"):
            created = _materialize_relationship_dir(
                artifact_path, repo_root, "_Related",
                item["linked_artifacts"], nodes, artifact_id
            )
            _cleanup_stale_links(artifact_path / "_Related", created)
        else:
            # No linked artifacts - cleanup entire _Related dir
            _cleanup_stale_links(artifact_path / "_Related", set())
        
        # Process depends_on_artifacts
        if item.get("depends_on_artifacts"):
            created = _materialize_relationship_dir(
                artifact_path, repo_root, "_Depends-On",
                item["depends_on_artifacts"], nodes, artifact_id
            )
            _cleanup_stale_links(artifact_path / "_Depends-On", created)
        else:
            _cleanup_stale_links(artifact_path / "_Depends-On", set())
```

**Alternative: unified cleanup pass (end of function):**
```python
# After all materialization, scan all artifacts for stale relationship links
for item in projection:
    artifact_path = repo_root / item["canonical_path"]
    
    # Determine desired names for each relationship dir
    linked_set = set()
    for aid in item.get("linked_artifacts", []):
        if aid in nodes:
            linked_set.add(Path(nodes[aid]["canonical_path"]).name)
    
    depends_set = set()
    for aid in item.get("depends_on_artifacts", []):
        if aid in nodes:
            depends_set.add(Path(nodes[aid]["canonical_path"]).name)
    
    _cleanup_stale_links(artifact_path / "_Related", linked_set)
    _cleanup_stale_links(artifact_path / "_Depends-On", depends_set)
```

## Test Plan
- [ ] Link removed from frontmatter: symlink removed on rebuild
- [ ] All links removed: entire `_Related/` directory removed
- [ ] Depends-on removed: symlink removed from `_Depends-On/`
- [ ] README.md preserved in relationship directory
- [ ] Operator-created file in `_Related/`: preserved (not a symlink)
- [ ] Empty directory after cleanup: directory removed
- [ ] Stale symlink points to non-existent target: still removed

## Dependencies
- SPEC-249 (relationship symlink creation)

## Linked Design Intent
From DESIGN-016:
- **Goal**: Materialize all graph edges
- **Guarantee**: Stale symlinks removed on rebuild
- **Safety**: Never remove operator-managed content