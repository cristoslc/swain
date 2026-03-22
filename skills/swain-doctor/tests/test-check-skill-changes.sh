#!/usr/bin/env bash
# test-check-skill-changes.sh — Tests for swain-doctor skill-change detection
#
# Usage: bash skills/swain-doctor/tests/test-check-skill-changes.sh

set +e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECK_SCRIPT="$(cd "$SCRIPT_DIR/.." && pwd)/scripts/check-skill-changes.sh"

PASS=0
FAIL=0

pass() { echo "  PASS: $1"; ((PASS++)); }
fail() { echo "  FAIL: $1 — $2"; ((FAIL++)); }

# Create a temporary git repo with skill files for testing
make_test_repo() {
  local repo_dir="$1"
  mkdir -p "$repo_dir/skills/test-skill"
  cd "$repo_dir"
  git init -q
  git config user.email "test@test.com"
  git config user.name "Test"

  # Initial commit with a skill file
  cat > skills/test-skill/SKILL.md <<'SKILL'
---
name: test-skill
description: A test skill
---

# Test Skill

## Overview

This is a test skill for unit testing.

## When to Use

Use when testing.
SKILL
  git add -A
  git commit -q -m "initial: add test skill"
}

echo "=== swain-doctor Skill Change Detection Tests ==="
echo "Script: $CHECK_SCRIPT"
echo ""

# --- AC2: Non-trivial skill change emits warning ---
echo "--- AC2: Non-trivial skill change on trunk emits warning ---"
TMPDIR="$(mktemp -d)"
REPO_DIR="$TMPDIR/repo"
make_test_repo "$REPO_DIR"

# Make a non-trivial change (20+ lines)
cat >> skills/test-skill/SKILL.md <<'ADDITION'

## New Section

This is a brand new section with lots of content.
Line 1 of new content.
Line 2 of new content.
Line 3 of new content.
Line 4 of new content.
Line 5 of new content.
Line 6 of new content.
Line 7 of new content.
Line 8 of new content.
Line 9 of new content.
Line 10 of new content.
Line 11 of new content.
Line 12 of new content.
Line 13 of new content.
Line 14 of new content.
Line 15 of new content.
ADDITION
git add -A
git commit -q -m "refactor(test-skill): add new section with content"

output="$(bash "$CHECK_SCRIPT" 2>&1)"
status=$?
if [[ $status -ne 0 && "$output" == *"skill files with non-trivial changes"* ]]; then
  pass "AC2: non-trivial skill change detected"
else
  fail "AC2" "status=$status output=$output"
fi
rm -rf "$TMPDIR"

# --- AC3: Trivial skill change passes clean ---
echo "--- AC3: Trivial skill change passes clean ---"
TMPDIR="$(mktemp -d)"
REPO_DIR="$TMPDIR/repo"
make_test_repo "$REPO_DIR"

# Make a trivial change (2-line typo fix, single file)
sed -i.bak 's/This is a test skill for unit testing./This is a test skill for unit testing purposes./' skills/test-skill/SKILL.md
rm -f skills/test-skill/SKILL.md.bak
git add -A
git commit -q -m "fix(test-skill): fix typo"

output="$(bash "$CHECK_SCRIPT" 2>&1)"
status=$?
if [[ $status -eq 0 ]]; then
  pass "AC3: trivial skill change passes clean"
else
  fail "AC3" "status=$status output=$output"
fi
rm -rf "$TMPDIR"

# --- Multi-file skill change is non-trivial ---
echo "--- Multi-file skill change is non-trivial ---"
TMPDIR="$(mktemp -d)"
REPO_DIR="$TMPDIR/repo"
make_test_repo "$REPO_DIR"

# Create a second skill file and change both (multi-file = non-trivial regardless of diff size)
mkdir -p skills/other-skill
cat > skills/other-skill/SKILL.md <<'SKILL2'
---
name: other-skill
description: Another skill
---
# Other Skill
SKILL2
# Also touch the first skill with a small change
sed -i.bak 's/A test skill/A modified test skill/' skills/test-skill/SKILL.md
rm -f skills/test-skill/SKILL.md.bak
git add -A
git commit -q -m "feat: add other skill and update test skill"

output="$(bash "$CHECK_SCRIPT" 2>&1)"
status=$?
if [[ $status -ne 0 && "$output" == *"skill files with non-trivial changes"* ]]; then
  pass "Multi-file skill change detected as non-trivial"
else
  fail "Multi-file" "status=$status output=$output"
fi
rm -rf "$TMPDIR"

# --- Non-skill commits pass clean ---
echo "--- Non-skill file changes pass clean ---"
TMPDIR="$(mktemp -d)"
REPO_DIR="$TMPDIR/repo"
make_test_repo "$REPO_DIR"

# Make a big change to a non-skill file
cat > README.md <<'README'
# Test Project
This is a big change to a non-skill file.
Line 1
Line 2
Line 3
Line 4
Line 5
Line 6
Line 7
Line 8
Line 9
Line 10
README
git add -A
git commit -q -m "docs: update README"

output="$(bash "$CHECK_SCRIPT" 2>&1)"
status=$?
if [[ $status -eq 0 ]]; then
  pass "Non-skill file changes pass clean"
else
  fail "Non-skill" "status=$status output=$output"
fi
rm -rf "$TMPDIR"

# --- Version bump in frontmatter is non-trivial even if small diff ---
echo "--- Version bump in frontmatter is non-trivial ---"
TMPDIR="$(mktemp -d)"
REPO_DIR="$TMPDIR/repo"
make_test_repo "$REPO_DIR"

# Add a version field then bump it (small diff but structural)
sed -i.bak 's/description: A test skill/description: A test skill\nversion: 1.0.0/' skills/test-skill/SKILL.md
rm -f skills/test-skill/SKILL.md.bak
git add -A
git commit -q -m "chore: add version field"

# Now bump the version
sed -i.bak 's/version: 1.0.0/version: 2.0.0/' skills/test-skill/SKILL.md
rm -f skills/test-skill/SKILL.md.bak
git add -A
git commit -q -m "chore(test-skill): bump version to 2.0.0"

output="$(bash "$CHECK_SCRIPT" 2>&1)"
status=$?
if [[ $status -ne 0 && "$output" == *"skill files with non-trivial changes"* ]]; then
  pass "Version bump detected as non-trivial"
else
  fail "Version bump" "status=$status output=$output"
fi
rm -rf "$TMPDIR"

echo ""
echo "=== Summary ==="
echo "PASS: $PASS"
echo "FAIL: $FAIL"

if [[ $FAIL -gt 0 ]]; then
  exit 1
fi
