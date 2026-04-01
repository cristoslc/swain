#!/usr/bin/env bash
# test-operator-bin-symlinks.sh — tests for SPEC-214 operator bin/ symlink auto-repair
# Validates: usr/bin/ manifest scanning, auto-repair, conflict detection, dynamic exclusion

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

get_check() {
  local name="$1"
  local output="$2"
  echo "$output" | jq -r ".checks[] | select(.name == \"$name\")"
}

# --- Test 1: usr/bin/ manifest exists with expected entries ---
echo "Test 1: usr/bin/ manifest directory"
assert "skills/swain/usr/bin/ exists" "$([ -d "$REPO_ROOT/skills/swain/usr/bin" ] && echo 0 || echo 1)"
assert "swain manifest entry exists" "$([ -L "$REPO_ROOT/skills/swain/usr/bin/swain" ] && echo 0 || echo 1)"
assert "swain-box manifest entry exists" "$([ -L "$REPO_ROOT/skills/swain/usr/bin/swain-box" ] && echo 0 || echo 1)"
assert "swain manifest resolves" "$([ -e "$REPO_ROOT/skills/swain/usr/bin/swain" ] && echo 0 || echo 1)"
assert "swain-box manifest resolves" "$([ -e "$REPO_ROOT/skills/swain/usr/bin/swain-box" ] && echo 0 || echo 1)"

# --- Test 2: AC1 — missing bin/swain auto-repaired ---
echo "Test 2: AC1 — missing bin/swain auto-repaired"
rm -f "$REPO_ROOT/bin/swain"
output=$(bash "$DOCTOR_SCRIPT" 2>/dev/null)
check=$(get_check "operator_bin_symlinks" "$output")
assert "bin/swain recreated" "$([ -L "$REPO_ROOT/bin/swain" ] && echo 0 || echo 1)"
assert "bin/swain resolves to script" "$([ -e "$REPO_ROOT/bin/swain" ] && echo 0 || echo 1)"

# --- Test 3: AC2 — missing bin/swain-box auto-repaired ---
echo "Test 3: AC2 — missing bin/swain-box auto-repaired"
rm -f "$REPO_ROOT/bin/swain-box"
output=$(bash "$DOCTOR_SCRIPT" 2>/dev/null)
assert "bin/swain-box recreated" "$([ -L "$REPO_ROOT/bin/swain-box" ] && echo 0 || echo 1)"
assert "bin/swain-box resolves to script" "$([ -e "$REPO_ROOT/bin/swain-box" ] && echo 0 || echo 1)"

# --- Test 4: AC3 — stale symlink repaired ---
echo "Test 4: AC3 — stale bin/swain symlink repaired"
ln -sf "/nonexistent/old/path/swain" "$REPO_ROOT/bin/swain"
output=$(bash "$DOCTOR_SCRIPT" 2>/dev/null)
check=$(get_check "operator_bin_symlinks" "$output")
assert "stale symlink replaced" "$([ -e "$REPO_ROOT/bin/swain" ] && echo 0 || echo 1)"
actual_target=$(readlink -f "$REPO_ROOT/bin/swain" 2>/dev/null)
expected_target=$(readlink -f "$REPO_ROOT/skills/swain/scripts/swain" 2>/dev/null)
assert "points to correct script" "$([ "$actual_target" = "$expected_target" ] && echo 0 || echo 1)"

# --- Test 5: AC4 — real file conflict not overwritten ---
echo "Test 5: AC4 — real file conflict not overwritten"
rm -f "$REPO_ROOT/bin/swain"
echo "real file" > "$REPO_ROOT/bin/swain"
output=$(bash "$DOCTOR_SCRIPT" 2>/dev/null)
check=$(get_check "operator_bin_symlinks" "$output")
status=$(echo "$check" | jq -r '.status')
message=$(echo "$check" | jq -r '.detail // .message')
assert "check status is warning" "$([ "$status" = "warning" ] && echo 0 || echo 1)"
assert "conflict mentioned" "$(echo "$message" | grep -q "conflict" && echo 0 || echo 1)"
assert "real file preserved" "$([ ! -L "$REPO_ROOT/bin/swain" ] && echo 0 || echo 1)"
# Restore
rm -f "$REPO_ROOT/bin/swain"
bash "$DOCTOR_SCRIPT" >/dev/null 2>&1  # let doctor recreate

# --- Test 6: AC5 — new script in usr/bin/ gets auto-linked ---
echo "Test 6: AC5 — new operator script added to manifest"
# Create a test script
mkdir -p "$REPO_ROOT/skills/swain/scripts"
echo '#!/bin/bash' > "$REPO_ROOT/skills/swain/scripts/test-operator-dummy"
chmod +x "$REPO_ROOT/skills/swain/scripts/test-operator-dummy"
ln -sf ../../scripts/test-operator-dummy "$REPO_ROOT/skills/swain/usr/bin/test-operator-dummy"
rm -f "$REPO_ROOT/bin/test-operator-dummy"
output=$(bash "$DOCTOR_SCRIPT" 2>/dev/null)
assert "new script gets bin/ symlink" "$([ -L "$REPO_ROOT/bin/test-operator-dummy" ] && echo 0 || echo 1)"
# Cleanup
rm -f "$REPO_ROOT/bin/test-operator-dummy" "$REPO_ROOT/skills/swain/usr/bin/test-operator-dummy" "$REPO_ROOT/skills/swain/scripts/test-operator-dummy"

# --- Test 7: AC6 — Check 20 excludes operator scripts dynamically ---
echo "Test 7: AC6 — .agents/bin/ check excludes operator scripts"
output=$(bash "$DOCTOR_SCRIPT" 2>/dev/null)
agents_check=$(get_check "agents_bin_symlinks" "$output")
agents_detail=$(echo "$agents_check" | jq -r '.detail // .message // ""')
# Operator scripts (swain, swain-box) should NOT appear as missing in .agents/bin/
assert "swain not flagged in .agents/bin/" "$(echo "$agents_detail" | grep -qv "missing.*swain[^-]" && echo 0 || echo 1)"
assert "swain-box not flagged in .agents/bin/" "$(echo "$agents_detail" | grep -qv "missing.*swain-box" && echo 0 || echo 1)"

# --- Test 8: old check names removed ---
echo "Test 8: old check names removed"
output=$(bash "$DOCTOR_SCRIPT" 2>/dev/null)
check_names=$(echo "$output" | jq -r '.checks[].name')
assert "no swain_box check" "$(echo "$check_names" | grep -q "^swain_box$" && echo 1 || echo 0)"
assert "no swain_symlink check" "$(echo "$check_names" | grep -q "^swain_symlink$" && echo 1 || echo 0)"
assert "operator_bin_symlinks present" "$(echo "$check_names" | grep -q "operator_bin_symlinks" && echo 0 || echo 1)"

# --- Summary ---
echo ""
echo "Results: $PASS/$TOTAL passed, $FAIL failed"
if [[ $FAIL -gt 0 ]]; then
  exit 1
fi
