"""Tests for hierarchy materialization."""

from __future__ import annotations

import os
import sys
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from specgraph.materialize import materialize_children


def test_materialize_creates_direct_child_symlinks(tmp_path):
    repo_root = tmp_path
    vision_dir = repo_root / "docs" / "vision" / "Active" / "(VISION-001)-Root"
    initiative_dir = repo_root / "docs" / "initiative" / "Active" / "(INITIATIVE-001)-Parent"
    epic_dir = repo_root / "docs" / "epic" / "Active" / "(EPIC-001)-Work"
    spec_dir = repo_root / "docs" / "spec" / "Proposed" / "(SPEC-001)-Child"
    for path in (vision_dir, initiative_dir, epic_dir, spec_dir):
        path.mkdir(parents=True)
        (path / "placeholder.md").write_text("# placeholder\n", encoding="utf-8")

    projection = [
        {
            "artifact": "VISION-001",
            "type": "VISION",
            "status": "Active",
            "canonical_file": "docs/vision/Active/(VISION-001)-Root/(VISION-001)-Root.md",
            "canonical_path": "docs/vision/Active/(VISION-001)-Root",
            "direct_parent": None,
            "placement_state": "root",
            "linked_artifacts": [],
            "depends_on_artifacts": [],
        },
        {
            "artifact": "INITIATIVE-001",
            "type": "INITIATIVE",
            "status": "Active",
            "canonical_file": "docs/initiative/Active/(INITIATIVE-001)-Parent/(INITIATIVE-001)-Parent.md",
            "canonical_path": "docs/initiative/Active/(INITIATIVE-001)-Parent",
            "direct_parent": "VISION-001",
            "placement_state": "placed",
            "linked_artifacts": [],
            "depends_on_artifacts": [],
        },
        {
            "artifact": "EPIC-001",
            "type": "EPIC",
            "status": "Active",
            "canonical_file": "docs/epic/Active/(EPIC-001)-Work/(EPIC-001)-Work.md",
            "canonical_path": "docs/epic/Active/(EPIC-001)-Work",
            "direct_parent": "INITIATIVE-001",
            "placement_state": "placed",
            "linked_artifacts": [],
            "depends_on_artifacts": [],
        },
        {
            "artifact": "SPEC-001",
            "type": "SPEC",
            "status": "Proposed",
            "canonical_file": "docs/spec/Proposed/(SPEC-001)-Child/(SPEC-001)-Child.md",
            "canonical_path": "docs/spec/Proposed/(SPEC-001)-Child",
            "direct_parent": "EPIC-001",
            "placement_state": "placed",
            "linked_artifacts": [],
            "depends_on_artifacts": [],
        },
    ]

    materialize_children(repo_root, projection)

    initiative_link = vision_dir / "(INITIATIVE-001)-Parent"
    epic_link = initiative_dir / "(EPIC-001)-Work"
    spec_link = epic_dir / "(SPEC-001)-Child"

    assert initiative_link.is_symlink()
    assert epic_link.is_symlink()
    assert spec_link.is_symlink()
    assert initiative_link.resolve() == initiative_dir.resolve()
    assert epic_link.resolve() == epic_dir.resolve()
    assert spec_link.resolve() == spec_dir.resolve()


def test_materialize_uses_relative_symlink_targets(tmp_path):
    repo_root = tmp_path
    parent_dir = repo_root / "docs" / "initiative" / "Active" / "(INITIATIVE-001)-Parent"
    child_dir = repo_root / "docs" / "spec" / "Proposed" / "(SPEC-001)-Child"
    parent_dir.mkdir(parents=True)
    child_dir.mkdir(parents=True)

    projection = [
        {
            "artifact": "INITIATIVE-001",
            "type": "INITIATIVE",
            "status": "Active",
            "canonical_file": "docs/initiative/Active/(INITIATIVE-001)-Parent/(INITIATIVE-001)-Parent.md",
            "canonical_path": "docs/initiative/Active/(INITIATIVE-001)-Parent",
            "direct_parent": None,
            "placement_state": "root",
            "linked_artifacts": [],
            "depends_on_artifacts": [],
        },
        {
            "artifact": "SPEC-001",
            "type": "SPEC",
            "status": "Proposed",
            "canonical_file": "docs/spec/Proposed/(SPEC-001)-Child/(SPEC-001)-Child.md",
            "canonical_path": "docs/spec/Proposed/(SPEC-001)-Child",
            "direct_parent": "INITIATIVE-001",
            "placement_state": "placed",
            "linked_artifacts": [],
            "depends_on_artifacts": [],
        },
    ]

    materialize_children(repo_root, projection)

    link = parent_dir / "(SPEC-001)-Child"
    assert link.is_symlink()
    target = os.readlink(link)
    assert not target.startswith("/")
    assert (parent_dir / target).resolve() == child_dir.resolve()


