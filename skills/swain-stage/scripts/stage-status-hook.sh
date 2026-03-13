#!/usr/bin/env bash
# stage-status-hook.sh — Claude Code hook that updates stage-status.json
# for the MOTD panel. Reads hook event JSON from stdin and writes agent
# state to the memory directory.
#
# Configured via .claude/settings.json hooks for PostToolUse and Stop events.

set -euo pipefail

# Determine output path
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SLUG=$(echo "$REPO_ROOT" | sed 's|/|-|g')
STATUS_FILE="$HOME/.claude/projects/$SLUG/memory/stage-status.json"

# Ensure directory exists
mkdir -p "$(dirname "$STATUS_FILE")"

# Read hook JSON from stdin
INPUT=$(cat)

EVENT=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('hook_event_name',''))" 2>/dev/null || echo "")

case "$EVENT" in
  PostToolUse)
    TOOL=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_name',''))" 2>/dev/null || echo "unknown")
    cat > "$STATUS_FILE" <<EOJSON
{"state": "working", "context": "$TOOL", "updated": $(date +%s)}
EOJSON
    ;;
  Stop)
    cat > "$STATUS_FILE" <<EOJSON
{"state": "idle", "context": "", "updated": $(date +%s)}
EOJSON
    ;;
  SubagentStart)
    cat > "$STATUS_FILE" <<EOJSON
{"state": "working", "context": "subagent", "updated": $(date +%s)}
EOJSON
    ;;
  SubagentStop)
    cat > "$STATUS_FILE" <<EOJSON
{"state": "working", "context": "processing", "updated": $(date +%s)}
EOJSON
    ;;
  *)
    # Unknown event — no-op
    ;;
esac

exit 0
