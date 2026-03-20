#!/bin/bash
# relink.sh — Fix broken artifact hyperlinks in docs/ by resolving artifact IDs to current paths.
#
# Usage:
#   bash relink.sh              # fix all broken links across all docs/ artifacts
#   bash relink.sh <FILE>       # fix broken links in a specific file only
#
# For each broken markdown link [text](broken-path) where the path doesn't resolve:
#   - Extracts the artifact ID from the link text or path
#   - Calls resolve-artifact-link.sh <ID> <SOURCE-FILE> to get the current path
#   - Replaces the broken path in the markdown link with the new path
#
# Also checks frontmatter artifact-refs entries with rel-path fields and updates
# those if the path is broken.
#
# Output:
#   RELINKED <file>:<line> <old-path> -> <new-path>
#
# Exit codes:
#   0 — all broken links were fixed (or none found)
#   1 — one or more broken links remain unfixed

set -euo pipefail

# --- Resolve repo root ---
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "Error: not inside a git repository" >&2
  exit 1
}
DOCS_DIR="$REPO_ROOT/docs"

# --- Locate resolve-artifact-link.sh ---
# Prefer the sibling script (same directory as this script),
# then fall back to a find-based search across the repo (excluding .git internals).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESOLVE_SCRIPT="$SCRIPT_DIR/resolve-artifact-link.sh"

if [ ! -x "$RESOLVE_SCRIPT" ]; then
  # Fallback: search across the repo tree (skip .git but allow other hidden dirs)
  RESOLVE_SCRIPT=""
  while IFS= read -r candidate; do
    RESOLVE_SCRIPT="$candidate"
    break
  done < <(find "$REPO_ROOT" -name "resolve-artifact-link.sh" -not -path "*/.git/*" 2>/dev/null | head -1)
fi

if [ -z "$RESOLVE_SCRIPT" ] || [ ! -x "$RESOLVE_SCRIPT" ]; then
  echo "Error: resolve-artifact-link.sh not found or not executable" >&2
  exit 1
fi

# --- Collect markdown files to process ---
TARGET_FILE="${1:-}"
declare -a MD_FILES=()

