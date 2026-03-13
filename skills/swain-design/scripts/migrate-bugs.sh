#!/bin/bash
# migrate-bugs.sh — Migrate BUG artifacts to SPEC type:bug (SPEC-006)
#
# Detects docs/bug/ directory and migrates each BUG-NNN artifact to
# docs/spec/<mapped-phase>/(SPEC-NNN)-<Title>/ with type:bug frontmatter.
# Rewrites cross-references, removes docs/bug/ and list-bug.md, updates list-spec.md.
#
# Idempotent: no-op if docs/bug/ does not exist.
# Uses git mv to preserve history.

set -eo pipefail

# --- Resolve repo root ---
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "Error: not inside a git repository" >&2
  exit 1
}

DOCS_DIR="$REPO_ROOT/docs"
BUG_DIR="$DOCS_DIR/bug"
SPEC_DIR="$DOCS_DIR/spec"

# --- Idempotency: no-op if no docs/bug/ ---
if [[ ! -d "$BUG_DIR" ]]; then
  exit 0
fi

# Check if there are any BUG artifact .md files (skip list-bug.md)
bug_count=0
while IFS= read -r -d '' f; do
  bug_count=$(( bug_count + 1 ))
done < <(find "$BUG_DIR" -name '*.md' -not -name 'list-*' -print0 2>/dev/null)

if [[ "$bug_count" -eq 0 ]]; then
  # No BUG artifacts, just clean up the empty directory
  git -C "$REPO_ROOT" rm -rf "$BUG_DIR" 2>/dev/null || rm -rf "$BUG_DIR"
  echo "migrate-bugs: removed empty docs/bug/ directory."
  exit 0
fi

# --- Phase mapping: BUG phase -> SPEC phase ---
map_phase() {
  local bug_phase="$1"
  case "$bug_phase" in
    Reported) echo "Proposed" ;;
    Triaged)  echo "Proposed" ;;
    Active)   echo "Ready" ;;
    Verified) echo "NeedsManualTest" ;;
    Resolved) echo "Complete" ;;
    Abandoned) echo "Abandoned" ;;
    *)        echo "Proposed" ;;
  esac
}

