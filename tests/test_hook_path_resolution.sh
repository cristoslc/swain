#!/usr/bin/env bash
# RED test: Verify .claude/settings.json hook commands use portable path resolution
# SPEC-050: Stage Status Hook Fails in Worktrees
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SETTINGS="$REPO_ROOT/.claude/settings.json"
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

echo "=== SPEC-050: Hook Path Resolution Tests ==="

# AC1: No hardcoded absolute paths in hook commands
HARDCODED=$(python3 -c "
import json, sys
with open('$SETTINGS') as f:
    data = json.load(f)
cmds = []
for event, entries in data.get('hooks', {}).items():
    for entry in entries:
        for h in entry.get('hooks', []):
            cmds.append(h.get('command', ''))
# Check for hardcoded /Users/ paths
print('true' if any('/Users/' in c for c in cmds) else 'false')
" 2>/dev/null)
assert "No hardcoded absolute paths in hook commands" "$([ "$HARDCODED" = "false" ] && echo true || echo false)"

# AC2: Hook commands reference CLAUDE_PROJECT_DIR or git rev-parse for portability
PORTABLE=$(python3 -c "
import json
with open('$SETTINGS') as f:
    data = json.load(f)
cmds = []
for event, entries in data.get('hooks', {}).items():
    for entry in entries:
        for h in entry.get('hooks', []):
            cmds.append(h.get('command', ''))
stage_cmds = [c for c in cmds if 'stage-status-hook' in c]
portable = all('CLAUDE_PROJECT_DIR' in c or 'rev-parse' in c for c in stage_cmds)
print('true' if portable and stage_cmds else 'false')
" 2>/dev/null)
assert "Hook commands use portable path resolution" "$PORTABLE"

# AC3: Hook command executes successfully from a non-repo cwd
# Simulate by running from /tmp with CLAUDE_PROJECT_DIR set
EXEC_OK=$(
  export CLAUDE_PROJECT_DIR="$REPO_ROOT"
  HOOK_CMD=$(python3 -c "
import json
with open('$SETTINGS') as f:
    data = json.load(f)
for entry in data['hooks'].get('Stop', []):
    for h in entry.get('hooks', []):
        if 'stage-status-hook' in h.get('command', ''):
            print(h['command'])
            break
" 2>/dev/null)
  if [ -z "$HOOK_CMD" ]; then
    echo "false"
  else
    # Check if the resolved script path exists (don't actually run it — needs stdin/tmux)
    RESOLVED=$(echo "$HOOK_CMD" | sed 's|bash ||' | sed 's|"||g')
    RESOLVED=$(eval echo "$RESOLVED" 2>/dev/null)
    [ -f "$RESOLVED" ] && echo "true" || echo "false"
  fi
)
assert "Hook script path resolves from arbitrary cwd" "$EXEC_OK"

# AC4: No "No such file or directory" when path is evaluated
RESOLVES=$(
  export CLAUDE_PROJECT_DIR="$REPO_ROOT"
  SCRIPT_PATH="$CLAUDE_PROJECT_DIR/skills/swain-stage/scripts/stage-status-hook.sh"
  [ -f "$SCRIPT_PATH" ] && echo "true" || echo "false"
)
assert "Script exists at CLAUDE_PROJECT_DIR-resolved path" "$RESOLVES"

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
