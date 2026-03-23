#!/bin/bash
# TDD tests for detect-duplicate-numbers.sh (SPEC-158)
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$SCRIPT_DIR/detect-duplicate-numbers.sh"
ORIG_DIR="$(pwd)"

PASS=0
FAIL=0
TMPDIR_BASE=""

pass() { echo "  PASS: $1"; ((PASS++)); }
fail() { echo "  FAIL: $1"; [ -n "${2:-}" ] && echo "    $2"; ((FAIL++)); }

setup_test_repo() {
  TMPDIR_BASE="$(mktemp -d)"
  local repo="$TMPDIR_BASE/repo"
  git init "$repo" >/dev/null 2>&1
  cd "$repo"
  git checkout -b trunk >/dev/null 2>&1
  mkdir -p docs/spec/Active docs/epic/Active
  touch docs/spec/Active/.gitkeep
  git add . && git commit -m "init" >/dev/null 2>&1
}

teardown_test_repo() {
  cd "$ORIG_DIR"
  if [ -n "$TMPDIR_BASE" ] && [ -d "$TMPDIR_BASE" ]; then
    rm -rf "$TMPDIR_BASE"
  fi
  TMPDIR_BASE=""
}

echo "=== detect-duplicate-numbers.sh tests ==="

# --- Test 1: No duplicates → exit 0, no output ---
echo "--- Test 1: no duplicates ---"
setup_test_repo
mkdir -p "docs/spec/Active/(SPEC-001)-Foo" "docs/spec/Complete/(SPEC-002)-Bar"
touch "docs/spec/Active/(SPEC-001)-Foo/(SPEC-001)-Foo.md"
touch "docs/spec/Complete/(SPEC-002)-Bar/(SPEC-002)-Bar.md"
git add . && git commit -m "add specs" >/dev/null 2>&1
output=$(bash "$SCRIPT" 2>/dev/null)
rc=$?
if [ $rc -eq 0 ]; then pass "exit 0 when no duplicates"; else fail "exit 0 when no duplicates" "got rc=$rc"; fi
if [ -z "$output" ]; then pass "no output when no duplicates"; else fail "no output when no duplicates" "got: $output"; fi
teardown_test_repo

# --- Test 2: Duplicate detected → exit 1, reports both paths ---
echo "--- Test 2: duplicate detected ---"
setup_test_repo
mkdir -p "docs/spec/Active/(SPEC-042)-First" "docs/spec/Proposed/(SPEC-042)-Second"
touch "docs/spec/Active/(SPEC-042)-First/(SPEC-042)-First.md"
touch "docs/spec/Proposed/(SPEC-042)-Second/(SPEC-042)-Second.md"
git add . && git commit -m "add dup specs" >/dev/null 2>&1
output=$(bash "$SCRIPT" 2>/dev/null)
rc=$?
if [ $rc -ne 0 ]; then pass "exit non-zero on duplicate"; else fail "exit non-zero on duplicate" "got rc=0"; fi
if echo "$output" | grep -q "SPEC-042"; then pass "output mentions SPEC-042"; else fail "output mentions SPEC-042" "got: $output"; fi
if echo "$output" | grep -q "Active"; then pass "output shows Active path"; else fail "output shows Active path" "got: $output"; fi
if echo "$output" | grep -q "Proposed"; then pass "output shows Proposed path"; else fail "output shows Proposed path" "got: $output"; fi
teardown_test_repo

# --- Test 3: Same artifact in different phase dirs (move in progress) → NOT a duplicate ---
echo "--- Test 3: phase-transition move not a false positive ---"
setup_test_repo
# Same artifact name in two phase dirs (mid-transition)
mkdir -p "docs/spec/Active/(SPEC-010)-Moved" "docs/spec/Complete/(SPEC-010)-Moved"
touch "docs/spec/Active/(SPEC-010)-Moved/(SPEC-010)-Moved.md"
touch "docs/spec/Complete/(SPEC-010)-Moved/(SPEC-010)-Moved.md"
git add . && git commit -m "mid-transition" >/dev/null 2>&1
output=$(bash "$SCRIPT" 2>/dev/null)
rc=$?
if [ $rc -eq 0 ]; then pass "same title in two phases = not a dup"; else fail "same title in two phases = not a dup" "rc=$rc, output: $output"; fi
teardown_test_repo

# --- Test 4: Multiple types, only one has a dup ---
echo "--- Test 4: mixed types, one dup ---"
setup_test_repo
mkdir -p "docs/spec/Active/(SPEC-001)-OK" "docs/epic/Active/(EPIC-001)-OK"
mkdir -p "docs/epic/Active/(EPIC-005)-Dup1" "docs/epic/Proposed/(EPIC-005)-Dup2"
touch "docs/spec/Active/(SPEC-001)-OK/(SPEC-001)-OK.md"
touch "docs/epic/Active/(EPIC-001)-OK/(EPIC-001)-OK.md"
touch "docs/epic/Active/(EPIC-005)-Dup1/(EPIC-005)-Dup1.md"
touch "docs/epic/Proposed/(EPIC-005)-Dup2/(EPIC-005)-Dup2.md"
git add . && git commit -m "mixed" >/dev/null 2>&1
output=$(bash "$SCRIPT" 2>/dev/null)
rc=$?
if [ $rc -ne 0 ]; then pass "detects EPIC-005 dup"; else fail "detects EPIC-005 dup"; fi
if echo "$output" | grep -q "EPIC-005"; then pass "reports EPIC-005"; else fail "reports EPIC-005" "got: $output"; fi
if echo "$output" | grep -q "SPEC"; then fail "should not mention SPEC (no SPEC dups)" "got: $output"; else pass "does not mention SPEC"; fi
teardown_test_repo

# --- Test 5: Specific type filter ---
echo "--- Test 5: filter by type ---"
setup_test_repo
mkdir -p "docs/spec/Active/(SPEC-042)-Dup1" "docs/spec/Proposed/(SPEC-042)-Dup2"
touch "docs/spec/Active/(SPEC-042)-Dup1/(SPEC-042)-Dup1.md"
touch "docs/spec/Proposed/(SPEC-042)-Dup2/(SPEC-042)-Dup2.md"
git add . && git commit -m "spec dup" >/dev/null 2>&1
# Filter to EPIC only — should not find the SPEC dup
output=$(bash "$SCRIPT" EPIC 2>/dev/null)
rc=$?
if [ $rc -eq 0 ]; then pass "EPIC filter misses SPEC dup"; else fail "EPIC filter misses SPEC dup" "rc=$rc"; fi
# Filter to SPEC — should find it
output=$(bash "$SCRIPT" SPEC 2>/dev/null)
rc=$?
if [ $rc -ne 0 ]; then pass "SPEC filter finds SPEC dup"; else fail "SPEC filter finds SPEC dup"; fi
teardown_test_repo

# --- Test 6: Outside git repo exits non-zero ---
echo "--- Test 6: outside git repo ---"
TMPDIR_NOGIT="$(mktemp -d)"
cd "$TMPDIR_NOGIT"
bash "$SCRIPT" >/dev/null 2>&1 && fail "non-git should exit non-zero" || pass "non-git exits non-zero"
cd "$ORIG_DIR"
rm -rf "$TMPDIR_NOGIT"

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
