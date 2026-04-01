#!/usr/bin/env bash
# test-session-greeting.sh — SPEC-194: Test the fast-path session greeting
#
# Tests swain-session-greeting.sh output for completeness and performance.
#
# Usage: bash test-session-greeting.sh [--verbose]

set -euo pipefail

VERBOSE=0
[[ "${1:-}" == "--verbose" ]] && VERBOSE=1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GREETING_SCRIPT="$SCRIPT_DIR/swain-session-greeting.sh"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

PASS=0
FAIL=0
TOTAL=0

assert_contains() {
  local test_name="$1" expected="$2" actual="$3"
  TOTAL=$((TOTAL + 1))
  if echo "$actual" | grep -q "$expected"; then
    PASS=$((PASS + 1))
    [[ $VERBOSE -eq 1 ]] && echo "  PASS: $test_name"
  else
    FAIL=$((FAIL + 1))
    echo "  FAIL: $test_name (expected to contain: '$expected')"
    [[ $VERBOSE -eq 1 ]] && echo "    Got: $(echo "$actual" | head -5)"
  fi
}

assert_not_contains() {
  local test_name="$1" unexpected="$2" actual="$3"
  TOTAL=$((TOTAL + 1))
  if ! echo "$actual" | grep -q "$unexpected"; then
    PASS=$((PASS + 1))
    [[ $VERBOSE -eq 1 ]] && echo "  PASS: $test_name"
  else
    FAIL=$((FAIL + 1))
    echo "  FAIL: $test_name (should NOT contain: '$unexpected')"
  fi
}

assert_eq() {
  local test_name="$1" expected="$2" actual="$3"
  TOTAL=$((TOTAL + 1))
  if [[ "$expected" == "$actual" ]]; then
    PASS=$((PASS + 1))
    [[ $VERBOSE -eq 1 ]] && echo "  PASS: $test_name"
  else
    FAIL=$((FAIL + 1))
    echo "  FAIL: $test_name (expected: '$expected', got: '$actual')"
  fi
}

# ─── Setup ───
echo "=== SPEC-194: Session greeting tests ==="

# Check greeting script exists
TOTAL=$((TOTAL + 1))
if [[ -x "$GREETING_SCRIPT" ]]; then
  PASS=$((PASS + 1))
  [[ $VERBOSE -eq 1 ]] && echo "  PASS: greeting script exists and is executable"
else
  FAIL=$((FAIL + 1))
  echo "  FAIL: greeting script not found or not executable at $GREETING_SCRIPT"
  echo "Results: $PASS/$TOTAL passed, $FAIL failed"
  exit 1
fi

# ─── Test 0b: .agents/bin/ symlinks for all swain-session scripts (SPEC-206) ───
echo "Test 0b: Symlinks in .agents/bin/ for swain-session scripts"
OPERATOR_SCRIPTS="swain swain-box"
for script in "$SCRIPT_DIR"/*; do
  [[ -f "$script" && -x "$script" ]] || continue
  sname="$(basename "$script")"
  [[ "$sname" == test-* || "$sname" == test_* ]] && continue
  echo " $OPERATOR_SCRIPTS " | grep -q " $sname " && continue
  SYMLINK_PATH="$REPO_ROOT/.agents/bin/$sname"
  TOTAL=$((TOTAL + 1))
  if [[ -L "$SYMLINK_PATH" && -e "$SYMLINK_PATH" ]]; then
    PASS=$((PASS + 1))
    [[ $VERBOSE -eq 1 ]] && echo "  PASS: .agents/bin/$sname symlink resolves"
  else
    FAIL=$((FAIL + 1))
    if [[ -L "$SYMLINK_PATH" ]]; then
      echo "  FAIL: .agents/bin/$sname symlink is broken"
    else
      echo "  FAIL: .agents/bin/$sname symlink missing"
    fi
  fi
done

# ─── Test 1: Greeting includes branch info ───
echo "Test 1: Branch info in output"
output=$(bash "$GREETING_SCRIPT" 2>/dev/null)
branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
assert_contains "greeting contains branch name" "$branch" "$output"

# ─── Test 2: JSON output mode ───
echo "Test 2: JSON output mode"
json_output=$(bash "$GREETING_SCRIPT" --json 2>/dev/null)
assert_contains "json has branch key" '"branch"' "$json_output"
assert_contains "json has greeting key" '"greeting"' "$json_output"

# ─── Test 3: Bookmark shown if present ───
echo "Test 3: Bookmark in output (if session.json has one)"
if [[ -f "$REPO_ROOT/.agents/session.json" ]]; then
  bookmark=$(jq -r '.bookmark.note // empty' "$REPO_ROOT/.agents/session.json" 2>/dev/null)
  if [[ -n "$bookmark" ]]; then
    assert_contains "greeting contains bookmark" "Bookmark" "$output"
  else
    TOTAL=$((TOTAL + 1))
    PASS=$((PASS + 1))
    [[ $VERBOSE -eq 1 ]] && echo "  PASS: no bookmark set (skip)"
  fi
else
  TOTAL=$((TOTAL + 1))
  PASS=$((PASS + 1))
  [[ $VERBOSE -eq 1 ]] && echo "  PASS: no session.json (skip)"
fi

# ─── Test 4: Focus lane shown if present ───
echo "Test 4: Focus lane in output (if set)"
if [[ -f "$REPO_ROOT/.agents/session.json" ]]; then
  focus=$(jq -r '.focus_lane // empty' "$REPO_ROOT/.agents/session.json" 2>/dev/null)
  if [[ -n "$focus" ]]; then
    assert_contains "greeting contains focus lane" "$focus" "$output"
  else
    TOTAL=$((TOTAL + 1))
    PASS=$((PASS + 1))
    [[ $VERBOSE -eq 1 ]] && echo "  PASS: no focus lane set (skip)"
  fi
else
  TOTAL=$((TOTAL + 1))
  PASS=$((PASS + 1))
  [[ $VERBOSE -eq 1 ]] && echo "  PASS: no session.json (skip)"
fi

# ─── Test 5: Does NOT include specgraph or GitHub data ───
echo "Test 5: No specgraph/GitHub data in greeting"
assert_not_contains "no specgraph output" "specgraph" "$output"
assert_not_contains "no GitHub issues" "github.com" "$output"

# ─── Test 6: Performance — greeting completes in <2000ms ───
echo "Test 6: Performance (<2000ms)"
start_ms=$(python3 -c "import time; print(int(time.time()*1000))")
bash "$GREETING_SCRIPT" >/dev/null 2>&1
end_ms=$(python3 -c "import time; print(int(time.time()*1000))")
elapsed=$((end_ms - start_ms))
TOTAL=$((TOTAL + 1))
if [[ $elapsed -lt 2000 ]]; then
  PASS=$((PASS + 1))
  [[ $VERBOSE -eq 1 ]] && echo "  PASS: performance (${elapsed}ms)"
else
  FAIL=$((FAIL + 1))
  echo "  FAIL: performance (${elapsed}ms, expected <2000ms)"
fi

# ─── Test 7: Dirty/clean state shown ───
echo "Test 7: Working tree state in output"
json_output=$(bash "$GREETING_SCRIPT" --json 2>/dev/null)
assert_contains "json has dirty key" '"dirty"' "$json_output"

# ─── Summary ───
echo ""
echo "Results: $PASS/$TOTAL passed, $FAIL failed"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
