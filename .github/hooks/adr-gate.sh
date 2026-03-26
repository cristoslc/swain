#!/usr/bin/env bash
# .github/hooks/adr-gate.sh — PreToolUse hook for GitHub Copilot CLI
# Blocks git commit when staged artifact files lack ADR review.
#
# Copilot CLI input format (JSON on stdin):
#   {"timestamp": ..., "cwd": ..., "toolName": "bash", "toolArgs": "{\"command\": \"...\"}"}
#
# Output format (JSON on stdout):
#   {"permissionDecision": "allow"|"deny", "permissionDecisionReason": "..."} # nosemgrep: hooks-unconditional-allow-generic
#
# Claude Code equivalent fields for reference:
#   toolName  ↔ tool_name
#   toolArgs  ↔ tool_input  (string vs object)

set -euo pipefail

INPUT=$(cat)

# Extract tool name — try Copilot's toolName first, then Claude's tool_name
TOOL_NAME=$(echo "$INPUT" | jq -r '.toolName // .tool_name // ""')

# If not a shell/bash tool, allow
if [[ "$TOOL_NAME" != "bash" && "$TOOL_NAME" != "shell" && "$TOOL_NAME" != "Bash" ]]; then
  echo '{"permissionDecision":"allow","permissionDecisionReason":"not a shell tool"}' # nosemgrep: hooks-unconditional-allow-generic
  exit 0
fi

# Extract command — Copilot wraps toolArgs as a JSON string, Claude uses tool_input object
COMMAND=""
TOOL_ARGS=$(echo "$INPUT" | jq -r '.toolArgs // ""')
if [[ -n "$TOOL_ARGS" && "$TOOL_ARGS" != "null" ]]; then
  # Copilot: toolArgs is a JSON string containing {"command": "..."}
  COMMAND=$(echo "$TOOL_ARGS" | jq -r '.command // ""' 2>/dev/null || echo "")
fi

# Fallback: Claude Code format (tool_input is an object with .command)
if [[ -z "$COMMAND" ]]; then
  COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""' 2>/dev/null || echo "")
fi

# If not a git commit, allow
if ! echo "$COMMAND" | grep -qE '\bgit\s+commit\b'; then
  echo '{"permissionDecision":"allow","permissionDecisionReason":"not a git commit"}' # nosemgrep: hooks-unconditional-allow-generic
  exit 0
fi

# Extract cwd
CWD=$(echo "$INPUT" | jq -r '.cwd // "."')

# Check for staged artifact files (docs/spec, docs/design, docs/adr patterns)
STAGED_ARTIFACTS=$(cd "$CWD" 2>/dev/null && git diff --cached --name-only 2>/dev/null | grep -cE '^docs/(spec|design|adr)/' || true)

if [[ "$STAGED_ARTIFACTS" -eq 0 ]]; then
  echo '{"permissionDecision":"allow","permissionDecisionReason":"no staged artifact files"}' # nosemgrep: hooks-unconditional-allow-generic
  exit 0
fi

# Check if ADR_REVIEWED marker exists in environment or commit message
# The convention: set ADR_REVIEWED=1 or include [adr-ok] in the commit message
if [[ "${ADR_REVIEWED:-}" == "1" ]]; then
  echo '{"permissionDecision":"allow","permissionDecisionReason":"ADR_REVIEWED=1 set"}' # nosemgrep: hooks-unconditional-allow-generic
  exit 0
fi

if echo "$COMMAND" | grep -qE '\[adr-ok\]'; then
  echo '{"permissionDecision":"allow","permissionDecisionReason":"[adr-ok] in commit message"}' # nosemgrep: hooks-unconditional-allow-generic
  exit 0
fi

# Deny: staged artifacts without ADR review
echo "{\"permissionDecision\":\"deny\",\"permissionDecisionReason\":\"$STAGED_ARTIFACTS staged artifact file(s) in docs/spec|design|adr — add [adr-ok] to commit message or set ADR_REVIEWED=1\"}"
exit 0
