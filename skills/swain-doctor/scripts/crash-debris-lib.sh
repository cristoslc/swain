#!/usr/bin/env bash
# crash-debris-lib.sh — standalone crash debris detection functions (SPEC-182)
#
# Each function takes a project root path as $1 and prints findings
# to stdout as tab-separated lines: TYPE\tSTATUS\tDETAIL
#
# STATUS values: found, clean
# When STATUS=found, DETAIL contains human-readable description
#
# These functions are sourceable by both the pre-runtime script
# (SPEC-180) and swain-doctor (SPEC-192).

# Check for stale .git/index.lock
# $1 = project root (must contain .git/ or be a worktree)
check_git_index_lock() {
  local root="$1"
  local git_dir="$root/.git"

  # Handle worktree: .git may be a file pointing to the real git dir
  if [[ -f "$git_dir" ]]; then
    git_dir=$(sed 's/^gitdir: //' "$git_dir")
    # Resolve relative paths
    [[ "$git_dir" != /* ]] && git_dir="$root/$git_dir"
  fi

  local lock="$git_dir/index.lock"
  if [[ ! -f "$lock" ]]; then
    printf "git_index_lock\tclean\n"
    return
  fi

  # Check if creating PID is still alive
  local pid
  pid=$(cat "$lock" 2>/dev/null | head -1 | grep -oE '^[0-9]+$' || echo "")
  if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
    # PID alive — lock is legitimate
    printf "git_index_lock\tclean\tlock held by live PID %s\n" "$pid"
    return
  fi

  printf "git_index_lock\tfound\t%s (owner PID %s not running)\n" "$lock" "${pid:-unknown}"
}

# Check for interrupted git operations (merge, rebase, cherry-pick)
check_interrupted_git_ops() {
  local root="$1"
  local git_dir="$root/.git"

  if [[ -f "$git_dir" ]]; then
    git_dir=$(sed 's/^gitdir: //' "$git_dir")
    [[ "$git_dir" != /* ]] && git_dir="$root/$git_dir"
  fi

  local found=()

  [[ -f "$git_dir/MERGE_HEAD" ]] && found+=("interrupted merge (MERGE_HEAD)")
  [[ -d "$git_dir/rebase-merge" ]] && found+=("interrupted rebase (rebase-merge/)")
  [[ -d "$git_dir/rebase-apply" ]] && found+=("interrupted rebase-apply (rebase-apply/)")
  [[ -f "$git_dir/CHERRY_PICK_HEAD" ]] && found+=("interrupted cherry-pick (CHERRY_PICK_HEAD)")

  if [[ ${#found[@]} -eq 0 ]]; then
    printf "interrupted_git_ops\tclean\n"
    return
  fi

  for item in "${found[@]}"; do
    printf "interrupted_git_ops\tfound\t%s\n" "$item"
  done
}
