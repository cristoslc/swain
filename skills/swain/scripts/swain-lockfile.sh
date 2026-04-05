#!/usr/bin/env bash
# swain-lockfile.sh — Lockfile claiming, releasing, and stale detection for worktrees
# SPEC-244 | EPIC-056
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
LOCKFILE_DIR="${SWAIN_LOCKFILE_DIR:-$REPO_ROOT/.agents/worktrees}"

# --- Helpers ---

_lockfile_path() {
  echo "$LOCKFILE_DIR/$1.lock"
}

_ensure_dir() {
  mkdir -p "$LOCKFILE_DIR"
}

_pid_alive() {
  local p="$1"
  kill -0 "$p" 2>/dev/null
}

_pane_alive() {
  local pane="$1"
  [ -z "$pane" ] && return 1
  [ -z "${TMUX:-}" ] && return 1  # not in tmux, can't check
  tmux list-panes -a -F '#{pane_id}' 2>/dev/null | grep -qF "$pane"
}

_is_stale() {
  local lockfile="$1"
  [ ! -f "$lockfile" ] && return 0  # missing = stale

  local pid user_field exe pane_id
  # shellcheck disable=SC1090
  source "$lockfile"

  # PID alive?
  if _pid_alive "${pid:-0}"; then
    # Check for PID recycling: user and exe must match
    local current_user
    current_user="$(whoami)"
    if [ "${user:-}" != "$current_user" ]; then
      return 0  # stale: different user owns the PID now
    fi
    # PID alive and user matches -> not stale
    return 1
  fi

  # PID dead. In tmux, also check pane.
  if [ -n "${TMUX:-}" ] && [ -n "${pane_id:-}" ]; then
    if _pane_alive "$pane_id"; then
      return 1  # pane alive, might be restarting — not stale yet
    fi
  fi

  # PID dead (and pane dead if applicable) -> stale
  return 0
}

# --- Commands ---

cmd_claim() {
  local branch="$1" worktree_path="$2" purpose="${3:-}"
  _ensure_dir

  local lockfile
  lockfile="$(_lockfile_path "$branch")"

  # Check existing claim
  if [ -f "$lockfile" ]; then
    if ! _is_stale "$lockfile"; then
      echo "ERROR: Worktree '$branch' already claimed (lockfile exists and is active)" >&2
      return 1
    fi
    # Stale — remove and reclaim
    rm -f "$lockfile"
  fi

  # Atomic write: temp file + mv
  local tmpfile
  tmpfile="$(mktemp "$LOCKFILE_DIR/.claim-XXXXXX")"
  cat > "$tmpfile" << EOF
version=1
pid=$$
user=$(whoami)
exe=${SWAIN_RUNTIME:-unknown}
pane_id=${TMUX_PANE:-}
claimed_at=$(date -Iseconds)
worktree_path=$worktree_path
purpose="$purpose"
status=active
EOF

  mv "$tmpfile" "$lockfile"
  echo "Claimed: $branch -> $worktree_path"
}

cmd_release() {
  local branch="$1"
  local lockfile
  lockfile="$(_lockfile_path "$branch")"

  if [ ! -f "$lockfile" ]; then
    return 0  # no-op
  fi

  rm -f "$lockfile"
  echo "Released: $branch"
}

cmd_is_stale() {
  local branch="$1"
  local lockfile
  lockfile="$(_lockfile_path "$branch")"

  if [ ! -f "$lockfile" ]; then
    echo "No lockfile for '$branch'" >&2
    return 0  # no lockfile = effectively stale
  fi

  if _is_stale "$lockfile"; then
    echo "Stale: $branch"
    return 0
  else
    echo "Active: $branch"
    return 1
  fi
}

