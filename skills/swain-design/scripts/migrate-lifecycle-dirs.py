#!/usr/bin/env python3
"""SPEC-020: Migrate existing artifacts to new phase directories.

Maps old phase subdirectory names to the normalized three-track lifecycle
from ADR-003. Updates frontmatter status fields and uses `git mv` to
preserve history.

Usage:
    uv run python3 migrate-lifecycle-dirs.py [--dry-run]
"""
import glob
import os
import re
import subprocess
import sys

DRY_RUN = "--dry-run" in sys.argv

# Phase directory mapping: old_dir -> new_dir
# Only entries where old != new need moving
DIR_MAPPING = {
    "Draft": "Proposed",
    "Planned": "Proposed",
    "Review": "Proposed",
    "Approved": "Ready",
    "Testing": "NeedsManualTest",
    "Implemented": "Complete",
    "Adopted": "Active",
    "Validated": "Active",
    "Deprecated": "Retired",
    "Archived": "Retired",
    "Sunset": "Retired",
    # These stay the same (no move needed):
    # "Proposed": "Proposed",
    # "Ready": "Ready",
    # "Active": "Active",
    # "In Progress": "InProgress",
    # "NeedsManualTest": "NeedsManualTest",
    # "Complete": "Complete",
    # "Retired": "Retired",
    # "Superseded": "Superseded",
    # "Abandoned": "Abandoned",
}

# Status field mapping: old_status -> new_status
STATUS_MAPPING = {
    "Draft": "Proposed",
    "Planned": "Proposed",
    "Review": "Proposed",
    "Approved": "Ready",
    "Testing": "Needs Manual Test",
    "Implemented": "Complete",
    "Adopted": "Active",
    "Validated": "Active",
    "Deprecated": "Retired",
    "Archived": "Retired",
    "Sunset": "Retired",
}


