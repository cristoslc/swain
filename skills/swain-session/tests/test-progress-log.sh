#!/usr/bin/env bash
# test-progress-log.sh — Tests for swain-progress-log.sh (SPEC-200)
#
# Uses the bash assert pattern (PASS/FAIL counters).
# Tests against EPIC-048 as a real artifact, reverting changes after each test.
#
# Usage: bash skills/swain-session/tests/test-progress-log.sh

set +e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROGRESS_LOG="$(cd "$SCRIPT_DIR/.." && pwd)/scripts/swain-progress-log.sh"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"

# Test artifact — must exist in the repo
TEST_ARTIFACT_ID="EPIC-048"
TEST_ARTIFACT_DIR="$REPO_ROOT/docs/epic/Active/(EPIC-048)-Session-Startup-Fast-Path"
TEST_ARTIFACT_FILE="$TEST_ARTIFACT_DIR/(EPIC-048)-Session-Startup-Fast-Path.md"
TEST_PROGRESS_FILE="$TEST_ARTIFACT_DIR/progress.md"

PASS=0
FAIL=0

pass() { echo "  PASS: $1"; ((PASS++)); }
fail() { echo "  FAIL: $1 — $2"; ((FAIL++)); }

cleanup() {
  # Revert any changes to the test artifact
  git checkout -- "$TEST_ARTIFACT_FILE" 2>/dev/null
  rm -f "$TEST_PROGRESS_FILE"
}
trap cleanup EXIT

# ═══════════════════════════════════════════════════════════
echo "═══ T1: Script exists and is executable"
# ═══════════════════════════════════════════════════════════

if [[ -f "$PROGRESS_LOG" ]]; then
  pass "T1a: script file exists"
else
  fail "T1a: script file exists" "not found at $PROGRESS_LOG"
fi

if [[ -x "$PROGRESS_LOG" ]]; then
  pass "T1b: script is executable"
else
  fail "T1b: script is executable" "missing execute permission"
fi

# Verify symlink in .agents/bin/
SYMLINK="$REPO_ROOT/.agents/bin/swain-progress-log.sh"
if [[ -L "$SYMLINK" ]]; then
  pass "T1c: symlink exists in .agents/bin/"
else
  fail "T1c: symlink exists in .agents/bin/" "not found at $SYMLINK"
fi

# ═══════════════════════════════════════════════════════════
echo "═══ T2: --entry creates progress.md if missing"
# ═══════════════════════════════════════════════════════════

# Ensure clean state
rm -f "$TEST_PROGRESS_FILE"

OUTPUT=$(bash "$PROGRESS_LOG" --artifact-id "$TEST_ARTIFACT_ID" --entry "First test entry" 2>&1)

if [[ -f "$TEST_PROGRESS_FILE" ]]; then
  pass "T2a: progress.md created"
else
  fail "T2a: progress.md created" "file not found after --entry"
fi

if grep -q "# Progress Log" "$TEST_PROGRESS_FILE" 2>/dev/null; then
  pass "T2b: progress.md has header"
else
  fail "T2b: progress.md has header" "missing '# Progress Log' header"
fi

TODAY=$(date +%Y-%m-%d)
if grep -q "## $TODAY" "$TEST_PROGRESS_FILE" 2>/dev/null; then
  pass "T2c: entry has today's date heading"
else
  fail "T2c: entry has today's date heading" "missing date $TODAY"
fi

if grep -q "First test entry" "$TEST_PROGRESS_FILE" 2>/dev/null; then
  pass "T2d: entry text is present"
else
  fail "T2d: entry text is present" "missing entry text"
fi

# ═══════════════════════════════════════════════════════════
echo "═══ T3: --entry appends without overwriting"
# ═══════════════════════════════════════════════════════════

bash "$PROGRESS_LOG" --artifact-id "$TEST_ARTIFACT_ID" --entry "Second test entry" 2>&1 >/dev/null

if grep -q "First test entry" "$TEST_PROGRESS_FILE" 2>/dev/null; then
  pass "T3a: first entry still present after second append"
else
  fail "T3a: first entry still present after second append" "first entry was overwritten"
fi

if grep -q "Second test entry" "$TEST_PROGRESS_FILE" 2>/dev/null; then
  pass "T3b: second entry is present"
else
  fail "T3b: second entry is present" "missing second entry text"
fi

ENTRY_COUNT=$(grep -c "^## [0-9]" "$TEST_PROGRESS_FILE" 2>/dev/null)
if [[ "$ENTRY_COUNT" -eq 2 ]]; then
  pass "T3c: two dated sections exist"
else
  fail "T3c: two dated sections exist" "found $ENTRY_COUNT sections"
fi

# ═══════════════════════════════════════════════════════════
echo "═══ T4: --synthesize replaces ## Progress section"
# ═══════════════════════════════════════════════════════════

# First, manually add a Progress section to the artifact so we can test replacement
# The artifact doesn't have one by default, so synthesize will insert it
bash "$PROGRESS_LOG" --artifact-id "$TEST_ARTIFACT_ID" --synthesize 2>&1 >/dev/null

if grep -q "## Progress" "$TEST_ARTIFACT_FILE" 2>/dev/null; then
  pass "T4a: ## Progress section exists in artifact after synthesize"
else
  fail "T4a: ## Progress section exists in artifact after synthesize" "section not found"
fi

if grep -q "First test entry" "$TEST_ARTIFACT_FILE" 2>/dev/null; then
  pass "T4b: synthesized content includes first entry"
else
  fail "T4b: synthesized content includes first entry" "content missing"
fi

if grep -q "Second test entry" "$TEST_ARTIFACT_FILE" 2>/dev/null; then
  pass "T4c: synthesized content includes second entry"
