#!/usr/bin/env bash
# swain-session-check.sh — Lightweight session detection for skill preambles
# SPEC-121: Session Detection Hooks Across All Skills
#
# Reads .agents/session-state.json and emits a JSON result:
#   {"status": "active|stale|closed|none", "focus_lane": "...", "session_id": "..."}
#
# Exit codes:
#   0 — session is active
#   1 — session is stale, closed, or missing (skill should prompt)
#
# Options:
#   --state-file <path>   Override state file location
#   --threshold <seconds> Staleness threshold (default: 3600 = 1 hour)
set -uo pipefail

STATE_FILE="${SWAIN_SESSION_STATE:-.agents/session-state.json}"
THRESHOLD=3600

while [ $# -gt 0 ]; do
  case "$1" in
    --state-file)  STATE_FILE="$2"; shift 2 ;;
    --threshold)   THRESHOLD="$2"; shift 2 ;;
    *)             shift ;;
  esac
done

if [ ! -f "$STATE_FILE" ]; then
  echo '{"status": "none", "focus_lane": null, "session_id": null}'
  exit 1
fi

python3 -c "
import json, sys
from datetime import datetime, timezone

with open('$STATE_FILE') as f:
    state = json.load(f)

phase = state.get('phase', 'unknown')
focus = state.get('focus_lane')
sid = state.get('session_id')
activity = state.get('last_activity_time') or state.get('start_time', '')

result = {'focus_lane': focus, 'session_id': sid}

if phase == 'closed':
    result['status'] = 'closed'
    json.dump(result, sys.stdout)
    sys.exit(1)
elif phase == 'active':
    # Check staleness
    try:
        activity_dt = datetime.fromisoformat(activity.replace('Z', '+00:00'))
        age = (datetime.now(timezone.utc) - activity_dt).total_seconds()
        if age > $THRESHOLD:
            result['status'] = 'stale'
            json.dump(result, sys.stdout)
            sys.exit(1)
        else:
            result['status'] = 'active'
            json.dump(result, sys.stdout)
            sys.exit(0)
    except (ValueError, TypeError):
        result['status'] = 'stale'
        json.dump(result, sys.stdout)
        sys.exit(1)
else:
    result['status'] = 'none'
    json.dump(result, sys.stdout)
    sys.exit(1)
"
