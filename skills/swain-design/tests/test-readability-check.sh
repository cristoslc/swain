#!/usr/bin/env bash
# test-readability-check.sh — tests for readability-check.sh (SPEC-194)
# Verifies Flesch-Kincaid readability enforcement

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
SCRIPT="$REPO_ROOT/.agents/bin/readability-check.sh"
FIXTURES="$REPO_ROOT/skills/swain-design/tests/fixtures"

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
echo "Test 1: readability-check.sh exists and is executable"
assert "script exists" "$([ -f "$SCRIPT" ] && echo 0 || echo 1)"
assert "script is executable" "$([ -x "$SCRIPT" ] && echo 0 || echo 1)"

# --- Test 2: PASS on readability-pass.md ---
echo "Test 2: PASS on simple prose"
if [[ -x "$SCRIPT" ]]; then
  output=$(bash "$SCRIPT" "$FIXTURES/readability-pass.md" 2>/dev/null || true)
  assert "outputs PASS" "$(echo "$output" | grep -q '^PASS' && echo 0 || echo 1)"
  exit_code=0
  bash "$SCRIPT" "$FIXTURES/readability-pass.md" >/dev/null 2>&1 || exit_code=$?
  assert "exits 0" "$([ "$exit_code" -eq 0 ] && echo 0 || echo 1)"
else
  assert "outputs PASS" "1"
  assert "exits 0" "1"
fi

# --- Test 3: FAIL on readability-fail.md ---
echo "Test 3: FAIL on complex prose"
if [[ -x "$SCRIPT" ]]; then
  output=$(bash "$SCRIPT" "$FIXTURES/readability-fail.md" 2>&1 || true)
  assert "outputs FAIL" "$(echo "$output" | grep -q '^FAIL' && echo 0 || echo 1)"
  exit_code=0
  bash "$SCRIPT" "$FIXTURES/readability-fail.md" >/dev/null 2>&1 || exit_code=$?
  assert "exits 1" "$([ "$exit_code" -eq 1 ] && echo 0 || echo 1)"
else
  assert "outputs FAIL" "1"
  assert "exits 1" "1"
fi

# --- Test 4: SKIP on readability-skip.md ---
echo "Test 4: SKIP on short file"
if [[ -x "$SCRIPT" ]]; then
  output=$(bash "$SCRIPT" "$FIXTURES/readability-skip.md" 2>/dev/null || true)
  assert "outputs SKIP" "$(echo "$output" | grep -q '^SKIP' && echo 0 || echo 1)"
  exit_code=0
  bash "$SCRIPT" "$FIXTURES/readability-skip.md" >/dev/null 2>&1 || exit_code=$?
  assert "exits 0" "$([ "$exit_code" -eq 0 ] && echo 0 || echo 1)"
else
  assert "outputs SKIP" "1"
  assert "exits 0" "1"
fi

# --- Test 5: Mixed-content file outputs PASS after stripping ---
echo "Test 5: PASS on mixed-content file after stripping non-prose"
if [[ -x "$SCRIPT" ]]; then
  output=$(bash "$SCRIPT" "$FIXTURES/readability-mixed-content.md" 2>/dev/null || true)
  assert "outputs PASS" "$(echo "$output" | grep -q '^PASS' && echo 0 || echo 1)"
  exit_code=0
  bash "$SCRIPT" "$FIXTURES/readability-mixed-content.md" >/dev/null 2>&1 || exit_code=$?
  assert "exits 0" "$([ "$exit_code" -eq 0 ] && echo 0 || echo 1)"
else
  assert "outputs PASS" "1"
  assert "exits 0" "1"
fi

# --- Test 6: --threshold flag ---
echo "Test 6: --threshold 1 fails even simple prose"
if [[ -x "$SCRIPT" ]]; then
  exit_code=0
  output=$(bash "$SCRIPT" --threshold 1 "$FIXTURES/readability-pass.md" 2>&1) || exit_code=$?
  assert "exits 1 with threshold 1" "$([ "$exit_code" -eq 1 ] && echo 0 || echo 1)"
  assert "outputs FAIL" "$(echo "$output" | grep -q '^FAIL' && echo 0 || echo 1)"
else
  assert "exits 1 with threshold 1" "1"
  assert "outputs FAIL" "1"
fi

# --- Test 7: --json flag ---
echo "Test 7: --json outputs valid JSON with correct result field"
if [[ -x "$SCRIPT" ]]; then
  output=$(bash "$SCRIPT" --json "$FIXTURES/readability-pass.md" 2>/dev/null || true)
  assert "output is valid JSON" "$(echo "$output" | python3 -m json.tool >/dev/null 2>&1 && echo 0 || echo 1)"
  assert "JSON contains result=PASS" "$(echo "$output" | python3 -c "import sys,json; d=json.load(sys.stdin); sys.exit(0 if d[0]['result']=='PASS' else 1)" 2>/dev/null && echo 0 || echo 1)"
else
  assert "output is valid JSON" "1"
  assert "JSON contains result=PASS" "1"
fi

# --- Test 8: Multiple files — exits 1 when any file fails ---
echo "Test 8: multiple files — exits 1 when any fails, reports all"
if [[ -x "$SCRIPT" ]]; then
  exit_code=0
  output=$(bash "$SCRIPT" "$FIXTURES/readability-pass.md" "$FIXTURES/readability-fail.md" 2>&1) || exit_code=$?
  assert "exits 1 when any file fails" "$([ "$exit_code" -eq 1 ] && echo 0 || echo 1)"
  assert "reports pass file" "$(echo "$output" | grep -q 'PASS.*readability-pass' && echo 0 || echo 1)"
  assert "reports fail file" "$(echo "$output" | grep -q 'FAIL.*readability-fail' && echo 0 || echo 1)"
else
  assert "exits 1 when any file fails" "1"
  assert "reports pass file" "1"
  assert "reports fail file" "1"
fi

# --- Summary ---
echo ""
echo "Results: $PASS/$TOTAL passed, $FAIL failed"
if [[ $FAIL -gt 0 ]]; then
  exit 1
fi