def test_materialize_writes_unparented_surface_and_readme(tmp_path):
    repo_root = tmp_path
    spec_dir = repo_root / "docs" / "spec" / "Proposed" / "(SPEC-001)-Lonely"
    spec_dir.mkdir(parents=True)
    (spec_dir / "(SPEC-001)-Lonely.md").write_text("# lonely\n", encoding="utf-8")

    projection = [
        {
            "artifact": "SPEC-001",
            "type": "SPEC",
            "status": "Proposed",
            "canonical_file": "docs/spec/Proposed/(SPEC-001)-Lonely/(SPEC-001)-Lonely.md",
            "canonical_path": "docs/spec/Proposed/(SPEC-001)-Lonely",
            "direct_parent": None,
            "placement_state": "unparented",
            "linked_artifacts": [],
            "depends_on_artifacts": [],
        },
    ]

    materialize_children(repo_root, projection)

    surface = repo_root / "docs" / "spec" / "_unparented"
    readme = surface / "README.md"
    link = surface / "(SPEC-001)-Lonely"

    assert readme.exists()
    assert "not a lifecycle state" in readme.read_text(encoding="utf-8")
    assert link.is_symlink()
    assert link.resolve() == spec_dir.resolve()


def test_materialize_falls_back_to_unparented_when_parent_is_missing(tmp_path):
    repo_root = tmp_path
    spec_dir = repo_root / "docs" / "spec" / "Proposed" / "(SPEC-001)-Dangling"
    spec_dir.mkdir(parents=True)
    (spec_dir / "(SPEC-001)-Dangling.md").write_text("# dangling\n", encoding="utf-8")

    projection = [
        {
            "artifact": "SPEC-001",
            "type": "SPEC",
            "status": "Proposed",
            "canonical_file": "docs/spec/Proposed/(SPEC-001)-Dangling/(SPEC-001)-Dangling.md",
            "canonical_path": "docs/spec/Proposed/(SPEC-001)-Dangling",
            "direct_parent": "EPIC-999",
            "placement_state": "placed",
            "linked_artifacts": [],
            "depends_on_artifacts": [],
        },
    ]

    materialize_children(repo_root, projection)

    surface = repo_root / "docs" / "spec" / "_unparented"
    link = surface / "(SPEC-001)-Dangling"

    assert (surface / "README.md").exists()
    assert link.is_symlink()
    assert link.resolve() == spec_dir.resolve()


def test_materialize_removes_stale_child_symlinks(tmp_path):
    repo_root = tmp_path
    vision_dir = repo_root / "docs" / "vision" / "Active" / "(VISION-001)-Root"
    old_child_dir = repo_root / "docs" / "initiative" / "Active" / "(INITIATIVE-001)-Old"
    new_child_dir = repo_root / "docs" / "initiative" / "Active" / "(INITIATIVE-002)-New"
    for path in (vision_dir, old_child_dir, new_child_dir):
        path.mkdir(parents=True)

    stale_link = vision_dir / "(INITIATIVE-001)-Old"
    stale_link.symlink_to(os.path.relpath(old_child_dir, start=vision_dir))

    projection = [
        {
            "artifact": "VISION-001",
            "type": "VISION",
            "status": "Active",
            "canonical_file": "docs/vision/Active/(VISION-001)-Root/(VISION-001)-Root.md",
            "canonical_path": "docs/vision/Active/(VISION-001)-Root",
            "direct_parent": None,
            "placement_state": "root",
            "linked_artifacts": [],
            "depends_on_artifacts": [],
        },
        {
            "artifact": "INITIATIVE-002",
            "type": "INITIATIVE",
            "status": "Active",
            "canonical_file": "docs/initiative/Active/(INITIATIVE-002)-New/(INITIATIVE-002)-New.md",
            "canonical_path": "docs/initiative/Active/(INITIATIVE-002)-New",
            "direct_parent": "VISION-001",
            "placement_state": "placed",
            "linked_artifacts": [],
            "depends_on_artifacts": [],
        },
    ]

    materialize_children(repo_root, projection)

    assert not stale_link.exists()
    assert (vision_dir / "(INITIATIVE-002)-New").is_symlink()


