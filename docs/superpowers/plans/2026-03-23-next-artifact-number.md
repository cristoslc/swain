# next-artifact-number.sh Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a single bash script that allocates the next artifact number for any type, scanning all worktrees and trunk to prevent collisions.

**Architecture:** A standalone bash script with no external dependencies beyond git and POSIX tools. Scans worktree filesystems + `git ls-tree` on trunk for committed-but-not-checked-out artifacts. Returns max+1 zero-padded to 3 digits.

**Tech Stack:** Bash, git, find, sed

---

## Chunk 1: Core Script + Tests

### Task 1: Write the test harness

**Files:**
- Create: `skills/swain-design/scripts/test-next-artifact-number.sh`

- [ ] **Step 1: Write the failing test scaffold**

```bash
#!/bin/bash
# TDD tests for next-artifact-number.sh
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$SCRIPT_DIR/next-artifact-number.sh"

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
  # Create initial commit so trunk exists
  mkdir -p docs/spec/Active
  touch docs/spec/Active/.gitkeep
  git add . && git commit -m "init" >/dev/null 2>&1
}

teardown_test_repo() {
  cd /
  if [ -n "$TMPDIR_BASE" ] && [ -d "$TMPDIR_BASE" ]; then
    rm -rf "$TMPDIR_BASE"
  fi
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
# Create a worktree with a higher-numbered spec
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
# Create worktree, delete the epic dir from its working tree (simulates diverged state)
git worktree add "$TMPDIR_BASE/wt2" -b wt-branch2 >/dev/null 2>&1
rm -rf "$TMPDIR_BASE/wt2/docs/epic/Active/(EPIC-025)-Committed"
# From the worktree, ls-tree on trunk should still find EPIC-025
cd "$TMPDIR_BASE/wt2"
result=$(bash "$SCRIPT" EPIC 2>/dev/null) || result=""
if [ "$result" = "026" ]; then pass "git ls-tree finds EPIC-025 on trunk"; else fail "git ls-tree finds EPIC-025 on trunk" "got: '$result'"; fi
teardown_test_repo

# --- Test 8: Non-git directory exits non-zero ---
echo "--- Test 8: outside git repo ---"
cd /tmp
bash "$SCRIPT" SPEC >/dev/null 2>&1 && fail "non-git should exit non-zero" || pass "non-git exits non-zero"

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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bash skills/swain-design/scripts/test-next-artifact-number.sh`
Expected: FAIL (script doesn't exist yet)

- [ ] **Step 3: Commit the test file**

```bash
git add skills/swain-design/scripts/test-next-artifact-number.sh
git commit -m "test(SPEC-156): add test harness for next-artifact-number.sh (RED)"
```

### Task 2: Implement next-artifact-number.sh

**Files:**
- Create: `skills/swain-design/scripts/next-artifact-number.sh`

- [ ] **Step 1: Write the implementation**

```bash
#!/usr/bin/env bash
# next-artifact-number.sh — Allocate the next artifact number for a given type
#
# Usage: next-artifact-number.sh <TYPE>
#   TYPE: SPEC | EPIC | INITIATIVE | VISION | SPIKE | ADR | PERSONA | RUNBOOK | DESIGN | JOURNEY | TRAIN
#
# Scans all worktrees + trunk branch to find the highest existing number,
# then returns max+1 zero-padded to 3 digits.
#
# SPEC-156 / EPIC-043

set -euo pipefail

# --- Validate we're in a git repo ---
git rev-parse --git-dir >/dev/null 2>&1 || {
  echo "Error: not inside a git repository" >&2
  exit 1
}

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# --- Validate and normalize TYPE argument ---
if [ $# -lt 1 ] || [ -z "${1:-}" ]; then
  echo "Usage: next-artifact-number.sh <TYPE>" >&2
  echo "  TYPE: SPEC | EPIC | INITIATIVE | VISION | SPIKE | ADR | PERSONA | RUNBOOK | DESIGN | JOURNEY | TRAIN" >&2
  exit 1
fi

TYPE="$(echo "$1" | tr '[:lower:]' '[:upper:]')"

# --- Map TYPE to docs subdirectory name ---
case "$TYPE" in
  SPEC)       DIR_NAME="spec" ;;
  EPIC)       DIR_NAME="epic" ;;
  INITIATIVE) DIR_NAME="initiative" ;;
  VISION)     DIR_NAME="vision" ;;
  SPIKE)      DIR_NAME="research" ;;
  ADR)        DIR_NAME="adr" ;;
  PERSONA)    DIR_NAME="persona" ;;
  RUNBOOK)    DIR_NAME="runbook" ;;
  DESIGN)     DIR_NAME="design" ;;
  JOURNEY)    DIR_NAME="journey" ;;
  TRAIN)      DIR_NAME="train" ;;
  *)
    echo "Error: unrecognized type '$TYPE'" >&2
    echo "  Valid types: SPEC EPIC INITIATIVE VISION SPIKE ADR PERSONA RUNBOOK DESIGN JOURNEY TRAIN" >&2
    exit 1
    ;;
esac

MAX_NUM=0

# --- Helper: extract max number from a list of paths ---
extract_max() {
  local line num
  while IFS= read -r line; do
    if [[ "$line" =~ ${TYPE}-([0-9]+) ]]; then
      num=$((10#${BASH_REMATCH[1]}))
      if (( num > MAX_NUM )); then
        MAX_NUM=$num
      fi
    fi
  done
}

# --- Scan all worktrees' filesystems ---
while IFS= read -r wt_path; do
  [ -d "$wt_path" ] || continue  # skip inaccessible/stale worktrees
  local_docs="$wt_path/docs/$DIR_NAME"
  [ -d "$local_docs" ] || continue
  find "$local_docs" -maxdepth 4 -name "(${TYPE}-[0-9]*)*" 2>/dev/null | extract_max
done < <(git worktree list --porcelain 2>/dev/null | sed -n 's/^worktree //p')

# --- Scan trunk (or fallback branch) via git ls-tree ---
BRANCH=""
for candidate in trunk main; do
  if git rev-parse --verify "$candidate" >/dev/null 2>&1; then
    BRANCH="$candidate"
    break
  fi
done
# Fallback: current branch's upstream
if [ -z "$BRANCH" ]; then
  BRANCH="$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)"
fi

if [ -n "$BRANCH" ]; then
  git ls-tree -r --name-only "$BRANCH" -- "docs/$DIR_NAME/" 2>/dev/null | extract_max
fi

# --- Output next number, zero-padded to 3 digits ---
NEXT=$(( MAX_NUM + 1 ))
printf "%03d\n" "$NEXT"
```

- [ ] **Step 2: Make it executable**

Run: `chmod +x skills/swain-design/scripts/next-artifact-number.sh`

- [ ] **Step 3: Run the tests**

Run: `bash skills/swain-design/scripts/test-next-artifact-number.sh`
Expected: All tests PASS

- [ ] **Step 4: Commit**

```bash
git add skills/swain-design/scripts/next-artifact-number.sh
git commit -m "feat(SPEC-156): implement next-artifact-number.sh with cross-worktree scanning"
```

### Task 3: Validate against the real repo

**Files:**
- None (validation only)

- [ ] **Step 1: Run against real artifact types and verify output matches reality**

```bash
# Expected: one more than the current max for each type
bash skills/swain-design/scripts/next-artifact-number.sh SPEC
bash skills/swain-design/scripts/next-artifact-number.sh EPIC
bash skills/swain-design/scripts/next-artifact-number.sh SPIKE
bash skills/swain-design/scripts/next-artifact-number.sh ADR
bash skills/swain-design/scripts/next-artifact-number.sh VISION
bash skills/swain-design/scripts/next-artifact-number.sh INITIATIVE
```

Cross-check each output against `find docs/<type>/ -maxdepth 3 -name "(<TYPE>-*)" | sort` to confirm correctness.

- [ ] **Step 2: Run the full test suite one more time**

Run: `bash skills/swain-design/scripts/test-next-artifact-number.sh`
Expected: All tests PASS

- [ ] **Step 3: Final commit if any fixes were needed**

Only if changes were required during validation.
