#!/usr/bin/env bash
# test-swain-doctor-sh.sh — tests for the consolidated swain-doctor.sh script
# Verifies SPEC-192: parallel check cascade failure fix

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
DOCTOR_SCRIPT="$REPO_ROOT/.agents/bin/swain-doctor.sh"

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
echo "Test 1: swain-doctor.sh exists and is executable"
assert "script exists" "$([ -f "$DOCTOR_SCRIPT" ] && echo 0 || echo 1)"
assert "script is executable" "$([ -x "$DOCTOR_SCRIPT" ] && echo 0 || echo 1)"

# --- Test 2: Script outputs valid JSON ---
echo "Test 2: outputs valid JSON"
if [[ -x "$DOCTOR_SCRIPT" ]]; then
  output=$(bash "$DOCTOR_SCRIPT" 2>/dev/null || true)
  echo "$output" | jq empty 2>/dev/null
  assert "output is valid JSON" "$?"
else
  assert "output is valid JSON" "1"
fi

# --- Test 3: JSON has expected structure ---
echo "Test 3: JSON has expected top-level fields"
if [[ -x "$DOCTOR_SCRIPT" ]]; then
  output=$(bash "$DOCTOR_SCRIPT" 2>/dev/null || true)
  assert "has 'checks' array" "$(echo "$output" | jq -e '.checks | type == "array"' >/dev/null 2>&1 && echo 0 || echo 1)"
  assert "has 'summary' object" "$(echo "$output" | jq -e '.summary | type == "object"' >/dev/null 2>&1 && echo 0 || echo 1)"
  assert "summary has total count" "$(echo "$output" | jq -e '.summary.total | type == "number"' >/dev/null 2>&1 && echo 0 || echo 1)"
else
  assert "has 'checks' array" "1"
  assert "has 'summary' object" "1"
  assert "summary has total count" "1"
fi

# --- Test 4: Each check has name, status, and message ---
echo "Test 4: each check entry has required fields"
if [[ -x "$DOCTOR_SCRIPT" ]]; then
  output=$(bash "$DOCTOR_SCRIPT" 2>/dev/null || true)
  # Every check must have name and status
  bad_checks=$(echo "$output" | jq '[.checks[] | select(.name == null or .status == null)] | length' 2>/dev/null || echo "999")
  assert "all checks have name and status" "$([ "$bad_checks" = "0" ] && echo 0 || echo 1)"
else
  assert "all checks have name and status" "1"
fi

# --- Test 5: Script does NOT exit non-zero when checks find issues ---
echo "Test 5: script always exits 0 (findings reported in JSON, not exit code)"
if [[ -x "$DOCTOR_SCRIPT" ]]; then
  bash "$DOCTOR_SCRIPT" >/dev/null 2>&1
  assert "exits 0 regardless of findings" "$?"
else
  assert "exits 0 regardless of findings" "1"
fi

# --- Test 6: Known check names are present ---
echo "Test 6: known check categories are present"
if [[ -x "$DOCTOR_SCRIPT" ]]; then
  output=$(bash "$DOCTOR_SCRIPT" 2>/dev/null || true)
  check_names=$(echo "$output" | jq -r '.checks[].name' 2>/dev/null || true)
  assert "governance check present" "$(echo "$check_names" | grep -q "governance" && echo 0 || echo 1)"
  assert "tools check present" "$(echo "$check_names" | grep -q "tools" && echo 0 || echo 1)"
  assert "agents_directory check present" "$(echo "$check_names" | grep -q "agents_directory" && echo 0 || echo 1)"
else
  assert "governance check present" "1"
  assert "tools check present" "1"
  assert "agents_directory check present" "1"
fi

# --- Summary ---
echo ""
echo "Results: $PASS/$TOTAL passed, $FAIL failed"
if [[ $FAIL -gt 0 ]]; then
  exit 1
fi
