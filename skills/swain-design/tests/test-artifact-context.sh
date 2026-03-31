#!/usr/bin/env bash
# test-artifact-context.sh — tests for artifact-context.sh (SPEC-201)
# Validates context-rich artifact display utility

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
SCRIPT="$REPO_ROOT/.agents/bin/artifact-context.sh"

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
echo "Test 1: artifact-context.sh exists and is executable"
assert "script exists" "$([ -f "$SCRIPT" ] && echo 0 || echo 1)"
assert "script is executable" "$([ -x "$SCRIPT" ] && echo 0 || echo 1)"

# --- Test 2: SPEC-196 returns a context line containing title and ID ---
echo "Test 2: SPEC-196 returns context line with title and ID"
if [[ -x "$SCRIPT" ]]; then
  output=$(bash "$SCRIPT" SPEC-196 2>/dev/null || true)
  assert "contains SPEC-196" "$(echo "$output" | grep -q 'SPEC-196' && echo 0 || echo 1)"
  assert "contains Collapse in title" "$(echo "$output" | grep -qi 'collapse' && echo 0 || echo 1)"
else
  assert "contains SPEC-196" "1"
  assert "contains Collapse in title" "1"
fi

# --- Test 3: EPIC-048 returns a context line containing its title ---
echo "Test 3: EPIC-048 returns context line with title"
if [[ -x "$SCRIPT" ]]; then
  output=$(bash "$SCRIPT" EPIC-048 2>/dev/null || true)
  assert "contains EPIC-048" "$(echo "$output" | grep -q 'EPIC-048' && echo 0 || echo 1)"
  assert "contains Session Startup Fast Path" "$(echo "$output" | grep -qi 'Session Startup Fast Path' && echo 0 || echo 1)"
else
  assert "contains EPIC-048" "1"
  assert "contains Session Startup Fast Path" "1"
fi

# --- Test 4: Artifact with children shows child count ---
echo "Test 4: EPIC-048 (has child specs) shows child count or progress"
if [[ -x "$SCRIPT" ]]; then
  output=$(bash "$SCRIPT" EPIC-048 2>/dev/null || true)
  # EPIC-048 has child specs — output should mention "child" or a count
  assert "shows child info or status" "$(echo "$output" | grep -qiE '(child|of [0-9]|Active)' && echo 0 || echo 1)"
else
  assert "shows child info or status" "1"
fi

# --- Test 5: --format json returns valid JSON with required fields ---
echo "Test 5: --format json returns valid JSON"
if [[ -x "$SCRIPT" ]]; then
  json_output=$(bash "$SCRIPT" --format json SPEC-196 2>/dev/null || true)
  # Check it parses as JSON
  assert "valid JSON" "$(echo "$json_output" | python3 -m json.tool >/dev/null 2>&1 && echo 0 || echo 1)"
  # Check required fields
  assert "has id field" "$(echo "$json_output" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d[0]["id"]' 2>/dev/null && echo 0 || echo 1)"
  assert "has title field" "$(echo "$json_output" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d[0]["title"]' 2>/dev/null && echo 0 || echo 1)"
  assert "has status field" "$(echo "$json_output" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d[0]["status"]' 2>/dev/null && echo 0 || echo 1)"
else
  assert "valid JSON" "1"
  assert "has id field" "1"
  assert "has title field" "1"
  assert "has status field" "1"
fi

# --- Test 6: Multiple IDs returns multiple lines ---
echo "Test 6: Multiple IDs produce multiple output lines"
if [[ -x "$SCRIPT" ]]; then
  output=$(bash "$SCRIPT" SPEC-196 EPIC-048 2>/dev/null || true)
  line_count=$(echo "$output" | grep -c '.')
  assert "at least 2 output lines" "$([ "$line_count" -ge 2 ] && echo 0 || echo 1)"
else
  assert "at least 2 output lines" "1"
fi

# --- Test 7: Invalid ID prints error to stderr, exits 1, valid results still output ---
echo "Test 7: Invalid ID (SPEC-999) prints stderr error, exits 1, valid results still output"
if [[ -x "$SCRIPT" ]]; then
  stderr_output=$(bash "$SCRIPT" SPEC-999 SPEC-196 2>&1 1>/dev/null || true)
  stdout_output=$(bash "$SCRIPT" SPEC-999 SPEC-196 2>/dev/null || true)
  exit_code=0
  bash "$SCRIPT" SPEC-999 SPEC-196 >/dev/null 2>&1 || exit_code=$?
  assert "stderr mentions SPEC-999" "$(echo "$stderr_output" | grep -q 'SPEC-999' && echo 0 || echo 1)"
  assert "exit code is 1" "$([ "$exit_code" -eq 1 ] && echo 0 || echo 1)"
  assert "stdout still contains SPEC-196 result" "$(echo "$stdout_output" | grep -q 'SPEC-196' && echo 0 || echo 1)"
else
  assert "stderr mentions SPEC-999" "1"
  assert "exit code is 1" "1"
  assert "stdout still contains SPEC-196 result" "1"
fi

# --- Test 8: No arguments exits 3 ---
echo "Test 8: No arguments exits with code 3"
if [[ -x "$SCRIPT" ]]; then
  exit_code=0
  bash "$SCRIPT" >/dev/null 2>&1 || exit_code=$?
  assert "exit code is 3" "$([ "$exit_code" -eq 3 ] && echo 0 || echo 1)"
else
  assert "exit code is 3" "1"
fi

# --- Summary ---
echo ""
echo "Results: $PASS/$TOTAL passed, $FAIL failed"
if [[ $FAIL -gt 0 ]]; then
  exit 1
fi