if [ -n "$TARGET_FILE" ]; then
  # Single-file mode: resolve to absolute path
  if [[ "$TARGET_FILE" != /* ]]; then
    TARGET_FILE="$PWD/$TARGET_FILE"
  fi
  if [ ! -f "$TARGET_FILE" ]; then
    echo "Error: file not found: $TARGET_FILE" >&2
    exit 1
  fi
  MD_FILES=("$TARGET_FILE")
else
  # Full-scan mode: all markdown files in docs/
  while IFS= read -r -d '' f; do
    MD_FILES+=("$f")
  done < <(find "$DOCS_DIR" -name '*.md' -print0 2>/dev/null)
fi

if [ "${#MD_FILES[@]}" -eq 0 ]; then
  echo "relink: no markdown files found."
  exit 0
fi

# --- Extract broken body-text markdown links using Python ---
# Output format: filepath\tline_num\tlink_text\tlink_target
LINKS_TMP=$(mktemp /tmp/relink-links-XXXXXX)
trap 'rm -f "$LINKS_TMP"' EXIT

python3 - "${MD_FILES[@]}" > "$LINKS_TMP" <<'PYEOF'
import re, sys, os

# Regex handles balanced parens: [text](path with (parens) inside)
link_re = re.compile(r'\[([^\]]*)\]\(((?:[^()\s]|\([^()]*\))+)\)')
# Inline code span regex: `...` (non-greedy, single backtick, no newlines)
code_span_re = re.compile(r'`[^`\n]+`')

for filepath in sys.argv[1:]:
    try:
        with open(filepath) as f:
            in_code_block = False
            for line_num, line in enumerate(f, 1):
                # Track fenced code blocks (``` or ~~~)
                stripped = line.strip()
                if stripped.startswith('```') or stripped.startswith('~~~'):
                    in_code_block = not in_code_block
                    continue
                if in_code_block:
                    continue

                # Strip inline code spans before searching for links
                # so that links inside backticks are not matched
                line_no_code = code_span_re.sub(lambda m: ' ' * len(m.group(0)), line)

                for m in link_re.finditer(line_no_code):
                    link_text = m.group(1)
                    target = m.group(2)
                    # Skip external URLs, anchors, mailto
                    if target.startswith(('http://', 'https://', 'mailto:', '#')):
                        continue
                    # Skip targets that can't be file paths
                    if '/' not in target and '.' not in target:
                        continue
                    # Strip anchor for resolution check
                    clean_target = target.split('#')[0]
                    if not clean_target:
                        continue
                    # Check if the path resolves
                    src_dir = os.path.dirname(filepath)
                    resolved = os.path.normpath(os.path.join(src_dir, clean_target))
                    if not os.path.exists(resolved):
                        print(f"{filepath}\t{line_num}\t{link_text}\t{target}")
    except (OSError, UnicodeDecodeError):
        pass
PYEOF

# --- Also extract broken frontmatter rel-path fields using Python ---
# Output format: filepath\tline_num\tartifact_id\trel_path_value
FMLINKS_TMP=$(mktemp /tmp/relink-fmlinks-XXXXXX)
trap 'rm -f "$LINKS_TMP" "$FMLINKS_TMP"' EXIT

python3 - "${MD_FILES[@]}" > "$FMLINKS_TMP" <<'PYEOF'
import re, sys, os

for filepath in sys.argv[1:]:
    try:
        with open(filepath) as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError):
        continue

    if not lines or lines[0].strip() != '---':
        continue

    # Parse frontmatter for artifact-refs entries with rel-path
    in_frontmatter = False
    in_artifact_refs = False
    current_artifact = None
    src_dir = os.path.dirname(filepath)

    for i, line in enumerate(lines):
        if i == 0:
            in_frontmatter = True
            continue
        if line.strip() == '---':
            if in_frontmatter:
                break
            continue

        # Detect artifact-refs block
        if re.match(r'^artifact-refs:\s*$', line):
            in_artifact_refs = True
            current_artifact = None
            continue

        # If we hit a top-level key (no leading spaces), exit artifact-refs block
        if in_artifact_refs and re.match(r'^[a-z]', line):
            in_artifact_refs = False
            current_artifact = None
            continue

        if in_artifact_refs:
            # New list item — may set current artifact
            m = re.match(r'^\s+-\s+artifact:\s*(.+)', line)
            if m:
                current_artifact = m.group(1).strip().strip('"').strip("'")
                continue
            # Nested continuation — look for artifact: sub-key
            m = re.match(r'^\s+artifact:\s*(.+)', line)
            if m:
                current_artifact = m.group(1).strip().strip('"').strip("'")
                continue
            # rel-path sub-key
            m = re.match(r'^\s+rel-path:\s*(.+)', line)
            if m and current_artifact:
                rel_path = m.group(1).strip().strip('"').strip("'")
                if rel_path and rel_path.upper() != 'NONE':
                    # Check if path resolves
                    resolved = os.path.normpath(os.path.join(src_dir, rel_path))
                    if not os.path.exists(resolved):
                        print(f"{filepath}\t{i+1}\t{current_artifact}\t{rel_path}")
PYEOF

# --- Process broken body-text links ---
RELINKED_COUNT=0
UNFIXED_COUNT=0

process_body_link() {
  local md_file="$1"
  local line_num="$2"
  local link_text="$3"
  local link_target="$4"

  # Extract anchor if present
  local anchor=""
  local clean_target="$link_target"
  if [[ "$link_target" == *"#"* ]]; then
    anchor="#${link_target#*#}"
    clean_target="${link_target%%#*}"
  fi

  # Extract artifact ID from link text first, then from path
  local artifact_id=""
  local id_re='(SPEC|EPIC|INITIATIVE|VISION|SPIKE|ADR|PERSONA|RUNBOOK|DESIGN|JOURNEY|TRAIN)-[0-9]+'

  # Try link text
  if [[ "$link_text" =~ $id_re ]]; then
    artifact_id="${BASH_REMATCH[0]}"
  fi

  # Try path (parenthesized: (TYPE-NNN) then bare: TYPE-NNN)
  if [ -z "$artifact_id" ]; then
    local paren_re='\(([A-Z]+-[0-9]+)\)'
    if [[ "$clean_target" =~ $paren_re ]]; then
      artifact_id="${BASH_REMATCH[1]}"
    fi
  fi
  if [ -z "$artifact_id" ]; then
    if [[ "$clean_target" =~ $id_re ]]; then
      artifact_id="${BASH_REMATCH[0]}"
    fi
  fi

  if [ -z "$artifact_id" ]; then
    echo "  SKIP: $md_file:$line_num — no artifact ID found in link text or path (link_text='$link_text', target='$clean_target')"
    UNFIXED_COUNT=$(( UNFIXED_COUNT + 1 ))
    return
  fi

  # Resolve the artifact ID to a new path
  local new_rel_path
  new_rel_path=$(bash "$RESOLVE_SCRIPT" "$artifact_id" "$md_file" 2>/dev/null) || {
    echo "  SKIP: $md_file:$line_num — $artifact_id not resolved"
    UNFIXED_COUNT=$(( UNFIXED_COUNT + 1 ))
    return
  }

  if [ -z "$new_rel_path" ]; then
    echo "  SKIP: $md_file:$line_num — $artifact_id resolve returned empty"
    UNFIXED_COUNT=$(( UNFIXED_COUNT + 1 ))
    return
  fi

  # Append anchor if original link had one
  local new_target="${new_rel_path}${anchor}"

  # If path is already correct, nothing to do
  if [ "$new_target" = "$link_target" ]; then
    return
  fi

  # sed-replace the broken path in the file (replace first occurrence on the line)
  # Escape special characters for sed
  local escaped_old
  escaped_old=$(printf '%s\n' "$link_target" | sed 's|[[\.*^$()+?{|]|\\&|g; s|]|\\]|g')
  local escaped_new
  escaped_new=$(printf '%s\n' "$new_target" | sed 's|[[\.*^$()+?{|]|\\&|g; s|]|\\]|g; s|/|\\/|g')

  # Use python to do the replacement safely (handles special chars better than sed)
  python3 - "$md_file" "$line_num" "$link_target" "$new_target" <<'PYEOF'
import sys

filepath = sys.argv[1]
target_line = int(sys.argv[2])
old_target = sys.argv[3]
new_target = sys.argv[4]

with open(filepath) as f:
    lines = f.readlines()

line_idx = target_line - 1
if line_idx < len(lines):
    # Replace first occurrence of the old target path in the link
    old_link_part = f"]({old_target})"
    new_link_part = f"]({new_target})"
    if old_link_part in lines[line_idx]:
        lines[line_idx] = lines[line_idx].replace(old_link_part, new_link_part, 1)
        with open(filepath, 'w') as f:
            f.writelines(lines)
        sys.exit(0)
sys.exit(1)
PYEOF

  local ret=$?
  if [ "$ret" -eq 0 ]; then
    # Report relative to repo root for cleaner output
    local rel_file="${md_file#"$REPO_ROOT"/}"
    echo "RELINKED $rel_file:$line_num $link_target -> $new_target"
    RELINKED_COUNT=$(( RELINKED_COUNT + 1 ))
  else
    echo "  SKIP: $md_file:$line_num — replacement failed for $link_target"
    UNFIXED_COUNT=$(( UNFIXED_COUNT + 1 ))
  fi
}

process_frontmatter_rel_path() {
  local md_file="$1"
  local line_num="$2"
  local artifact_id="$3"
  local old_rel_path="$4"

  # Resolve the artifact ID to a new path
  local new_rel_path
  new_rel_path=$(bash "$RESOLVE_SCRIPT" "$artifact_id" "$md_file" 2>/dev/null) || {
    echo "  SKIP: $md_file:$line_num (frontmatter) — $artifact_id not resolved"
    UNFIXED_COUNT=$(( UNFIXED_COUNT + 1 ))
    return
  }

  if [ -z "$new_rel_path" ]; then
    echo "  SKIP: $md_file:$line_num (frontmatter) — $artifact_id resolve returned empty"
    UNFIXED_COUNT=$(( UNFIXED_COUNT + 1 ))
    return
  fi

  if [ "$new_rel_path" = "$old_rel_path" ]; then
    return
  fi

  # Replace the rel-path value on that line
  python3 - "$md_file" "$line_num" "$old_rel_path" "$new_rel_path" <<'PYEOF'
import sys, re

filepath = sys.argv[1]
target_line = int(sys.argv[2])
old_path = sys.argv[3]
new_path = sys.argv[4]

with open(filepath) as f:
    lines = f.readlines()

line_idx = target_line - 1
if line_idx < len(lines):
    line = lines[line_idx]
    # Match rel-path: <value> and replace the value
    m = re.match(r'^(\s+rel-path:\s*)(.+)$', line.rstrip('\n'))
    if m:
        prefix = m.group(1)
        lines[line_idx] = f"{prefix}{new_path}\n"
        with open(filepath, 'w') as f:
            f.writelines(lines)
        sys.exit(0)
sys.exit(1)
PYEOF

  local ret=$?
  if [ "$ret" -eq 0 ]; then
    local rel_file="${md_file#"$REPO_ROOT"/}"
    echo "RELINKED $rel_file:$line_num (frontmatter rel-path) $old_rel_path -> $new_rel_path"
    RELINKED_COUNT=$(( RELINKED_COUNT + 1 ))
  else
    echo "  SKIP: $md_file:$line_num (frontmatter) — replacement failed for $old_rel_path"
    UNFIXED_COUNT=$(( UNFIXED_COUNT + 1 ))
  fi
}

# --- Process body-text links ---
while IFS=$'\t' read -r md_file line_num link_text link_target; do
  [ -z "$md_file" ] && continue
  process_body_link "$md_file" "$line_num" "$link_text" "$link_target"
done < "$LINKS_TMP"

# --- Process frontmatter rel-path fields ---
while IFS=$'\t' read -r md_file line_num artifact_id rel_path_val; do
  [ -z "$md_file" ] && continue
  process_frontmatter_rel_path "$md_file" "$line_num" "$artifact_id" "$rel_path_val"
done < "$FMLINKS_TMP"

# --- Summary ---
if [ "$RELINKED_COUNT" -eq 0 ] && [ "$UNFIXED_COUNT" -eq 0 ]; then
  echo "relink: no broken links found."
elif [ "$RELINKED_COUNT" -gt 0 ] && [ "$UNFIXED_COUNT" -eq 0 ]; then
  echo "relink: fixed $RELINKED_COUNT broken link(s). All resolved."
else
  echo "relink: fixed $RELINKED_COUNT, $UNFIXED_COUNT remain unfixed."
fi

[ "$UNFIXED_COUNT" -eq 0 ] && exit 0 || exit 1
