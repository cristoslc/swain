#!/usr/bin/env bash
# test-next-artifact-id.sh — tests for next-artifact-id.sh (SPEC-193)
# Verifies cross-branch artifact ID allocation

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
SCRIPT="$REPO_ROOT/.agents/bin/next-artifact-id.sh"

PASS=0
FAIL=0
TOTAL=0

assert() {
  local desc="$1"
  local result="$2"
  TOTAL=$((TOTAL + 1))
  if [[ "$result" == "0" ]]; then
    PASS=$((PASS + 1))
    echo "  PASS: $desc"
  else
    FAIL=$((FAIL + 1))
    echo "  FAIL: $desc"
  fi
}

# --- Test 1: Script exists and is executable ---
echo "Test 1: next-artifact-id.sh exists and is executable"
assert "script exists" "$([ -f "$SCRIPT" ] && echo 0 || echo 1)"
assert "script is executable" "$([ -x "$SCRIPT" ] && echo 0 || echo 1)"

# --- Test 2: Accepts artifact type prefix and returns a number ---
echo "Test 2: accepts type prefix and returns a number"
if [[ -x "$SCRIPT" ]]; then
  output=$(bash "$SCRIPT" SPEC 2>/dev/null || true)
  assert "returns a number for SPEC" "$(echo "$output" | grep -qE '^[0-9]+$' && echo 0 || echo 1)"
else
  assert "returns a number for SPEC" "1"
fi

# --- Test 3: Returns value higher than highest known SPEC ---
echo "Test 3: returns value higher than highest known SPEC on any branch"
if [[ -x "$SCRIPT" ]]; then
  next_id=$(bash "$SCRIPT" SPEC 2>/dev/null || echo "0")
  # Check trunk for highest SPEC
  trunk_max=$(git ls-tree -r --name-only trunk -- docs/spec/ 2>/dev/null | sed -n 's/.*SPEC-\([0-9]*\).*/\1/p' | sort -n | tail -1 || echo "0")
  # Check working tree
  local_max=$(find "$REPO_ROOT/docs/spec" -name '*SPEC-*' 2>/dev/null | sed -n 's/.*SPEC-\([0-9]*\).*/\1/p' | sort -n | tail -1 || echo "0")
  highest=$((trunk_max > local_max ? trunk_max : local_max))
  assert "next ID ($next_id) > highest known ($highest)" "$([ "$next_id" -gt "$highest" ] && echo 0 || echo 1)"
else
  assert "next ID > highest known" "1"
fi

# --- Test 4: Works with other artifact types ---
echo "Test 4: works with EPIC, INITIATIVE, ADR prefixes"
if [[ -x "$SCRIPT" ]]; then
  for prefix in EPIC INITIATIVE ADR; do
    output=$(bash "$SCRIPT" "$prefix" 2>/dev/null || true)
    assert "$prefix returns a number" "$(echo "$output" | grep -qE '^[0-9]+$' && echo 0 || echo 1)"
  done
else
  for prefix in EPIC INITIATIVE ADR; do
    assert "$prefix returns a number" "1"
  done
fi

# --- Test 5: Handles unknown prefix gracefully ---
echo "Test 5: unknown prefix returns 1 (start of series)"
if [[ -x "$SCRIPT" ]]; then
  output=$(bash "$SCRIPT" NONEXISTENT 2>/dev/null || true)
  assert "NONEXISTENT returns 1" "$([ "$output" = "1" ] && echo 0 || echo 1)"
else
  assert "NONEXISTENT returns 1" "1"
fi

# --- Test 6: Runs under 2 seconds ---
echo "Test 6: performance — completes under 2 seconds"
if [[ -x "$SCRIPT" ]]; then
  start=$(date +%s)
  bash "$SCRIPT" SPEC >/dev/null 2>&1
  end=$(date +%s)
  elapsed=$((end - start))
  assert "completes in under 2 seconds (took ${elapsed}s)" "$([ "$elapsed" -lt 2 ] && echo 0 || echo 1)"
else
  assert "completes in under 2 seconds" "1"
fi

# --- Summary ---
echo ""
echo "Results: $PASS/$TOTAL passed, $FAIL failed"
if [[ $FAIL -gt 0 ]]; then
  exit 1
fi