def test_materialize_replaces_stale_child_symlink_targets(tmp_path):
    repo_root = tmp_path
    parent_dir = repo_root / "docs" / "initiative" / "Active" / "(INITIATIVE-001)-Parent"
    old_child_dir = repo_root / "docs" / "spec" / "Complete" / "(SPEC-001)-Child"
    new_child_dir = repo_root / "docs" / "spec" / "Active" / "(SPEC-001)-Child"
    for path in (parent_dir, old_child_dir, new_child_dir):
        path.mkdir(parents=True)

    stale_link = parent_dir / "(SPEC-001)-Child"
    stale_link.symlink_to(os.path.relpath(old_child_dir, start=parent_dir))

    projection = [
        {
            "artifact": "INITIATIVE-001",
            "type": "INITIATIVE",
            "status": "Active",
            "canonical_file": "docs/initiative/Active/(INITIATIVE-001)-Parent/(INITIATIVE-001)-Parent.md",
            "canonical_path": "docs/initiative/Active/(INITIATIVE-001)-Parent",
            "direct_parent": None,
            "placement_state": "root",
            "linked_artifacts": [],
            "depends_on_artifacts": [],
        },
        {
            "artifact": "SPEC-001",
            "type": "SPEC",
            "status": "Active",
            "canonical_file": "docs/spec/Active/(SPEC-001)-Child/(SPEC-001)-Child.md",
            "canonical_path": "docs/spec/Active/(SPEC-001)-Child",
            "direct_parent": "INITIATIVE-001",
            "placement_state": "placed",
            "linked_artifacts": [],
            "depends_on_artifacts": [],
        },
    ]

    materialize_children(repo_root, projection)

    assert stale_link.is_symlink()
    assert stale_link.resolve() == new_child_dir.resolve()


def test_materialize_raises_on_real_directory_collision(tmp_path):
    repo_root = tmp_path
    parent_dir = repo_root / "docs" / "vision" / "Active" / "(VISION-001)-Root"
    child_dir = repo_root / "docs" / "initiative" / "Active" / "(INITIATIVE-001)-Parent"
    parent_dir.mkdir(parents=True)
    child_dir.mkdir(parents=True)
    (parent_dir / "(INITIATIVE-001)-Parent").mkdir()

    projection = [
        {
            "artifact": "VISION-001",
            "type": "VISION",
            "status": "Active",
            "canonical_file": "docs/vision/Active/(VISION-001)-Root/(VISION-001)-Root.md",
            "canonical_path": "docs/vision/Active/(VISION-001)-Root",
            "direct_parent": None,
            "placement_state": "root",
            "linked_artifacts": [],
            "depends_on_artifacts": [],
        },
        {
            "artifact": "INITIATIVE-001",
            "type": "INITIATIVE",
            "status": "Active",
            "canonical_file": "docs/initiative/Active/(INITIATIVE-001)-Parent/(INITIATIVE-001)-Parent.md",
            "canonical_path": "docs/initiative/Active/(INITIATIVE-001)-Parent",
            "direct_parent": "VISION-001",
            "placement_state": "placed",
            "linked_artifacts": [],
            "depends_on_artifacts": [],
        },
    ]

    try:
        materialize_children(repo_root, projection)
    except FileExistsError:
        return
    assert False, "Expected FileExistsError for real directory collision"


