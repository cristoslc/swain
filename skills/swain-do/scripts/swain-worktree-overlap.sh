#!/usr/bin/env bash
# swain-worktree-overlap.sh — SPEC-195: Check for existing worktrees matching a spec/context
#
# Usage:
#   swain-worktree-overlap.sh SPEC-194        # check for worktrees matching SPEC-194
#   swain-worktree-overlap.sh "fast greeting"  # check for worktrees matching text
#
# Output (JSON):
#   { "found": true, "worktrees": [{ "path": "...", "branch": "..." }] }
#   { "found": false, "worktrees": [] }

set +e

SEARCH_TERM="${1:-}"
if [[ -z "$SEARCH_TERM" ]]; then
  echo '{"found":false,"worktrees":[],"error":"no search term provided"}'
  exit 1
fi

# Normalize search term for case-insensitive matching
SEARCH_LOWER=$(echo "$SEARCH_TERM" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')

MATCHES=()

# Parse git worktree list --porcelain
while IFS= read -r line; do
  case "$line" in
    "worktree "*)
      current_path="${line#worktree }"
      current_branch=""
      ;;
    "branch "*)
      current_branch="${line#branch refs/heads/}"
      # Check if branch name contains the search term
      branch_lower=$(echo "$current_branch" | tr '[:upper:]' '[:lower:]')
      if echo "$branch_lower" | grep -q "$SEARCH_LOWER"; then
        MATCHES+=("{\"path\":\"$current_path\",\"branch\":\"$current_branch\"}")
      fi
      ;;
  esac
done < <(git worktree list --porcelain 2>/dev/null)

# Build JSON output
if [[ ${#MATCHES[@]} -eq 0 ]]; then
  echo '{"found":false,"worktrees":[]}'
else
  echo -n '{"found":true,"worktrees":['
  for ((i=0; i<${#MATCHES[@]}; i++)); do
    [[ $i -gt 0 ]] && echo -n ","
    echo -n "${MATCHES[$i]}"
  done
  echo ']}'
fi
