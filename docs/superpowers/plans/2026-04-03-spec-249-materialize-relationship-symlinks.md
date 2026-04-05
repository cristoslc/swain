# SPEC-249: Materialize Related Artifacts Symlinks

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create `_Related/` and `_Depends-On/` symlink directories inside artifact folders based on new projection fields.

**Architecture:** Add `_materialize_relationship_dir()` helper that creates relationship symlinks. Called from `materialize_children()` after hierarchy symlinks.

**Tech Stack:** Python 3.11, pytest, existing materialize infrastructure

---

## File Structure

- Modify: `skills/swain-design/scripts/specgraph/materialize.py` (add relationship symlinks)
- Test: `skills/swain-design/scripts/tests/test_materialize_hierarchy.py` (add relationship tests)

---

## Task 1: Write failing tests for relationship symlinks

**Files:**
- Modify: `skills/swain-design/scripts/tests/test_materialize_hierarchy.py`

- [ ] **Step 1: Write test for _Related/ symlinks**

```python
def test_materialize_creates_related_symlinks(tmp_path):
    """_Related/ directory created for linked_artifacts."""
    repo_root = tmp_path
    epic_dir = repo_root / "docs" / "epic" / "Active" / "(EPIC-001)-Work"
    design_dir = repo_root / "docs" / "design" / "Active" / "(DESIGN-001)-Arch"
    for path in (epic_dir, design_dir):
        path.mkdir(parents=True)
        (path / "placeholder.md").write_text("# placeholder\n", encoding="utf-8")
    
    projection = [
        {
            "artifact": "EPIC-001",
            "type": "EPIC",
            "status": "Active",
            "canonical_file": "docs/epic/Active/(EPIC-001)-Work/(EPIC-001)-Work.md",
            "canonical_path": "docs/epic/Active/(EPIC-001)-Work",
            "direct_parent": None,
            "placement_state": "unparented",
            "linked_artifacts": ["DESIGN-001"],
            "depends_on_artifacts": [],
        },
        {
            "artifact": "DESIGN-001",
            "type": "DESIGN",
            "status": "Active",
            "canonical_file": "docs/design/Active/(DESIGN-001)-Arch/(DESIGN-001)-Arch.md",
            "canonical_path": "docs/design/Active/(DESIGN-001)-Arch",
            "direct_parent": None,
            "placement_state": "unparented",
            "linked_artifacts": [],
            "depends_on_artifacts": [],
        },
    ]
    
    materialize_children(repo_root, projection)
    
    related_link = epic_dir / "_Related" / "(DESIGN-001)-Arch"
    assert related_link.is_symlink()
    assert related_link.resolve() == design_dir.resolve()
```

- [ ] **Step 2: Write test for _Depends-On/ symlinks**

```python
def test_materialize_creates_depends_on_symlinks(tmp_path):
    """_Depends-On/ directory created for depends_on_artifacts."""
    repo_root = tmp_path
    spec1_dir = repo_root / "docs" / "spec" / "Proposed" / "(SPEC-001)-First"
    spec2_dir = repo_root / "docs" / "spec" / "Complete" / "(SPEC-002)-Second"
    for path in (spec1_dir, spec2_dir):
        path.mkdir(parents=True)
        (path / "placeholder.md").write_text("# placeholder\n", encoding="utf-8")
    
    projection = [
        {
            "artifact": "SPEC-001",
            "type": "SPEC",
            "status": "Proposed",
            "canonical_file": "docs/spec/Proposed/(SPEC-001)-First/(SPEC-001)-First.md",
            "canonical_path": "docs/spec/Proposed/(SPEC-001)-First",
            "direct_parent": None,
            "placement_state": "unparented",
            "linked_artifacts": [],
            "depends_on_artifacts": ["SPEC-002"],
        },
        {
            "artifact": "SPEC-002",
            "type": "SPEC",
            "status": "Complete",
            "canonical_file": "docs/spec/Complete/(SPEC-002)-Second/(SPEC-002)-Second.md",
            "canonical_path": "docs/spec/Complete/(SPEC-002)-Second",
            "direct_parent": None,
            "placement_state": "unparented",
            "linked_artifacts": [],
            "depends_on_artifacts": [],
        },
    ]
    
    materialize_children(repo_root, projection)
    
    depends_link = spec1_dir / "_Depends-On" / "(SPEC-002)-Second"
    assert depends_link.is_symlink()
    assert depends_link.resolve() == spec2_dir.resolve()
```

- [ ] **Step 3: Write test for empty relationships (no directory)**