# --- Determine next available SPEC number ---
get_next_spec_number() {
  local max_num=0
  local num
  while IFS= read -r -d '' f; do
    local bname
    bname="$(basename "$f")"
    if [[ "$bname" =~ SPEC-([0-9]+) ]]; then
      num="${BASH_REMATCH[1]}"
      # Strip leading zeros for arithmetic
      num=$((10#$num))
      if (( num > max_num )); then
        max_num=$num
      fi
    fi
  done < <(find "$SPEC_DIR" -name '*.md' -not -name 'list-*' -print0 2>/dev/null)
  echo $(( max_num + 1 ))
}

# --- Extract frontmatter field value ---
# Usage: get_fm_field <file> <field>
get_fm_field() {
  local file="$1"
  local field="$2"
  local in_fm=false
  while IFS= read -r line; do
    if [[ "$line" == "---" ]]; then
      if $in_fm; then
        break
      fi
      in_fm=true
      continue
    fi
    if $in_fm; then
      if [[ "$line" =~ ^${field}:\ *(.*) ]]; then
        local val="${BASH_REMATCH[1]}"
        # Strip quotes
        val="${val#\"}"
        val="${val%\"}"
        val="${val#\'}"
        val="${val%\'}"
        echo "$val"
        return
      fi
    fi
  done < "$file"
}

# --- Migration tracking ---
# Parallel arrays instead of associative array (for portability)
BUG_IDS=()
SPEC_IDS=()
migrated_count=0
rewritten_refs=0
migration_report=""

# --- Process each BUG artifact ---
next_spec=$(get_next_spec_number)

while IFS= read -r -d '' bug_md; do
  # Extract artifact ID from frontmatter
  bug_id=$(get_fm_field "$bug_md" "artifact")
  if [[ -z "$bug_id" ]] || [[ ! "$bug_id" =~ ^BUG-[0-9]+ ]]; then
    echo "migrate-bugs: SKIP $bug_md — no valid artifact ID in frontmatter" >&2
    continue
  fi

  # Extract other frontmatter fields
  bug_title=$(get_fm_field "$bug_md" "title")
  bug_status=$(get_fm_field "$bug_md" "status")

  # Map phase
  spec_phase=$(map_phase "$bug_status")

  # Assign next SPEC number
  spec_num=$(printf "%03d" "$next_spec")
  spec_id="SPEC-$spec_num"
  BUG_IDS+=("$bug_id")
  SPEC_IDS+=("$spec_id")

  # Derive title slug from the BUG directory name
  bug_dir="$(dirname "$bug_md")"
  bug_dir_name="$(basename "$bug_dir")"

  # Extract title part from directory name: (BUG-001)-Title-Here -> Title-Here
  if [[ "$bug_dir_name" =~ ^\(BUG-[0-9]+\)-(.*) ]]; then
    title_slug="${BASH_REMATCH[1]}"
  else
    # Fallback: sanitize from frontmatter title
    title_slug=$(echo "$bug_title" | sed 's/[^a-zA-Z0-9]/-/g; s/--*/-/g; s/^-//; s/-$//')
  fi

  spec_dir_name="($spec_id)-$title_slug"
  spec_phase_dir="$SPEC_DIR/$spec_phase"
  spec_target_dir="$spec_phase_dir/$spec_dir_name"

  # Create target phase directory if needed
  mkdir -p "$spec_phase_dir"

  # Move artifact directory with git mv
  git -C "$REPO_ROOT" mv "$bug_dir" "$spec_target_dir"

  # Now rename the .md file inside the moved directory
  old_md_name="$(basename "$bug_md")"
  new_md_name="($spec_id)-$title_slug.md"
  if [[ "$old_md_name" != "$new_md_name" ]]; then
    git -C "$REPO_ROOT" mv "$spec_target_dir/$old_md_name" "$spec_target_dir/$new_md_name"
  fi

  spec_md="$spec_target_dir/$new_md_name"

  # --- Rewrite frontmatter using Python for reliability ---
  today=$(date +%Y-%m-%d)
  migration_row="| Migrated | $today | — | Migrated from $bug_id to $spec_id (SPEC-006) |"

  python3 - "$spec_md" "$bug_id" "$spec_id" "$bug_status" "$spec_phase" "$migration_row" <<'PYEOF'
import sys, re

filepath = sys.argv[1]
bug_id = sys.argv[2]
spec_id = sys.argv[3]
bug_status = sys.argv[4]
spec_phase = sys.argv[5]
migration_row = sys.argv[6]

with open(filepath) as f:
    content = f.read()

lines = content.split('\n')
new_lines = []
in_fm = False
fm_done = False
added_type = False
skip_fields = {'severity', 'fix-ref', 'discovered-in'}

for line in lines:
    if line.strip() == '---':
        if not in_fm:
            in_fm = True
            new_lines.append(line)
            continue
        else:
            # Closing frontmatter delimiter
            # Add type: bug if we haven't yet
            if not added_type:
                new_lines.append('type: bug')
                added_type = True
            in_fm = False
            fm_done = True
            new_lines.append(line)
            continue

    if in_fm:
        # Replace artifact field
        if line.startswith('artifact:'):
            new_lines.append(f'artifact: {spec_id}')
            new_lines.append('type: bug')
            added_type = True
            continue
        # Replace status field
        if line.startswith('status:'):
            new_lines.append(f'status: {spec_phase}')
            continue
        # Skip BUG-specific fields
        field_name = line.split(':')[0].strip() if ':' in line else ''
        if field_name in skip_fields:
            continue
        # Skip existing type field (we add our own)
        if line.startswith('type:'):
            continue
        new_lines.append(line)
    else:
        new_lines.append(line)

# Rejoin content
content = '\n'.join(new_lines)

# First, append migration row to lifecycle table (before body-text replacement
# so the migration row preserves the original BUG-NNN ID in its text)
lines = content.split('\n')
final_lines = []
in_lifecycle = False
last_table_idx = -1

for i, line in enumerate(lines):
    final_lines.append(line)
    if '## Lifecycle' in line:
        in_lifecycle = True
    elif in_lifecycle and line.startswith('|'):
        last_table_idx = len(final_lines) - 1
    elif in_lifecycle and not line.startswith('|') and line.strip() and last_table_idx > -1:
        in_lifecycle = False

if last_table_idx >= 0:
    final_lines.insert(last_table_idx + 1, migration_row)

content = '\n'.join(final_lines)

# Now replace any remaining BUG-ID references in body text (but not inside
# the migration row — protect it with a placeholder)
placeholder = f'__MIGRATION_ROW_{spec_id}__'
content = content.replace(migration_row, placeholder)
content = content.replace(bug_id, spec_id)
content = content.replace(placeholder, migration_row)

with open(filepath, 'w') as f:
    f.write(content)
PYEOF

  migrated_count=$(( migrated_count + 1 ))
  next_spec=$(( next_spec + 1 ))

  migration_report="${migration_report}  ${bug_id} -> ${spec_id} (${bug_status} -> ${spec_phase}): ${bug_title}\n"

done < <(find "$BUG_DIR" -name '*.md' -not -name 'list-*' -print0 2>/dev/null)

# --- Rewrite cross-references in all docs ---
for i in "${!BUG_IDS[@]}"; do
  bug_id="${BUG_IDS[$i]}"
  spec_id="${SPEC_IDS[$i]}"

  # Find all .md files that reference this BUG-ID
  while IFS= read -r ref_file; do
    # Skip files in the bug directory (already handled or about to be deleted)
    [[ "$ref_file" == *"/docs/bug/"* ]] && continue

    # Replace all occurrences of the BUG ID with the SPEC ID
    if sed -i '' "s/${bug_id}/${spec_id}/g" "$ref_file" 2>/dev/null; then
      rewritten_refs=$(( rewritten_refs + 1 ))
    fi
  done < <(grep -rl "$bug_id" "$DOCS_DIR" 2>/dev/null || true)

  # Also check AGENTS.md and other root-level docs
  for root_file in "$REPO_ROOT/AGENTS.md" "$REPO_ROOT/CLAUDE.md"; do
    if [[ -f "$root_file" ]] && grep -q "$bug_id" "$root_file" 2>/dev/null; then
      sed -i '' "s/${bug_id}/${spec_id}/g" "$root_file"
      rewritten_refs=$(( rewritten_refs + 1 ))
    fi
  done
done

# --- Remove docs/bug/ directory ---
# First remove list-bug.md if tracked
if [[ -f "$BUG_DIR/list-bug.md" ]]; then
  git -C "$REPO_ROOT" rm -f "$BUG_DIR/list-bug.md" 2>/dev/null || rm -f "$BUG_DIR/list-bug.md"
fi

# Remove remaining bug directory (should be empty after git mv of artifacts)
if [[ -d "$BUG_DIR" ]]; then
  # Remove any remaining untracked files
  rm -rf "$BUG_DIR"
  # If git still tracks the directory, remove from index
  git -C "$REPO_ROOT" rm -rf --ignore-unmatch "$BUG_DIR" 2>/dev/null || true
fi

# --- Update list-spec.md ---
# Add migrated artifacts to the appropriate sections
SPEC_LIST="$SPEC_DIR/list-spec.md"
if [[ -f "$SPEC_LIST" ]]; then
  for i in "${!BUG_IDS[@]}"; do
    spec_id="${SPEC_IDS[$i]}"

    # Get the migrated artifact details from the new location
    spec_md_file=$(find "$SPEC_DIR" -name "*${spec_id}*" -name "*.md" -not -name "list-*" 2>/dev/null | head -1)
    if [[ -z "$spec_md_file" ]]; then
      continue
    fi

    spec_title=$(get_fm_field "$spec_md_file" "title")
    spec_status=$(get_fm_field "$spec_md_file" "status")
    today=$(date +%Y-%m-%d)

    # Check if already in list-spec.md
    if grep -q "$spec_id" "$SPEC_LIST" 2>/dev/null; then
      continue
    fi

    # Add to the appropriate phase section
    python3 - "$SPEC_LIST" "$spec_id" "$spec_title" "$spec_status" "$today" <<'PYEOF'
import sys

filepath = sys.argv[1]
spec_id = sys.argv[2]
spec_title = sys.argv[3]
spec_status = sys.argv[4]
today = sys.argv[5]

with open(filepath) as f:
    lines = f.readlines()

new_row = f"| {spec_id} | {spec_title} | {today} | — |\n"

# Find the section for this status
section_header = f"## {spec_status}"
in_section = False
insert_idx = -1

for i, line in enumerate(lines):
    if line.strip() == section_header:
        in_section = True
        continue
    if in_section:
        if line.startswith('## '):
            # Next section — insert before it
            if insert_idx == -1:
                insert_idx = i
            break
        if line.startswith('|') and not line.startswith('| Artifact') and not line.startswith('|---'):
            # This is a data row — keep going, insert after last data row
            insert_idx = i + 1
        elif line.strip() == '' and insert_idx == -1:
            continue

if insert_idx == -1:
    # Section not found — create it at end
    insert_idx = len(lines)
    section_block = f"\n{section_header}\n\n| Artifact | Title | Last Updated | Commit |\n|----------|-------|-------------|--------|\n{new_row}"
    lines.insert(insert_idx, section_block)
else:
    lines.insert(insert_idx, new_row)

with open(filepath, 'w') as f:
    f.writelines(lines)
PYEOF
  done
fi

# --- Stage all changes ---
git -C "$REPO_ROOT" add "$SPEC_DIR" 2>/dev/null || true
git -C "$REPO_ROOT" add "$SPEC_LIST" 2>/dev/null || true

# --- Print migration report ---
echo "migrate-bugs: migrated $migrated_count BUG artifact(s) to SPEC type:bug"
if [[ $rewritten_refs -gt 0 ]]; then
  echo "migrate-bugs: rewrote cross-references in $rewritten_refs file(s)"
fi
echo ""
echo "Migration details:"
printf "%b" "$migration_report"
echo ""
echo "Phase mapping applied:"
echo "  Reported  -> Proposed"
echo "  Triaged   -> Proposed"
echo "  Active    -> Ready"
echo "  Verified  -> NeedsManualTest"
echo "  Resolved  -> Complete"
echo "  Abandoned -> Abandoned"
