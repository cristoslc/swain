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
        },
        {
            "artifact": "INITIATIVE-001",
            "type": "INITIATIVE",
            "status": "Active",
            "canonical_file": "docs/initiative/Active/(INITIATIVE-001)-Parent/(INITIATIVE-001)-Parent.md",
            "canonical_path": "docs/initiative/Active/(INITIATIVE-001)-Parent",
            "direct_parent": "VISION-001",
            "placement_state": "placed",
        },
        {
            "artifact": "EPIC-001",
            "type": "EPIC",
            "status": "Active",
            "canonical_file": "docs/epic/Active/(EPIC-001)-Work/(EPIC-001)-Work.md",
            "canonical_path": "docs/epic/Active/(EPIC-001)-Work",
            "direct_parent": "INITIATIVE-001",
            "placement_state": "placed",
        },
        {
            "artifact": "SPEC-001",
            "type": "SPEC",
            "status": "Proposed",
            "canonical_file": "docs/spec/Proposed/(SPEC-001)-Child/(SPEC-001)-Child.md",
            "canonical_path": "docs/spec/Proposed/(SPEC-001)-Child",
            "direct_parent": "EPIC-001",
            "placement_state": "placed",
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
        },
        {
            "artifact": "SPEC-001",
            "type": "SPEC",
            "status": "Proposed",
            "canonical_file": "docs/spec/Proposed/(SPEC-001)-Child/(SPEC-001)-Child.md",
            "canonical_path": "docs/spec/Proposed/(SPEC-001)-Child",
            "direct_parent": "INITIATIVE-001",
            "placement_state": "placed",
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
        },
        {
            "artifact": "INITIATIVE-002",
            "type": "INITIATIVE",
            "status": "Active",
            "canonical_file": "docs/initiative/Active/(INITIATIVE-002)-New/(INITIATIVE-002)-New.md",
            "canonical_path": "docs/initiative/Active/(INITIATIVE-002)-New",
            "direct_parent": "VISION-001",
            "placement_state": "placed",
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
        },
        {
            "artifact": "SPEC-001",
            "type": "SPEC",
            "status": "Active",
            "canonical_file": "docs/spec/Active/(SPEC-001)-Child/(SPEC-001)-Child.md",
            "canonical_path": "docs/spec/Active/(SPEC-001)-Child",
            "direct_parent": "INITIATIVE-001",
            "placement_state": "placed",
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
        },
        {
            "artifact": "INITIATIVE-001",
            "type": "INITIATIVE",
            "status": "Active",
            "canonical_file": "docs/initiative/Active/(INITIATIVE-001)-Parent/(INITIATIVE-001)-Parent.md",
            "canonical_path": "docs/initiative/Active/(INITIATIVE-001)-Parent",
            "direct_parent": "VISION-001",
            "placement_state": "placed",
        },
    ]

    try:
        materialize_children(repo_root, projection)
    except FileExistsError:
        return
    assert False, "Expected FileExistsError for real directory collision"
