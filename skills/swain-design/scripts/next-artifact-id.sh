#!/usr/bin/env bash
# next-artifact-id.sh — cross-branch artifact ID allocation (SPEC-193)
#
# Scans ALL local branches and the working tree to find the highest
# existing artifact ID for a given type prefix, then returns max + 1.
# This prevents ID collisions in worktree-based parallel workflows.
#
# Usage: next-artifact-id.sh <PREFIX>
#   PREFIX: SPEC, EPIC, INITIATIVE, VISION, SPIKE, ADR, PERSONA, RUNBOOK, DESIGN, JOURNEY, TRAIN
#
# Output: a single integer (the next available ID)
# Exit: 0 on success

set -euo pipefail

PREFIX="${1:-}"
if [[ -z "$PREFIX" ]]; then
  echo "Usage: next-artifact-id.sh <PREFIX>" >&2
  echo "  PREFIX: SPEC, EPIC, INITIATIVE, VISION, SPIKE, ADR, etc." >&2
  exit 1
fi

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# Map prefix to docs subdirectory
case "$PREFIX" in
  SPEC)       subdir="spec" ;;
  EPIC)       subdir="epic" ;;
  INITIATIVE) subdir="initiative" ;;
  VISION)     subdir="vision" ;;
  SPIKE)      subdir="spike" ;;
  ADR)        subdir="adr" ;;
  PERSONA)    subdir="persona" ;;
  RUNBOOK)    subdir="runbook" ;;
  DESIGN)     subdir="design" ;;
  JOURNEY)    subdir="journey" ;;
  TRAIN)      subdir="train" ;;
  *)          subdir="" ;;
esac

max_id=0

doc_path="docs/${subdir:+$subdir/}"

# 1. Scan all local branches in a single pass
#    Collect all branch tips, then batch ls-tree via xargs for speed
all_ids=$(
  git for-each-ref --format='%(refname:short)' refs/heads/ 2>/dev/null |
  xargs -I{} git ls-tree -r --name-only {} -- "$doc_path" 2>/dev/null |
  grep "${PREFIX}-[0-9]" |
  sed -n "s/.*${PREFIX}-0*\([0-9][0-9]*\).*/\1/p" |
  sort -rn |
  head -1
) || true

if [[ -n "$all_ids" ]] && [[ "$all_ids" -gt "$max_id" ]]; then
  max_id="$all_ids"
fi

# 2. Scan the current working tree (catches uncommitted artifacts)
if [[ -n "$subdir" ]]; then
  search_dir="$REPO_ROOT/docs/$subdir"
else
  search_dir="$REPO_ROOT/docs"
fi

if [[ -d "$search_dir" ]]; then
  local_max=$(
    find "$search_dir" -name "*${PREFIX}-*" -type f 2>/dev/null |
    sed -n "s/.*${PREFIX}-0*\([0-9][0-9]*\).*/\1/p" |
    sort -rn |
    head -1
  ) || true

  if [[ -n "$local_max" ]] && [[ "$local_max" -gt "$max_id" ]]; then
    max_id="$local_max"
  fi
fi

echo $((max_id + 1))
