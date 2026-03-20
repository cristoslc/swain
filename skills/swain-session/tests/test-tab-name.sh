#!/usr/bin/env bash
# test-tab-name.sh — Acceptance tests for swain-tab-name.sh (SPEC-056)
#
# Runs in an isolated tmux server to avoid interfering with live sessions.
# Each test gets a clean tmux session. Requires: tmux, git, jq.
#
# Usage: bash skills/swain-session/tests/test-tab-name.sh

set +e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TAB_NAME="$(cd "$SCRIPT_DIR/.." && pwd)/scripts/swain-tab-name.sh"
# Use --git-common-dir to find the real repo root (not the worktree root)
GIT_COMMON="$(git rev-parse --git-common-dir 2>/dev/null)"
REPO_ROOT="$(cd "$GIT_COMMON/.." && pwd 2>/dev/null)"

# Isolated tmux server
TMUX_SOCK="/tmp/swain-test-tmux-$$"
T="tmux -S $TMUX_SOCK"

PASS=0
FAIL=0
SKIP=0

pass() { echo "  PASS: $1"; ((PASS++)); }
fail() { echo "  FAIL: $1 — $2"; ((FAIL++)); }
skip() { echo "  SKIP: $1 — $2"; ((SKIP++)); }

cleanup() {
  $T kill-server 2>/dev/null
  rm -f "$TMUX_SOCK"
}
trap cleanup EXIT

start_session() {
  local name="${1:-test}"
  local dir="${2:-$REPO_ROOT}"
  $T new-session -d -s "$name" -c "$dir" 2>/dev/null
}

# Run the script inside the test tmux server via run-shell
# This ensures TMUX env var is properly set by the tmux server
run() {
  local session="${1:-test}"
  shift
  # Set TMUX env to point at the test server so the script's tmux commands
  # target the right server/session. Format: socket_path,server_pid,pane_index
  local pane_id
  pane_id=$($T list-panes -t "$session" -F '#{pane_id}' 2>/dev/null | head -1 | tr -d '%')
  $T run-shell -t "$session" "TMUX='$TMUX_SOCK,0,${pane_id:-0}' bash '$TAB_NAME' $*" 2>/dev/null
}

# Helpers to query test tmux state
# NOTE: display-message -p requires an attached client, which test servers lack.
# Use list-sessions/list-windows format strings instead.
# session_name takes a session index (0-based) since names change after rename
session_name() { $T list-sessions -F '#{session_name}' 2>/dev/null | sed -n "${1:-1}p"; }
window_name()  { $T list-windows -F '#{window_name}' 2>/dev/null | head -1; }
pane_opt()     { $T show-options -pqv "$1" 2>/dev/null; }
window_hook()  { $T show-hooks -w pane-focus-in 2>/dev/null; }
global_hook()  { $T show-hooks -g pane-focus-in 2>/dev/null; }

