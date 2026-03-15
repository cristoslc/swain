#!/usr/bin/env bash
set -euo pipefail

# Set or clear the focus lane in session.json
# Usage: swain-focus.sh set VISION-001
#        swain-focus.sh clear
#        swain-focus.sh (show current)

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "Error: not inside a git repository" >&2
  exit 1
}
SESSION_FILE="$REPO_ROOT/.agents/session.json"

ACTION="${1:-}"
FOCUS_ID="${2:-}"

if [[ ! -f "$SESSION_FILE" ]]; then
  echo '{}' > "$SESSION_FILE"
fi

case "$ACTION" in
  set)
    if [[ -z "$FOCUS_ID" ]]; then
      echo "Usage: swain-focus.sh set <VISION-ID or INITIATIVE-ID>" >&2
      exit 1
    fi
    jq --arg focus "$FOCUS_ID" '.focus_lane = $focus' "$SESSION_FILE" > "${SESSION_FILE}.tmp" \
      && mv "${SESSION_FILE}.tmp" "$SESSION_FILE"
    echo "Focus lane set to: $FOCUS_ID"
    ;;
  clear)
    jq 'del(.focus_lane)' "$SESSION_FILE" > "${SESSION_FILE}.tmp" \
      && mv "${SESSION_FILE}.tmp" "$SESSION_FILE"
    echo "Focus lane cleared"
    ;;
  *)
    # Show current focus
    CURRENT=$(jq -r '.focus_lane // "none"' "$SESSION_FILE" 2>/dev/null || echo "none")
    echo "Current focus: $CURRENT"
    ;;
esac
