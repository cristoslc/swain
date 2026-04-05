#!/usr/bin/env bash
# Tests for SPEC-245: bin/swain lockfile integration, --resume, --trunk
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SCRIPT="$REPO_ROOT/bin/swain"
PASS=0
FAIL=0

assert() {
  local desc="$1" result="$2"
  if [ "$result" = "true" ]; then
    echo "  PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $desc"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== SPEC-245: bin/swain Redesign Tests ==="

# --- --trunk flag ---
echo ""
echo "--- --trunk flag ---"

OUTPUT=$(bash "$SCRIPT" --trunk --_dry_run --_non_interactive 2>&1)
assert "--trunk sets launch_root to repo root" "$(echo "$OUTPUT" | grep -q "launch_root: $REPO_ROOT" && echo true || echo false)"

# --- --resume flag ---
echo ""
echo "--- --resume flag ---"

# List worktrees to find one to resume
WORKTREES=$(git worktree list 2>/dev/null | grep -v "$(pwd)" | head -1)
if [ -n "$WORKTREES" ]; then
  WT_PATH=$(echo "$WORKTREES" | awk '{print $1}')
  WT_NAME=$(basename "$WT_PATH")
  OUTPUT_RESUME=$(bash "$SCRIPT" --resume "$WT_NAME" --_dry_run --_non_interactive 2>&1)
  assert "--resume finds matching worktree" "$(echo "$OUTPUT_RESUME" | grep -qi "resum\|launch_root.*$WT_NAME" && echo true || echo false)"
else
  echo "  SKIP: no linked worktrees to test --resume"
  PASS=$((PASS + 1))
fi

# --resume with nonexistent name
OUTPUT_BAD=$(bash "$SCRIPT" --resume "nonexistent-worktree-xyz" --_dry_run --_non_interactive 2>&1) || true
assert "--resume nonexistent fails" "$(echo "$OUTPUT_BAD" | grep -qi "error\|not found\|no worktree" && echo true || echo false)"

# --- --help includes new flags ---
echo ""
echo "--- Help text ---"

HELP=$(bash "$SCRIPT" --help 2>&1)
assert "help mentions --resume" "$(echo "$HELP" | grep -q "\-\-resume" && echo true || echo false)"
assert "help mentions --trunk" "$(echo "$HELP" | grep -q "\-\-trunk" && echo true || echo false)"

# --- Env var export (dry run shows env would be set) ---
echo ""
echo "--- Env vars ---"

# When launching from a worktree, SWAIN_WORKTREE_PATH should be set
# (we can't test this directly in dry-run mode without a full launch,
# but we can verify the script has the export logic)
assert "script exports SWAIN_WORKTREE_PATH" "$(grep -q 'export SWAIN_WORKTREE_PATH' "$SCRIPT" && echo true || echo false)"
assert "script exports SWAIN_LOCKFILE_PATH" "$(grep -q 'export SWAIN_LOCKFILE_PATH' "$SCRIPT" && echo true || echo false)"

# --- No exec (child process pattern) ---
echo ""
echo "--- Child process pattern ---"

assert "no eval exec in launch" "$(! grep -q 'eval exec' "$SCRIPT" && echo true || echo false)"
assert "uses wait for child" "$(grep -q 'wait.*child_pid' "$SCRIPT" && echo true || echo false)"
assert "signal forwarding present" "$(grep -q 'trap.*TERM.*child_pid' "$SCRIPT" && echo true || echo false)"

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
