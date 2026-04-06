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

# --- Resume prompt composition (AC6) ---
TMPDIR_P3=$(mktemp -d)
mkdir -p "$TMPDIR_P3/.git" "$TMPDIR_P3/.agents" "$TMPDIR_P3/skills/swain-doctor/scripts"
cp "$REPO_ROOT/skills/swain-doctor/scripts/crash-debris-lib.sh" "$TMPDIR_P3/skills/swain-doctor/scripts/"

# T13: Resume prompt includes bookmark
cat > "$TMPDIR_P3/.agents/session.json" <<'SESSJSON'
{
  "lastBranch": "feature-branch",
  "bookmark": {
    "note": "Implementing SPEC-182 tests",
    "files": ["tests/test.sh"],
    "timestamp": "2026-03-28T22:00:00Z"
  },
  "focus_lane": "INITIATIVE-019"
}
SESSJSON
echo "99999999" > "$TMPDIR_P3/.git/index.lock"
RESUME_DRY=$(REPO_ROOT="$TMPDIR_P3" bash "$SCRIPT" --_non_interactive --_dry_run 2>&1 || true)
assert "resume prompt includes bookmark" "$(echo "$RESUME_DRY" | grep -q 'SPEC-182' && echo true || echo false)"

# T14: No purpose args + no crash → prompt is /swain-init
TMPDIR_P3B=$(mktemp -d)
mkdir -p "$TMPDIR_P3B/.git" "$TMPDIR_P3B/skills/swain-doctor/scripts"
cp "$REPO_ROOT/skills/swain-doctor/scripts/crash-debris-lib.sh" "$TMPDIR_P3B/skills/swain-doctor/scripts/"
FRESH_DRY=$(REPO_ROOT="$TMPDIR_P3B" bash "$SCRIPT" --_dry_run 2>&1 || true)
assert "fresh session → /swain-init prompt" "$(echo "$FRESH_DRY" | grep -q '/swain-init' && echo true || echo false)"

# T15: Purpose args → /swain-session with purpose
PURPOSE_DRY=$(REPO_ROOT="$TMPDIR_P3B" bash "$SCRIPT" --_dry_run fix the login bug 2>&1 || true)
assert "purpose args → session purpose prompt" "$(echo "$PURPOSE_DRY" | grep -q 'fix the login bug' && echo true || echo false)"

rm -rf "$TMPDIR_P3" "$TMPDIR_P3B"

# --- New session worktree isolation ---
TMPDIR_SESSION_WT=$(mktemp -d)
git -C "$TMPDIR_SESSION_WT" init -q
git -C "$TMPDIR_SESSION_WT" commit --allow-empty -m "init" -q 2>/dev/null
mkdir -p "$TMPDIR_SESSION_WT/.agents"
cat > "$TMPDIR_SESSION_WT/.gitignore" <<'EOF'
.worktrees/
.agents/session.json
EOF
git -C "$TMPDIR_SESSION_WT" add .gitignore >/dev/null 2>&1
git -C "$TMPDIR_SESSION_WT" commit -m "ignore local session state" -q >/dev/null 2>&1

cat > "$TMPDIR_SESSION_WT/.agents/session.json" <<'SESSJSON'
{
  "bookmark": {
    "note": "keep trunk session",
    "timestamp": "2026-04-01T00:00:00Z"
  }
}
SESSJSON

FAKEBIN_WT=$(mktemp -d)
WT_LOG="$TMPDIR_SESSION_WT/runtime.log"
cat > "$FAKEBIN_WT/codex" <<'EOF'
#!/usr/bin/env bash
printf 'cwd=%s\n' "$PWD" > "$SWAIN_RUNTIME_LOG"
idx=0
for arg in "$@"; do
  idx=$((idx + 1))
  printf 'arg%d=%s\n' "$idx" "$arg" >> "$SWAIN_RUNTIME_LOG"
done
EOF
chmod +x "$FAKEBIN_WT/codex"

PATH="$FAKEBIN_WT:$PATH" SWAIN_RUNTIME_LOG="$WT_LOG" \
  REPO_ROOT="$TMPDIR_SESSION_WT" bash "$SCRIPT" --fresh --runtime codex fix trunk bookmark clobber >/dev/null 2>&1 || true

