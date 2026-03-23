#!/usr/bin/env bash
# detect-duplicate-numbers.sh — Find duplicate artifact numbers across phase dirs
#
# Usage: detect-duplicate-numbers.sh [TYPE ...]
#   TYPE: SPEC, EPIC, INITIATIVE, VISION, SPIKE, ADR, PERSONA, RUNBOOK, DESIGN, JOURNEY, TRAIN
#   No args = scan all types.
#
# Exit 0 + no output if no duplicates. Exit 1 + report if duplicates found.
# A "duplicate" is two directories with the same TYPE-NNN but DIFFERENT titles.
# Same TYPE-NNN with the same title in different phase dirs = phase transition in progress, not a dup.
#
# SPEC-158 / EPIC-043

set -euo pipefail

git rev-parse --git-dir >/dev/null 2>&1 || {
  echo "Error: not inside a git repository" >&2
  exit 1
}

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# --- Type-to-directory mapping ---
type_to_dir() {
  case "$1" in
    SPEC)       echo "spec" ;;
    EPIC)       echo "epic" ;;
    INITIATIVE) echo "initiative" ;;
    VISION)     echo "vision" ;;
    SPIKE)      echo "research" ;;
    ADR)        echo "adr" ;;
    PERSONA)    echo "persona" ;;
    RUNBOOK)    echo "runbook" ;;
    DESIGN)     echo "design" ;;
    JOURNEY)    echo "journey" ;;
    TRAIN)      echo "train" ;;
    *) return 1 ;;
  esac
}

ALL_TYPES="SPEC EPIC INITIATIVE VISION SPIKE ADR PERSONA RUNBOOK DESIGN JOURNEY TRAIN"

# --- Parse args: optional type filter ---
if [ $# -gt 0 ]; then
  TYPES=""
  for arg in "$@"; do
    TYPE_UPPER="$(echo "$arg" | tr '[:lower:]' '[:upper:]')"
    if type_to_dir "$TYPE_UPPER" >/dev/null 2>&1; then
      TYPES="$TYPES $TYPE_UPPER"
    else
      echo "Error: unrecognized type '$arg'" >&2
      exit 1
    fi
  done
else
  TYPES="$ALL_TYPES"
fi

FOUND_DUPS=0
OUTPUT=""
TMPFILE="$(mktemp)"
trap 'rm -f "$TMPFILE"' EXIT

for TYPE in $TYPES; do
  DIR_NAME="$(type_to_dir "$TYPE")"
  DOCS_DIR="$REPO_ROOT/docs/$DIR_NAME"
  [ -d "$DOCS_DIR" ] || continue

  # Collect: "number<TAB>title<TAB>relative-path" for each artifact dir
  > "$TMPFILE"
  while IFS= read -r dir_path; do
    dir_name="$(basename "$dir_path")"
    if [[ "$dir_name" =~ ^\(${TYPE}-([0-9]+)\)-(.+)$ ]]; then
      num="${BASH_REMATCH[1]}"
      title="${BASH_REMATCH[2]}"
      rel_path="${dir_path#"$REPO_ROOT/"}"
      printf '%s\t%s\t%s\n' "$num" "$title" "$rel_path" >> "$TMPFILE"
    fi
  done < <(find "$DOCS_DIR" -maxdepth 3 -type d -name "(${TYPE}-*" 2>/dev/null | sort)

  # Find numbers that appear more than once
  dup_nums="$(cut -f1 "$TMPFILE" | sort | uniq -d)"
  [ -z "$dup_nums" ] && continue

  # For each dup number, check if titles differ
  for num in $dup_nums; do
    titles="$(grep "^${num}	" "$TMPFILE" | cut -f2 | sort -u)"
    title_count="$(echo "$titles" | wc -l | tr -d ' ')"
    if [ "$title_count" -gt 1 ]; then
      # Different titles = real duplicate
      FOUND_DUPS=1
      paths="$(grep "^${num}	" "$TMPFILE" | cut -f3 | tr '\n' ' ')"
      OUTPUT="${OUTPUT}DUPLICATE ${TYPE}-${num}: ${paths}\n"
    fi
    # Same title across phases = transition in progress, not a dup
  done
done

if [ "$FOUND_DUPS" -ne 0 ]; then
  printf "%b" "$OUTPUT"
  exit 1
fi

exit 0
