#!/usr/bin/env bash
# RED tests for SPEC-244: Lockfile Management
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SCRIPT="$REPO_ROOT/.agents/bin/swain-lockfile.sh"
TEST_DIR="$(mktemp -d)"
PASS=0
FAIL=0

cleanup() {
  rm -rf "$TEST_DIR"
}
trap cleanup EXIT

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

# Override lockfile dir for testing
export SWAIN_LOCKFILE_DIR="$TEST_DIR/worktrees"

echo "=== SPEC-244: Lockfile Management Tests ==="

# --- Script existence ---
echo ""
echo "--- Script existence ---"
assert "swain-lockfile.sh exists" "$([ -f "$SCRIPT" ] && echo true || echo false)"
assert "swain-lockfile.sh is executable" "$([ -x "$SCRIPT" ] && echo true || echo false)"

# --- AC1: Claim creates lockfile atomically ---
echo ""
echo "--- AC1: Claim creates lockfile ---"

# Create a fake worktree path for testing
FAKE_WT="$TEST_DIR/fake-worktree"
mkdir -p "$FAKE_WT"

OUTPUT=$(bash "$SCRIPT" claim "test-branch" "$FAKE_WT" "test purpose" 2>&1) || true
assert "claim creates lockfile" "$([ -f "$SWAIN_LOCKFILE_DIR/test-branch.lock" ] && echo true || echo false)"

# Read lockfile and verify fields
if [ -f "$SWAIN_LOCKFILE_DIR/test-branch.lock" ]; then
  source "$SWAIN_LOCKFILE_DIR/test-branch.lock"
  assert "lockfile has version=1" "$([ "${version:-}" = "1" ] && echo true || echo false)"
  assert "lockfile has pid" "$([ -n "${pid:-}" ] && echo true || echo false)"
  assert "lockfile has user" "$([ -n "${user:-}" ] && echo true || echo false)"
  assert "lockfile has worktree_path" "$([ "${worktree_path:-}" = "$FAKE_WT" ] && echo true || echo false)"
  assert "lockfile has purpose" "$([ "${purpose:-}" = "test purpose" ] && echo true || echo false)"
  assert "lockfile has status=active" "$([ "${status:-}" = "active" ] && echo true || echo false)"
  assert "lockfile has claimed_at" "$([ -n "${claimed_at:-}" ] && echo true || echo false)"
else
  for f in "lockfile has version=1" "lockfile has pid" "lockfile has user" "lockfile has worktree_path" "lockfile has purpose" "lockfile has status=active" "lockfile has claimed_at"; do
    assert "$f" "false"
  done
fi

# Double-claim should fail
OUTPUT2=$(bash "$SCRIPT" claim "test-branch" "$FAKE_WT" "test purpose 2" 2>&1) || true
EXIT_CODE=$?
assert "double-claim fails" "$([ $EXIT_CODE -ne 0 ] || echo "$OUTPUT2" | grep -qi "already\|exists\|claimed" && echo true || echo false)"

# --- AC2: Release removes lockfile ---
echo ""
echo "--- AC2: Release removes lockfile ---"

bash "$SCRIPT" release "test-branch" 2>&1 || true
assert "release removes lockfile" "$([ ! -f "$SWAIN_LOCKFILE_DIR/test-branch.lock" ] && echo true || echo false)"

# Release non-existent is no-op
OUTPUT3=$(bash "$SCRIPT" release "nonexistent-branch" 2>&1) || true
assert "release non-existent is no-op (exit 0)" "$(bash "$SCRIPT" release "nonexistent-branch" 2>/dev/null; [ $? -eq 0 ] && echo true || echo false)"

# --- AC3: Stale detection ---
echo ""
echo "--- AC3: Stale detection ---"

# Create a lockfile with a dead PID
mkdir -p "$SWAIN_LOCKFILE_DIR"
cat > "$SWAIN_LOCKFILE_DIR/stale-branch.lock" << STALE_EOF
version=1
pid=99999
user=$(whoami)
exe=claude
pane_id=
claimed_at=$(date -Iseconds)
worktree_path=$FAKE_WT
purpose="stale test"
status=active
STALE_EOF

STALE_OUTPUT=$(bash "$SCRIPT" is-stale "stale-branch" 2>&1) || true
STALE_EXIT=$?
assert "dead PID detected as stale" "$([ $STALE_EXIT -eq 0 ] && echo true || echo false)"

# Create a lockfile with THIS process's PID (should NOT be stale)
# Can't use claim (runs in subshell, PID dies). Write directly with our PID.
mkdir -p "$SWAIN_LOCKFILE_DIR"
cat > "$SWAIN_LOCKFILE_DIR/alive-branch.lock" << ALIVE_EOF
version=1
pid=$$
user=$(whoami)
exe=bash
pane_id=
claimed_at=$(date -Iseconds)
worktree_path=$FAKE_WT
purpose="alive test"
status=active
ALIVE_EOF
ALIVE_EXIT=0
bash "$SCRIPT" is-stale "alive-branch" >/dev/null 2>&1 || ALIVE_EXIT=$?
assert "live PID not stale" "$([ $ALIVE_EXIT -ne 0 ] && echo true || echo false)"

# --- AC4: List returns structured output ---
echo ""
echo "--- AC4: List ---"

LIST_OUTPUT=$(bash "$SCRIPT" list 2>&1) || true
assert "list returns JSON" "$(echo "$LIST_OUTPUT" | python3 -m json.tool >/dev/null 2>&1 && echo true || echo false)"

# --- AC5: Mark ready_for_cleanup ---
echo ""
echo "--- AC5: Mark ready ---"

# Need a git repo context for HEAD
bash "$SCRIPT" mark-ready "alive-branch" 2>&1 || true
if [ -f "$SWAIN_LOCKFILE_DIR/alive-branch.lock" ]; then
  source "$SWAIN_LOCKFILE_DIR/alive-branch.lock"
  assert "mark-ready sets ready_for_cleanup=true" "$([ "${ready_for_cleanup:-}" = "true" ] && echo true || echo false)"
  assert "mark-ready sets ready_commit" "$([ -n "${ready_commit:-}" ] && echo true || echo false)"
else
  assert "mark-ready sets ready_for_cleanup=true" "false"
  assert "mark-ready sets ready_commit" "false"
fi

# --- AC6: Verify ready ---
echo ""
echo "--- AC6: Verify ready ---"

bash "$SCRIPT" verify-ready "alive-branch" 2>&1 || true
VERIFY_EXIT=$?
assert "verify-ready returns 0 when commit matches" "$([ $VERIFY_EXIT -eq 0 ] && echo true || echo false)"

# Non-ready lockfile
cat > "$SWAIN_LOCKFILE_DIR/not-ready-branch.lock" << NOTREADY_EOF
version=1
pid=$$
user=$(whoami)
exe=bash
pane_id=
claimed_at=$(date -Iseconds)
worktree_path=$FAKE_WT
purpose="not ready"
status=active
NOTREADY_EOF
bash "$SCRIPT" verify-ready "not-ready-branch" 2>&1
NOT_READY_EXIT=$?
assert "verify-ready returns 2 when not marked ready" "$([ $NOT_READY_EXIT -eq 2 ] && echo true || echo false)"

# --- Cleanup test lockfiles ---
bash "$SCRIPT" release "alive-branch" 2>/dev/null || true
bash "$SCRIPT" release "stale-branch" 2>/dev/null || true
bash "$SCRIPT" release "not-ready-branch" 2>/dev/null || true

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
