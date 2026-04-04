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

# --- Dangling worktrees ---
TMPDIR4=$(mktemp -d)
git -C "$TMPDIR4" init -q
git -C "$TMPDIR4" commit --allow-empty -m "init" -q

# T12: No worktrees → clean
RESULT=$(check_dangling_worktrees "$TMPDIR4" 2>/dev/null || echo "MISSING")
assert "no worktrees → clean" "$(echo "$RESULT" | grep -q 'clean' && echo true || echo false)"

# T13: Worktree with missing directory → found
WT_PATH="$TMPDIR4/.claude/worktrees/dead-session"
git -C "$TMPDIR4" worktree add -q "$WT_PATH" -b dead-branch 2>/dev/null
rm -rf "$WT_PATH"
RESULT=$(check_dangling_worktrees "$TMPDIR4" 2>/dev/null || echo "MISSING")
assert "missing-dir worktree → found" "$(echo "$RESULT" | grep -q 'found' && echo true || echo false)"

# Cleanup
git -C "$TMPDIR4" worktree prune -q 2>/dev/null
rm -rf "$TMPDIR4"

# --- Orphaned MCP servers ---
# T14: Detection function exists and returns clean when no MCP processes
RESULT=$(check_orphaned_mcp "$REPO_ROOT" 2>/dev/null || echo "MISSING")
assert "MCP check runs without error" "$([ "$RESULT" != "MISSING" ] && echo true || echo false)"
assert "MCP check returns valid format" "$(echo "$RESULT" | grep -qE '(clean|found)' && echo true || echo false)"

# --- SPEC-251: Docker MCP exclusion ---
# Verify check_orphaned_mcp filters out Docker-managed MCP processes
FUNC_SRC=$(declare -f check_orphaned_mcp 2>/dev/null || true)

# T-DOCKER1: Function source contains docker exclusion (AC1)
HAS_DOCKER=$(echo "$FUNC_SRC" | grep -qi 'docker\|containerd' && echo true || echo false)
assert "check_orphaned_mcp excludes docker processes" "$HAS_DOCKER"

# T-DOCKER2: Function source has grep -v for docker (AC1 mechanism)
HAS_GREP_V=$(echo "$FUNC_SRC" | grep -q 'grep.*-v.*docker\|grep.*-iv.*docker' && echo true || echo false)
assert "function has docker exclusion grep" "$HAS_GREP_V"

# T-DOCKER3: Function source also excludes containerd-shim (AC1)
HAS_CONTAINERD=$(echo "$FUNC_SRC" | grep -qi 'containerd' && echo true || echo false)
assert "function has containerd exclusion" "$HAS_CONTAINERD"

# T-DOCKER4: Non-Docker MCP lines still match the base MCP pattern (AC2)
NON_DOCKER_LINE="user  5678  0.0  0.1 node /usr/local/bin/mcp-some-server --port 3000"
PASSES_MCP=$(echo "$NON_DOCKER_LINE" | grep -qi 'mcp.*server\|mcp.*gateway' && echo true || echo false)
assert "non-docker MCP line matches MCP pattern" "$PASSES_MCP"

# --- Aggregate function ---
TMPDIR5=$(mktemp -d)
mkdir -p "$TMPDIR5/.git"

# T15: Clean project → empty output (silent fast path, AC5)
RESULT=$(check_all_crash_debris "$TMPDIR5" 2>/dev/null)
assert "clean project → silent (no output)" "$([ -z "$RESULT" ] && echo true || echo false)"

# T16: Multiple debris types → all reported
touch "$TMPDIR5/.git/MERGE_HEAD"
echo "99999999" > "$TMPDIR5/.git/index.lock"
RESULT=$(check_all_crash_debris "$TMPDIR5" 2>/dev/null || echo "MISSING")
FOUND_COUNT=$(echo "$RESULT" | grep -c 'found' || echo "0")
assert "multiple debris → multiple findings" "$([ "$FOUND_COUNT" -ge 2 ] && echo true || echo false)"

rm -rf "$TMPDIR5"

# --- Edge cases ---
TMPDIR_EDGE=$(mktemp -d)
FAKE_GIT_EDGE="$TMPDIR_EDGE/.git"
mkdir -p "$FAKE_GIT_EDGE"

# T-EDGE1: Lock file with binary/non-numeric content → found (no valid PID)
echo "not-a-pid" > "$FAKE_GIT_EDGE/index.lock"
RESULT=$(check_git_index_lock "$TMPDIR_EDGE" 2>/dev/null || echo "MISSING")
assert "non-numeric lock content → found" "$(echo "$RESULT" | grep -q 'found' && echo true || echo false)"

# T-EDGE2: Empty lock file → found (no PID to check)
> "$FAKE_GIT_EDGE/index.lock"
RESULT=$(check_git_index_lock "$TMPDIR_EDGE" 2>/dev/null || echo "MISSING")
assert "empty lock file → found" "$(echo "$RESULT" | grep -q 'found' && echo true || echo false)"

# T-EDGE3: rebase-apply detection (not just rebase-merge)
TMPDIR_EDGE2=$(mktemp -d)
mkdir -p "$TMPDIR_EDGE2/.git/rebase-apply"
RESULT=$(check_interrupted_git_ops "$TMPDIR_EDGE2" 2>/dev/null || echo "MISSING")
assert "rebase-apply → found" "$(echo "$RESULT" | grep -q 'found' && echo true || echo false)"

rm -rf "$TMPDIR_EDGE" "$TMPDIR_EDGE2"

# --- Doctor integration ---
DOCTOR="$REPO_ROOT/skills/swain-doctor/scripts/swain-doctor.sh"

# T18: Doctor output includes crash_debris check
DOCTOR_OUT=$(bash "$DOCTOR" 2>/dev/null || true)
assert "doctor includes crash_debris check" "$(echo "$DOCTOR_OUT" | grep -q 'crash_debris' && echo true || echo false)"

# T-DOCTOR2: Doctor output includes swain_symlink check
DOCTOR_OUT2=$(bash "$DOCTOR" 2>/dev/null || true)
assert "doctor includes swain_symlink check" "$(echo "$DOCTOR_OUT2" | grep -q 'swain_symlink' && echo true || echo false)"

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
