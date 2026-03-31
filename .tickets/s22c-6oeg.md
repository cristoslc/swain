---
id: s22c-6oeg
status: closed
deps: [s22c-azmv]
links: []
created: 2026-03-31T03:21:00Z
type: task
priority: 1
assignee: Cristos L-C
parent: s22c-33it
tags: [spec:SPEC-194]
---
# Task 2: Write the test script

**Files:**
- Create: `skills/swain-design/tests/test-readability-check.sh`

- [ ] **Step 1: Write the test script**

Follow the pattern from `test-next-artifact-id.sh` — pure bash with assert helper, PASS/FAIL counters.

```bash
#!/usr/bin/env bash
# test-readability-check.sh — tests for readability-check.sh (SPEC-194)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
SCRIPT="$REPO_ROOT/.agents/bin/readability-check.sh"
FIXTURES="$(cd "$(dirname "$0")" && pwd)/fixtures"

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

# --- Test 2: PASS on simple prose ---
echo "Test 2: PASS on simple prose (grade <= 9)"
output=$(bash "$SCRIPT" "$FIXTURES/readability-pass.md" 2>/dev/null || true)
assert "outputs PASS" "$(echo "$output" | grep -q '^PASS' && echo 0 || echo 1)"
exit_code=0
bash "$SCRIPT" "$FIXTURES/readability-pass.md" >/dev/null 2>&1 || exit_code=$?
assert "exits 0" "$([ "$exit_code" -eq 0 ] && echo 0 || echo 1)"

# --- Test 3: FAIL on complex prose ---
echo "Test 3: FAIL on complex prose (grade > 9)"
output=$(bash "$SCRIPT" "$FIXTURES/readability-fail.md" 2>/dev/null || true)
assert "outputs FAIL" "$(echo "$output" | grep -q '^FAIL' && echo 0 || echo 1)"
exit_code=0
bash "$SCRIPT" "$FIXTURES/readability-fail.md" >/dev/null 2>&1 || exit_code=$?
assert "exits 1" "$([ "$exit_code" -eq 1 ] && echo 0 || echo 1)"

# --- Test 4: SKIP on tiny file ---
echo "Test 4: SKIP on file with < 50 words of prose"
output=$(bash "$SCRIPT" "$FIXTURES/readability-skip.md" 2>/dev/null || true)
assert "outputs SKIP" "$(echo "$output" | grep -q '^SKIP' && echo 0 || echo 1)"
exit_code=0
bash "$SCRIPT" "$FIXTURES/readability-skip.md" >/dev/null 2>&1 || exit_code=$?
assert "exits 0 for SKIP" "$([ "$exit_code" -eq 0 ] && echo 0 || echo 1)"

# --- Test 5: Stripping removes non-prose content ---
echo "Test 5: mixed-content file strips code/tables/frontmatter"
output=$(bash "$SCRIPT" "$FIXTURES/readability-mixed-content.md" 2>/dev/null || true)
assert "outputs PASS (prose is simple after stripping)" "$(echo "$output" | grep -q '^PASS' && echo 0 || echo 1)"

# --- Test 6: --threshold flag ---
echo "Test 6: --threshold override"
exit_code=0
bash "$SCRIPT" --threshold 12 "$FIXTURES/readability-fail.md" >/dev/null 2>&1 || exit_code=$?
# The fail fixture is ~grade 15+, so threshold 12 should still fail
# Use the pass fixture with threshold 1 to test that threshold lowers the bar
exit_code_low=0
bash "$SCRIPT" --threshold 1 "$FIXTURES/readability-pass.md" >/dev/null 2>&1 || exit_code_low=$?
assert "threshold 1 fails even simple prose" "$([ "$exit_code_low" -eq 1 ] && echo 0 || echo 1)"

# --- Test 7: --json flag ---
echo "Test 7: --json outputs valid JSON"
json_output=$(bash "$SCRIPT" --json "$FIXTURES/readability-pass.md" 2>/dev/null || true)
assert "output is valid JSON" "$(echo "$json_output" | python3 -m json.tool >/dev/null 2>&1 && echo 0 || echo 1)"
assert "JSON has result field" "$(echo "$json_output" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d[0]['result']=='PASS'" 2>/dev/null && echo 0 || echo 1)"

# --- Test 8: Multiple files, one fail ---
echo "Test 8: multiple files with mixed results"
exit_code=0
output=$(bash "$SCRIPT" "$FIXTURES/readability-pass.md" "$FIXTURES/readability-fail.md" 2>/dev/null) || exit_code=$?
assert "exits 1 when any file fails" "$([ "$exit_code" -eq 1 ] && echo 0 || echo 1)"
line_count=$(echo "$output" | wc -l | tr -d ' ')
assert "reports both files" "$([ "$line_count" -ge 2 ] && echo 0 || echo 1)"

# --- Summary ---
echo ""
echo "Results: $PASS/$TOTAL pas...

