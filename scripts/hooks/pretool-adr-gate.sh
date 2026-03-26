#!/bin/bash
# pretool-adr-gate.sh — PreToolUse hook that blocks git commit
# unless ADR compliance has been verified on staged artifact files.
#
# Protocol: receives JSON on stdin with tool_name, tool_input, tool_use_id.
# Returns JSON on stdout with permissionDecision and optional reason.
#
# Exit codes:
#   0 — success (parse stdout JSON)
#   2 — blocking error (deny the tool call)
#   other — non-blocking warning

set -euo pipefail

# Read the hook input from stdin
INPUT=$(cat)

# Extract tool name and input
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
TOOL_INPUT=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Only gate Bash tool calls that look like git commit
if [ "$TOOL_NAME" != "Bash" ]; then
  echo '{"permissionDecision": "allow"}' # nosemgrep: hooks-unconditional-allow-generic
  exit 0
fi

# Check if this is a git commit command
if ! echo "$TOOL_INPUT" | grep -qE '^\s*git\s+commit\b'; then
  echo '{"permissionDecision": "allow"}' # nosemgrep: hooks-unconditional-allow-generic
  exit 0
fi

# --- This is a git commit. Check ADR compliance. ---

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
STATE_DIR="${PROJECT_ROOT}/.agents/hook-state"
ADR_CHECK_STAMP="${STATE_DIR}/adr-check-passed"
ADR_CHECK_SCRIPT="$(find "$PROJECT_ROOT" -path '*/swain-design/scripts/adr-check.sh' -print -quit 2>/dev/null)"

# Check if any staged files are artifact documents
STAGED_ARTIFACTS=$(git diff --cached --name-only 2>/dev/null | grep -E '^docs/(spec|epic|initiative|vision|research|adr|design|persona|runbook|journey|train)/' | head -20 || true)

if [ -z "$STAGED_ARTIFACTS" ]; then
  # No artifact files staged — allow the commit
  echo '{"permissionDecision": "allow"}' # nosemgrep: hooks-unconditional-allow-generic
  exit 0
fi

# Check if ADR compliance stamp exists and is recent (within last 5 minutes)
if [ -f "$ADR_CHECK_STAMP" ]; then
  STAMP_TIME=$(stat -f %m "$ADR_CHECK_STAMP" 2>/dev/null || echo 0)
  NOW=$(date +%s)
  AGE=$(( NOW - STAMP_TIME ))
  if [ "$AGE" -lt 300 ]; then
    # ADR check passed recently — allow
    echo '{"permissionDecision": "allow"}' # nosemgrep: hooks-unconditional-allow-generic
    exit 0
  fi
fi

# ADR check not run or stale. Run it now on staged artifacts.
if [ -z "$ADR_CHECK_SCRIPT" ]; then
  # Can't find the script — warn but allow
  echo '{"permissionDecision": "allow", "reason": "adr-check.sh not found — skipping ADR gate"}' # nosemgrep: hooks-unconditional-allow-generic
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
  # ADR compliance failures found — deny the commit
  REASON="ADR compliance check failed on staged artifacts. Fix these before committing:$(echo -e "$FAILURES" | head -10)"
  jq -n --arg reason "$REASON" '{"permissionDecision": "deny", "reason": $reason}'
  exit 0
fi

# All checks passed — stamp and allow
mkdir -p "$STATE_DIR"
date > "$ADR_CHECK_STAMP"
echo '{"permissionDecision": "allow"}' # nosemgrep: hooks-unconditional-allow-generic
exit 0
