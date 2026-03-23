#!/usr/bin/env bash
# next-artifact-number.sh — Allocate the next artifact number for a given type
#
# Usage: next-artifact-number.sh <TYPE>
#   TYPE: SPEC | EPIC | INITIATIVE | VISION | SPIKE | ADR | PERSONA | RUNBOOK | DESIGN | JOURNEY | TRAIN
#
# Scans all worktrees + trunk branch to find the highest existing number,
# then returns max+1 zero-padded to 3 digits.
#
# SPEC-156 / EPIC-043

set -euo pipefail

# --- Validate we're in a git repo ---
git rev-parse --git-dir >/dev/null 2>&1 || {
  echo "Error: not inside a git repository" >&2
  exit 1
}

# --- Validate and normalize TYPE argument ---
if [ $# -lt 1 ] || [ -z "${1:-}" ]; then
  echo "Usage: next-artifact-number.sh <TYPE>" >&2
  echo "  TYPE: SPEC | EPIC | INITIATIVE | VISION | SPIKE | ADR | PERSONA | RUNBOOK | DESIGN | JOURNEY | TRAIN" >&2
  exit 1
fi

TYPE="$(echo "$1" | tr '[:lower:]' '[:upper:]')"

# --- Map TYPE to docs subdirectory name ---
case "$TYPE" in
  SPEC)       DIR_NAME="spec" ;;
  EPIC)       DIR_NAME="epic" ;;
  INITIATIVE) DIR_NAME="initiative" ;;
  VISION)     DIR_NAME="vision" ;;
  SPIKE)      DIR_NAME="research" ;;
  ADR)        DIR_NAME="adr" ;;
  PERSONA)    DIR_NAME="persona" ;;
  RUNBOOK)    DIR_NAME="runbook" ;;
  DESIGN)     DIR_NAME="design" ;;
  JOURNEY)    DIR_NAME="journey" ;;
  TRAIN)      DIR_NAME="train" ;;
  *)
    echo "Error: unrecognized type '$TYPE'" >&2
    echo "  Valid types: SPEC EPIC INITIATIVE VISION SPIKE ADR PERSONA RUNBOOK DESIGN JOURNEY TRAIN" >&2
    exit 1
    ;;
esac

MAX_NUM=0

# --- Helper: update MAX_NUM from a line containing TYPE-NNN ---
update_max() {
  local line="$1"
  if [[ "$line" =~ ${TYPE}-([0-9]+) ]]; then
    local num=$((10#${BASH_REMATCH[1]}))
    if (( num > MAX_NUM )); then
      MAX_NUM=$num
    fi
  fi
}

# --- Scan all worktrees' filesystems ---
while IFS= read -r wt_path; do
  [ -d "$wt_path" ] || continue  # skip inaccessible/stale worktrees
  local_docs="$wt_path/docs/$DIR_NAME"
  [ -d "$local_docs" ] || continue
  while IFS= read -r found_path; do
    update_max "$found_path"
  done < <(find "$local_docs" -maxdepth 4 -name "(${TYPE}-*" 2>/dev/null)
done < <(git worktree list --porcelain 2>/dev/null | sed -n 's/^worktree //p')

# --- Scan trunk (or fallback branch) via git ls-tree ---
BRANCH=""
for candidate in trunk main; do
  if git rev-parse --verify "$candidate" >/dev/null 2>&1; then
    BRANCH="$candidate"
    break
  fi
done
# Fallback: current branch's upstream
if [ -z "$BRANCH" ]; then
  BRANCH="$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)"
fi

if [ -n "$BRANCH" ]; then
  while IFS= read -r tree_path; do
    update_max "$tree_path"
  done < <(git ls-tree -r --name-only "$BRANCH" -- "docs/$DIR_NAME/" 2>/dev/null)
fi

# --- Output next number, zero-padded to 3 digits ---
NEXT=$(( MAX_NUM + 1 ))
printf "%03d\n" "$NEXT"
