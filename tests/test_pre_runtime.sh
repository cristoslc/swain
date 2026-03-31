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

# --- Phase 1: Crash detection (AC1, AC3) ---
TMPDIR_P1=$(mktemp -d)
mkdir -p "$TMPDIR_P1/.git" "$TMPDIR_P1/skills/swain-doctor/scripts"
cp "$REPO_ROOT/skills/swain-doctor/scripts/crash-debris-lib.sh" "$TMPDIR_P1/skills/swain-doctor/scripts/"

# T9: Phase 1 sources crash-debris-lib.sh and detects debris
echo "99999999" > "$TMPDIR_P1/.git/index.lock"
P1_OUT=$(REPO_ROOT="$TMPDIR_P1" bash "$SCRIPT" --_phase1_only --_non_interactive 2>&1 || true)
assert "phase 1 detects crash debris" "$(echo "$P1_OUT" | grep -qi 'debris\|lock\|found' && echo true || echo false)"

# T10: Clean project → phase 1 is silent (AC2 fast path)
TMPDIR_P1B=$(mktemp -d)
mkdir -p "$TMPDIR_P1B/.git" "$TMPDIR_P1B/skills/swain-doctor/scripts"
cp "$REPO_ROOT/skills/swain-doctor/scripts/crash-debris-lib.sh" "$TMPDIR_P1B/skills/swain-doctor/scripts/"
P1_CLEAN=$(REPO_ROOT="$TMPDIR_P1B" bash "$SCRIPT" --_phase1_only --_non_interactive 2>&1 || true)
assert "clean project → phase 1 silent" "$([ -z "$P1_CLEAN" ] && echo true || echo false)"

rm -rf "$TMPDIR_P1" "$TMPDIR_P1B"

# --- Phase 2: Session selection (AC1, AC5, AC6) ---
TMPDIR_P2=$(mktemp -d)
mkdir -p "$TMPDIR_P2/.git" "$TMPDIR_P2/.agents" "$TMPDIR_P2/skills/swain-doctor/scripts"
cp "$REPO_ROOT/skills/swain-doctor/scripts/crash-debris-lib.sh" "$TMPDIR_P2/skills/swain-doctor/scripts/"

# T11: No crashed sessions → phase 2 skipped (AC2 fast path)
P2_CLEAN=$(REPO_ROOT="$TMPDIR_P2" bash "$SCRIPT" --_phase2_only --_non_interactive 2>&1 || true)
assert "no crashed sessions → phase 2 silent" "$([ -z "$P2_CLEAN" ] && echo true || echo false)"

# T12: With session bookmark + crash debris → resume context shown
cat > "$TMPDIR_P2/.agents/session.json" <<'SESSJSON'
{
  "lastBranch": "trunk",
  "bookmark": {
    "note": "Working on crash detection",
    "files": ["scripts/test.sh"],
    "timestamp": "2026-03-28T22:00:00Z"
  },
  "focus_lane": "INITIATIVE-019"
}
SESSJSON
echo "99999999" > "$TMPDIR_P2/.git/index.lock"
P2_RESUME=$(REPO_ROOT="$TMPDIR_P2" bash "$SCRIPT" --_phase2_only --_non_interactive 2>&1 || true)
assert "crashed session → shows resume context" "$(echo "$P2_RESUME" | grep -q 'Working on crash detection' && echo true || echo false)"

rm -rf "$TMPDIR_P2"

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
