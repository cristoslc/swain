#!/usr/bin/env bash
# test-bootstrap.sh — Acceptance tests for swain-session-bootstrap.sh (SPEC-172)
#
# Tests the consolidated bootstrap script that replaces multi-step session startup.
# Runs in an isolated tmux server and temp git repos. Requires: tmux, git, jq.
#
# Usage: bash skills/swain-session/tests/test-bootstrap.sh

set +e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOOTSTRAP="$(cd "$SCRIPT_DIR/.." && pwd)/scripts/swain-session-bootstrap.sh"
GIT_COMMON="$(git rev-parse --git-common-dir 2>/dev/null)"
REPO_ROOT="$(cd "$GIT_COMMON/.." && pwd 2>/dev/null)"

# Isolated tmux server
TMUX_SOCK="/tmp/swain-test-bootstrap-$$"
T="tmux -S $TMUX_SOCK"

# Temp dir for test repos
TMPDIR_BASE="/tmp/swain-test-bootstrap-repos-$$"

PASS=0
FAIL=0
SKIP=0

pass() { echo "  PASS: $1"; ((PASS++)); }
fail() { echo "  FAIL: $1 — $2"; ((FAIL++)); }
skip() { echo "  SKIP: $1 — $2"; ((SKIP++)); }

cleanup() {
  $T kill-server 2>/dev/null
  rm -f "$TMUX_SOCK"
  rm -rf "$TMPDIR_BASE"
}
trap cleanup EXIT

start_session() {
  local name="${1:-test}"
  local dir="${2:-$REPO_ROOT}"
  $T new-session -d -s "$name" -c "$dir" 2>/dev/null
}

# Run the bootstrap script with given args, capturing JSON output
run_bootstrap() {
  local extra_env="${1:-}"
  shift
  SWAIN_TMUX_SOCKET="$TMUX_SOCK" TMUX="$TMUX_SOCK,0,0" $extra_env \
    bash "$BOOTSTRAP" "$@" 2>/dev/null
}

# ─── Preflight ───

if [[ ! -x "$BOOTSTRAP" && ! -f "$BOOTSTRAP" ]]; then
  echo "FATAL: bootstrap script not found at $BOOTSTRAP"
  exit 1
fi

if ! command -v jq &>/dev/null; then
  echo "FATAL: jq is required for tests"
  exit 1
fi

mkdir -p "$TMPDIR_BASE"

# ═══════════════════════════════════════════════════════════
echo "═══ AC1: tmux session — single call does tab + worktree + session"
# ═══════════════════════════════════════════════════════════

start_session "ac1" "$REPO_ROOT"

OUTPUT=$(SWAIN_TMUX_SOCKET="$TMUX_SOCK" TMUX="$TMUX_SOCK,0,0" \
  bash "$BOOTSTRAP" --path "$REPO_ROOT" --auto 2>/dev/null)

if echo "$OUTPUT" | jq empty 2>/dev/null; then
  pass "AC1: output is valid JSON"
else
  fail "AC1: output is valid JSON" "got: $OUTPUT"
fi

# Check tab field exists
TAB=$(echo "$OUTPUT" | jq -r '.tab // empty' 2>/dev/null)
if [[ -n "$TAB" ]]; then
  pass "AC1: tab field present"
else
  fail "AC1: tab field present" "missing from output"
fi

# Check worktree field exists (use has() since isolated can be false)
WT_HAS=$(echo "$OUTPUT" | jq 'has("worktree") and (.worktree | has("isolated"))' 2>/dev/null)
if [[ "$WT_HAS" == "true" ]]; then
  pass "AC1: worktree.isolated field present"
else
  fail "AC1: worktree.isolated field present" "missing from output"
fi

# Check session field exists
SESSION=$(echo "$OUTPUT" | jq -r '.session // empty' 2>/dev/null)
if [[ -n "$SESSION" && "$SESSION" != "null" ]]; then
  pass "AC1: session field present"
else
  fail "AC1: session field present" "missing from output"
fi

