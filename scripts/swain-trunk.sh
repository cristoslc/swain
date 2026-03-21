#!/usr/bin/env bash
# swain-trunk.sh — Auto-detect the trunk (development) branch from git state.
# EPIC-029: No configuration required for the common case.
#
# Usage:
#   TRUNK=$(bash scripts/swain-trunk.sh)
#   git merge "origin/$TRUNK" --no-edit
#
# Detection logic:
#   1. If swain.settings.json has git.trunk, use that (explicit override).
#   2. If NOT in a worktree (GIT_COMMON_DIR == GIT_DIR), current branch IS trunk.
#   3. If IN a worktree (GIT_COMMON_DIR != GIT_DIR), read the main worktree's branch.
#   4. Fallback: "trunk" if detection fails (detached HEAD, unusual state).

set -euo pipefail

_swain_trunk_detect() {
  local repo_root
  repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "trunk"; return; }

  # 1. Settings override
  local settings_file="$repo_root/swain.settings.json"
  if [ -f "$settings_file" ]; then
    local override
    override=$(python3 -c "
import json, sys
try:
    d = json.load(open(sys.argv[1]))
    v = d.get('git', {}).get('trunk', '')
    if v: print(v)
except Exception:
    pass
" "$settings_file" 2>/dev/null) || true
    if [ -n "${override:-}" ]; then
      echo "$override"
      return
    fi
  fi

  # 2/3. Auto-detect from git worktree state
  local git_common git_dir
  git_common="$(git rev-parse --git-common-dir 2>/dev/null)" || { echo "trunk"; return; }
  git_dir="$(git rev-parse --git-dir 2>/dev/null)" || { echo "trunk"; return; }

  # Normalize paths for comparison (resolve symlinks, trailing slashes)
  git_common="$(cd "$git_common" 2>/dev/null && pwd -P)"
  git_dir="$(cd "$git_dir" 2>/dev/null && pwd -P)"

  if [ "$git_common" = "$git_dir" ]; then
    # Not in a worktree — current branch IS trunk
    local branch
    branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null)" || { echo "trunk"; return; }
    if [ "$branch" = "HEAD" ]; then
      # Detached HEAD — fallback
      echo "trunk"
    else
      echo "$branch"
    fi
  else
    # In a worktree — trunk is the main worktree's branch
    local main_head="$git_common/HEAD"
    if [ -f "$main_head" ]; then
      local ref
      ref="$(cat "$main_head")"
      if [[ "$ref" == ref:\ refs/heads/* ]]; then
        echo "${ref#ref: refs/heads/}"
      else
        # Detached HEAD in main worktree — fallback
        echo "trunk"
      fi
    else
      echo "trunk"
    fi
  fi
}

_swain_trunk_detect