```python
def test_materialize_skips_empty_relationship_dirs(tmp_path):
    """No _Related/ or _Depends-On/ created when empty."""
    repo_root = tmp_path
    spec_dir = repo_root / "docs" / "spec" / "Proposed" / "(SPEC-003)-Solo"
    spec_dir.mkdir(parents=True)
    (spec_dir / "placeholder.md").write_text("# placeholder\n", encoding="utf-8")
    
    projection = [
        {
            "artifact": "SPEC-003",
            "type": "SPEC",
            "status": "Proposed",
            "canonical_file": "docs/spec/Proposed/(SPEC-003)-Solo/(SPEC-003)-Solo.md",
            "canonical_path": "docs/spec/Proposed/(SPEC-003)-Solo",
            "direct_parent": None,
            "placement_state": "unparented",
            "linked_artifacts": [],
            "depends_on_artifacts": [],
        },
    ]
    
    materialize_children(repo_root, projection)
    
    assert not (spec_dir / "_Related").exists()
    assert not (spec_dir / "_Depends-On").exists()
```

- [ ] **Step 4: Write test for broken reference skip**

```python
def test_materialize_skips_broken_references(tmp_path):
    """Broken references are skipped gracefully."""
    repo_root = tmp_path
    spec_dir = repo_root / "docs" / "spec" / "Proposed" / "(SPEC-004)-Broken"
    spec_dir.mkdir(parents=True)
    (spec_dir / "placeholder.md").write_text("# placeholder\n", encoding="utf-8")
    
    projection = [
        {
            "artifact": "SPEC-004",
            "type": "SPEC",
            "status": "Proposed",
            "canonical_file": "docs/spec/Proposed/(SPEC-004)-Broken/(SPEC-004)-Broken.md",
            "canonical_path": "docs/spec/Proposed/(SPEC-004)-Broken",
            "direct_parent": None,
            "placement_state": "unparented",
            "linked_artifacts": ["MISSING-001"],  # Target doesn't exist
            "depends_on_artifacts": [],
        },
    ]
    
    materialize_children(repo_root, projection)  # Should not raise
    
    # No _Related/ created because no valid targets
    assert not (spec_dir / "_Related").exists()
```

- [ ] **Step 5: Run tests to confirm they fail**

```bash
cd /Users/cristos/Documents/code/swain
python3 -m pytest skills/swain-design/scripts/tests/test_materialize_hierarchy.py::test_materialize_creates_related_symlinks -xvs
python3 -m pytest skills/swain-design/scripts/tests/test_materialize_hierarchy.py::test_materialize_creates_depends_on_symlinks -xvs
python3 -m pytest skills/swain-design/scripts/tests/test_materialize_hierarchy.py::test_materialize_skips_empty_relationship_dirs -xvs
python3 -m pytest skills/swain-design/scripts/tests/test_materialize_hierarchy.py::test_materialize_skips_broken_references -xvs
```

---

## Task 2: Implement relationship symlink creation

**Files:**
- Modify: `skills/swain-design/scripts/specgraph/materialize.py`

- [ ] **Step 1: Add _materialize_relationship_dir() helper**

Add this function after `_remove_stale_symlinks()`:

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

- [ ] **Step 2: Integrate into materialize_children()**

Add a nodes dict and relationship processing to `materialize_children()`:

```python
def materialize_children(repo_root: Path, projection: list[dict]) -> None:
    paths = {item["artifact"]: item["canonical_path"] for item in projection}
    nodes = {item["artifact"]: item for item in projection}  # NEW: for lookups
    
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

- [ ] **Step 3: Run tests to confirm they pass**

```bash
python3 -m pytest skills/swain-design/scripts/tests/test_materialize_hierarchy.py -xvs
```

---

## Task 3: Run full test suite

- [ ] **Step 1: Run all materialize tests**

```bash
python3 -m pytest skills/swain-design/scripts/tests/test_materialize_hierarchy.py -v
```

- [ ] **Step 2: Run specgraph tests**

```bash
python3 -m pytest skills/swain-design/scripts/specgraph/tests/ -v
```

---

## Task 4: Test integration with chart build

- [ ] **Step 1: Rebuild chart**

```bash
cd /Users/cristos/Documents/code/swain
bash skills/swain-design/scripts/chart.sh build
```

- [ ] **Step 2: Verify symlinks created**

```bash
ls -la docs/epic/Proposed/EPIC-058-Related-Artifacts-Symlink-Materialization/_Related/
```

---

## Task 5: Commit SPEC-249

- [ ] **Step 1: Stage changes**

```bash
git add skills/swain-design/scripts/specgraph/materialize.py
git add skills/swain-design/scripts/tests/test_materialize_hierarchy.py
```

- [ ] **Step 2: Commit**

```bash
git commit -m "feat(chart): materialize _Related and _Depends-On symlinks (SPEC-249)

Add relationship symlink directories to artifact folders:
- _Related/ for linked-artifacts and artifact-refs edges
- _Depends-On/ for depends-on-artifacts edges

Skips broken references and self-references. Only creates
directories when non-empty.

💘 Generated with Crush

Assisted-by: GLM 5 (Reasoning & Agentic) via Crush <crush@charm.land>"
```