$T kill-session -t ac1 2>/dev/null

# ═══════════════════════════════════════════════════════════
echo "═══ AC2: non-tmux terminal — tab field omitted"
# ═══════════════════════════════════════════════════════════

# Run WITHOUT TMUX env var
OUTPUT_NO_TMUX=$(TMUX="" SWAIN_TMUX_SOCKET="" \
  bash "$BOOTSTRAP" --path "$REPO_ROOT" --auto 2>/dev/null)

if echo "$OUTPUT_NO_TMUX" | jq empty 2>/dev/null; then
  pass "AC2: output is valid JSON without tmux"
else
  fail "AC2: output is valid JSON without tmux" "got: $OUTPUT_NO_TMUX"
fi

TAB_NO_TMUX=$(echo "$OUTPUT_NO_TMUX" | jq -r '.tab // "MISSING"' 2>/dev/null)
if [[ "$TAB_NO_TMUX" == "null" || "$TAB_NO_TMUX" == "MISSING" ]]; then
  pass "AC2: tab field omitted without tmux"
else
  fail "AC2: tab field omitted without tmux" "got: $TAB_NO_TMUX"
fi

# ═══════════════════════════════════════════════════════════
echo "═══ AC3: already in a worktree — worktree.isolated is true"
# ═══════════════════════════════════════════════════════════

# We're running from a worktree already (spec-172-session-bootstrap)
WT_DIR="$(pwd)"
GIT_COMMON_TEST=$(git -C "$WT_DIR" rev-parse --git-common-dir 2>/dev/null)
GIT_DIR_TEST=$(git -C "$WT_DIR" rev-parse --git-dir 2>/dev/null)

if [[ "$GIT_COMMON_TEST" != "$GIT_DIR_TEST" ]]; then
  # We are in a worktree
  start_session "ac3" "$WT_DIR"
  OUTPUT_WT=$(SWAIN_TMUX_SOCKET="$TMUX_SOCK" TMUX="$TMUX_SOCK,0,0" \
    bash "$BOOTSTRAP" --path "$WT_DIR" --auto 2>/dev/null)

  WT_IS=$(echo "$OUTPUT_WT" | jq -r '.worktree.isolated' 2>/dev/null)
  if [[ "$WT_IS" == "true" ]]; then
    pass "AC3: worktree.isolated is true in worktree"
  else
    fail "AC3: worktree.isolated is true in worktree" "got: $WT_IS"
  fi

  WT_BRANCH=$(echo "$OUTPUT_WT" | jq -r '.worktree.branch // empty' 2>/dev/null)
  if [[ -n "$WT_BRANCH" ]]; then
    pass "AC3: worktree.branch is populated"
  else
    fail "AC3: worktree.branch is populated" "empty"
  fi

  $T kill-session -t ac3 2>/dev/null
else
  # Running from main worktree — use REPO_ROOT and check isolated=false
  start_session "ac3" "$REPO_ROOT"
  OUTPUT_MAIN=$(SWAIN_TMUX_SOCKET="$TMUX_SOCK" TMUX="$TMUX_SOCK,0,0" \
    bash "$BOOTSTRAP" --path "$REPO_ROOT" --auto 2>/dev/null)

  WT_IS=$(echo "$OUTPUT_MAIN" | jq -r '.worktree.isolated' 2>/dev/null)
  if [[ "$WT_IS" == "false" ]]; then
    pass "AC3: worktree.isolated is false in main worktree"
  else
    fail "AC3: worktree.isolated is false in main worktree" "got: $WT_IS"
  fi

  $T kill-session -t ac3 2>/dev/null
fi

# ═══════════════════════════════════════════════════════════
echo "═══ AC4: no session.json — session fields are null/empty"
# ═══════════════════════════════════════════════════════════

# Create a temp git repo with no session.json
TEMP_REPO="$TMPDIR_BASE/no-session"
mkdir -p "$TEMP_REPO"
git -C "$TEMP_REPO" init -q 2>/dev/null
git -C "$TEMP_REPO" commit --allow-empty -m "init" -q 2>/dev/null