def test_materialize_standalone_skips_hierarchy_creates_relationships(tmp_path):
    """Standalone artifacts (e.g. RETROs) get _Related but no _unparented surface."""
    repo_root = tmp_path
    retro_dir = repo_root / "docs" / "swain-retro" / "2026-01-01-test-retro"
    spec_dir = repo_root / "docs" / "spec" / "Complete" / "(SPEC-001)-Target"
    for path in (retro_dir, spec_dir):
        path.mkdir(parents=True)
        (path / "placeholder.md").write_text("# placeholder\n", encoding="utf-8")

    projection = [
        {
            "artifact": "RETRO-2026-01-01-test-retro",
            "type": "RETRO",
            "status": "Active",
            "canonical_file": "docs/swain-retro/2026-01-01-test-retro/2026-01-01-test-retro.md",
            "canonical_path": "docs/swain-retro/2026-01-01-test-retro",
            "direct_parent": None,
            "placement_state": "standalone",
            "linked_artifacts": ["SPEC-001"],
            "depends_on_artifacts": [],
        },
        {
            "artifact": "SPEC-001",
            "type": "SPEC",
            "status": "Complete",
            "canonical_file": "docs/spec/Complete/(SPEC-001)-Target/(SPEC-001)-Target.md",
            "canonical_path": "docs/spec/Complete/(SPEC-001)-Target",
            "direct_parent": None,
            "placement_state": "unparented",
            "linked_artifacts": [],
            "depends_on_artifacts": [],
        },
    ]

    materialize_children(repo_root, projection)

    # Relationship symlink created
    related_link = retro_dir / "_Related" / "(SPEC-001)-Target"
    assert related_link.is_symlink()
    assert related_link.resolve() == spec_dir.resolve()

    # No _unparented surface created for retro type
    assert not (repo_root / "docs" / "retro" / "_unparented").exists()


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


def test_materialize_creates_depends_on_symlinks(tmp_path):
    """_Depends-On/ directory created for depends_on_artifacts."""
    repo_root = tmp_path
    spec1_dir = repo_root / "docs" / "spec" / "Proposed" / "(SPEC-251)-First"
    spec2_dir = repo_root / "docs" / "spec" / "Complete" / "(SPEC-252)-Second"
    for path in (spec1_dir, spec2_dir):
        path.mkdir(parents=True)
        (path / "placeholder.md").write_text("# placeholder\n", encoding="utf-8")
    
    projection = [
        {
            "artifact": "SPEC-251",
            "type": "SPEC",
            "status": "Proposed",
            "canonical_file": "docs/spec/Proposed/(SPEC-251)-First/(SPEC-251)-First.md",
            "canonical_path": "docs/spec/Proposed/(SPEC-251)-First",
            "direct_parent": None,
            "placement_state": "unparented",
            "linked_artifacts": [],
            "depends_on_artifacts": ["SPEC-252"],
        },
        {
            "artifact": "SPEC-252",
            "type": "SPEC",
            "status": "Complete",
            "canonical_file": "docs/spec/Complete/(SPEC-252)-Second/(SPEC-252)-Second.md",
            "canonical_path": "docs/spec/Complete/(SPEC-252)-Second",
            "direct_parent": None,
            "placement_state": "unparented",
            "linked_artifacts": [],
            "depends_on_artifacts": [],
        },
    ]
    
    materialize_children(repo_root, projection)
    
    depends_link = spec1_dir / "_Depends-On" / "(SPEC-252)-Second"
    assert depends_link.is_symlink()
    assert depends_link.resolve() == spec2_dir.resolve()


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


def test_materialize_skips_broken_references(tmp_path):
    """Broken references are skipped gracefully."""
    repo_root = tmp_path
    spec_dir = repo_root / "docs" / "spec" / "Proposed" / "(SPEC-004)-Broken"
    spec_dir.mkdir(parents=True)
    (spec_dir / "placeholder.md").write_text("# placeholder\n", encoding="utf-8")
    
    projection = [
        {
            "artifact": "SPEC-254",
            "type": "SPEC",
            "status": "Proposed",
            "canonical_file": "docs/spec/Proposed/(SPEC-254)-Broken/(SPEC-254)-Broken.md",
            "canonical_path": "docs/spec/Proposed/(SPEC-254)-Broken",
            "direct_parent": None,
            "placement_state": "unparented",
            "linked_artifacts": ["MISSING-001"],  # Target doesn't exist
            "depends_on_artifacts": [],
        },
    ]
    
    materialize_children(repo_root, projection)  # Should not raise

    # No _Related/ created because no valid targets
    assert not (spec_dir / "_Related").exists()


