#!/usr/bin/env python3
"""SPEC-009: Migrate artifact frontmatter fields.

Replaces per-type linked-* fields with unified linked-artifacts.
Renames depends-on to depends-on-artifacts (removed for spikes).

Usage:
    uv run python3 migrate-frontmatter-fields.py [--dry-run]
"""
import glob
import re
import sys

DRY_RUN = "--dry-run" in sys.argv

# Fields to merge into linked-artifacts
LINKED_FIELDS = [
    "linked-research", "linked-adrs", "linked-epics", "linked-specs",
    "linked-stories", "linked-personas", "linked-journeys", "linked-designs",
    "linked-bugs",
]


def parse_frontmatter(text):
    """Return (frontmatter_lines, body) split at second ---."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, text
    end = None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            end = i
            break
    if end is None:
        return None, text
    return lines[1:end], "\n".join(lines[end:])


def extract_field(fm_lines, field_name):
    """Extract a field and its list values from frontmatter lines.
    Returns (values_list, remaining_lines)."""
    values = []
    remaining = []
    in_field = False
    for line in fm_lines:
        if line.startswith(f"{field_name}:"):
            in_field = True
            # Check for inline value
            inline = line[len(f"{field_name}:"):].strip()
            if inline and inline != "[]":
                # Could be a YAML inline list or single value
                if inline.startswith("["):
                    inner = inline.strip("[] ")
                    for v in inner.split(","):
                        v = v.strip().strip("'\"")
                        if v:
                            values.append(v)
                else:
                    values.append(inline)
            continue
        if in_field:
            if line.startswith("  - "):
                val = line.strip().lstrip("- ").strip()
                if val:
                    values.append(val)
                continue
            elif line.startswith("  ") and not line.startswith("  -"):
                # continuation of previous value? skip
                continue
            else:
                in_field = False
        remaining.append(line)
    return values, remaining


def migrate_file(filepath):
    with open(filepath, "r") as f:
        text = f.read()

    fm_lines, body = parse_frontmatter(text)
    if fm_lines is None:
        return False

    # Check if file has any old fields
    fm_text = "\n".join(fm_lines)
    has_old = any(f"\n{field}:" in f"\n{fm_text}" or fm_text.startswith(f"{field}:")
                  for field in LINKED_FIELDS + ["depends-on"])
    if not has_old:
        return False

    # Already migrated?
    if any(line.startswith("linked-artifacts:") for line in fm_lines):
        return False

    is_spike = "/research/" in filepath or any(
        line.startswith("artifact: SPIKE-") for line in fm_lines
    )

    # Collect all linked values
    all_linked = []
    remaining = fm_lines
    for field in LINKED_FIELDS:
        values, remaining = extract_field(remaining, field)
        all_linked.extend(values)

    # Collect depends-on values
    depends_values, remaining = extract_field(remaining, "depends-on")

    # Build new fields
    new_fields = []
    if all_linked:
        new_fields.append("linked-artifacts:")
        for v in all_linked:
            new_fields.append(f"  - {v}")
    else:
        new_fields.append("linked-artifacts: []")

    if not is_spike:
        if depends_values:
            new_fields.append("depends-on-artifacts:")
            for v in depends_values:
                new_fields.append(f"  - {v}")
        else:
            new_fields.append("depends-on-artifacts: []")

    # Rebuild frontmatter
    new_fm = remaining + new_fields
    new_text = "---\n" + "\n".join(new_fm) + "\n" + body

    if DRY_RUN:
        print(f"  [dry-run] {filepath}")
        return True

    with open(filepath, "w") as f:
        f.write(new_text)
    print(f"  Migrated: {filepath}")
    return True


def main():
    print("SPEC-009: Frontmatter field migration")
    if DRY_RUN:
        print("DRY RUN — no files modified\n")

    files = sorted(glob.glob("docs/**/*.md", recursive=True))
    files = [f for f in files if not any(
        f.endswith(x) for x in ["list-spec.md", "list-epic.md", "list-adr.md",
                                  "list-spike.md", "list-story.md", "list-journey.md",
                                  "list-vision.md", "list-persona.md", "list-runbook.md",
                                  "list-design.md", "README.md"]
    )]

    count = 0
    for f in files:
        if migrate_file(f):
            count += 1

    print(f"\n{count} file(s) {'would be ' if DRY_RUN else ''}migrated.")


if __name__ == "__main__":
    main()