start_session "ac4" "$TEMP_REPO"
OUTPUT_NO_SESSION=$(SWAIN_TMUX_SOCKET="$TMUX_SOCK" TMUX="$TMUX_SOCK,0,0" \
  bash "$BOOTSTRAP" --path "$TEMP_REPO" --auto 2>/dev/null)

if echo "$OUTPUT_NO_SESSION" | jq empty 2>/dev/null; then
  pass "AC4: valid JSON with no session.json"
else
  fail "AC4: valid JSON with no session.json" "got: $OUTPUT_NO_SESSION"
fi

BOOKMARK=$(echo "$OUTPUT_NO_SESSION" | jq -r '.session.bookmark // "null"' 2>/dev/null)
if [[ "$BOOKMARK" == "null" || "$BOOKMARK" == "" ]]; then
  pass "AC4: bookmark is null when no session.json"
else
  fail "AC4: bookmark is null when no session.json" "got: $BOOKMARK"
fi

$T kill-session -t ac4 2>/dev/null

# ═══════════════════════════════════════════════════════════
echo "═══ AC4b: session.json with bookmark — values populated"
# ═══════════════════════════════════════════════════════════

TEMP_REPO_B="$TMPDIR_BASE/with-session"
mkdir -p "$TEMP_REPO_B/.agents"
git -C "$TEMP_REPO_B" init -q 2>/dev/null
git -C "$TEMP_REPO_B" commit --allow-empty -m "init" -q 2>/dev/null
cat > "$TEMP_REPO_B/.agents/session.json" <<'SESS'
{
  "lastBranch": "trunk",
  "focus_lane": "VISION-001",
  "bookmark": {
    "note": "Working on bootstrap consolidation",
    "timestamp": "2026-03-26T01:00:00Z"
  }
}
SESS

start_session "ac4b" "$TEMP_REPO_B"
OUTPUT_WITH_SESSION=$(SWAIN_TMUX_SOCKET="$TMUX_SOCK" TMUX="$TMUX_SOCK,0,0" \
  bash "$BOOTSTRAP" --path "$TEMP_REPO_B" --auto 2>/dev/null)

FOCUS=$(echo "$OUTPUT_WITH_SESSION" | jq -r '.session.focus // empty' 2>/dev/null)
if [[ "$FOCUS" == "VISION-001" ]]; then
  pass "AC4b: focus lane read from session.json"
else
  fail "AC4b: focus lane read from session.json" "got: $FOCUS"
fi

BM_NOTE=$(echo "$OUTPUT_WITH_SESSION" | jq -r '.session.bookmark // empty' 2>/dev/null)
if [[ -n "$BM_NOTE" && "$BM_NOTE" != "null" ]]; then
  pass "AC4b: bookmark note read from session.json"
else
  fail "AC4b: bookmark note read from session.json" "got: $BM_NOTE"
fi

$T kill-session -t ac4b 2>/dev/null

# ═══════════════════════════════════════════════════════════
echo "═══ JSON schema validation"
# ═══════════════════════════════════════════════════════════

# Re-run on the real repo and validate all expected top-level keys
start_session "schema" "$REPO_ROOT"
OUTPUT_SCHEMA=$(SWAIN_TMUX_SOCKET="$TMUX_SOCK" TMUX="$TMUX_SOCK,0,0" \
  bash "$BOOTSTRAP" --path "$REPO_ROOT" --auto 2>/dev/null)

KEYS=$(echo "$OUTPUT_SCHEMA" | jq -r 'keys[]' 2>/dev/null | sort | tr '\n' ',')
# Expected keys: session, tab, warnings, worktree (alphabetical)
if [[ "$KEYS" == *"session"* && "$KEYS" == *"worktree"* && "$KEYS" == *"warnings"* ]]; then
  pass "Schema: required keys present (session, worktree, warnings)"
else
  fail "Schema: required keys present" "got keys: $KEYS"
fi

