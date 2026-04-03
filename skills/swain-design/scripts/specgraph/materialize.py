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


def materialize_children(repo_root: Path, projection: list[dict]) -> None:
    """Create direct-child symlinks for placed projection records.

    This minimal pass creates child folder links only. Cleanup and
    `_unparented` handling are added in follow-on tasks.
    """
    paths = {item["artifact"]: item["canonical_path"] for item in projection}

    desired_children: dict[Path, set[str]] = {}
    desired_unparented: dict[Path, set[str]] = {}

    for item in projection:
        parent_id = item.get("direct_parent")
        placement_state = item.get("placement_state")
        if placement_state == "placed" and parent_id in paths:
            parent_path = repo_root / paths[parent_id]
            child_path = repo_root / item["canonical_path"]
            desired_children.setdefault(parent_path, set()).add(child_path.name)

            parent_path.mkdir(parents=True, exist_ok=True)
            _ensure_link(parent_path, child_path)
            continue

        if placement_state != "unparented" and not (placement_state == "placed" and parent_id not in paths):
            continue

        artifact_type = item["type"].lower()
        surface = repo_root / "docs" / artifact_type / "_unparented"
        surface.mkdir(parents=True, exist_ok=True)
        _write_unparented_readme(surface, item["type"])
        child_path = repo_root / item["canonical_path"]
        desired_unparented.setdefault(surface, set()).add(child_path.name)
        _ensure_link(surface, child_path)

    for parent_path, desired_names in desired_children.items():
        _remove_stale_symlinks(parent_path, desired_names)

    for surface, desired_names in desired_unparented.items():
        _remove_stale_symlinks(surface, desired_names)
