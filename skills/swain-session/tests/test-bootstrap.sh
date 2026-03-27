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
echo ""
echo "Results: $PASS passed, $FAIL failed, $SKIP skipped"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
