#!/usr/bin/env bash
# Tests for SPEC-276: bin/swain tmux wrapping
# AC1: tmux new-session when $TMUX unset
# AC2: tmux rename-window when $TMUX set
# AC3: dry-run reports tmux_action
# AC4: graceful fallback when tmux not installed
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SCRIPT="$REPO_ROOT/bin/swain"
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

echo "=== SPEC-276: bin/swain Tmux Wrapping Tests ==="

# --- AC1 + AC3: Outside tmux, dry-run reports new-session ---
echo ""
echo "--- AC1/AC3: Outside tmux (dry-run) ---"

OUTPUT_NO_TMUX=$(unset TMUX; bash "$SCRIPT" --trunk --_dry_run --_non_interactive "test session" 2>&1)
assert "dry-run reports tmux_action: new-session when TMUX unset" \
  "$(echo "$OUTPUT_NO_TMUX" | grep -q 'tmux_action: new-session' && echo true || echo false)"
assert "dry-run reports tmux_session name" \
  "$(echo "$OUTPUT_NO_TMUX" | grep -q 'tmux_session:' && echo true || echo false)"

# --- AC2 + AC3: Inside tmux, dry-run reports rename-window ---
echo ""
echo "--- AC2/AC3: Inside tmux (dry-run) ---"

OUTPUT_IN_TMUX=$(TMUX="/tmp/tmux-fake/default,12345,0" bash "$SCRIPT" --trunk --_dry_run --_non_interactive "test session" 2>&1)
assert "dry-run reports tmux_action: rename-window when TMUX set" \
  "$(echo "$OUTPUT_IN_TMUX" | grep -q 'tmux_action: rename-window' && echo true || echo false)"

# --- AC3: Session name derivation ---
echo ""
echo "--- AC3: Session name sanitization ---"

OUTPUT_NAME=$(unset TMUX; bash "$SCRIPT" --trunk --_dry_run --_non_interactive "Fix Bug #123!" 2>&1)
SESSION_NAME=$(echo "$OUTPUT_NAME" | grep 'tmux_session:' | sed 's/.*tmux_session: //')
# Should be sanitized: no special chars
assert "session name has no special chars" \
  "$(echo "$SESSION_NAME" | grep -qE '^[a-z0-9_-]+$' && echo true || echo false)"

# --- AC4: Fallback when tmux not found ---
echo ""
echo "--- AC4: tmux not installed fallback ---"

# Create a wrapper that hides tmux from PATH
TMPBIN=$(mktemp -d)
# Create a fake PATH without tmux
CLEAN_PATH=""
while IFS=: read -ra DIRS; do
  for d in "${DIRS[@]}"; do
    if [ -d "$d" ] && ! [ -x "$d/tmux" ]; then
      CLEAN_PATH="${CLEAN_PATH:+$CLEAN_PATH:}$d"
    elif [ -d "$d" ] && [ -x "$d/tmux" ]; then
      # Copy everything except tmux
      :
    fi
  done
done <<< "$PATH"

# Use env -i to get a clean environment, then restore just what we need
OUTPUT_NO_TMUX_BIN=$(unset TMUX; PATH="$TMPBIN:$CLEAN_PATH" bash "$SCRIPT" --trunk --_dry_run --_non_interactive "test session" 2>&1)
rm -rf "$TMPBIN"

assert "warns when tmux not found" \
  "$(echo "$OUTPUT_NO_TMUX_BIN" | grep -q 'warning:.*tmux' && echo true || echo false)"
assert "dry-run reports tmux_action: none when tmux missing" \
  "$(echo "$OUTPUT_NO_TMUX_BIN" | grep -q 'tmux_action: none' && echo true || echo false)"

# --- Structural checks ---
echo ""
echo "--- Structural: tmux logic exists in script ---"

assert "script references TMUX env var" \
  "$(grep -q 'TMUX' "$SCRIPT" && echo true || echo false)"
assert "script has tmux new-session logic" \
  "$(grep -q 'tmux new-session' "$SCRIPT" && echo true || echo false)"
assert "script has tmux rename-window logic" \
  "$(grep -q 'tmux rename-window' "$SCRIPT" && echo true || echo false)"

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
