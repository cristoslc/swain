"""Materialize hierarchy child views from projection records."""

from __future__ import annotations

import os
from pathlib import Path


def _ensure_link(parent_path: Path, child_path: Path) -> None:
    link_path = parent_path / child_path.name
    if link_path.exists() or link_path.is_symlink():
        if link_path.is_symlink() and link_path.resolve() == child_path.resolve():
            return
        if link_path.is_symlink():
            link_path.unlink()
        else:
            raise FileExistsError(f"Cannot create child link at {link_path}")

    relative_target = os.path.relpath(child_path, start=parent_path)
    link_path.symlink_to(relative_target)


def _write_unparented_readme(surface: Path, artifact_type: str) -> None:
    readme = surface / "README.md"
    if readme.exists():
        return
    readme.write_text(
        f"# {artifact_type} _unparented\n\n"
        "This directory is a repair surface, not a lifecycle state.\n"
        "Artifacts appear here when chart cannot place them under a valid parent.\n"
        "They leave this directory automatically after parent links are fixed.\n",
        encoding="utf-8",
    )


def _remove_stale_symlinks(parent_path: Path, desired_names: set[str]) -> None:
    if not parent_path.exists():
        return
    for entry in parent_path.iterdir():
        if entry.name == "README.md":
            continue
        if entry.is_symlink() and entry.name not in desired_names:
            entry.unlink()


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

    # Artifact directory must already exist (ADR-027: materializer must not
    # create artifact directories; doctor handles flat-file migration).
    if not parent_path.is_dir():
        return set()

    # Filter to valid targets first
    valid_targets = []
    for aid in artifact_ids:
        if aid not in nodes:
            continue  # skip broken reference
        if aid == current_artifact_id:
            continue  # skip self-reference
        valid_targets.append(aid)

    if not valid_targets:
        return set()

    rel_dir = parent_path / dir_name
    rel_dir.mkdir(exist_ok=True)
    
    created_names: set[str] = set()
    for aid in valid_targets:
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


def materialize_children(repo_root: Path, projection: list[dict]) -> list[str]:
    """Create direct-child symlinks for placed projection records.

    Returns a list of artifact IDs that were skipped because their
    canonical path (or parent path) is not a directory.  Callers
    should surface these so the operator knows to run doctor.
    """
    paths = {item["artifact"]: item["canonical_path"] for item in projection}
    nodes = {item["artifact"]: item for item in projection}

    desired_children: dict[Path, set[str]] = {}
    desired_unparented: dict[Path, set[str]] = {}
    skipped_flat: list[str] = []

    for item in projection:
        parent_id = item.get("direct_parent")
        placement_state = item.get("placement_state")
        artifact_path = repo_root / item["canonical_path"]

        # Standalone artifacts (e.g. RETROs) skip hierarchy but get relationships
        if placement_state == "standalone":
            has_rels = item.get("linked_artifacts") or item.get("depends_on_artifacts")
            if has_rels and not artifact_path.is_dir():
                skipped_flat.append(item["artifact"])
            else:
                if item.get("linked_artifacts"):
                    _materialize_relationship_dir(
                        artifact_path, repo_root, "_Related",
                        item["linked_artifacts"], nodes, item["artifact"]
                    )
                if item.get("depends_on_artifacts"):
                    _materialize_relationship_dir(
                        artifact_path, repo_root, "_Depends-On",
                        item["depends_on_artifacts"], nodes, item["artifact"]
                    )
            continue

        if placement_state == "placed" and parent_id in paths:
            parent_path = repo_root / paths[parent_id]
            if not parent_path.is_dir():
                skipped_flat.append(str(parent_id))
                continue
            child_path = artifact_path
            desired_children.setdefault(parent_path, set()).add(child_path.name)

            _ensure_link(parent_path, child_path)
            
            # Materialize relationship directories
            if item.get("linked_artifacts"):
                _materialize_relationship_dir(
                    artifact_path, repo_root, "_Related",
                    item["linked_artifacts"], nodes, item["artifact"]
                )
            
            if item.get("depends_on_artifacts"):
                _materialize_relationship_dir(
                    artifact_path, repo_root, "_Depends-On",
                    item["depends_on_artifacts"], nodes, item["artifact"]
                )
            continue

        if placement_state != "unparented" and not (placement_state == "placed" and parent_id not in paths):
            continue

        artifact_type = item["type"].lower()
        surface = repo_root / "docs" / artifact_type / "_unparented"
        surface.mkdir(parents=True, exist_ok=True)
        _write_unparented_readme(surface, item["type"])
        child_path = artifact_path
        desired_unparented.setdefault(surface, set()).add(child_path.name)
        _ensure_link(surface, child_path)
        
        # Materialize relationship directories for unparented artifacts too
        if item.get("linked_artifacts"):
            _materialize_relationship_dir(
                artifact_path, repo_root, "_Related",
                item["linked_artifacts"], nodes, item["artifact"]
            )
        
        if item.get("depends_on_artifacts"):
            _materialize_relationship_dir(
                artifact_path, repo_root, "_Depends-On",
                item["depends_on_artifacts"], nodes, item["artifact"]
            )

    for parent_path, desired_names in desired_children.items():
        _remove_stale_symlinks(parent_path, desired_names)

    for surface, desired_names in desired_unparented.items():
        _remove_stale_symlinks(surface, desired_names)

    # Deduplicate: a flat parent may be referenced by multiple children
    seen: set[str] = set()
    unique: list[str] = []
    for aid in skipped_flat:
        if aid not in seen:
            seen.add(aid)
            unique.append(aid)
    return unique
