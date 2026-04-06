#!/usr/bin/env bash
# swain-session-preflight.sh — read-only session state scanner
#
# Consolidates all session startup reads into a single script.
# Replaces the subprocess chain: greeting → bootstrap → tab-name.
# This script NEVER mutates state (no tab renames, no file writes,
# no lock cleanup). The caller applies mutations using the JSON output.
#
# Usage: bash swain-session-preflight.sh [--repo-root /path] [--path /dir]
#
# JSON schema (all keys present, some may be null on error):
#
#   git.repo_root          string  — resolved repository root
#   git.branch             string  — current branch name
#   git.dirty              bool    — uncommitted changes present
#   git.worktree.isolated  bool    — running inside a linked worktree
#   git.worktree.path      string  — worktree path (null if not isolated)
#
#   tmux.active            bool    — running inside a tmux session
#   tmux.tab_format        string  — tab name format from settings
#   tmux.tab_name          string  — computed tab name (not applied)
#
#   session.focus          string  — focus lane from session.json
#   session.bookmark       string  — bookmark note from session.json
#   session.last_branch    string  — last branch from session.json
#
#   prev_session.exists    bool    — session-state.json found
#   prev_session.status    string  — "active" | "stale" | "closed" | "none"
#   prev_session.session_id string — session identifier
#   prev_session.focus_lane string — focus lane from state
#   prev_session.phase     string  — lifecycle phase
#   prev_session.start_time string — ISO timestamp
#   prev_session.end_time  string  — ISO timestamp (null if active)
#   prev_session.decisions_made int — count
#   prev_session.walkaway  string  — walk-away note (null if none)
#
#   warnings               array   — preflight warnings (read-only observations)
#
# Exit: always 0 (partial results on individual check failures)

set -euo pipefail

REPO_ROOT=""
DETECT_PATH=""

while [ $# -gt 0 ]; do
  case "$1" in
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    --path) DETECT_PATH="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if [ -z "$REPO_ROOT" ]; then
  REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
fi

if [ -z "$DETECT_PATH" ]; then
  DETECT_PATH="$REPO_ROOT"
fi

# --- Collector variables ---

WARNINGS_RAW=""
add_warning() {
  WARNINGS_RAW="${WARNINGS_RAW}${1}
"
}

