#!/usr/bin/env bash
# test-session-digest.sh — tests for swain-session-digest.sh (SPEC-199)
# Verifies session digest generation and JSONL output

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
SCRIPT="$REPO_ROOT/.agents/bin/swain-session-digest.sh"

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
echo "Test 1: swain-session-digest.sh exists and is executable"
assert "script exists" "$([ -f "$SCRIPT" ] && echo 0 || echo 1)"
assert "script is executable" "$([ -x "$SCRIPT" ] && echo 0 || echo 1)"

# --- Test 2: Missing required args exits with code 1 ---
echo "Test 2: missing required args exits with code 1"
result=$(bash "$SCRIPT" 2>/dev/null && echo 0 || echo $?)
assert "no args exits non-zero" "$([ "$result" != "0" ] && echo 0 || echo 1)"

result=$(bash "$SCRIPT" --session-id test-123 2>/dev/null && echo 0 || echo $?)
assert "missing --start-time exits non-zero" "$([ "$result" != "0" ] && echo 0 || echo 1)"

result=$(bash "$SCRIPT" --start-time 2026-01-01T00:00:00Z 2>/dev/null && echo 0 || echo $?)
assert "missing --session-id exits non-zero" "$([ "$result" != "0" ] && echo 0 || echo 1)"

# --- Test 3: Produces valid JSONL with required args ---
echo "Test 3: produces valid JSONL with --session-id and --start-time"
TMPDIR_TEST=$(mktemp -d)
trap 'rm -rf "$TMPDIR_TEST"' EXIT

# Use a recent timestamp to get some commits from the real repo
ONE_HOUR_AGO=$(date -u -v-1H +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null)
OUTPUT_FILE="$TMPDIR_TEST/session-log.jsonl"

if bash "$SCRIPT" \
    --session-id "test-session-001" \
    --start-time "$ONE_HOUR_AGO" \
    --repo-root "$REPO_ROOT" \
    --output "$OUTPUT_FILE" 2>/dev/null; then
  assert "script exits 0 with valid args" "0"
else
  assert "script exits 0 with valid args" "1"
fi

# Check output file exists and has content
assert "output file exists" "$([ -f "$OUTPUT_FILE" ] && echo 0 || echo 1)"
if [ -f "$OUTPUT_FILE" ]; then
  LINE=$(head -1 "$OUTPUT_FILE")
  # Validate it's valid JSON using python
  echo "$LINE" | uv run python3 -c "import sys, json; json.loads(sys.stdin.read())" 2>/dev/null
  assert "output is valid JSON" "$?"
else
  assert "output is valid JSON" "1"
fi

# --- Test 4: JSONL contains required fields ---
echo "Test 4: JSONL contains required fields"
if [ -f "$OUTPUT_FILE" ]; then
  LINE=$(head -1 "$OUTPUT_FILE")
  for field in session_id timestamp artifacts_touched commits tasks_closed session_summary; do
    echo "$LINE" | uv run python3 -c "import sys, json; d=json.loads(sys.stdin.read()); assert '$field' in d" 2>/dev/null
    assert "contains field: $field" "$?"
  done
  # Verify session_id matches what we passed
  sid=$(echo "$LINE" | uv run python3 -c "import sys, json; print(json.loads(sys.stdin.read())['session_id'])" 2>/dev/null)
  assert "session_id matches input" "$([ "$sid" = "test-session-001" ] && echo 0 || echo 1)"
else
  for field in session_id timestamp artifacts_touched commits tasks_closed session_summary; do
    assert "contains field: $field" "1"
  done
  assert "session_id matches input" "1"
fi

# --- Test 5: With --focus, focus_lane is populated ---
echo "Test 5: --focus populates focus_lane"
OUTPUT_FILE2="$TMPDIR_TEST/session-log2.jsonl"
if bash "$SCRIPT" \
    --session-id "test-session-002" \
    --start-time "$ONE_HOUR_AGO" \
    --focus "INITIATIVE-019" \
    --repo-root "$REPO_ROOT" \
    --output "$OUTPUT_FILE2" 2>/dev/null; then
  LINE=$(head -1 "$OUTPUT_FILE2")
  focus=$(echo "$LINE" | uv run python3 -c "import sys, json; print(json.loads(sys.stdin.read())['focus_lane'])" 2>/dev/null)
  assert "focus_lane is INITIATIVE-019" "$([ "$focus" = "INITIATIVE-019" ] && echo 0 || echo 1)"
else
  assert "focus_lane is INITIATIVE-019" "1"
fi

# --- Test 6: Without --focus, focus_lane is null ---
echo "Test 6: without --focus, focus_lane is null"
if [ -f "$OUTPUT_FILE" ]; then
  LINE=$(head -1 "$OUTPUT_FILE")
  focus=$(echo "$LINE" | uv run python3 -c "import sys, json; print(json.loads(sys.stdin.read()).get('focus_lane'))" 2>/dev/null)
  assert "focus_lane is None" "$([ "$focus" = "None" ] && echo 0 || echo 1)"
else
  assert "focus_lane is None" "1"
fi

# --- Test 7: Output is appended, not overwritten ---
echo "Test 7: output is appended, not overwritten"
OUTPUT_FILE3="$TMPDIR_TEST/session-log3.jsonl"
bash "$SCRIPT" \
    --session-id "test-session-003a" \
    --start-time "$ONE_HOUR_AGO" \
    --repo-root "$REPO_ROOT" \
    --output "$OUTPUT_FILE3" 2>/dev/null || true
bash "$SCRIPT" \
    --session-id "test-session-003b" \
    --start-time "$ONE_HOUR_AGO" \
    --repo-root "$REPO_ROOT" \
    --output "$OUTPUT_FILE3" 2>/dev/null || true
if [ -f "$OUTPUT_FILE3" ]; then
  line_count=$(wc -l < "$OUTPUT_FILE3" | tr -d ' ')
  assert "file has 2 lines after 2 runs" "$([ "$line_count" = "2" ] && echo 0 || echo 1)"
else
  assert "file has 2 lines after 2 runs" "1"
fi

# --- Test 8: Handles empty sessions gracefully ---
echo "Test 8: handles empty sessions (far future start-time)"
OUTPUT_FILE4="$TMPDIR_TEST/session-log4.jsonl"
if bash "$SCRIPT" \
    --session-id "test-session-004" \
    --start-time "2099-01-01T00:00:00Z" \
    --repo-root "$REPO_ROOT" \
    --output "$OUTPUT_FILE4" 2>/dev/null; then
  assert "exits 0 for empty session" "0"
  LINE=$(head -1 "$OUTPUT_FILE4")
  commits=$(echo "$LINE" | uv run python3 -c "import sys, json; print(json.loads(sys.stdin.read())['commits'])" 2>/dev/null)
  assert "commits is 0 for empty session" "$([ "$commits" = "0" ] && echo 0 || echo 1)"
else
  assert "exits 0 for empty session" "1"
  assert "commits is 0 for empty session" "1"
fi

# --- Summary ---
echo ""
echo "Results: $PASS/$TOTAL passed, $FAIL failed"
if [[ $FAIL -gt 0 ]]; then
  exit 1
fi
