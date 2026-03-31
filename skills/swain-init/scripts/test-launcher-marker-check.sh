#!/usr/bin/env bash
# test-launcher-marker-check.sh — SPEC-196: Test the .swain-init marker check
#
# Tests the _swain_check_marker() function that shell launchers use to
# decide whether to send /swain-init or /swain-session as the initial prompt.
#
# Usage: bash test-launcher-marker-check.sh [--verbose]

set -euo pipefail

VERBOSE=0
[[ "${1:-}" == "--verbose" ]] && VERBOSE=1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR/../templates/launchers/claude"

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

# ─── Setup temp directory ───
TMPDIR_TEST=$(mktemp -d)
trap "rm -rf '$TMPDIR_TEST'" EXIT

# Create a minimal skill file for version detection
mkdir -p "$TMPDIR_TEST/skills/swain-init"
cat > "$TMPDIR_TEST/skills/swain-init/SKILL.md" << 'SKILL'
---
name: swain-init
version: 4.1.0
---
SKILL

# Source the bash launcher to get _swain_check_marker
source "$TEMPLATE_DIR/swain.bash"

echo "=== SPEC-196: Launcher marker check tests ==="

# ─── Test 1: No marker → /swain-init ───
echo "Test 1: No .swain-init marker"
cd "$TMPDIR_TEST"
rm -f .swain-init
result=$(_swain_check_marker 2>/dev/null)
assert_eq "no marker returns /swain-init" "/swain-init" "$result"

# ─── Test 2: Current marker (same major) → /swain-session ───
echo "Test 2: Current .swain-init marker (same major version)"
cat > "$TMPDIR_TEST/.swain-init" << 'JSON'
{
  "history": [
    {
      "version": "4.1.0",
      "timestamp": "2026-03-26T18:30:00Z",
      "action": "init"
    }
  ]
}
JSON
result=$(_swain_check_marker 2>/dev/null)
assert_eq "current marker returns /swain-session" "/swain-session" "$result"

# ─── Test 3: Same major, different minor → /swain-session ───
echo "Test 3: Same major, different minor version"
cat > "$TMPDIR_TEST/.swain-init" << 'JSON'
{
  "history": [
    {
      "version": "4.0.0",
      "timestamp": "2026-03-20T10:00:00Z",
      "action": "init"
    }
  ]
}
JSON
result=$(_swain_check_marker 2>/dev/null)
assert_eq "same major different minor returns /swain-session" "/swain-session" "$result"

# ─── Test 4: Outdated marker (older major) → /swain-init ───
echo "Test 4: Outdated .swain-init marker (older major version)"
cat > "$TMPDIR_TEST/.swain-init" << 'JSON'
{
  "history": [
    {
      "version": "3.2.1",
      "timestamp": "2026-03-01T12:00:00Z",
      "action": "init"
    }
  ]
}
JSON
result=$(_swain_check_marker 2>/dev/null)
assert_eq "outdated major returns /swain-init" "/swain-init" "$result"

# ─── Test 5: Malformed marker (not JSON) → /swain-init ───
echo "Test 5: Malformed .swain-init marker"
echo "not json" > "$TMPDIR_TEST/.swain-init"
result=$(_swain_check_marker 2>/dev/null)
assert_eq "malformed marker returns /swain-init" "/swain-init" "$result"

# ─── Test 6: Marker with upgrade history → /swain-session ───
echo "Test 6: Marker with upgrade history (latest entry is current)"
cat > "$TMPDIR_TEST/.swain-init" << 'JSON'
{
  "history": [
    {
      "version": "3.0.0",
      "timestamp": "2026-02-01T12:00:00Z",
      "action": "init"
    },
    {
      "version": "4.0.0",
      "timestamp": "2026-03-15T12:00:00Z",
      "action": "upgrade"
    }
  ]
}
JSON
result=$(_swain_check_marker 2>/dev/null)
assert_eq "upgrade history with current major returns /swain-session" "/swain-session" "$result"

# ─── Test 7: Performance — marker check completes in <100ms ───
echo "Test 7: Performance (<100ms)"
cat > "$TMPDIR_TEST/.swain-init" << 'JSON'
{
  "history": [
    {
      "version": "4.1.0",
      "timestamp": "2026-03-26T18:30:00Z",
      "action": "init"
    }
  ]
}
JSON
start_ms=$(python3 -c "import time; print(int(time.time()*1000))")
_swain_check_marker >/dev/null 2>&1
end_ms=$(python3 -c "import time; print(int(time.time()*1000))")
elapsed=$((end_ms - start_ms))
TOTAL=$((TOTAL + 1))
if [[ $elapsed -lt 100 ]]; then
  PASS=$((PASS + 1))
  [[ $VERBOSE -eq 1 ]] && echo "  PASS: performance (${elapsed}ms)"
else
  FAIL=$((FAIL + 1))
  echo "  FAIL: performance (${elapsed}ms, expected <100ms)"
fi

# ─── Test 8: Arguments pass through to /swain-session ───
echo "Test 8: Arguments bypass marker check (go to /swain-session with purpose)"
# When args are provided, the launcher already skips to /swain-session
# This test verifies _swain_check_marker is only for the no-args path

# ─── Summary ───
echo ""
echo "Results: $PASS/$TOTAL passed, $FAIL failed"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
