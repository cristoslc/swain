#!/usr/bin/env bash
# RED tests for SPEC-182: Crash Debris Detection Checks
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
LIB="$REPO_ROOT/skills/swain-doctor/scripts/crash-debris-lib.sh"
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

echo "=== SPEC-182: Crash Debris Detection Tests ==="

# T1: Library file exists and is sourceable
assert "crash-debris-lib.sh exists" "$([ -f "$LIB" ] && echo true || echo false)"
source "$LIB" 2>/dev/null || true

# --- Git index lock detection ---
TMPDIR=$(mktemp -d)
FAKE_GIT="$TMPDIR/.git"
mkdir -p "$FAKE_GIT"

# T2: No lock file → clean
RESULT=$(check_git_index_lock "$TMPDIR" 2>/dev/null || echo "MISSING")
assert "no index.lock → clean" "$(echo "$RESULT" | grep -q 'clean' && echo true || echo false)"

# T3: Lock file from dead PID → found
echo "99999999" > "$FAKE_GIT/index.lock"
RESULT=$(check_git_index_lock "$TMPDIR" 2>/dev/null || echo "MISSING")
assert "dead-pid index.lock → found" "$(echo "$RESULT" | grep -q 'found' && echo true || echo false)"

# T4: Lock file from live PID → clean (not stale)
echo "$$" > "$FAKE_GIT/index.lock"
RESULT=$(check_git_index_lock "$TMPDIR" 2>/dev/null || echo "MISSING")
assert "live-pid index.lock → clean" "$(echo "$RESULT" | grep -q 'clean' && echo true || echo false)"

rm -rf "$TMPDIR"

# --- Interrupted git operations ---
TMPDIR2=$(mktemp -d)
FAKE_GIT2="$TMPDIR2/.git"
mkdir -p "$FAKE_GIT2"

# T5: No interrupted ops → clean
RESULT=$(check_interrupted_git_ops "$TMPDIR2" 2>/dev/null || echo "MISSING")
assert "no interrupted ops → clean" "$(echo "$RESULT" | grep -q 'clean' && echo true || echo false)"

# T6: MERGE_HEAD → found
touch "$FAKE_GIT2/MERGE_HEAD"
RESULT=$(check_interrupted_git_ops "$TMPDIR2" 2>/dev/null || echo "MISSING")
assert "MERGE_HEAD → found merge" "$(echo "$RESULT" | grep -q 'found' && echo true || echo false)"
rm "$FAKE_GIT2/MERGE_HEAD"

# T7: rebase-merge dir → found
mkdir -p "$FAKE_GIT2/rebase-merge"
RESULT=$(check_interrupted_git_ops "$TMPDIR2" 2>/dev/null || echo "MISSING")
assert "rebase-merge → found rebase" "$(echo "$RESULT" | grep -q 'found' && echo true || echo false)"
rm -rf "$FAKE_GIT2/rebase-merge"

# T8: CHERRY_PICK_HEAD → found
touch "$FAKE_GIT2/CHERRY_PICK_HEAD"
RESULT=$(check_interrupted_git_ops "$TMPDIR2" 2>/dev/null || echo "MISSING")
assert "CHERRY_PICK_HEAD → found cherry-pick" "$(echo "$RESULT" | grep -q 'found' && echo true || echo false)"
rm "$FAKE_GIT2/CHERRY_PICK_HEAD"

rm -rf "$TMPDIR2"

# --- Stale tk claim locks ---
TMPDIR3=$(mktemp -d)
TICKETS="$TMPDIR3/.tickets"
mkdir -p "$TICKETS/.locks"

# T9: No locks → clean
RESULT=$(check_stale_tk_locks "$TMPDIR3" 2>/dev/null || echo "MISSING")
assert "no tk locks → clean" "$(echo "$RESULT" | grep -q 'clean' && echo true || echo false)"

# T10: Lock with dead PID → found
LOCK_DIR="$TICKETS/.locks/task-1"
mkdir -p "$LOCK_DIR"
echo "99999999" > "$LOCK_DIR/owner"
RESULT=$(check_stale_tk_locks "$TMPDIR3" 2>/dev/null || echo "MISSING")
assert "dead-pid tk lock → found" "$(echo "$RESULT" | grep -q 'found' && echo true || echo false)"

# T11: Lock with live PID → clean
echo "$$" > "$LOCK_DIR/owner"
RESULT=$(check_stale_tk_locks "$TMPDIR3" 2>/dev/null || echo "MISSING")
assert "live-pid tk lock → clean" "$(echo "$RESULT" | grep -q 'clean' && echo true || echo false)"

rm -rf "$TMPDIR3"

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
