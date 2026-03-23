#!/bin/bash
# adr-gate.sh — Gemini CLI BeforeTool hook that blocks run_shell_command
# calls containing "git commit" unless ADR compliance has been verified
# on staged artifact files.
#
# Gemini CLI hook protocol:
#   - Receives JSON on stdin with tool_name, tool_input, etc.
#   - Returns JSON on stdout with decision and optional reason
#   - Exit 0: success (parse stdout)
#   - Exit 2: emergency brake (block action, stderr = reason)
#   - Other: warning (non-fatal)

set -euo pipefail

INPUT=$(cat)

# Extract the tool input — Gemini uses different field names
TOOL_INPUT=$(echo "$INPUT" | jq -r '.tool_input // empty' 2>/dev/null)

# For run_shell_command, the command is in the tool_input
# Try both common field names
COMMAND=$(echo "$TOOL_INPUT" | jq -r '.command // .args // empty' 2>/dev/null)

# If tool_input is a string (not JSON object), use it directly
if [ -z "$COMMAND" ] && [ -n "$TOOL_INPUT" ]; then
  COMMAND="$TOOL_INPUT"
fi

# Check if this is a git commit
if ! echo "$COMMAND" | grep -qE 'git\s+commit\b' 2>/dev/null; then
  echo '{"decision": "allow"}'
  exit 0
fi

# --- This is a git commit. Check ADR compliance. ---

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
STATE_DIR="${PROJECT_ROOT}/.agents/hook-state"
ADR_CHECK_STAMP="${STATE_DIR}/adr-check-passed"
ADR_CHECK_SCRIPT="$(find "$PROJECT_ROOT" -path '*/swain-design/scripts/adr-check.sh' -print -quit 2>/dev/null)"

# Check staged artifact files
STAGED_ARTIFACTS=$(git diff --cached --name-only 2>/dev/null | grep -E '^docs/(spec|epic|initiative|vision|research|adr|design|persona|runbook|journey|train)/' | head -20 || true)

if [ -z "$STAGED_ARTIFACTS" ]; then
  echo '{"decision": "allow"}'
  exit 0
fi

# Check recent ADR stamp
if [ -f "$ADR_CHECK_STAMP" ]; then
  STAMP_TIME=$(stat -f %m "$ADR_CHECK_STAMP" 2>/dev/null || echo 0)
  NOW=$(date +%s)
  AGE=$(( NOW - STAMP_TIME ))
  if [ "$AGE" -lt 300 ]; then
    echo '{"decision": "allow"}'
    exit 0
  fi
fi

# Run ADR check
if [ -z "$ADR_CHECK_SCRIPT" ]; then
  echo '{"decision": "allow", "reason": "adr-check.sh not found"}'
  exit 0
fi

FAILURES=""
while IFS= read -r artifact_path; do
  RESULT=$("$ADR_CHECK_SCRIPT" "$artifact_path" 2>&1) || true
  if echo "$RESULT" | grep -qv "^OK "; then
    FAILURES="${FAILURES}\n${RESULT}"
  fi
done <<< "$STAGED_ARTIFACTS"

if [ -n "$FAILURES" ]; then
  REASON="ADR compliance check failed on staged artifacts. Fix before committing: $(echo -e "$FAILURES" | head -5)"
  jq -n --arg reason "$REASON" '{"decision": "deny", "reason": $reason}'
  exit 0
fi

# Passed — stamp and allow
mkdir -p "$STATE_DIR"
date > "$ADR_CHECK_STAMP"
echo '{"decision": "allow"}'
exit 0
