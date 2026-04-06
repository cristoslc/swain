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

# Check for stale tk claim locks (dead owner PID or age >1 hour)
check_stale_tk_locks() {
  local root="$1"
  local locks_dir="$root/.tickets/.locks"

  if [[ ! -d "$locks_dir" ]]; then
    printf "stale_tk_locks\tclean\n"
    return
  fi

  local found=0
  for lock_dir in "$locks_dir"/*/; do
    [[ -d "$lock_dir" ]] || continue
    local owner_file="$lock_dir/owner"
    local task_id
    task_id=$(basename "$lock_dir")

    if [[ -f "$owner_file" ]]; then
      local pid
      pid=$(cat "$owner_file" 2>/dev/null | tr -d '[:space:]')
      if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
        continue  # alive — legitimate lock
      fi
      printf "stale_tk_locks\tfound\ttask %s locked by dead PID %s\n" "$task_id" "$pid"
    else
      # Lock dir exists but no owner file — treat as stale
      printf "stale_tk_locks\tfound\ttask %s lock has no owner file\n" "$task_id"
    fi
    found=$((found + 1))
  done

  [[ $found -eq 0 ]] && printf "stale_tk_locks\tclean\n"
}

# Check for dangling worktrees (missing directory or merged branches)
check_dangling_worktrees() {
  local root="$1"
  local found=0
  local in_first=1
  local path="" branch=""

  while IFS= read -r line; do
    if [[ "$line" == worktree\ * ]]; then
      path="${line#worktree }"
    elif [[ "$line" == branch\ * ]]; then
      branch="${line#branch }"
    elif [[ -z "$line" ]]; then
      if [[ $in_first -eq 1 ]]; then
        in_first=0
        path=""
        branch=""
        continue
      fi
      if [[ -n "$path" ]]; then
        if [[ ! -d "$path" ]]; then
          printf "dangling_worktrees\tfound\tmissing directory: %s (branch: %s)\n" "$path" "${branch:-detached}"
          found=$((found + 1))
        else
          # Cross-reference with runtime sessions (best-effort)
          local has_live_session=false
          if [[ -d "$HOME/.claude/sessions" ]]; then
            for sess in "$HOME/.claude/sessions"/*.json; do
              [[ -f "$sess" ]] || continue
              local sess_cwd sess_pid
              sess_cwd=$(grep -o '"cwd":"[^"]*"' "$sess" 2>/dev/null | head -1 | sed 's/"cwd":"//;s/"$//')
              if [[ "$sess_cwd" == "$path" ]]; then
                sess_pid=$(grep -o '"pid":[0-9]*' "$sess" 2>/dev/null | head -1 | sed 's/"pid"://')
                if [[ -n "$sess_pid" ]] && kill -0 "$sess_pid" 2>/dev/null; then
                  has_live_session=true
                fi
              fi
            done
          fi

          if [[ "$has_live_session" == "true" ]]; then
            continue
          fi

          local wt_status
          wt_status=$(git -C "$path" status --porcelain 2>/dev/null | head -5)
          if [[ -n "$wt_status" ]]; then
            local change_count
            change_count=$(git -C "$path" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
            printf "dangling_worktrees\tfound\tuncommitted changes (%s files) in %s\n" "$change_count" "$path"
            found=$((found + 1))
          fi
        fi
      fi
      path=""
      branch=""
    fi
  done < <(git -C "$root" worktree list --porcelain 2>/dev/null; echo "")

  [[ $found -eq 0 ]] && printf "dangling_worktrees\tclean\n"
}

# Check for orphaned MCP servers associated with this project
# Best-effort: matches process names containing "mcp" with cwd matching project root
check_orphaned_mcp() {
  local root="$1"
  local real_root
  real_root=$(cd "$root" && pwd -P 2>/dev/null || echo "$root")
  local found=0

  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    local pid cmd
    pid=$(echo "$line" | awk '{print $1}')
    cmd=$(echo "$line" | awk '{$1=""; print $0}' | sed 's/^ //')

    local proc_cwd=""
    if [[ -d "/proc/$pid" ]]; then
      proc_cwd=$(readlink "/proc/$pid/cwd" 2>/dev/null || echo "")
    else
      proc_cwd=$(lsof -p "$pid" -Fn 2>/dev/null | grep '^n/' | head -1 | sed 's/^n//' || echo "")
    fi

    if [[ "$proc_cwd" == "$real_root"* ]]; then
      printf "orphaned_mcp\tfound\tPID %s: %s\n" "$pid" "$cmd"
      found=$((found + 1))
    fi
  done < <(ps aux 2>/dev/null | grep -i '[m]cp.*server\|[m]cp.*gateway' | grep -iv 'docker\|containerd' | awk '{print $2, $11, $12, $13}' || true)

  [[ $found -eq 0 ]] && printf "orphaned_mcp\tclean\n"
}

# Run all crash debris checks and return combined results
# $1 = project root
# Returns: only "found" lines (tab-separated), or nothing if clean (AC5 silent fast path)
check_all_crash_debris() {
  local root="$1"
  local output=""

  output+=$(check_git_index_lock "$root" 2>/dev/null)
  output+=$'\n'
  output+=$(check_interrupted_git_ops "$root" 2>/dev/null)
  output+=$'\n'
  output+=$(check_stale_tk_locks "$root" 2>/dev/null)
  output+=$'\n'
  output+=$(check_dangling_worktrees "$root" 2>/dev/null)
  output+=$'\n'
  output+=$(check_orphaned_mcp "$root" 2>/dev/null)

  # AC5: silent fast path — only emit lines with findings, nothing if clean
  echo "$output" | grep 'found' || true
}
