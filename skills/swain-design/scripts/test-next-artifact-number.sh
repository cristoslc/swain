#!/bin/bash
# TDD tests for next-artifact-number.sh (SPEC-156)
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$SCRIPT_DIR/next-artifact-number.sh"

PASS=0
FAIL=0
TMPDIR_BASE=""
ORIG_DIR="$(pwd)"

pass() { echo "  PASS: $1"; ((PASS++)); }
fail() { echo "  FAIL: $1"; [ -n "${2:-}" ] && echo "    $2"; ((FAIL++)); }

setup_test_repo() {
  TMPDIR_BASE="$(mktemp -d)"
  local repo="$TMPDIR_BASE/repo"
  git init "$repo" >/dev/null 2>&1
  cd "$repo"
  git checkout -b trunk >/dev/null 2>&1
  mkdir -p docs/spec/Active
  touch docs/spec/Active/.gitkeep
  git add . && git commit -m "init" >/dev/null 2>&1
}

teardown_test_repo() {
  cd "$ORIG_DIR"
  if [ -n "$TMPDIR_BASE" ] && [ -d "$TMPDIR_BASE" ]; then
    # Remove worktrees first to avoid git locks
    if [ -d "$TMPDIR_BASE/repo" ]; then
      git -C "$TMPDIR_BASE/repo" worktree prune 2>/dev/null || true
    fi
    rm -rf "$TMPDIR_BASE"
  fi
  TMPDIR_BASE=""
}

echo "=== next-artifact-number.sh tests ==="

# --- Test 1: Invalid type exits non-zero ---
echo "--- Test 1: invalid type ---"
setup_test_repo
bash "$SCRIPT" INVALID >/dev/null 2>&1 && fail "INVALID should exit non-zero" || pass "INVALID exits non-zero"
teardown_test_repo

# --- Test 2: No args exits non-zero ---
echo "--- Test 2: no args ---"
setup_test_repo
bash "$SCRIPT" >/dev/null 2>&1 && fail "no args should exit non-zero" || pass "no args exits non-zero"
teardown_test_repo

# --- Test 3: Returns 001 for empty type ---
echo "--- Test 3: no existing artifacts ---"
setup_test_repo
result=$(bash "$SCRIPT" TRAIN 2>/dev/null) || result=""
if [ "$result" = "001" ]; then pass "returns 001 for empty type"; else fail "returns 001 for empty type" "got: '$result'"; fi
teardown_test_repo

# --- Test 4: Finds max in local working tree ---
echo "--- Test 4: local working tree scan ---"
setup_test_repo
mkdir -p "docs/spec/Active/(SPEC-042)-Foo"
mkdir -p "docs/spec/Complete/(SPEC-100)-Bar"
touch "docs/spec/Active/(SPEC-042)-Foo/(SPEC-042)-Foo.md"
touch "docs/spec/Complete/(SPEC-100)-Bar/(SPEC-100)-Bar.md"
git add . && git commit -m "add specs" >/dev/null 2>&1
result=$(bash "$SCRIPT" SPEC 2>/dev/null) || result=""
if [ "$result" = "101" ]; then pass "returns 101 after SPEC-100"; else fail "returns 101 after SPEC-100" "got: '$result'"; fi
teardown_test_repo

# --- Test 5: Scans across worktrees ---
echo "--- Test 5: cross-worktree scan ---"
setup_test_repo
mkdir -p "docs/spec/Active/(SPEC-050)-Foo"
touch "docs/spec/Active/(SPEC-050)-Foo/(SPEC-050)-Foo.md"
git add . && git commit -m "add spec-050" >/dev/null 2>&1
git worktree add "$TMPDIR_BASE/wt1" -b wt-branch >/dev/null 2>&1
mkdir -p "$TMPDIR_BASE/wt1/docs/spec/Active/(SPEC-160)-WT"
touch "$TMPDIR_BASE/wt1/docs/spec/Active/(SPEC-160)-WT/(SPEC-160)-WT.md"
# From main repo, should see the worktree's SPEC-160
result=$(bash "$SCRIPT" SPEC 2>/dev/null) || result=""
if [ "$result" = "161" ]; then pass "sees SPEC-160 in worktree, returns 161"; else fail "sees SPEC-160 in worktree, returns 161" "got: '$result'"; fi
# From the worktree itself, should also return 161
cd "$TMPDIR_BASE/wt1"
result=$(bash "$SCRIPT" SPEC 2>/dev/null) || result=""
if [ "$result" = "161" ]; then pass "from worktree, also returns 161"; else fail "from worktree, also returns 161" "got: '$result'"; fi
teardown_test_repo

# --- Test 6: SPIKE maps to docs/research/ ---
echo "--- Test 6: SPIKE type mapping ---"
setup_test_repo
mkdir -p "docs/research/Active/(SPIKE-010)-Research"
touch "docs/research/Active/(SPIKE-010)-Research/(SPIKE-010)-Research.md"
git add . && git commit -m "add spike" >/dev/null 2>&1
result=$(bash "$SCRIPT" SPIKE 2>/dev/null) || result=""
if [ "$result" = "011" ]; then pass "SPIKE maps to research dir, returns 011"; else fail "SPIKE maps to research dir, returns 011" "got: '$result'"; fi
teardown_test_repo

# --- Test 7: Picks up committed-but-not-checked-out artifacts via git ls-tree ---
echo "--- Test 7: git ls-tree fallback ---"
setup_test_repo
mkdir -p "docs/epic/Active/(EPIC-025)-Committed"
touch "docs/epic/Active/(EPIC-025)-Committed/(EPIC-025)-Committed.md"
git add . && git commit -m "add epic" >/dev/null 2>&1
git worktree add "$TMPDIR_BASE/wt2" -b wt-branch2 >/dev/null 2>&1
rm -rf "$TMPDIR_BASE/wt2/docs/epic/Active/(EPIC-025)-Committed"
cd "$TMPDIR_BASE/wt2"
result=$(bash "$SCRIPT" EPIC 2>/dev/null) || result=""
if [ "$result" = "026" ]; then pass "git ls-tree finds EPIC-025 on trunk"; else fail "git ls-tree finds EPIC-025 on trunk" "got: '$result'"; fi
teardown_test_repo

# --- Test 8: Non-git directory exits non-zero ---
echo "--- Test 8: outside git repo ---"
TMPDIR_NOGIT="$(mktemp -d)"
cd "$TMPDIR_NOGIT"
bash "$SCRIPT" SPEC >/dev/null 2>&1 && fail "non-git should exit non-zero" || pass "non-git exits non-zero"
cd "$ORIG_DIR"
rm -rf "$TMPDIR_NOGIT"

# --- Test 9: Case insensitive type input ---
echo "--- Test 9: case insensitive type ---"
setup_test_repo
mkdir -p "docs/spec/Active/(SPEC-005)-Case"
touch "docs/spec/Active/(SPEC-005)-Case/(SPEC-005)-Case.md"
git add . && git commit -m "add spec" >/dev/null 2>&1
result=$(bash "$SCRIPT" spec 2>/dev/null) || result=""
if [ "$result" = "006" ]; then pass "lowercase 'spec' works"; else fail "lowercase 'spec' works" "got: '$result'"; fi
teardown_test_repo

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
