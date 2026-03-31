#!/usr/bin/env bash
# test-worktree-overlap.sh — SPEC-195: Test worktree overlap detection
#
# Usage: bash test-worktree-overlap.sh [--verbose]

set -euo pipefail

VERBOSE=0
[[ "${1:-}" == "--verbose" ]] && VERBOSE=1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OVERLAP_SCRIPT="$SCRIPT_DIR/swain-worktree-overlap.sh"

PASS=0
FAIL=0
TOTAL=0

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

echo "=== SPEC-195: Worktree overlap detection tests ==="

# Test 1: Script exists
TOTAL=$((TOTAL + 1))
if [[ -x "$OVERLAP_SCRIPT" ]]; then
  PASS=$((PASS + 1))
  [[ $VERBOSE -eq 1 ]] && echo "  PASS: overlap script exists and is executable"
else
  FAIL=$((FAIL + 1))
  echo "  FAIL: overlap script not found at $OVERLAP_SCRIPT"
  echo "Results: $PASS/$TOTAL passed, $FAIL failed"
  exit 1
fi

# Test 2: No search term → error
echo "Test 2: No search term returns error"
result=$(bash "$OVERLAP_SCRIPT" 2>/dev/null || true)
found=$(echo "$result" | jq -r '.found' 2>/dev/null || echo "")
assert_eq "no search term returns found=false" "false" "$found"

# Test 3: Search for current worktree (should find this one)
echo "Test 3: Search for current worktree branch"
current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
result=$(bash "$OVERLAP_SCRIPT" "$current_branch" 2>/dev/null)
found=$(echo "$result" | jq -r '.found' 2>/dev/null)
assert_eq "current branch found" "true" "$found"

# Test 4: Search for nonexistent spec
echo "Test 4: Search for nonexistent spec"
result=$(bash "$OVERLAP_SCRIPT" "SPEC-99999" 2>/dev/null)
found=$(echo "$result" | jq -r '.found' 2>/dev/null)
assert_eq "nonexistent spec not found" "false" "$found"

# Test 5: Case-insensitive search
echo "Test 5: Case-insensitive search"
result_upper=$(bash "$OVERLAP_SCRIPT" "$(echo "$current_branch" | tr '[:lower:]' '[:upper:]')" 2>/dev/null)
found_upper=$(echo "$result_upper" | jq -r '.found' 2>/dev/null)
assert_eq "case-insensitive search works" "true" "$found_upper"

# Test 6: Performance (<100ms)
echo "Test 6: Performance (<500ms)"
start_ms=$(python3 -c "import time; print(int(time.time()*1000))")
bash "$OVERLAP_SCRIPT" "SPEC-195" >/dev/null 2>&1
end_ms=$(python3 -c "import time; print(int(time.time()*1000))")
elapsed=$((end_ms - start_ms))
TOTAL=$((TOTAL + 1))
if [[ $elapsed -lt 500 ]]; then
  PASS=$((PASS + 1))
  [[ $VERBOSE -eq 1 ]] && echo "  PASS: performance (${elapsed}ms)"
else
  FAIL=$((FAIL + 1))
  echo "  FAIL: performance (${elapsed}ms, expected <100ms)"
fi

# Test 7: JSON output is valid
echo "Test 7: Valid JSON output"
result=$(bash "$OVERLAP_SCRIPT" "test" 2>/dev/null)
TOTAL=$((TOTAL + 1))
if echo "$result" | jq . >/dev/null 2>&1; then
  PASS=$((PASS + 1))
  [[ $VERBOSE -eq 1 ]] && echo "  PASS: valid JSON output"
else
  FAIL=$((FAIL + 1))
  echo "  FAIL: invalid JSON output: $result"
fi

echo ""
echo "Results: $PASS/$TOTAL passed, $FAIL failed"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
