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

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