WARNINGS_TYPE=$(echo "$OUTPUT_SCHEMA" | jq -r '.warnings | type' 2>/dev/null)
if [[ "$WARNINGS_TYPE" == "array" ]]; then
  pass "Schema: warnings is an array"
else
  fail "Schema: warnings is an array" "got type: $WARNINGS_TYPE"
fi

$T kill-session -t schema 2>/dev/null

# ═══════════════════════════════════════════════════════════
echo "═══ --skip-worktree flag"
# ═══════════════════════════════════════════════════════════

start_session "skipwt" "$REPO_ROOT"
OUTPUT_SKIP_WT=$(SWAIN_TMUX_SOCKET="$TMUX_SOCK" TMUX="$TMUX_SOCK,0,0" \
  bash "$BOOTSTRAP" --path "$REPO_ROOT" --skip-worktree --auto 2>/dev/null)

# When --skip-worktree is set, worktree fields should be at defaults
WT_SKIP_ISOLATED=$(echo "$OUTPUT_SKIP_WT" | jq -r '.worktree.isolated' 2>/dev/null)
WT_SKIP_BRANCH=$(echo "$OUTPUT_SKIP_WT" | jq -r '.worktree.branch' 2>/dev/null)
if [[ "$WT_SKIP_ISOLATED" == "false" && "$WT_SKIP_BRANCH" == "null" ]]; then
  pass "--skip-worktree: worktree detection skipped (isolated=false, branch=null)"
else
  fail "--skip-worktree: worktree detection skipped" "isolated=$WT_SKIP_ISOLATED, branch=$WT_SKIP_BRANCH"
fi

$T kill-session -t skipwt 2>/dev/null

# ═══════════════════════════════════════════════════════════
echo "═══ lastBranch write side effect"
# ═══════════════════════════════════════════════════════════

TEMP_REPO_LB="$TMPDIR_BASE/lastbranch"
mkdir -p "$TEMP_REPO_LB/.agents"
git -C "$TEMP_REPO_LB" init -q 2>/dev/null
git -C "$TEMP_REPO_LB" commit --allow-empty -m "init" -q 2>/dev/null
cat > "$TEMP_REPO_LB/.agents/session.json" <<'SESS'
{
  "lastBranch": "old-branch"
}
SESS

start_session "lb" "$TEMP_REPO_LB"
SWAIN_TMUX_SOCKET="$TMUX_SOCK" TMUX="$TMUX_SOCK,0,0" \
  bash "$BOOTSTRAP" --path "$TEMP_REPO_LB" --auto >/dev/null 2>&1

# Check that session.json was updated with the current branch
CURRENT=$(git -C "$TEMP_REPO_LB" rev-parse --abbrev-ref HEAD 2>/dev/null)
WRITTEN=$(jq -r '.lastBranch' "$TEMP_REPO_LB/.agents/session.json" 2>/dev/null)
if [[ "$WRITTEN" == "$CURRENT" ]]; then
  pass "lastBranch: session.json updated to current branch ($CURRENT)"
else
  fail "lastBranch: session.json updated" "expected=$CURRENT, got=$WRITTEN"
fi

$T kill-session -t lb 2>/dev/null

# ═══════════════════════════════════════════════════════════
echo "═══ jq-unavailable fallback"
# ═══════════════════════════════════════════════════════════

# Hide jq by creating a wrapper that makes `command -v jq` fail.
# We rename jq temporarily via a PATH-prefix dir with a non-executable jq.
FAKE_BIN="$TMPDIR_BASE/fake-bin"
mkdir -p "$FAKE_BIN"
# Create a non-executable jq placeholder — command -v still finds executables
# in PATH, so instead create a wrapper that always fails
cat > "$FAKE_BIN/jq" <<'FAKE'
#!/usr/bin/env bash
exit 127
FAKE
chmod +x "$FAKE_BIN/jq"

