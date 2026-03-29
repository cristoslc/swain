#!/usr/bin/env bash
# swain-session-state.sh — Session lifecycle state management
# SPEC-119: Session Lifecycle in swain-session
#
# Commands:
#   init            Create a new session state
#   record-decision Record a decision made during the session
#   close           Close the session with a walk-away signal
#   resume          Read previous session state and emit resume context
#   show            Display current session state
#
# All commands accept --state-file <path> to override the default location.
set -uo pipefail

# Defaults
STATE_FILE="${SWAIN_SESSION_STATE:-.agents/session-state.json}"
SESSION_ROADMAP=""
REPO_ROOT=""
FOCUS=""
BUDGET=5
WALKAWAY=""
NOTE=""

usage() {
  echo "usage: swain-session-state.sh <command> [options]"
  echo ""
  echo "Commands: init, record-decision, close, resume, show"
  echo ""
  echo "Common options:"
  echo "  --state-file <path>      Override state file location"
  echo ""
  echo "init options:"
  echo "  --focus <ID>             Focus lane (vision/initiative ID)"
  echo "  --budget <N>             Decision budget (default: 5)"
  echo "  --session-roadmap <path> Path for SESSION-ROADMAP.md"
  echo "  --repo-root <path>       Repository root for chart.sh"
  echo ""
  echo "record-decision options:"
  echo "  --note <text>            Decision description"
  echo ""
  echo "close options:"
  echo "  --walkaway <text>        Walk-away signal text"
  echo "  --session-roadmap <path> Path to SESSION-ROADMAP.md to finalize"
}

# Parse command
COMMAND="${1:-}"
shift 2>/dev/null || true

if [ -z "$COMMAND" ]; then
  usage
  exit 1
fi

# Parse options
while [ $# -gt 0 ]; do
  case "$1" in
    --state-file)   STATE_FILE="$2"; shift 2 ;;
    --focus)        FOCUS="$2"; shift 2 ;;
    --budget)       BUDGET="$2"; shift 2 ;;
    --walkaway)     WALKAWAY="$2"; shift 2 ;;
    --note)         NOTE="$2"; shift 2 ;;
    --session-roadmap) SESSION_ROADMAP="$2"; shift 2 ;;
    --repo-root)    REPO_ROOT="$2"; shift 2 ;;
    -h|--help)      usage; exit 0 ;;
    *)              echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

# Generate a short session ID (timestamp + random suffix)
generate_session_id() {
  local ts
  ts=$(date +%Y%m%d-%H%M%S)
  local suffix
  suffix=$(head -c 4 /dev/urandom | od -An -tx1 | tr -d ' \n' | head -c 4)
  echo "session-${ts}-${suffix}"
}

# ISO 8601 timestamp
now_iso() {
  date -u +"%Y-%m-%dT%H:%M:%SZ"
}

cmd_init() {
  local session_id
  session_id=$(generate_session_id)
  local start_time
  start_time=$(now_iso)

  # Ensure directory exists
  mkdir -p "$(dirname "$STATE_FILE")"

  # Write initial state
  python3 -c "
import json
state = {
    'session_id': '$session_id',
    'focus_lane': '$FOCUS',
    'phase': 'active',
    'start_time': '$start_time',
    'end_time': None,
    'decision_budget': $BUDGET,
    'decisions_made': 0,
    'decisions': [],
    'walkaway': None
}
with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)
"

  # Generate SESSION-ROADMAP.md if path provided and chart.sh available
  if [ -n "$SESSION_ROADMAP" ]; then
    local repo="${REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
    local chart
    chart=$(find "$repo" -path '*/swain-design/scripts/chart.sh' -print -quit 2>/dev/null)
    if [ -n "$chart" ] && [ -n "$FOCUS" ]; then
      bash "$chart" session --focus "$FOCUS" 2>/dev/null
      # chart.sh writes to SESSION-ROADMAP.md in repo root; move if needed
      local default_roadmap="$repo/SESSION-ROADMAP.md"
      if [ "$SESSION_ROADMAP" != "$default_roadmap" ] && [ -f "$default_roadmap" ]; then
        cp "$default_roadmap" "$SESSION_ROADMAP"
      fi
    fi
  fi

  echo "$session_id"
}

cmd_record_decision() {
  if [ ! -f "$STATE_FILE" ]; then
    echo "Error: No active session. Run 'init' first." >&2
    exit 1
  fi

  python3 -c "
import json
from datetime import datetime, timezone

with open('$STATE_FILE') as f:
    state = json.load(f)

state['decisions_made'] = state.get('decisions_made', 0) + 1
state['decisions'].append({
    'note': '''$NOTE''',
    'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
})

with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)
"
}

cmd_close() {
  if [ ! -f "$STATE_FILE" ]; then
    echo "Error: No active session. Run 'init' first." >&2
    exit 1
  fi

  local end_time
  end_time=$(now_iso)

  python3 -c "
import json

with open('$STATE_FILE') as f:
    state = json.load(f)

state['phase'] = 'closed'
state['end_time'] = '$end_time'
state['walkaway'] = '''$WALKAWAY'''

with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)
"

  # Append walk-away signal to SESSION-ROADMAP.md if provided
  if [ -n "$SESSION_ROADMAP" ] && [ -f "$SESSION_ROADMAP" ]; then
    cat >> "$SESSION_ROADMAP" <<EOF

## Walk-Away Signal

> $WALKAWAY

*Session closed: $end_time*
EOF
  fi
}

cmd_resume() {
  if [ ! -f "$STATE_FILE" ]; then
    echo "No previous session found."
    exit 0
  fi

  python3 -c "
import json

with open('$STATE_FILE') as f:
    state = json.load(f)

focus = state.get('focus_lane', 'none')
walkaway = state.get('walkaway', 'none')
decisions = state.get('decisions_made', 0)
phase = state.get('phase', 'unknown')
start = state.get('start_time', 'unknown')
end = state.get('end_time', 'unknown')
session_id = state.get('session_id', 'unknown')

print(f'Previous session: {session_id}')
print(f'Focus: {focus}')
print(f'Phase: {phase}')
print(f'Started: {start}')
if end and end != 'None':
    print(f'Ended: {end}')
print(f'Decisions made: {decisions}')
if walkaway and walkaway != 'None':
    print(f'Walk-away: {walkaway}')
"
}

cmd_show() {
  if [ ! -f "$STATE_FILE" ]; then
    echo "No active session."
    exit 0
  fi
  python3 -c "
import json
with open('$STATE_FILE') as f:
    print(json.dumps(json.load(f), indent=2))
"
}

case "$COMMAND" in
  init)             cmd_init ;;
  record-decision)  cmd_record_decision ;;
  close)            cmd_close ;;
  resume)           cmd_resume ;;
  show)             cmd_show ;;
  *)                echo "Unknown command: $COMMAND" >&2; usage; exit 1 ;;
esac
