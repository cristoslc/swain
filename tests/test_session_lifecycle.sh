#!/usr/bin/env bash
# RED tests for SPEC-119: Session Lifecycle in swain-session
# Covers: session-state.json schema, start, close, resume, decision budget
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SCRIPTS_DIR="$REPO_ROOT/skills/swain-session/scripts"
STATE_SCRIPT="$SCRIPTS_DIR/swain-session-state.sh"
PASS=0
FAIL=0
TMPDIR_BASE=""

setup_tmpdir() {
  TMPDIR_BASE=$(mktemp -d)
  export SWAIN_SESSION_STATE="$TMPDIR_BASE/session-state.json"
}

teardown_tmpdir() {
  [ -n "$TMPDIR_BASE" ] && rm -rf "$TMPDIR_BASE"
}

assert() {
  local desc="$1" result="$2"
  if [ "$result" = "true" ]; then
    echo "  PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $desc"
    FAIL=$((FAIL + 1))
  fi
}

assert_file_exists() {
  local desc="$1" path="$2"
  if [ -f "$path" ]; then
    echo "  PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $desc (file not found: $path)"
    FAIL=$((FAIL + 1))
  fi
}

assert_json_field() {
  local desc="$1" file="$2" field="$3" expected="$4"
  local actual
  actual=$(python3 -c "
import json
with open('$file') as f:
    d = json.load(f)
keys = '$field'.split('.')
v = d
for k in keys:
    v = v.get(k) if isinstance(v, dict) else None
print(v)
" 2>/dev/null)
  if [ "$actual" = "$expected" ]; then
    echo "  PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $desc (expected '$expected', got '$actual')"
    FAIL=$((FAIL + 1))
  fi
}

# ============================================================
echo "=== SPEC-119 T1: Session State Schema and Lifecycle ==="
# ============================================================

setup_tmpdir

# T1.1: Script exists
assert_file_exists "swain-session-state.sh exists" "$STATE_SCRIPT"

# T1.2: Init creates session-state.json with required fields
bash "$STATE_SCRIPT" init --focus "INITIATIVE-019" --state-file "$SWAIN_SESSION_STATE" 2>/dev/null
assert_file_exists "init creates session-state.json" "$SWAIN_SESSION_STATE"

# T1.3: Schema has required fields
assert_json_field "has session_id" "$SWAIN_SESSION_STATE" "session_id" "$(python3 -c "
import json
with open('$SWAIN_SESSION_STATE') as f: d=json.load(f)
print(d.get('session_id',''))
" 2>/dev/null)"
assert_json_field "has focus_lane" "$SWAIN_SESSION_STATE" "focus_lane" "INITIATIVE-019"
assert_json_field "has phase=active" "$SWAIN_SESSION_STATE" "phase" "active"
assert_json_field "has decisions_made=0" "$SWAIN_SESSION_STATE" "decisions_made" "0"
assert_json_field "has decision_budget=5" "$SWAIN_SESSION_STATE" "decision_budget" "5"

# T1.4: Has start_time (non-null)
HAS_START=$(python3 -c "
import json
with open('$SWAIN_SESSION_STATE') as f: d=json.load(f)
print('true' if d.get('start_time') else 'false')
" 2>/dev/null)
assert "has non-null start_time" "$HAS_START"

# T1.5: Update increments decision count
bash "$STATE_SCRIPT" record-decision --note "Approved SPEC-119 focus" --state-file "$SWAIN_SESSION_STATE" 2>/dev/null
assert_json_field "record-decision increments count" "$SWAIN_SESSION_STATE" "decisions_made" "1"

# T1.6: Close sets phase to closed
bash "$STATE_SCRIPT" close --walkaway "Left off at SPEC-119 tests" --state-file "$SWAIN_SESSION_STATE" 2>/dev/null
assert_json_field "close sets phase=closed" "$SWAIN_SESSION_STATE" "phase" "closed"

# T1.7: Close sets end_time
HAS_END=$(python3 -c "
import json
with open('$SWAIN_SESSION_STATE') as f: d=json.load(f)
print('true' if d.get('end_time') else 'false')
" 2>/dev/null)
assert "close sets end_time" "$HAS_END"

# T1.8: Close sets walkaway note
assert_json_field "close sets walkaway" "$SWAIN_SESSION_STATE" "walkaway" "Left off at SPEC-119 tests"

teardown_tmpdir

# ============================================================
echo ""
echo "=== SPEC-119 T2: Session Start ==="
# ============================================================

setup_tmpdir

# T2.1: Start with focus lane creates SESSION-ROADMAP.md
export SWAIN_SESSION_STATE="$TMPDIR_BASE/session-state.json"
SESSION_ROADMAP="$TMPDIR_BASE/SESSION-ROADMAP.md"
bash "$STATE_SCRIPT" init --focus "INITIATIVE-019" --state-file "$SWAIN_SESSION_STATE" --session-roadmap "$SESSION_ROADMAP" --repo-root "$REPO_ROOT" 2>/dev/null
assert_file_exists "start generates SESSION-ROADMAP.md" "$SESSION_ROADMAP"

# T2.2: SESSION-ROADMAP.md references the focus lane
if [ -f "$SESSION_ROADMAP" ]; then
  HAS_FOCUS=$(grep -c "INITIATIVE-019" "$SESSION_ROADMAP" 2>/dev/null || echo "0")
  assert "SESSION-ROADMAP references focus lane" "$([ "$HAS_FOCUS" -gt 0 ] && echo true || echo false)"
else
  assert "SESSION-ROADMAP references focus lane" "false"
fi

# T2.3: Default decision budget is 5
assert_json_field "default budget is 5" "$SWAIN_SESSION_STATE" "decision_budget" "5"

# T2.4: Custom budget via --budget flag
rm -f "$SWAIN_SESSION_STATE"
bash "$STATE_SCRIPT" init --focus "INITIATIVE-019" --budget 7 --state-file "$SWAIN_SESSION_STATE" 2>/dev/null
assert_json_field "custom budget=7" "$SWAIN_SESSION_STATE" "decision_budget" "7"

teardown_tmpdir

# ============================================================
echo ""
echo "=== SPEC-119 T3: Session Close ==="
# ============================================================

setup_tmpdir
export SWAIN_SESSION_STATE="$TMPDIR_BASE/session-state.json"
SESSION_ROADMAP="$TMPDIR_BASE/SESSION-ROADMAP.md"

# Init a session first
bash "$STATE_SCRIPT" init --focus "INITIATIVE-019" --state-file "$SWAIN_SESSION_STATE" --session-roadmap "$SESSION_ROADMAP" --repo-root "$REPO_ROOT" 2>/dev/null

# T3.1: Close appends walk-away signal to SESSION-ROADMAP.md
bash "$STATE_SCRIPT" close --walkaway "Finished SPEC-119 RED tests" --state-file "$SWAIN_SESSION_STATE" --session-roadmap "$SESSION_ROADMAP" 2>/dev/null
if [ -f "$SESSION_ROADMAP" ]; then
  HAS_WALKAWAY=$(grep -c "Finished SPEC-119 RED tests" "$SESSION_ROADMAP" 2>/dev/null || echo "0")
  assert "close appends walkaway to SESSION-ROADMAP" "$([ "$HAS_WALKAWAY" -gt 0 ] && echo true || echo false)"
else
  assert "close appends walkaway to SESSION-ROADMAP" "false"
fi

# T3.2: Close sets session phase to closed
assert_json_field "close sets phase=closed" "$SWAIN_SESSION_STATE" "phase" "closed"

teardown_tmpdir

# ============================================================
echo ""
echo "=== SPEC-119 T4: Session Resume ==="
# ============================================================

setup_tmpdir
export SWAIN_SESSION_STATE="$TMPDIR_BASE/session-state.json"

# Create a closed session to resume from
bash "$STATE_SCRIPT" init --focus "INITIATIVE-019" --state-file "$SWAIN_SESSION_STATE" 2>/dev/null
bash "$STATE_SCRIPT" record-decision --note "Test decision" --state-file "$SWAIN_SESSION_STATE" 2>/dev/null
bash "$STATE_SCRIPT" close --walkaway "Left off at RED tests" --state-file "$SWAIN_SESSION_STATE" 2>/dev/null

# T4.1: Resume reads previous session
RESUME_OUTPUT=$(bash "$STATE_SCRIPT" resume --state-file "$SWAIN_SESSION_STATE" 2>/dev/null)
assert "resume produces output" "$([ -n "$RESUME_OUTPUT" ] && echo true || echo false)"

# T4.2: Resume output includes previous focus lane
HAS_PREV_FOCUS=$(echo "$RESUME_OUTPUT" | grep -c "INITIATIVE-019" 2>/dev/null || echo "0")
assert "resume includes previous focus lane" "$([ "$HAS_PREV_FOCUS" -gt 0 ] && echo true || echo false)"

# T4.3: Resume output includes walkaway note
HAS_PREV_WALKAWAY=$(echo "$RESUME_OUTPUT" | grep -c "Left off at RED tests" 2>/dev/null || echo "0")
assert "resume includes previous walkaway" "$([ "$HAS_PREV_WALKAWAY" -gt 0 ] && echo true || echo false)"

# T4.4: Resume output includes decision count
HAS_DECISION_COUNT=$(echo "$RESUME_OUTPUT" | grep -c "1" 2>/dev/null || echo "0")
assert "resume includes decision count" "$([ "$HAS_DECISION_COUNT" -gt 0 ] && echo true || echo false)"

teardown_tmpdir

# ============================================================
echo ""
echo "=== Results ==="
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
