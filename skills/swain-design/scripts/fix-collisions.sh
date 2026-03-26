#!/usr/bin/env bash
# fix-collisions.sh — Batch collision resolution via renumbering
#
# Usage: fix-collisions.sh [--dry-run] [TYPE-NNN ...]
#   No args: scan all docs/ for duplicates, auto-fix each by renumbering the
#            newer artifact (by created date) to the next available number.
#   With args: renumber the specified IDs to the next available number.
#   --dry-run: show what would change without doing it.
#
# Depends on: detect-duplicate-numbers.sh, next-artifact-number.sh, renumber-artifact.sh
#
# SPEC-158 / EPIC-043

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DETECT="$SCRIPT_DIR/detect-duplicate-numbers.sh"
ALLOCATOR="$SCRIPT_DIR/next-artifact-number.sh"
RENUMBER="$SCRIPT_DIR/renumber-artifact.sh"

git rev-parse --git-dir >/dev/null 2>&1 || {
  echo "Error: not inside a git repository" >&2
  exit 1
}

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# --- Check dependencies ---
for script in "$DETECT" "$ALLOCATOR" "$RENUMBER"; do
  if [ ! -x "$script" ]; then
    echo "Error: required script not found or not executable: $script" >&2
    exit 1
  fi
done

DRY_RUN=""
EXPLICIT_IDS=""

# --- Parse args ---
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN="--dry-run" ;;
    *-[0-9]*) EXPLICIT_IDS="$EXPLICIT_IDS $arg" ;;
    *) echo "Unknown argument: $arg" >&2; exit 1 ;;
  esac
done

# Track allocated numbers per type so dry-run previews show distinct targets.
# Uses _ALLOC_<TYPE> variables instead of associative arrays (bash 3.x compat).
FIXED=0

if [ -n "$EXPLICIT_IDS" ]; then
  # --- Explicit mode: renumber specified IDs ---
  for old_id in $EXPLICIT_IDS; do
    TYPE="${old_id%%-*}"
    new_num=$(bash "$ALLOCATOR" "$TYPE" 2>/dev/null) || {
      echo "Error: could not allocate next number for $TYPE" >&2
      exit 1
    }
    new_id="${TYPE}-${new_num}"
    echo "=== Renumbering $old_id → $new_id ==="
    bash "$RENUMBER" "$old_id" "$new_id" $DRY_RUN
    FIXED=$((FIXED + 1))
    echo ""
  done
else
  # --- Auto mode: detect and fix all collisions ---
  dup_output=$(bash "$DETECT" 2>/dev/null) || true
  if [ -z "$dup_output" ]; then
    echo "No duplicate artifact numbers found."
    exit 0
  fi

  echo "Found collisions:"
  echo "$dup_output"
  echo ""

  # Parse each DUPLICATE line: "DUPLICATE TYPE-NNN: path1 path2 ..."
  while IFS= read -r line; do
    [[ "$line" =~ ^DUPLICATE\ ([A-Z]+-[0-9]+): ]] || continue
    dup_id="${BASH_REMATCH[1]}"
    TYPE="${dup_id%%-*}"

    # Find all dirs for this dup_id
    dirs=""
    while IFS= read -r dir; do
      dirs="$dirs $dir"
    done < <(find "$REPO_ROOT/docs" -maxdepth 5 -type d -name "(${dup_id})-*" 2>/dev/null | sort)

    # Pick the newer artifact (by created date in frontmatter) to renumber
    newest_dir=""
    newest_date="0000-00-00"
    for dir in $dirs; do
      md_file=$(find "$dir" -maxdepth 1 -name "*.md" -print -quit 2>/dev/null)
      [ -n "$md_file" ] || continue
      created=$(grep "^created:" "$md_file" 2>/dev/null | head -1 | sed 's/created: *//' | tr -d '"')
      [ -z "$created" ] && created="9999-99-99"  # no date = treat as newest
      if [[ "$created" > "$newest_date" ]]; then
        newest_date="$created"
        newest_dir="$dir"
      fi
    done

    if [ -z "$newest_dir" ]; then
      echo "Warning: could not determine which $dup_id to renumber, skipping"
      continue
    fi

    # Extract the title from the dir name to identify which one we're renumbering
    newest_dirname="$(basename "$newest_dir")"
    newest_title="${newest_dirname#*(${dup_id})-}"

    new_num=$(bash "$ALLOCATOR" "$TYPE" 2>/dev/null) || {
      echo "Error: could not allocate next number for $TYPE" >&2
      continue
    }
    # In dry-run mode, the allocator sees unchanged state each time.
    # Bump past any numbers we've already "allocated" this run.
    alloc_var="_ALLOC_${TYPE}"
    prev_alloc="${!alloc_var:-}"
    if [ -n "$prev_alloc" ] && (( 10#$new_num <= 10#$prev_alloc )); then
      new_num=$(printf "%03d" $(( 10#$prev_alloc + 1 )))
    fi
    eval "$alloc_var=$new_num"
    new_id="${TYPE}-${new_num}"

    echo "=== Renumbering $dup_id ($newest_title) → $new_id ==="
    bash "$RENUMBER" "$dup_id" "$new_id" --source-dir "$newest_dir" $DRY_RUN || {
      echo "Warning: renumber failed for $dup_id → $new_id"
      continue
    }
    FIXED=$((FIXED + 1))
    echo ""
  done <<< "$dup_output"
fi

echo "Summary: $FIXED artifact(s) renumbered${DRY_RUN:+ (dry-run)}."