start_session "nojq" "$REPO_ROOT"
# Prepend FAKE_BIN so our broken jq shadows the real one
OUTPUT_NOJQ=$(SWAIN_TMUX_SOCKET="$TMUX_SOCK" TMUX="$TMUX_SOCK,0,0" \
  PATH="$FAKE_BIN:$PATH" bash "$BOOTSTRAP" --path "$REPO_ROOT" --auto 2>/dev/null)

# The fallback path fires when `command -v jq` succeeds but jq calls fail.
# Our fake jq makes command -v succeed, so the script takes the jq path but
# jq -n fails, producing broken output. The REAL no-jq fallback requires
# jq to be completely absent. Test what actually matters: the script doesn't crash.
if [[ -n "$OUTPUT_NOJQ" ]]; then
  pass "jq-unavailable: script produces output (does not crash)"
else
  fail "jq-unavailable: script produces output" "empty output"
fi

# Test the actual no-jq codepath by using a clean PATH
CLEAN_PATH=""
while IFS=: read -ra dirs; do
  for dir in "${dirs[@]}"; do
    if ! [[ -x "$dir/jq" ]]; then
      CLEAN_PATH="${CLEAN_PATH:+$CLEAN_PATH:}$dir"
    fi
  done
done <<< "$PATH"

OUTPUT_NOJQ_REAL=$(SWAIN_TMUX_SOCKET="$TMUX_SOCK" TMUX="$TMUX_SOCK,0,0" \
  PATH="$CLEAN_PATH" bash "$BOOTSTRAP" --path "$REPO_ROOT" --auto 2>/dev/null)

# The no-jq fallback constructs JSON manually — verify it's parseable
if echo "$OUTPUT_NOJQ_REAL" | jq empty 2>/dev/null; then
  pass "jq-unavailable (real): fallback JSON is valid"
else
  fail "jq-unavailable (real): fallback JSON is valid" "got: $OUTPUT_NOJQ_REAL"
fi

# Check for the jq warning in the fallback output
if echo "$OUTPUT_NOJQ_REAL" | grep -q "jq not available"; then
  pass "jq-unavailable (real): warning present about missing jq"
else
  fail "jq-unavailable (real): warning present about missing jq" "output: $OUTPUT_NOJQ_REAL"
fi

$T kill-session -t nojq 2>/dev/null

# ═══════════════════════════════════════════════════════════
echo "═══ Warnings population (missing tab-name script)"
# ═══════════════════════════════════════════════════════════

# Create a temp copy of the bootstrap script with a bogus SCRIPT_DIR
TEMP_REPO_WARN="$TMPDIR_BASE/warn-test"
mkdir -p "$TEMP_REPO_WARN/scripts"
git -C "$TEMP_REPO_WARN" init -q 2>/dev/null
git -C "$TEMP_REPO_WARN" commit --allow-empty -m "init" -q 2>/dev/null

# Copy bootstrap but override SCRIPT_DIR to a dir without tab-name
cp "$BOOTSTRAP" "$TEMP_REPO_WARN/scripts/swain-session-bootstrap.sh"
# The script resolves SCRIPT_DIR from its own location — since tab-name.sh
# won't exist in the temp dir, it should warn.

start_session "warn" "$TEMP_REPO_WARN"
OUTPUT_WARN=$(SWAIN_TMUX_SOCKET="$TMUX_SOCK" TMUX="$TMUX_SOCK,0,0" \
  bash "$TEMP_REPO_WARN/scripts/swain-session-bootstrap.sh" --path "$TEMP_REPO_WARN" --auto 2>/dev/null)

WARN_COUNT=$(echo "$OUTPUT_WARN" | jq '.warnings | length' 2>/dev/null)
if [[ "$WARN_COUNT" -gt 0 ]]; then
  pass "warnings: populated when tab-name script missing ($WARN_COUNT warning(s))"
else
  fail "warnings: populated when tab-name script missing" "warnings array empty"
fi

HAS_TAB_WARN=$(echo "$OUTPUT_WARN" | jq -r '.warnings[]' 2>/dev/null | grep -c "tab-name")
if [[ "$HAS_TAB_WARN" -gt 0 ]]; then
  pass "warnings: mentions tab-name script"
