#!/usr/bin/env python3
"""Fix cross-reference gaps: add body-referenced artifacts to linked-artifacts frontmatter."""

from __future__ import annotations

import subprocess
import re
import sys
from pathlib import Path
from typing import Optional

def parse_xref_output(output: str) -> dict[str, list[str]]:
    """Parse chart.sh xref output into {filepath: [missing_refs]}."""
    gaps: dict[str, list[str]] = {}
    current_file = None

    for line in output.splitlines():
        # Match artifact header: "ARTIFACT-NNN (path):"
        header = re.match(r'^(\S+-\d+)\s+\((.+?)\):', line)
        if header:
            current_file = header.group(2)
            if current_file not in gaps:
                gaps[current_file] = []
            continue

        # Match body-not-in-frontmatter gap
        body_gap = re.match(r'^\s+->\s+(\S+-\d+)\s+\(mentioned in body, not in frontmatter\)', line)
        if body_gap and current_file:
            gaps[current_file].append(body_gap.group(1))

    # Remove files with no gaps
    return {k: v for k, v in gaps.items() if v}


def parse_missing_reciprocals(status_output: str) -> dict[str, list[str]]:
    """Parse status cross-ref section for missing reciprocals.

    Format in status output:
      SPEC-001
        missing reciprocal: SPEC-002, SPEC-003

    This means SPEC-001's frontmatter has SPEC-002/003, but their frontmatter doesn't have SPEC-001.
    Fix: add SPEC-001 to SPEC-002's and SPEC-003's linked-artifacts.
    """
    reciprocals: dict[str, list[str]] = {}  # {target_artifact_id: [source_artifact_ids_to_add]}
    current_artifact = None

    for line in status_output.splitlines():
        # Match artifact ID at start of line (in the xref section)
        art_match = re.match(r'^- (\S+-\d+)$', line.strip())
        if art_match:
            current_artifact = art_match.group(1)
            continue

        # Match "missing reciprocal: X, Y"
        recip_match = re.match(r'^\s+missing reciprocal:\s+(.+)', line)
        if recip_match and current_artifact:
            targets = [t.strip() for t in recip_match.group(1).split(',')]
            for target in targets:
                if target not in reciprocals:
                    reciprocals[target] = []
                reciprocals[target].append(current_artifact)

    return reciprocals


def find_artifact_file(artifact_id: str) -> Optional[str]:
    """Find the file path for an artifact ID."""
    result = subprocess.run(
        ['find', 'docs', '-name', f'*{artifact_id}*', '-name', '*.md'],
        capture_output=True, text=True
    )
    files = [f for f in result.stdout.strip().splitlines() if f]
    if files:
        return files[0]
    return None


def add_to_linked_artifacts(filepath: str, refs_to_add: list[str], dry_run: bool = False) -> bool:
    """Add references to the linked-artifacts field in frontmatter."""
    path = Path(filepath)
    if not path.exists():
        print(f"  SKIP: {filepath} not found")
        return False

    content = path.read_text()

    # Parse frontmatter boundaries
    if not content.startswith('---'):
        print(f"  SKIP: {filepath} has no frontmatter")
        return False

    end_idx = content.index('---', 3)
    frontmatter = content[3:end_idx]
    body = content[end_idx:]

    # Find existing linked-artifacts
    existing_refs = set()

    # Check all frontmatter fields for already-declared refs
    for field in ['linked-artifacts', 'depends-on-artifacts', 'parent-epic', 'parent-initiative',
                  'parent-vision', 'source-issue', 'addresses']:
        field_match = re.search(rf'^{field}:\s*(.+)$', frontmatter, re.MULTILINE)
        if field_match:
            val = field_match.group(1).strip()
            if val and val != '[]':
                # Single value field
                refs_in_val = re.findall(r'[A-Z]+-\d+', val)
                existing_refs.update(refs_in_val)

        # Multi-line list
        list_match = re.search(rf'^{field}:\s*\n((?:\s+-\s+.+\n)*)', frontmatter, re.MULTILINE)
        if list_match:
            for item in re.findall(r'-\s+(.+)', list_match.group(1)):
                refs_in_item = re.findall(r'[A-Z]+-\d+', item)
                existing_refs.update(refs_in_item)

    # Filter out already-declared refs
    new_refs = [r for r in refs_to_add if r not in existing_refs]
    if not new_refs:
        return False

    # Find the linked-artifacts line and modify it
    # Case 1: linked-artifacts: []
    empty_list = re.search(r'^(linked-artifacts:\s*)\[\]\s*$', frontmatter, re.MULTILINE)
    if empty_list:
        items = '\n'.join(f'  - {ref}' for ref in sorted(new_refs))
        new_frontmatter = frontmatter[:empty_list.start()] + 'linked-artifacts:\n' + items + '\n' + frontmatter[empty_list.end():]
        if not dry_run:
            path.write_text('---' + new_frontmatter + body)
        print(f"  FIXED: {filepath} — added {new_refs}")
        return True

    # Case 2: linked-artifacts: with existing items
    list_match = re.search(r'^linked-artifacts:\s*\n((?:\s+-\s+.+\n)*)', frontmatter, re.MULTILINE)
    if list_match:
        existing_block = list_match.group(1)
        items = ''.join(f'  - {ref}\n' for ref in sorted(new_refs))
        new_block = existing_block + items
        new_frontmatter = frontmatter[:list_match.start(1)] + new_block + frontmatter[list_match.end(1):]
        if not dry_run:
            path.write_text('---' + new_frontmatter + body)
        print(f"  FIXED: {filepath} — added {new_refs}")
        return True

    # Case 3: linked-artifacts: (single line, non-empty, non-list) — unlikely but handle
    single_match = re.search(r'^linked-artifacts:\s*$', frontmatter, re.MULTILINE)
    if single_match:
        items = '\n'.join(f'  - {ref}' for ref in sorted(new_refs))
        new_frontmatter = frontmatter[:single_match.end()] + '\n' + items + '\n' + frontmatter[single_match.end()+1:]
        if not dry_run:
            path.write_text('---' + new_frontmatter + body)
        print(f"  FIXED: {filepath} — added {new_refs}")
        return True

    # Case 4: No linked-artifacts field at all — add one before depends-on-artifacts or at end
    insert_before = re.search(r'^depends-on-artifacts:', frontmatter, re.MULTILINE)
    if insert_before:
        items = '\n'.join(f'  - {ref}' for ref in sorted(new_refs))
        insert_text = 'linked-artifacts:\n' + items + '\n'
        new_frontmatter = frontmatter[:insert_before.start()] + insert_text + frontmatter[insert_before.start():]
    else:
        items = '\n'.join(f'  - {ref}' for ref in sorted(new_refs))
        new_frontmatter = frontmatter.rstrip() + '\nlinked-artifacts:\n' + items + '\n'

    if not dry_run:
        path.write_text('---' + new_frontmatter + body)
    print(f"  FIXED: {filepath} — added {new_refs}")
    return True