cmd_list() {
  _ensure_dir

  local first=true
  echo "["
  for lockfile in "$LOCKFILE_DIR"/*.lock; do
    [ -f "$lockfile" ] || continue

    local branch
    branch="$(basename "$lockfile" .lock)"

    # Source to get fields
    local version pid user exe pane_id claimed_at worktree_path purpose status ready_for_cleanup ready_commit
    version="" pid="" user="" exe="" pane_id="" claimed_at="" worktree_path="" purpose="" status="" ready_for_cleanup="" ready_commit=""
    # shellcheck disable=SC1090
    source "$lockfile"

    local lock_status="active"
    if _is_stale "$lockfile"; then
      lock_status="stale"
    elif [ "${ready_for_cleanup:-}" = "true" ]; then
      lock_status="ready"
    fi

    # Calculate age
    local age_seconds=0
    if [ -n "$claimed_at" ]; then
      local claimed_epoch now_epoch
      claimed_epoch="$(date -j -f "%Y-%m-%dT%H:%M:%S%z" "$claimed_at" "+%s" 2>/dev/null || echo 0)"
      now_epoch="$(date +%s)"
      age_seconds=$(( now_epoch - claimed_epoch ))
    fi

    if [ "$first" = true ]; then
      first=false
    else
      echo ","
    fi

    # Strip quotes from purpose if present
    purpose="${purpose#\"}"
    purpose="${purpose%\"}"

    cat << ENTRY_EOF
  {
    "branch": "$branch",
    "status": "$lock_status",
    "pid": ${pid:-0},
    "user": "${user:-}",
    "exe": "${exe:-}",
    "pane_id": "${pane_id:-}",
    "worktree_path": "${worktree_path:-}",
    "purpose": "$purpose",
    "claimed_at": "${claimed_at:-}",
    "age_seconds": $age_seconds,
    "ready_for_cleanup": ${ready_for_cleanup:-false},
    "ready_commit": "${ready_commit:-}"
  }
ENTRY_EOF
  done
  echo ""
  echo "]"
}

cmd_mark_ready() {
  local branch="$1"
  local lockfile
  lockfile="$(_lockfile_path "$branch")"

  if [ ! -f "$lockfile" ]; then
    echo "ERROR: No lockfile for '$branch'" >&2
    return 1
  fi

  # Get current HEAD
  local head_commit
  head_commit="$(git rev-parse HEAD 2>/dev/null || echo "unknown")"

  # Append ready fields (atomic rewrite)
  local tmpfile
  tmpfile="$(mktemp "$LOCKFILE_DIR/.ready-XXXXXX")"

  # Copy existing content, filter out any previous ready fields
  grep -v '^ready_for_cleanup=' "$lockfile" | grep -v '^ready_commit=' > "$tmpfile"

  # Append ready fields
  echo "ready_for_cleanup=true" >> "$tmpfile"
  echo "ready_commit=$head_commit" >> "$tmpfile"

  mv "$tmpfile" "$lockfile"
  echo "Marked ready: $branch (commit: $head_commit)"
}

cmd_verify_ready() {
  local branch="$1"
  local lockfile
  lockfile="$(_lockfile_path "$branch")"

  if [ ! -f "$lockfile" ]; then
    echo "ERROR: No lockfile for '$branch'" >&2
    return 2
  fi

  # Source lockfile
  local ready_for_cleanup ready_commit
  ready_for_cleanup="" ready_commit=""
  # shellcheck disable=SC1090
  source "$lockfile"

  if [ "${ready_for_cleanup:-}" != "true" ]; then
    echo "Not marked ready: $branch"
    return 2
  fi

  local current_head
  current_head="$(git rev-parse HEAD 2>/dev/null || echo "unknown")"

  if [ "$ready_commit" = "$current_head" ]; then
    echo "Verified: $branch (commit matches)"
    return 0
  else
    echo "Mismatch: $branch (ready=$ready_commit, current=$current_head)"
    return 1
  fi
}

# --- Main dispatch ---

cmd="${1:-help}"
shift || true

case "$cmd" in
  claim)        cmd_claim "$@" ;;
  release)      cmd_release "$@" ;;
  is-stale)     cmd_is_stale "$@" ;;
  list)         cmd_list ;;
  mark-ready)   cmd_mark_ready "$@" ;;
  verify-ready) cmd_verify_ready "$@" ;;
  help)
    echo "Usage: swain-lockfile.sh <command> [args]"
    echo ""
    echo "Commands:"
    echo "  claim <branch> <worktree-path> [purpose]  Claim a worktree"
    echo "  release <branch>                           Release a claim"
    echo "  is-stale <branch>                          Check if claim is stale (exit 0=stale, 1=active)"
    echo "  list                                       List all lockfiles (JSON)"
    echo "  mark-ready <branch>                        Mark lockfile ready_for_cleanup"
    echo "  verify-ready <branch>                      Verify ready commit matches HEAD"
    echo ""
    ;;
  *)
    echo "Unknown command: $cmd" >&2
    exit 1
    ;;
esac
