#!/usr/bin/env bash
# RED tests for SPEC-180: Pre-Runtime Swain Script
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SCRIPT="$REPO_ROOT/skills/swain/scripts/swain"
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

echo "=== SPEC-180: Pre-Runtime Swain Script Tests ==="

# T1: Script exists and is executable
assert "swain script exists" "$([ -f "$SCRIPT" ] && echo true || echo false)"
assert "swain script is executable" "$([ -x "$SCRIPT" ] && echo true || echo false)"

# T2: bin/swain symlink resolves
assert "bin/swain symlink resolves" "$([ -L "$REPO_ROOT/bin/swain" ] && [ -e "$REPO_ROOT/bin/swain" ] && echo true || echo false)"

# --- Argument parsing ---
# T3: --help exits cleanly
HELP_OUT=$("$SCRIPT" --help 2>&1 || true)
assert "--help shows usage" "$(echo "$HELP_OUT" | grep -q 'Usage: swain' && echo true || echo false)"

# T4: --fresh flag is accepted
FRESH_OUT=$("$SCRIPT" --fresh --runtime nonexistent 2>&1 || true)
assert "--fresh flag accepted" "$(echo "$FRESH_OUT" | grep -qv 'unknown option' && echo true || echo false)"

# --- Runtime resolution (AC4) ---
# T5: --runtime flag overrides all other resolution
RUNTIME_OUT=$("$SCRIPT" --runtime gemini --_dry_run 2>&1 || true)
assert "--runtime flag sets runtime" "$(echo "$RUNTIME_OUT" | grep -q 'runtime: gemini' && echo true || echo false)"

# T6: --_dry_run shows resolved runtime without launching
DRY_OUT=$("$SCRIPT" --_dry_run 2>&1 || true)
assert "--_dry_run shows runtime info" "$(echo "$DRY_OUT" | grep -qE 'runtime:' && echo true || echo false)"

# T7: Per-project swain.settings.json runtime is used when no --runtime flag
TMPDIR_RT2=$(mktemp -d)
mkdir -p "$TMPDIR_RT2/.git"
cat > "$TMPDIR_RT2/swain.settings.json" <<'SETTJSON'
{"runtime": "codex"}
SETTJSON
RT_PROJ=$(REPO_ROOT="$TMPDIR_RT2" bash "$SCRIPT" --_dry_run 2>&1 || true)
assert "per-project setting used" "$(echo "$RT_PROJ" | grep -q 'runtime: codex' && echo true || echo false)"

rm -rf "$TMPDIR_RT2"

# T8: --fresh skips crash recovery (AC7)
FRESH_DRY=$("$SCRIPT" --fresh --_dry_run 2>&1 || true)
assert "--fresh skips crash detection" "$(echo "$FRESH_DRY" | grep -qv 'crash debris\|recovery' && echo true || echo false)"
assert "--fresh still shows runtime" "$(echo "$FRESH_DRY" | grep -q 'runtime:' && echo true || echo false)"

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