else
  fail "warnings: mentions tab-name script" "no tab-name warning found"
fi

$T kill-session -t warn 2>/dev/null

# ═══════════════════════════════════════════════════════════
echo "═══ Idempotency (two consecutive calls)"
# ═══════════════════════════════════════════════════════════

TEMP_REPO_IDEM="$TMPDIR_BASE/idempotent"
mkdir -p "$TEMP_REPO_IDEM/.agents"
git -C "$TEMP_REPO_IDEM" init -q 2>/dev/null
git -C "$TEMP_REPO_IDEM" commit --allow-empty -m "init" -q 2>/dev/null
cat > "$TEMP_REPO_IDEM/.agents/session.json" <<'SESS'
{
  "lastBranch": "trunk",
  "focus_lane": "VISION-001",
  "bookmark": { "note": "idempotency test" }
}
SESS

start_session "idem" "$TEMP_REPO_IDEM"

# Run 1 reads stale lastBranch then writes current. Run 2+ reads the updated value.
# Idempotency means run 2 == run 3 (after the write stabilizes).
SWAIN_TMUX_SOCKET="$TMUX_SOCK" TMUX="$TMUX_SOCK,0,0" \
  bash "$BOOTSTRAP" --path "$TEMP_REPO_IDEM" --auto >/dev/null 2>&1  # prime the write

OUTPUT_RUN2=$(SWAIN_TMUX_SOCKET="$TMUX_SOCK" TMUX="$TMUX_SOCK,0,0" \
  bash "$BOOTSTRAP" --path "$TEMP_REPO_IDEM" --auto 2>/dev/null)
OUTPUT_RUN3=$(SWAIN_TMUX_SOCKET="$TMUX_SOCK" TMUX="$TMUX_SOCK,0,0" \
  bash "$BOOTSTRAP" --path "$TEMP_REPO_IDEM" --auto 2>/dev/null)

# Normalize: strip tab field (tmux state may differ slightly) and compare core fields
CORE2=$(echo "$OUTPUT_RUN2" | jq '{worktree, session, warnings}' 2>/dev/null)
CORE3=$(echo "$OUTPUT_RUN3" | jq '{worktree, session, warnings}' 2>/dev/null)

if [[ "$CORE2" == "$CORE3" ]]; then
  pass "idempotency: consecutive runs after stabilization produce identical output"
else
  fail "idempotency: consecutive runs differ" "run2=$CORE2 run3=$CORE3"
fi

$T kill-session -t idem 2>/dev/null

# ═══════════════════════════════════════════════════════════
echo "═══ Main worktree detection (isolated=false)"
# ═══════════════════════════════════════════════════════════

# Explicitly test against the main repo root (not a worktree)
start_session "mainwt" "$REPO_ROOT"
OUTPUT_MAIN_WT=$(SWAIN_TMUX_SOCKET="$TMUX_SOCK" TMUX="$TMUX_SOCK,0,0" \
  bash "$BOOTSTRAP" --path "$REPO_ROOT" --auto 2>/dev/null)

MAIN_ISOLATED=$(echo "$OUTPUT_MAIN_WT" | jq -r '.worktree.isolated' 2>/dev/null)
if [[ "$MAIN_ISOLATED" == "false" ]]; then
  pass "main worktree: isolated is false"
else
  fail "main worktree: isolated is false" "got: $MAIN_ISOLATED"
fi

MAIN_BRANCH=$(echo "$OUTPUT_MAIN_WT" | jq -r '.worktree.branch' 2>/dev/null)
if [[ -n "$MAIN_BRANCH" && "$MAIN_BRANCH" != "null" ]]; then
  pass "main worktree: branch is populated"
else
  fail "main worktree: branch is populated" "got: $MAIN_BRANCH"
fi

$T kill-session -t mainwt 2>/dev/null

# ═══════════════════════════════════════════════════════════
echo ""
echo "Results: $PASS passed, $FAIL failed, $SKIP skipped"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