def main():
    dry_run = '--dry-run' in sys.argv
    if dry_run:
        print("=== DRY RUN ===\n")

    # Step 1: Get xref gaps
    print("Parsing xref gaps...")
    result = subprocess.run(
        ['bash', 'skills/swain-design/scripts/chart.sh', 'xref'],
        capture_output=True, text=True
    )
    gaps = parse_xref_output(result.stdout + result.stderr)

    # Step 2: Fix body-not-in-frontmatter gaps
    fixed = 0
    total_refs = 0
    print(f"\n=== Fixing {len(gaps)} artifacts with body-reference gaps ===\n")
    for filepath, refs in sorted(gaps.items()):
        total_refs += len(refs)
        if add_to_linked_artifacts(filepath, refs, dry_run):
            fixed += 1

    print(f"\nFixed {fixed} files, {total_refs} total references")

    # Step 3: Handle missing reciprocals
    # Parse from the status script output cross-reference section
    print("\n=== Checking missing reciprocals ===\n")

    # Read the status cross-ref data from chart.sh
    # Missing reciprocals: when A's frontmatter has B, but B's frontmatter doesn't have A
    # We need to parse this from the status output
    status_result = subprocess.run(
        ['bash', 'skills/swain-status/scripts/swain-status.sh', '--json'],
        capture_output=True, text=True
    )

    # Parse reciprocals from chart xref using a different approach
    # Re-run chart.sh xref and look for the pattern
    xref_text = result.stdout + result.stderr

    # Build a map of all frontmatter declarations to find missing reciprocals
    # For each artifact, check if its linked-artifacts/depends-on entries reciprocate
    reciprocal_fixes = 0

    # Known missing reciprocals from the status output
    # Format: (artifact_id, refs_to_add) — artifact_id needs refs_to_add in its linked-artifacts
    # "ADR-004 missing reciprocal: SPEC-030" = ADR-004 needs SPEC-030 added
    missing_reciprocals = [
        ("ADR-004", ["SPEC-030"]),
        ("EPIC-006", ["EPIC-007"]),
        ("EPIC-015", ["EPIC-016"]),
        ("EPIC-017", ["EPIC-023"]),
        ("EPIC-019", ["EPIC-021"]),
        ("SPEC-001", ["SPEC-002", "SPEC-003"]),
        ("SPEC-004", ["SPEC-005", "SPEC-006"]),
        ("SPEC-015", ["SPEC-016"]),
        ("SPEC-018", ["SPEC-019", "SPEC-020"]),
        ("SPEC-019", ["SPEC-020"]),
        ("SPEC-020", ["SPEC-021"]),
        ("SPEC-023", ["SPEC-024"]),
        ("SPEC-030", ["SPEC-031", "SPEC-032"]),
        ("SPEC-032", ["SPEC-033"]),
        ("SPEC-039", ["SPEC-044"]),
        ("SPEC-043", ["SPEC-044"]),
        ("SPEC-045", ["SPEC-046"]),
        ("SPEC-048", ["SPEC-049"]),
        ("SPIKE-018", ["EPIC-014", "SPEC-045", "SPEC-046", "SPEC-047"]),
    ]

    for artifact_id, refs_to_add in missing_reciprocals:
        artifact_file = find_artifact_file(artifact_id)
        if artifact_file:
            if add_to_linked_artifacts(artifact_file, refs_to_add, dry_run):
                    reciprocal_fixes += 1

    print(f"\nFixed {reciprocal_fixes} missing reciprocals")
    print(f"\nTotal: {fixed + reciprocal_fixes} files modified")


if __name__ == '__main__':
    main()