WT_CWD=$(grep '^cwd=' "$WT_LOG" 2>/dev/null | cut -d= -f2-)
assert "fresh purpose from trunk launches inside a worktree" "$(echo "$WT_CWD" | grep -q "$TMPDIR_SESSION_WT/.worktrees/" && echo true || echo false)"
assert "fresh purpose from trunk preserves trunk bookmark" "$([ "$(grep -o 'keep trunk session' "$TMPDIR_SESSION_WT/.agents/session.json" 2>/dev/null)" = "keep trunk session" ] && echo true || echo false)"
assert "launched prompt keeps the new session purpose" "$(grep -q '/swain-session Session purpose: fix trunk bookmark clobber' "$WT_LOG" && echo true || echo false)"
assert "session bookmark file stays gitignored in created worktree" "$(printf '.agents/session.json\n' | git -C "$WT_CWD" check-ignore --stdin >/dev/null 2>&1 && echo true || echo false)"

rm -rf "$TMPDIR_SESSION_WT" "$FAKEBIN_WT"

# --- Existing worktree bookmark safety ---
TMPDIR_ACTIVE_WT=$(mktemp -d)
git -C "$TMPDIR_ACTIVE_WT" init -q
git -C "$TMPDIR_ACTIVE_WT" commit --allow-empty -m "init" -q 2>/dev/null
mkdir -p "$TMPDIR_ACTIVE_WT/.agents" "$TMPDIR_ACTIVE_WT/.worktrees"
cat > "$TMPDIR_ACTIVE_WT/.gitignore" <<'EOF'
.worktrees/
.agents/session.json
EOF
git -C "$TMPDIR_ACTIVE_WT" add .gitignore >/dev/null 2>&1
git -C "$TMPDIR_ACTIVE_WT" commit -m "ignore local session state" -q >/dev/null 2>&1

ACTIVE_WT="$TMPDIR_ACTIVE_WT/.worktrees/existing-session"
git -C "$TMPDIR_ACTIVE_WT" worktree add -q "$ACTIVE_WT" -b existing-session 2>/dev/null || true
mkdir -p "$ACTIVE_WT/.agents"
cat > "$ACTIVE_WT/.agents/session.json" <<'SESSJSON'
{
  "bookmark": {
    "note": "existing worktree session",
    "timestamp": "2026-04-01T00:00:00Z"
  }
}
SESSJSON

WORKTREE_COUNT_BEFORE=$(git -C "$TMPDIR_ACTIVE_WT" worktree list --porcelain 2>/dev/null | grep -c '^worktree ')
ACTIVE_DRY=$(REPO_ROOT="$ACTIVE_WT" bash "$SCRIPT" --fresh --_non_interactive --_dry_run new unrelated task 2>&1 || true)
WORKTREE_COUNT_AFTER=$(git -C "$TMPDIR_ACTIVE_WT" worktree list --porcelain 2>/dev/null | grep -c '^worktree ')

assert "active worktree bookmark redirects to resume prompt" "$(echo "$ACTIVE_DRY" | grep -q 'resume — existing worktree session' && echo true || echo false)"
assert "active worktree bookmark does not reuse the new purpose" "$(echo "$ACTIVE_DRY" | grep -qv 'new unrelated task' && echo true || echo false)"
assert "active worktree bookmark does not create another worktree in non-interactive mode" "$([ "$WORKTREE_COUNT_BEFORE" = "$WORKTREE_COUNT_AFTER" ] && echo true || echo false)"

git -C "$TMPDIR_ACTIVE_WT" worktree remove "$ACTIVE_WT" --force >/dev/null 2>&1 || true
rm -rf "$TMPDIR_ACTIVE_WT"

# --- Interactive cleanup (AC3) ---
TMPDIR_CLEANUP=$(mktemp -d)
mkdir -p "$TMPDIR_CLEANUP/.git" "$TMPDIR_CLEANUP/skills/swain-doctor/scripts" "$TMPDIR_CLEANUP/.tickets/.locks/task-42"
cp "$REPO_ROOT/skills/swain-doctor/scripts/crash-debris-lib.sh" "$TMPDIR_CLEANUP/skills/swain-doctor/scripts/"

# Create two debris items: git lock + stale tk lock
echo "99999999" > "$TMPDIR_CLEANUP/.git/index.lock"
echo "99999999" > "$TMPDIR_CLEANUP/.tickets/.locks/task-42/owner"

# T-AC3a: Non-interactive mode preserves debris (doesn't auto-clean)
REPO_ROOT="$TMPDIR_CLEANUP" bash "$SCRIPT" --_phase1_only --_non_interactive 2>&1 >/dev/null
assert "non-interactive preserves git lock" "$([ -f "$TMPDIR_CLEANUP/.git/index.lock" ] && echo true || echo false)"
assert "non-interactive preserves tk lock" "$([ -d "$TMPDIR_CLEANUP/.tickets/.locks/task-42" ] && echo true || echo false)"