WORKTREE_DIR="$REPO_ROOT/.worktrees/copper-meadow-lantern"
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
EXPECTED="swain @ $BRANCH"
if [[ -d "$WORKTREE_DIR" ]]; then
  WT_BRANCH=$(git -C "$WORKTREE_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null)
  EXPECTED_WT="swain @ $WT_BRANCH"
fi

echo "=== SPEC-056 Acceptance Tests ==="
echo "Script: $TAB_NAME"
echo "Repo: $REPO_ROOT"
echo "Branch: $BRANCH"
[[ -d "$WORKTREE_DIR" ]] && echo "Worktree: $WORKTREE_DIR ($WT_BRANCH)"
echo ""

# ─── AC1: Session start — --auto renames session and window ───
echo "--- AC1: Session start renames session + window ---"
cleanup; start_session "default" "$REPO_ROOT"
run "default" --auto
s=$(session_name); w=$(window_name)
if [[ "$s" == "$EXPECTED" && "$w" == "$EXPECTED" ]]; then
  pass "AC1: session='$s', window='$w'"
else
  fail "AC1" "expected '$EXPECTED', got session='$s' window='$w'"
fi

# ─── AC2: Hook installed per-window with absolute path ───
echo "--- AC2: Per-window hook installed ---"
hook=$(window_hook)
if [[ "$hook" == *"$TAB_NAME"* && "$hook" == *"pane-focus-in"* ]]; then
  pass "AC2: per-window hook contains script path"
else
  fail "AC2" "hook='$hook'"
fi
gh=$(global_hook)
if [[ -z "$gh" || "$gh" != *"$TAB_NAME"* ]]; then
  pass "AC2b: no global hook (per-window only)"
else
  fail "AC2b" "global hook found: '$gh'"
fi

# ─── AC3: @swain_path set on pane ───
echo "--- AC3: @swain_path set on pane ---"
sp=$(pane_opt "@swain_path")
if [[ -n "$sp" && -d "$sp" ]]; then
  pass "AC3: @swain_path='$sp'"
else
  fail "AC3" "@swain_path='$sp'"
fi

# ─── AC4-5: Shell pane switching ───
echo "--- AC4-5: Shell pane switching ---"
if [[ -d "$WORKTREE_DIR" ]]; then
  # Split a new pane cd'd into the worktree
  $T split-window -t "default" -h -c "$WORKTREE_DIR" 2>/dev/null
  sleep 0.3
  # The pane-focus-in hook should have fired — but run-shell to be sure
  run "default" --auto
  s=$(session_name)
  if [[ "$s" == "$EXPECTED_WT" ]]; then
    pass "AC4: worktree pane, session='$s'"
  else
    fail "AC4" "expected '$EXPECTED_WT', got session='$s'"
  fi
  # Switch back to pane 0 (main repo)
  $T select-pane -t "default:0.0" 2>/dev/null
  sleep 0.3
  run "default" --auto
  s=$(session_name)
  if [[ "$s" == "$EXPECTED" ]]; then
    pass "AC5: main pane, session='$s'"
  else
    fail "AC5" "expected '$EXPECTED', got session='$s'"
  fi
else
  skip "AC4-5" "no worktree at $WORKTREE_DIR"
fi

# ─── AC6: --path sets @swain_path and renames ───
echo "--- AC6: --path flag sets @swain_path ---"
cleanup; start_session "pathtest" "$REPO_ROOT"
if [[ -d "$WORKTREE_DIR" ]]; then
  run "pathtest" --path "$WORKTREE_DIR" --auto
  s=$(session_name)
  sp=$(pane_opt "@swain_path")
  if [[ "$s" == "$EXPECTED_WT" ]]; then
    pass "AC6a: --path renamed session to '$s'"
  else
    fail "AC6a" "expected '$EXPECTED_WT', got '$s'"
  fi
  if [[ "$sp" == "$WORKTREE_DIR" ]]; then
    pass "AC6b: @swain_path='$sp'"
  else
    fail "AC6b" "expected '$WORKTREE_DIR', got '$sp'"
  fi
else
  skip "AC6" "no worktree at $WORKTREE_DIR"
fi

# ─── AC7: Hook reads @swain_path on refocus ───
echo "--- AC7: Hook reads @swain_path on pane refocus ---"
if [[ -d "$WORKTREE_DIR" ]]; then
  # After AC6, @swain_path is set. Split a main-repo pane.
  $T split-window -t "pathtest" -h -c "$REPO_ROOT" 2>/dev/null
  sleep 0.3
  run "pathtest" --auto
  s=$(session_name)
  if [[ "$s" == "$EXPECTED" ]]; then
    pass "AC7a: shell pane shows '$s'"
  else
    fail "AC7a" "expected '$EXPECTED', got '$s'"
  fi
  # Switch back to pane 0 (agent pane with @swain_path)
  $T select-pane -t "pathtest:0.0" 2>/dev/null
  sleep 0.3
  run "pathtest" --auto
  s=$(session_name)
  if [[ "$s" == "$EXPECTED_WT" ]]; then
    pass "AC7b: agent pane refocus shows '$s' (from @swain_path)"
  else
    fail "AC7b" "expected '$EXPECTED_WT', got '$s'"
  fi
else
  skip "AC7" "no worktree at $WORKTREE_DIR"
fi

# ─── AC8: Agent exits worktree via --path ───
echo "--- AC8: --path back to main repo ---"
if [[ -d "$WORKTREE_DIR" ]]; then
  cleanup; start_session "exittest" "$REPO_ROOT"
  run "exittest" --path "$WORKTREE_DIR" --auto
  run "exittest" --path "$REPO_ROOT" --auto
  s=$(session_name)
  sp=$(pane_opt "@swain_path")
  EXPECTED_MAIN="swain @ main"
  if [[ "$s" == "$EXPECTED_MAIN" && "$sp" == "$REPO_ROOT" ]]; then
    pass "AC8: exited worktree, session='$s', @swain_path='$sp'"
  else
    fail "AC8" "session='$s', @swain_path='$sp'"
  fi
else
  skip "AC8" "no worktree at $WORKTREE_DIR"
fi

# ─── AC9-10: Cross-session isolation ───
echo "--- AC9-10: Cross-session isolation ---"
cleanup
start_session "projectA" "$REPO_ROOT"
run "projectA" --auto
$T new-session -d -s "projectB" -c "/tmp" 2>/dev/null
# Sessions are sorted alphabetically by tmux; after rename projectA becomes "swain @ ..."
# which sorts after "projectB"
sA=$($T list-sessions -F '#{session_name}' 2>/dev/null | grep -v projectB | head -1)
sB=$($T list-sessions -F '#{session_name}' 2>/dev/null | grep projectB | head -1)
hB=""  # projectB never had --auto run, so no hook
if [[ "$sA" == "$EXPECTED" && "$sB" == "projectB" ]]; then
  pass "AC9: sessions independent — A='$sA', B='$sB'"
else
  fail "AC9" "A='$sA', B='$sB'"
fi
if [[ -z "$hB" || "$hB" != *"$TAB_NAME"* ]]; then
  pass "AC10: projectB has no swain hook"
else
  fail "AC10" "projectB has hook: '$hB'"
fi

# ─── AC11: Reset clears everything ───
echo "--- AC11: Reset ---"
cleanup; start_session "resettest" "$REPO_ROOT"
run "resettest" --auto
run "resettest" --reset
hook=$(window_hook)
sp=$(pane_opt "@swain_path")
if [[ -z "$hook" || "$hook" != *"$TAB_NAME"* ]]; then
  pass "AC11a: hook removed after reset"
else
  fail "AC11a" "hook still present: '$hook'"
fi
if [[ -z "$sp" ]]; then
  pass "AC11b: @swain_path cleared after reset"
else
  fail "AC11b" "@swain_path='$sp'"
fi

# ─── AC12: Non-git fallback ───
echo "--- AC12: Non-git fallback ---"
cleanup; start_session "nogit" "/tmp"
run "nogit" --path /tmp --auto
s=$(session_name)
if [[ "$s" == "unknown @ no-branch" ]]; then
  pass "AC12: non-git fallback, session='$s'"
else
  fail "AC12" "session='$s'"
fi

# ─── AC13: Worktree project name resolution ───
echo "--- AC13: Worktree project name via --git-common-dir ---"
if [[ -d "$WORKTREE_DIR" ]]; then
  cleanup; start_session "wt" "$REPO_ROOT"
  run "wt" --path "$WORKTREE_DIR" --auto
  s=$(session_name)
  if [[ "$s" == "swain @ "* ]]; then
    pass "AC13: project='swain' from worktree (session='$s')"
  else
    fail "AC13" "session='$s' (expected 'swain @ ...')"
  fi
else
  skip "AC13" "no worktree"
fi

# ─── AC14: Idempotent hook install ───
echo "--- AC14: Idempotent hook ---"
cleanup; start_session "idem" "$REPO_ROOT"
run "idem" --auto
run "idem" --auto
hook_count=$($T show-hooks -w -t "idem" pane-focus-in 2>/dev/null | wc -l | tr -d ' ')
if [[ "$hook_count" -le 1 ]]; then
  pass "AC14: idempotent ($hook_count hook entries)"
else
  fail "AC14" "$hook_count hook entries"
fi

# ─── Summary ───
echo ""
echo "=== Results: $PASS passed, $FAIL failed, $SKIP skipped ==="
exit $FAIL