def git_mv(src, dst):
    """Move a file/directory using git mv."""
    if DRY_RUN:
        print(f"  [dry-run] git mv {src} -> {dst}")
        return True
    result = subprocess.run(
        ["git", "mv", src, dst],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  ERROR: git mv failed: {result.stderr.strip()}")
        return False
    return True


def update_status_in_file(filepath, old_status, new_status):
    """Update the status field in frontmatter."""
    with open(filepath, "r") as f:
        text = f.read()

    # Match status field in frontmatter
    pattern = re.compile(r'^(status:\s*)' + re.escape(old_status) + r'\s*$', re.MULTILINE)
    if not pattern.search(text):
        return False

    new_text = pattern.sub(r'\g<1>' + new_status, text)
    if new_text == text:
        return False

    if DRY_RUN:
        print(f"  [dry-run] Update status: {old_status} -> {new_status} in {filepath}")
        return True

    with open(filepath, "w") as f:
        f.write(new_text)
    return True


def find_artifact_files(directory):
    """Find all .md files in a directory (recursively for artifact dirs)."""
    results = []
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith(".md") and not f.startswith("list-"):
                results.append(os.path.join(root, f))
    return results


def get_frontmatter_status(filepath):
    """Read the status field from a file's frontmatter."""
    try:
        with open(filepath, "r") as f:
            text = f.read()
    except FileNotFoundError:
        return None
    m = re.search(r'^status:\s*(.+?)\s*$', text, re.MULTILINE)
    return m.group(1) if m else None


def migrate_phase_dir(type_dir, old_phase_dir, new_phase_name, old_status, new_status):
    """Migrate all artifacts from an old phase directory to a new one.

    Handles both flat-file types (ADR) and directory-per-artifact types (SPEC, EPIC, etc.).
    For artifacts whose frontmatter status already matches the target (e.g., already Complete),
    they are moved to the correct new directory without status change.
    """
    old_path = os.path.join(type_dir, old_phase_dir)
    new_path = os.path.join(type_dir, new_phase_name)

    if not os.path.isdir(old_path):
        return 0

    # Create target directory if needed
    if not DRY_RUN:
        os.makedirs(new_path, exist_ok=True)
    else:
        if not os.path.isdir(new_path):
            print(f"  [dry-run] mkdir -p {new_path}")

    entries = sorted(os.listdir(old_path))
    moved = 0

    for entry in entries:
        src = os.path.join(old_path, entry)
        if entry.startswith("list-") or entry.startswith("."):
            continue

        # Determine if this is a file or directory artifact
        if os.path.isdir(src):
            # Directory-per-artifact: check frontmatter status
            md_files = glob.glob(os.path.join(src, "*.md"))
            actual_status = None
            main_md = None
            for mf in md_files:
                s = get_frontmatter_status(mf)
                if s:
                    actual_status = s
                    main_md = mf
                    break

            # If artifact's status already matches a DIFFERENT target (e.g., Complete
            # while dir is Draft), route it to the correct directory instead
            if actual_status and actual_status != old_status:
                # Find the right target for this artifact's actual status
                actual_target_dir = STATUS_MAPPING.get(actual_status)
                if actual_target_dir is None:
                    # Status is already in new format — use it directly as dir name
                    actual_target_dir = actual_status.replace(" ", "")
                    # Map "Needs Manual Test" -> "NeedsManualTest"
                else:
                    actual_target_dir = actual_target_dir.replace(" ", "")

                actual_target_path = os.path.join(type_dir, actual_target_dir)
                if not DRY_RUN:
                    os.makedirs(actual_target_path, exist_ok=True)
                else:
                    print(f"  [dry-run] mkdir -p {actual_target_path}")

                dst = os.path.join(actual_target_path, entry)
                print(f"  Move (status override): {src} -> {dst}")
                if git_mv(src, dst):
                    moved += 1
                continue

            dst = os.path.join(new_path, entry)
            print(f"  Move: {src} -> {dst}")
            if git_mv(src, dst):
                moved += 1
                # Update status in the moved file
                if main_md:
                    new_md_path = os.path.join(new_path, entry, os.path.basename(main_md))
                    if not DRY_RUN and os.path.exists(new_md_path):
                        update_status_in_file(new_md_path, old_status, new_status)
                    elif DRY_RUN:
                        print(f"  [dry-run] Update status: {old_status} -> {new_status} in {new_md_path}")

        elif os.path.isfile(src) and entry.endswith(".md"):
            # Flat-file artifact (e.g., ADR)
            actual_status = get_frontmatter_status(src)

            dst = os.path.join(new_path, entry)
            print(f"  Move: {src} -> {dst}")
            if git_mv(src, dst):
                moved += 1
                # Update status
                new_file = os.path.join(new_path, entry)
                if not DRY_RUN and os.path.exists(new_file):
                    update_status_in_file(new_file, old_status, new_status)
                elif DRY_RUN:
                    print(f"  [dry-run] Update status: {old_status} -> {new_status} in {new_file}")

    return moved


def remove_empty_dirs(base_dir):
    """Remove empty phase subdirectories."""
    for entry in os.listdir(base_dir):
        path = os.path.join(base_dir, entry)
        if os.path.isdir(path) and entry not in (".", ".."):
            try:
                contents = [x for x in os.listdir(path) if not x.startswith(".")]
                if not contents:
                    if DRY_RUN:
                        print(f"  [dry-run] rmdir {path}")
                    else:
                        os.rmdir(path)
                        print(f"  Removed empty dir: {path}")
            except OSError:
                pass


def main():
    print("SPEC-020: Migrate artifacts to normalized phase directories")
    print(f"ADR-003 three-track lifecycle normalization\n")
    if DRY_RUN:
        print("DRY RUN — no files modified\n")

    total_moved = 0

    # Define all type directories and their phase migrations
    migrations = [
        # (type_dir, old_phase_dir, new_phase_dir, old_status, new_status)
        ("docs/adr",      "Adopted",     "Active",    "Adopted",     "Active"),
        ("docs/journey",  "Validated",   "Active",    "Validated",   "Active"),
        ("docs/persona",  "Validated",   "Active",    "Validated",   "Active"),
        ("docs/research", "Planned",     "Proposed",  "Planned",     "Proposed"),
        ("docs/spec",     "Draft",       "Proposed",  "Draft",       "Proposed"),
        ("docs/spec",     "Approved",    "Ready",     "Approved",    "Ready"),
        ("docs/spec",     "Implemented", "Complete",  "Implemented", "Complete"),
    ]

    for type_dir, old_phase, new_phase, old_status, new_status in migrations:
        if old_phase == new_phase:
            continue
        old_path = os.path.join(type_dir, old_phase)
        if not os.path.isdir(old_path):
            continue

        entries = [e for e in os.listdir(old_path)
                   if not e.startswith("list-") and not e.startswith(".")]
        if not entries:
            continue

        print(f"\n--- {type_dir}: {old_phase}/ -> {new_phase}/ ({len(entries)} items) ---")
        count = migrate_phase_dir(type_dir, old_phase, new_phase, old_status, new_status)
        total_moved += count

    # Clean up empty old directories
    print("\n--- Cleanup empty directories ---")
    for type_dir in ["docs/adr", "docs/journey", "docs/persona", "docs/research",
                     "docs/spec", "docs/epic", "docs/vision"]:
        if os.path.isdir(type_dir):
            remove_empty_dirs(type_dir)

    print(f"\n{total_moved} artifact(s) {'would be ' if DRY_RUN else ''}moved.")


if __name__ == "__main__":
    main()
