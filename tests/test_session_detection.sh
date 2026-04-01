#!/usr/bin/env bash
# RED tests for SPEC-121: Session Detection Hooks
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
CHECK_SCRIPT="$REPO_ROOT/skills/swain-session/scripts/swain-session-check.sh"
PASS=0
FAIL=0

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

echo "=== SPEC-121: Session Detection Tests ==="

# T1: Script exists
assert "swain-session-check.sh exists" "$([ -f "$CHECK_SCRIPT" ] && echo true || echo false)"

# T2: Active session returns status=active
TMPDIR=$(mktemp -d)
STATE="$TMPDIR/session-state.json"
python3 -c "
import json
from datetime import datetime, timezone
state = {
    'session_id': 'test-session',
    'focus_lane': 'INITIATIVE-019',
    'phase': 'active',
    'start_time': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'end_time': None,
    'decision_budget': 5,
    'decisions_made': 0,
    'decisions': [],
    'walkaway': None
}
with open('$STATE', 'w') as f:
    json.dump(state, f)
"
RESULT=$(bash "$CHECK_SCRIPT" --state-file "$STATE" 2>/dev/null)
STATUS=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null)
assert "active session returns status=active" "$([ "$STATUS" = "active" ] && echo true || echo false)"

# T3: Stale session returns status=stale (session older than threshold)
python3 -c "
import json
state = {
    'session_id': 'stale-session',
    'focus_lane': 'INITIATIVE-019',
    'phase': 'active',
    'start_time': '2020-01-01T00:00:00Z',
    'end_time': None,
    'decision_budget': 5,
    'decisions_made': 0,
    'decisions': [],
    'walkaway': None
}
with open('$STATE', 'w') as f:
    json.dump(state, f)
"
RESULT=$(bash "$CHECK_SCRIPT" --state-file "$STATE" --threshold 3600 2>/dev/null)
STATUS=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null)
assert "stale session returns status=stale" "$([ "$STATUS" = "stale" ] && echo true || echo false)"

# T3b: Recent activity keeps an old session active
python3 -c "
import json
from datetime import datetime, timezone
state = {
    'session_id': 'active-by-activity',
    'focus_lane': 'INITIATIVE-019',
    'phase': 'active',
    'start_time': '2020-01-01T00:00:00Z',
    'last_activity_time': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'end_time': None,
    'decision_budget': 5,
    'decisions_made': 1,
    'decisions': [{'note': 'fresh update', 'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}],
    'walkaway': None
}
with open('$STATE', 'w') as f:
    json.dump(state, f)
"
RESULT=$(bash "$CHECK_SCRIPT" --state-file "$STATE" --threshold 3600 2>/dev/null)
STATUS=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null)
assert "recent activity keeps session active" "$([ "$STATUS" = "active" ] && echo true || echo false)"

# T4: Missing state file returns status=none
rm -f "$STATE"
RESULT=$(bash "$CHECK_SCRIPT" --state-file "$STATE" 2>/dev/null)
STATUS=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null)
assert "missing state file returns status=none" "$([ "$STATUS" = "none" ] && echo true || echo false)"

# T5: Closed session returns status=closed
python3 -c "
import json
state = {
    'session_id': 'closed-session',
    'focus_lane': 'INITIATIVE-019',
    'phase': 'closed',
    'start_time': '2026-03-28T20:00:00Z',
    'end_time': '2026-03-28T21:00:00Z',
    'decision_budget': 5,
    'decisions_made': 3,
    'decisions': [],
    'walkaway': 'Done for now'
}
with open('$STATE', 'w') as f:
    json.dump(state, f)
"
RESULT=$(bash "$CHECK_SCRIPT" --state-file "$STATE" 2>/dev/null)
STATUS=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null)
assert "closed session returns status=closed" "$([ "$STATUS" = "closed" ] && echo true || echo false)"

# T6: Output includes focus_lane
FOCUS=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('focus_lane',''))" 2>/dev/null)
assert "output includes focus_lane" "$([ "$FOCUS" = "INITIATIVE-019" ] && echo true || echo false)"

# T7: Performance — check completes in < 100ms
python3 -c "
import json
from datetime import datetime, timezone
state = {
    'session_id': 'perf-test',
    'focus_lane': 'TEST',
    'phase': 'active',
    'start_time': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'end_time': None,
    'decision_budget': 5,
    'decisions_made': 0,
    'decisions': [],
    'walkaway': None
}
with open('$STATE', 'w') as f:
    json.dump(state, f)
"
START_MS=$(python3 -c "import time; print(int(time.time() * 1000))")
bash "$CHECK_SCRIPT" --state-file "$STATE" >/dev/null 2>/dev/null
END_MS=$(python3 -c "import time; print(int(time.time() * 1000))")
ELAPSED=$((END_MS - START_MS))
assert "check completes in < 100ms (took ${ELAPSED}ms)" "$([ "$ELAPSED" -lt 100 ] && echo true || echo false)"

rm -rf "$TMPDIR"

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