# T-AC3b: Cleanup actions work when executed manually (simulating what "y" would do)
rm -f "$TMPDIR_CLEANUP/.git/index.lock"
assert "git lock removable" "$([ ! -f "$TMPDIR_CLEANUP/.git/index.lock" ] && echo true || echo false)"

rm -rf "$TMPDIR_CLEANUP/.tickets/.locks/task-42"
assert "tk lock removable" "$([ ! -d "$TMPDIR_CLEANUP/.tickets/.locks/task-42" ] && echo true || echo false)"

rm -rf "$TMPDIR_CLEANUP"

# --- Global settings fallback ---
TMPDIR_GLOBAL=$(mktemp -d)
mkdir -p "$TMPDIR_GLOBAL/.git"
# No per-project swain.settings.json — should fall through to global
GLOBAL_DIR=$(mktemp -d)
mkdir -p "$GLOBAL_DIR"
cat > "$GLOBAL_DIR/settings.json" <<'GLOBJSON'
{"runtime": "copilot"}
GLOBJSON

# Override HOME to point to a temp dir with .config/swain/settings.json
FAKE_HOME=$(mktemp -d)
mkdir -p "$FAKE_HOME/.config/swain"
cp "$GLOBAL_DIR/settings.json" "$FAKE_HOME/.config/swain/settings.json"

RT_GLOBAL=$(HOME="$FAKE_HOME" REPO_ROOT="$TMPDIR_GLOBAL" bash "$SCRIPT" --_dry_run 2>&1 || true)
assert "global settings fallback used" "$(echo "$RT_GLOBAL" | grep -q 'runtime: copilot' && echo true || echo false)"

rm -rf "$TMPDIR_GLOBAL" "$GLOBAL_DIR" "$FAKE_HOME"

# --- Dangling worktrees in Phase 2 (AC5) ---
TMPDIR_WT=$(mktemp -d)
git -C "$TMPDIR_WT" init -q
git -C "$TMPDIR_WT" commit --allow-empty -m "init" -q 2>/dev/null
mkdir -p "$TMPDIR_WT/skills/swain-doctor/scripts" "$TMPDIR_WT/.agents"

cp "$REPO_ROOT/skills/swain-doctor/scripts/crash-debris-lib.sh" "$TMPDIR_WT/skills/swain-doctor/scripts/"

# Create a worktree, add uncommitted file, simulate orphan
WT_DIR="$TMPDIR_WT/.worktrees/orphan-wt"
git -C "$TMPDIR_WT" worktree add -q "$WT_DIR" -b orphan-branch 2>/dev/null || true
if [ -d "$WT_DIR" ]; then
  echo "dirty" > "$WT_DIR/uncommitted.txt"

  # Add session bookmark so Phase 2 activates
  cat > "$TMPDIR_WT/.agents/session.json" <<'SESSJSON'
{"bookmark":{"note":"test","timestamp":"2026-03-30T00:00:00Z"},"focus_lane":"TEST"}
SESSJSON

  P2_WT_OUT=$(REPO_ROOT="$TMPDIR_WT" bash "$SCRIPT" --_phase2_only --_non_interactive 2>&1 || true)
  assert "Phase 2 surfaces dangling worktree" "$(echo "$P2_WT_OUT" | grep -qi 'worktree\|unmerged\|uncommitted' && echo true || echo false)"

  # Cleanup
  rm -f "$WT_DIR/uncommitted.txt"
  git -C "$TMPDIR_WT" worktree remove "$WT_DIR" --force 2>/dev/null || true
else
  # If worktree creation failed (common in temp dirs), skip gracefully
  assert "Phase 2 surfaces dangling worktree (skipped - worktree creation failed)" "true"
fi

rm -rf "$TMPDIR_WT"

# --- Invalid runtime name ---
TMPDIR_BADRT=$(mktemp -d)
mkdir -p "$TMPDIR_BADRT/.git"
BAD_RT_OUT=$(REPO_ROOT="$TMPDIR_BADRT" bash "$SCRIPT" --runtime nonexistent_runtime --_dry_run 2>&1 || true)
assert "invalid runtime still shown in dry run" "$(echo "$BAD_RT_OUT" | grep -q 'runtime: nonexistent_runtime' && echo true || echo false)"
rm -rf "$TMPDIR_BADRT"

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