def test_materialize_skips_flat_file_artifacts(tmp_path):
    """Flat-file artifacts (no directory) get no symlinks and no shadow dirs."""
    repo_root = tmp_path
    # Create a flat file ADR (no folder wrapping it)
    adr_phase = repo_root / "docs" / "adr" / "Active"
    adr_phase.mkdir(parents=True)
    (adr_phase / "(ADR-001)-Flat-Decision.md").write_text("# ADR\n", encoding="utf-8")

    target_dir = repo_root / "docs" / "spec" / "Active" / "(SPEC-001)-Target"
    target_dir.mkdir(parents=True)
    (target_dir / "(SPEC-001)-Target.md").write_text("# spec\n", encoding="utf-8")

    projection = [
        {
            "artifact": "ADR-001",
            "type": "ADR",
            "status": "Active",
            "canonical_file": "docs/adr/Active/(ADR-001)-Flat-Decision.md",
            "canonical_path": "docs/adr/Active/(ADR-001)-Flat-Decision",
            "direct_parent": None,
            "placement_state": "standalone",
            "linked_artifacts": ["SPEC-001"],
            "depends_on_artifacts": [],
        },
        {
            "artifact": "SPEC-001",
            "type": "SPEC",
            "status": "Active",
            "canonical_file": "docs/spec/Active/(SPEC-001)-Target/(SPEC-001)-Target.md",
            "canonical_path": "docs/spec/Active/(SPEC-001)-Target",
            "direct_parent": None,
            "placement_state": "unparented",
            "linked_artifacts": [],
            "depends_on_artifacts": [],
        },
    ]

    materialize_children(repo_root, projection)

    # No shadow directory created for the flat-file ADR
    shadow = repo_root / "docs" / "adr" / "Active" / "(ADR-001)-Flat-Decision"
    assert not shadow.exists(), "Materializer must not create directories for flat-file artifacts"

    # No _Related/ anywhere for the flat-file artifact
    assert not (shadow / "_Related").exists()


def test_materialize_skips_placed_child_when_parent_is_flat(tmp_path):
    """Placed children are skipped when the parent directory doesn't exist."""
    repo_root = tmp_path
    # Flat-file parent (no folder)
    parent_phase = repo_root / "docs" / "epic" / "Active"
    parent_phase.mkdir(parents=True)
    (parent_phase / "(EPIC-001)-Parent.md").write_text("# epic\n", encoding="utf-8")

    child_dir = repo_root / "docs" / "spec" / "Active" / "(SPEC-001)-Child"
    child_dir.mkdir(parents=True)
    (child_dir / "(SPEC-001)-Child.md").write_text("# spec\n", encoding="utf-8")

    projection = [
        {
            "artifact": "EPIC-001",
            "type": "EPIC",
            "status": "Active",
            "canonical_file": "docs/epic/Active/(EPIC-001)-Parent.md",
            "canonical_path": "docs/epic/Active/(EPIC-001)-Parent",
            "direct_parent": None,
            "placement_state": "unparented",
            "linked_artifacts": [],
            "depends_on_artifacts": [],
        },
        {
            "artifact": "SPEC-001",
            "type": "SPEC",
            "status": "Active",
            "canonical_file": "docs/spec/Active/(SPEC-001)-Child/(SPEC-001)-Child.md",
            "canonical_path": "docs/spec/Active/(SPEC-001)-Child",
            "direct_parent": "EPIC-001",
            "placement_state": "placed",
            "linked_artifacts": [],
            "depends_on_artifacts": [],
        },
    ]

    materialize_children(repo_root, projection)

    # No shadow directory created for the flat-file parent
    shadow = repo_root / "docs" / "epic" / "Active" / "(EPIC-001)-Parent"
    assert not shadow.exists(), "Materializer must not create directories for flat-file parents"
