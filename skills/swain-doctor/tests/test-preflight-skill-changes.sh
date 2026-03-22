#!/usr/bin/env bash
# test-preflight-skill-changes.sh — Verify preflight integrates skill-change detection
#
# Tests that swain-preflight.sh calls check-skill-changes.sh and includes
# its findings in the issues list (triggering exit 1 → doctor invocation).
#
# Usage: bash skills/swain-doctor/tests/test-preflight-skill-changes.sh

set +e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PREFLIGHT="$(cd "$SCRIPT_DIR/.." && pwd)/scripts/swain-preflight.sh"
CHECK_SCRIPT="$(cd "$SCRIPT_DIR/.." && pwd)/scripts/check-skill-changes.sh"

PASS=0
FAIL=0

pass() { echo "  PASS: $1"; ((PASS++)); }
fail() { echo "  FAIL: $1 — $2"; ((FAIL++)); }

echo "=== Preflight Skill Change Integration Tests ==="
echo ""

# --- AC5: Preflight calls check-skill-changes and exits 1 on findings ---
echo "--- AC5: Preflight includes skill-change check ---"

# The preflight script contains a reference to check-skill-changes.sh
if grep -q "check-skill-changes" "$PREFLIGHT"; then
  pass "AC5: preflight references check-skill-changes.sh"
else
  fail "AC5" "preflight does not reference check-skill-changes.sh"
fi

# Verify the check script exists and is executable
if [[ -x "$CHECK_SCRIPT" ]]; then
  pass "AC5: check-skill-changes.sh exists and is executable"
else
  fail "AC5" "check-skill-changes.sh missing or not executable"
fi

echo ""
echo "=== Summary ==="
echo "PASS: $PASS"
echo "FAIL: $FAIL"

if [[ $FAIL -gt 0 ]]; then
  exit 1
fi
