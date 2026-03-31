#!/usr/bin/env bash
# test-session-close-integration.sh — SPEC-205
# Verify that swain-session SKILL.md session close section invokes
# the digest and progress-log scripts.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_FILE="$SCRIPT_DIR/../SKILL.md"

PASS=0
FAIL=0

assert() {
  local label="$1" exit_code="$2"
  if [ "$exit_code" -eq 0 ]; then
    echo "  PASS: $label"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $label"
    FAIL=$((FAIL + 1))
  fi
}

# Extract the session close section (between "### Session close" and the next "### ")
CLOSE_SECTION=$(sed -n '/^### Session close$/,/^### /p' "$SKILL_FILE")

echo "=== T1: Session close section references digest script"
echo "$CLOSE_SECTION" | grep -q "swain-session-digest" && T1=0 || T1=1
assert "T1a: mentions swain-session-digest" "$T1"

echo "=== T2: Session close section references progress-log script"
echo "$CLOSE_SECTION" | grep -q "swain-progress-log" && T2=0 || T2=1
assert "T2a: mentions swain-progress-log" "$T2"

echo "=== T3: Digest runs before progress-log"
DIGEST_LINE=$(echo "$CLOSE_SECTION" | grep -n "swain-session-digest" | head -1 | cut -d: -f1 || true)
PROGRESS_LINE=$(echo "$CLOSE_SECTION" | grep -n "swain-progress-log" | head -1 | cut -d: -f1 || true)
if [ -n "$DIGEST_LINE" ] && [ -n "$PROGRESS_LINE" ] && [ "$DIGEST_LINE" -lt "$PROGRESS_LINE" ]; then
  assert "T3a: digest appears before progress-log" "0"
else
  assert "T3a: digest appears before progress-log" "1"
fi

echo "=== T4: Progress-log uses --digest flag"
echo "$CLOSE_SECTION" | grep -q "progress-log.*--digest\|progress-log.sh.*--digest" && T4=0 || T4=1
assert "T4a: progress-log invoked with --digest" "$T4"

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] || exit 1