# --- Git state ---
check_git() {
  GIT_BRANCH=$(git -C "$DETECT_PATH" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
  GIT_DIRTY=false
  if [ -n "$(git -C "$DETECT_PATH" status --porcelain 2>/dev/null | head -1)" ]; then
    GIT_DIRTY=true
  fi

  GIT_WT_ISOLATED=false
  GIT_WT_PATH=""
  GIT_COMMON=$(git -C "$DETECT_PATH" rev-parse --git-common-dir 2>/dev/null || true)
  GIT_DIR=$(git -C "$DETECT_PATH" rev-parse --git-dir 2>/dev/null || true)
  if [ -n "$GIT_COMMON" ] && [ -n "$GIT_DIR" ] && [ "$GIT_COMMON" != "$GIT_DIR" ]; then
    GIT_WT_ISOLATED=true
    GIT_WT_PATH="$DETECT_PATH"
  fi
}

# --- Tmux state (read-only — no renames) ---
check_tmux() {
  TMUX_ACTIVE=false
  TMUX_TAB_FORMAT=""
  TMUX_TAB_NAME=""

  if [ -n "${TMUX:-}" ]; then
    TMUX_ACTIVE=true
  fi

  # Read tab format from settings (project, then user)
  SETTINGS_PROJECT="$REPO_ROOT/swain.settings.json"
  SETTINGS_USER="${XDG_CONFIG_HOME:-$HOME/.config}/swain/settings.json"
  TMUX_TAB_FORMAT='{project} @ {branch}'

  if [ -f "$SETTINGS_USER" ] && command -v jq &>/dev/null; then
    val=$(jq -r '.terminal.tabNameFormat // empty' "$SETTINGS_USER" 2>/dev/null || true)
    [ -n "$val" ] && TMUX_TAB_FORMAT="$val"
  fi
  if [ -f "$SETTINGS_PROJECT" ] && command -v jq &>/dev/null; then
    val=$(jq -r '.terminal.tabNameFormat // empty' "$SETTINGS_PROJECT" 2>/dev/null || true)
    [ -n "$val" ] && TMUX_TAB_FORMAT="$val"
  fi

  # Compute tab name from git context (same logic as tab-name.sh auto_title)
  local common_dir repo_root project
  common_dir=$(git -C "$DETECT_PATH" rev-parse --git-common-dir 2>/dev/null || true)
  if [ -n "$common_dir" ]; then
    repo_root=$(cd "$DETECT_PATH" && cd "$common_dir/.." && pwd 2>/dev/null || true)
  fi
  project=$(basename "${repo_root:-unknown}")

  TMUX_TAB_NAME="${TMUX_TAB_FORMAT//\{project\}/$project}"
  TMUX_TAB_NAME="${TMUX_TAB_NAME//\{branch\}/$GIT_BRANCH}"
}

# --- Session.json (bookmark, focus, last branch) ---
check_session_json() {
  SESSION_FOCUS=""
  SESSION_BOOKMARK=""
  SESSION_LAST_BRANCH=""

  local session_file="$REPO_ROOT/.agents/session.json"

  if [ -f "$session_file" ] && command -v jq &>/dev/null; then
    SESSION_FOCUS=$(jq -r '.focus_lane // empty' "$session_file" 2>/dev/null || true)
    SESSION_BOOKMARK=$(jq -r '.bookmark.note // empty' "$session_file" 2>/dev/null || true)
    SESSION_LAST_BRANCH=$(jq -r '.lastBranch // empty' "$session_file" 2>/dev/null || true)
  fi
}

# --- Session state (previous session resume context) ---
check_session_state() {
  PREV_EXISTS=false
  PREV_STATUS="none"
  PREV_SESSION_ID=""
  PREV_FOCUS_LANE=""
  PREV_PHASE=""
  PREV_START_TIME=""
  PREV_END_TIME=""
  PREV_DECISIONS=0
  PREV_WALKAWAY=""

  local state_file="${SWAIN_SESSION_STATE:-$REPO_ROOT/.agents/session-state.json}"

  if [ -f "$state_file" ]; then
    PREV_EXISTS=true
    # Extract all fields in one python3 call
    eval "$(python3 -c "
import json, sys
from datetime import datetime, timezone

with open('$state_file') as f:
    state = json.load(f)

phase = state.get('phase', 'unknown')
focus = state.get('focus_lane') or ''
sid = state.get('session_id') or ''
activity = state.get('last_activity_time') or state.get('start_time', '')
start = state.get('start_time', '')
end = state.get('end_time') or ''
decisions = state.get('decisions_made', 0)
walkaway = state.get('walkaway') or ''

status = 'none'
if phase == 'closed':
    status = 'closed'
elif phase == 'active':
    try:
        activity_dt = datetime.fromisoformat(activity.replace('Z', '+00:00'))
        age = (datetime.now(timezone.utc) - activity_dt).total_seconds()
        status = 'stale' if age > 3600 else 'active'
    except (ValueError, TypeError):
        status = 'stale'

# Shell-safe quoting via repr
def q(s):
    return s.replace(\"'\", \"'\\\"'\\\"'\")

print(f\"PREV_STATUS='{q(status)}'\")
print(f\"PREV_SESSION_ID='{q(sid)}'\")
print(f\"PREV_FOCUS_LANE='{q(focus)}'\")
print(f\"PREV_PHASE='{q(phase)}'\")
print(f\"PREV_START_TIME='{q(start)}'\")
print(f\"PREV_END_TIME='{q(end)}'\")
print(f\"PREV_DECISIONS={decisions}\")
print(f\"PREV_WALKAWAY='{q(walkaway)}'\")
" 2>/dev/null)" || true
  fi
}

# --- Preflight warnings (read-only observations) ---
check_warnings() {
  # Stale tk locks (report only — don't clean)
  if [ -d "$REPO_ROOT/.tickets/.locks" ]; then
    stale_count=$(find "$REPO_ROOT/.tickets/.locks" -type d -mmin +60 2>/dev/null | wc -l | tr -d ' ')
    if [ "$stale_count" -gt 0 ]; then
      add_warning "stale_tk_locks:$stale_count"
    fi
  fi

  # Stale git index.lock
  if [ -f "$REPO_ROOT/.git/index.lock" ]; then
    add_warning "stale_git_index_lock"
  fi

  # Missing .agents directory
  if [ ! -d "$REPO_ROOT/.agents" ]; then
    add_warning "missing_agents_dir"
  fi
}

# --- Run all checks ---
check_git || true
check_tmux || true
check_session_json || true
check_session_state || true
check_warnings || true

# --- Emit JSON via python3 ---
python3 -c "
import json, sys

def to_bool(v):
    return v.lower() == 'true'

def to_int(v):
    try: return int(v)
    except: return 0

def to_str_or_null(v):
    return v if v else None

def to_list(raw):
    return [x for x in raw.strip().split('\n') if x] if raw.strip() else []

data = {
    'git': {
        'repo_root': sys.argv[1],
        'branch': sys.argv[2] or 'unknown',
        'dirty': to_bool(sys.argv[3]),
        'worktree': {
            'isolated': to_bool(sys.argv[4]),
            'path': to_str_or_null(sys.argv[5]),
        },
    },
    'tmux': {
        'active': to_bool(sys.argv[6]),
        'tab_format': sys.argv[7],
        'tab_name': sys.argv[8],
    },
    'session': {
        'focus': to_str_or_null(sys.argv[9]),
        'bookmark': to_str_or_null(sys.argv[10]),
        'last_branch': to_str_or_null(sys.argv[11]),
    },
    'prev_session': {
        'exists': to_bool(sys.argv[12]),
        'status': sys.argv[13],
        'session_id': to_str_or_null(sys.argv[14]),
        'focus_lane': to_str_or_null(sys.argv[15]),
        'phase': to_str_or_null(sys.argv[16]),
        'start_time': to_str_or_null(sys.argv[17]),
        'end_time': to_str_or_null(sys.argv[18]),
        'decisions_made': to_int(sys.argv[19]),
        'walkaway': to_str_or_null(sys.argv[20]),
    },
    'warnings': to_list(sys.argv[21]),
}

json.dump(data, sys.stdout, indent=2)
print()
" \
  "$REPO_ROOT" "$GIT_BRANCH" "$GIT_DIRTY" \
  "$GIT_WT_ISOLATED" "$GIT_WT_PATH" \
  "$TMUX_ACTIVE" "$TMUX_TAB_FORMAT" "$TMUX_TAB_NAME" \
  "$SESSION_FOCUS" "$SESSION_BOOKMARK" "$SESSION_LAST_BRANCH" \
  "$PREV_EXISTS" "$PREV_STATUS" "$PREV_SESSION_ID" "$PREV_FOCUS_LANE" \
  "$PREV_PHASE" "$PREV_START_TIME" "$PREV_END_TIME" "$PREV_DECISIONS" \
  "$PREV_WALKAWAY" \
  "$WARNINGS_RAW"