else
  fail "T4c: synthesized content includes second entry" "content missing"
fi

# Now add a third entry and re-synthesize — should replace, not duplicate
bash "$PROGRESS_LOG" --artifact-id "$TEST_ARTIFACT_ID" --entry "Third test entry" 2>&1 >/dev/null
bash "$PROGRESS_LOG" --artifact-id "$TEST_ARTIFACT_ID" --synthesize 2>&1 >/dev/null

PROGRESS_COUNT=$(grep -c "## Progress" "$TEST_ARTIFACT_FILE" 2>/dev/null)
if [[ "$PROGRESS_COUNT" -eq 1 ]]; then
  pass "T4d: only one ## Progress section after re-synthesize"
else
  fail "T4d: only one ## Progress section after re-synthesize" "found $PROGRESS_COUNT sections"
fi

if grep -q "Third test entry" "$TEST_ARTIFACT_FILE" 2>/dev/null; then
  pass "T4e: third entry present in re-synthesized content"
else
  fail "T4e: third entry present in re-synthesized content" "content missing"
fi

# ═══════════════════════════════════════════════════════════
echo "═══ T5: --synthesize inserts ## Progress if missing"
# ═══════════════════════════════════════════════════════════

# Revert the artifact to its original state (no ## Progress)
git checkout -- "$TEST_ARTIFACT_FILE" 2>/dev/null

# Verify it doesn't have ## Progress
if ! grep -q "## Progress" "$TEST_ARTIFACT_FILE" 2>/dev/null; then
  pass "T5a: artifact has no ## Progress before synthesize"
else
  fail "T5a: artifact has no ## Progress before synthesize" "section already exists"
fi

bash "$PROGRESS_LOG" --artifact-id "$TEST_ARTIFACT_ID" --synthesize 2>&1 >/dev/null

if grep -q "## Progress" "$TEST_ARTIFACT_FILE" 2>/dev/null; then
  pass "T5b: ## Progress inserted by synthesize"
else
  fail "T5b: ## Progress inserted by synthesize" "section not found after synthesize"
fi

# Verify it's between Desired Outcomes and Scope Boundaries (for epics, after Goal / Objective)
# Check that Progress comes before Scope Boundaries
PROGRESS_LINE=$(grep -n "## Progress" "$TEST_ARTIFACT_FILE" | head -1 | cut -d: -f1)
SCOPE_LINE=$(grep -n "## Scope Boundaries" "$TEST_ARTIFACT_FILE" | head -1 | cut -d: -f1)
GOAL_LINE=$(grep -n "## Goal / Objective" "$TEST_ARTIFACT_FILE" | head -1 | cut -d: -f1)

if [[ -n "$PROGRESS_LINE" && -n "$SCOPE_LINE" && "$PROGRESS_LINE" -lt "$SCOPE_LINE" ]]; then
  pass "T5c: ## Progress appears before ## Scope Boundaries"
else
  fail "T5c: ## Progress appears before ## Scope Boundaries" "progress=$PROGRESS_LINE scope=$SCOPE_LINE"
fi

if [[ -n "$PROGRESS_LINE" && -n "$GOAL_LINE" && "$PROGRESS_LINE" -gt "$GOAL_LINE" ]]; then
  pass "T5d: ## Progress appears after ## Goal / Objective"
else
  fail "T5d: ## Progress appears after ## Goal / Objective" "progress=$PROGRESS_LINE goal=$GOAL_LINE"
fi

# ═══════════════════════════════════════════════════════════
echo "═══ T6: Template files contain ## Progress section"
# ═══════════════════════════════════════════════════════════

EPIC_TEMPLATE="$REPO_ROOT/skills/swain-design/references/epic-template.md.template"
INIT_TEMPLATE="$REPO_ROOT/skills/swain-design/references/initiative-template.md.template"

if grep -q "## Progress" "$EPIC_TEMPLATE" 2>/dev/null; then
  pass "T6a: epic template has ## Progress"
else
  fail "T6a: epic template has ## Progress" "section not found"
fi

if grep -q "## Progress" "$INIT_TEMPLATE" 2>/dev/null; then
  pass "T6b: initiative template has ## Progress"
else
  fail "T6b: initiative template has ## Progress" "section not found"
fi

# Verify Progress comes before Scope Boundaries in templates
EPIC_PROG=$(grep -n "## Progress" "$EPIC_TEMPLATE" | head -1 | cut -d: -f1)
EPIC_SCOPE=$(grep -n "## Scope Boundaries" "$EPIC_TEMPLATE" | head -1 | cut -d: -f1)
if [[ -n "$EPIC_PROG" && -n "$EPIC_SCOPE" && "$EPIC_PROG" -lt "$EPIC_SCOPE" ]]; then
  pass "T6c: epic template: Progress before Scope Boundaries"
else
  fail "T6c: epic template: Progress before Scope Boundaries" "prog=$EPIC_PROG scope=$EPIC_SCOPE"
fi

INIT_PROG=$(grep -n "## Progress" "$INIT_TEMPLATE" | head -1 | cut -d: -f1)
INIT_SCOPE=$(grep -n "## Scope Boundaries" "$INIT_TEMPLATE" | head -1 | cut -d: -f1)
if [[ -n "$INIT_PROG" && -n "$INIT_SCOPE" && "$INIT_PROG" -lt "$INIT_SCOPE" ]]; then
  pass "T6d: initiative template: Progress before Scope Boundaries"
else
  fail "T6d: initiative template: Progress before Scope Boundaries" "prog=$INIT_PROG scope=$INIT_SCOPE"
fi

# ═══════════════════════════════════════════════════════════
echo ""
echo "Results: $PASS passed, $FAIL failed"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
