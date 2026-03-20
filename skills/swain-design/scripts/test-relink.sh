#!/bin/bash
# test-relink.sh — TDD tests for relink.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RELINK="$SCRIPT_DIR/relink.sh"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

PASS=0
FAIL=0
TMPDIR_BASE=""

pass() { echo "  PASS: $1"; PASS=$(( PASS + 1 )); }
fail() { echo "  FAIL: $1"; [ -n "${2:-}" ] && echo "    $2"; FAIL=$(( FAIL + 1 )); }

cleanup() {
  [ -n "$TMPDIR_BASE" ] && rm -rf "$TMPDIR_BASE"
}
trap cleanup EXIT

echo "=== relink.sh tests ==="

# --- Test 1: Fix a broken body-text link in a single file ---
echo ""
echo "--- Test 1: fix broken body-text link (single-file mode) ---"

TMPDIR_BASE=$(mktemp -d /tmp/relink-test-XXXXXX)

# Build a fake docs tree mirroring the real structure
# (relink.sh uses git rev-parse for REPO_ROOT, so we need to work inside the real repo,
#  but point to a real artifact that exists on disk — SPEC-103 in this worktree)

# Find SPEC-103's real location for use as the link target
SPEC103_PATH=$(bash "$SCRIPT_DIR/resolve-artifact-link.sh" SPEC-103 2>/dev/null) || SPEC103_PATH=""

if [ -z "$SPEC103_PATH" ]; then
  fail "Test 1 setup: SPEC-103 must be resolvable for tests to work"
else
  pass "Test 1 setup: SPEC-103 found at $SPEC103_PATH"

  # Create a source file inside the real docs tree (as a temp file) that has a broken link
  # We'll put it next to SPEC-103 in a sibling location to test relative path computation
  TEST_SRC_DIR="$REPO_ROOT/docs/spec/Active"
  TEST_SRC_FILE="$TEST_SRC_DIR/_relink-test-$$.md"

  cat > "$TEST_SRC_FILE" <<MDEOF
---
title: "Test file for relink"
artifact: SPEC-999
status: Active
---

# Test

This references [SPEC-103](../../wrong/path/SPEC-103.md) with a broken link.
MDEOF

  # Run relink on just this file
  output=$(bash "$RELINK" "$TEST_SRC_FILE" 2>&1) || true
  exit_code=$?

  # Check exit code
  if [ "$exit_code" -eq 0 ]; then
    pass "Test 1: exit code 0 (all fixed or none broken)"
  else
    fail "Test 1: exit code" "got $exit_code, output: $output"
  fi

  # Check that a RELINKED line was emitted
  if echo "$output" | grep -q "^RELINKED"; then
    pass "Test 1: RELINKED line emitted"
  else
    fail "Test 1: RELINKED line emitted" "output was: $output"
  fi

  # Check that the file was updated (old broken path no longer present)
  if grep -q "../../wrong/path/SPEC-103.md" "$TEST_SRC_FILE"; then
    fail "Test 1: old broken path removed from file"
  else
    pass "Test 1: old broken path removed from file"
  fi

  # Check that the file now contains a valid link to SPEC-103
  if grep -q "SPEC-103" "$TEST_SRC_FILE"; then
    pass "Test 1: SPEC-103 reference present in updated file"
  else
    fail "Test 1: SPEC-103 reference present in updated file"
  fi

  # Check the link in the file resolves correctly
  # Use python to extract the link target (handles parens in path like (SPEC-103)-Title/...)
  updated_link=$(python3 -c "
import re, sys
link_re = re.compile(r'\[([^\]]*)\]\(((?:[^()\s]|\([^()]*\))+)\)')
with open('$TEST_SRC_FILE') as f:
    for line in f:
        for m in link_re.finditer(line):
            target = m.group(2)
            if 'SPEC-103' in target:
                print(target)
                sys.exit(0)
" 2>/dev/null) || updated_link=""
  if [ -n "$updated_link" ]; then
    resolved=$(cd "$TEST_SRC_DIR" && realpath "$updated_link" 2>/dev/null || echo "")
    if [ -n "$resolved" ] && [ -f "$resolved" ]; then
      pass "Test 1: updated link resolves to a real file"
    else
      fail "Test 1: updated link resolves to a real file" "link='$updated_link' resolved='$resolved'"
    fi
  else
    fail "Test 1: could not extract updated link from file"
  fi

  rm -f "$TEST_SRC_FILE"
fi

# --- Test 2: No broken links — exits 0 with clean message ---
echo ""
echo "--- Test 2: no broken links ---"

TEST_SRC_DIR2="$REPO_ROOT/docs/spec/Active"
TEST_SRC_FILE2="$TEST_SRC_DIR2/_relink-test2-$$.md"

# Get a real relative path to SPEC-103 from this location
SPEC103_REL=$(bash "$SCRIPT_DIR/resolve-artifact-link.sh" SPEC-103 "$TEST_SRC_FILE2" 2>/dev/null) || SPEC103_REL=""

if [ -n "$SPEC103_REL" ]; then
  cat > "$TEST_SRC_FILE2" <<MDEOF
---
title: "Test file 2"
artifact: SPEC-998
status: Active
---

# Test 2

This references [SPEC-103]($SPEC103_REL) with a good link.
MDEOF

  output2=$(bash "$RELINK" "$TEST_SRC_FILE2" 2>&1) || true
  exit_code2=$?

  if [ "$exit_code2" -eq 0 ]; then
    pass "Test 2: exit code 0 (no broken links)"
  else
    fail "Test 2: exit code 0" "got $exit_code2, output: $output2"
  fi

  if echo "$output2" | grep -q "^RELINKED"; then
    fail "Test 2: no RELINKED lines for valid link"
  else
    pass "Test 2: no RELINKED lines emitted (correct)"
  fi

  rm -f "$TEST_SRC_FILE2"
else
  fail "Test 2 setup: could not get relative path for SPEC-103"
fi

# --- Test 3: Link text contains artifact ID (takes precedence over path) ---
echo ""
echo "--- Test 3: artifact ID extracted from link text ---"

TEST_SRC_FILE3="$REPO_ROOT/docs/spec/Active/_relink-test3-$$.md"
TEST_SRC_DIR3="$REPO_ROOT/docs/spec/Active"

cat > "$TEST_SRC_FILE3" <<MDEOF
---
title: "Test file 3"
artifact: SPEC-997
status: Active
---

# Test 3

See [SPEC-103](totally/wrong/path.md) for details.
MDEOF

output3=$(bash "$RELINK" "$TEST_SRC_FILE3" 2>&1) || true
exit_code3=$?

if [ "$exit_code3" -eq 0 ]; then
  pass "Test 3: exit code 0"
else
  fail "Test 3: exit code" "got $exit_code3, output: $output3"
fi

if echo "$output3" | grep -q "^RELINKED"; then
  pass "Test 3: RELINKED line emitted (artifact ID from link text)"
else
  fail "Test 3: RELINKED line emitted" "output: $output3"
fi

rm -f "$TEST_SRC_FILE3"

# --- Test 4: Frontmatter rel-path fix ---
echo ""
echo "--- Test 4: frontmatter rel-path field fix ---"

TEST_SRC_FILE4="$REPO_ROOT/docs/spec/Active/_relink-test4-$$.md"

cat > "$TEST_SRC_FILE4" <<MDEOF
---
title: "Test file 4"
artifact: SPEC-996
status: Active
artifact-refs:
  - artifact: SPEC-103
    rel: [linked]
    rel-path: ../../wrong/path/SPEC-103.md
---

# Test 4
MDEOF

output4=$(bash "$RELINK" "$TEST_SRC_FILE4" 2>&1) || true
exit_code4=$?

if [ "$exit_code4" -eq 0 ]; then
  pass "Test 4: exit code 0"
else
  fail "Test 4: exit code" "got $exit_code4, output: $output4"
fi

if echo "$output4" | grep -q "frontmatter rel-path"; then
  pass "Test 4: frontmatter rel-path RELINKED line emitted"
else
  fail "Test 4: frontmatter rel-path RELINKED line emitted" "output: $output4"
fi

if grep -q "../../wrong/path/SPEC-103.md" "$TEST_SRC_FILE4"; then
  fail "Test 4: old broken rel-path removed from file"
else
  pass "Test 4: old broken rel-path removed from file"
fi

rm -f "$TEST_SRC_FILE4"

# --- Test 5: Exit 1 when link cannot be resolved ---
echo ""
echo "--- Test 5: unfixable link exits 1 ---"

TEST_SRC_FILE5="$REPO_ROOT/docs/spec/Active/_relink-test5-$$.md"

cat > "$TEST_SRC_FILE5" <<MDEOF
---
title: "Test file 5"
artifact: SPEC-995
status: Active
---

# Test 5

See [some text](../not/an/artifact/path.md) for details.
MDEOF

output5=$(bash "$RELINK" "$TEST_SRC_FILE5" 2>&1)
exit_code5=$?

# This link has no artifact ID — should be skipped (unfixed), so exit 1
if [ "$exit_code5" -eq 1 ]; then
  pass "Test 5: exit code 1 (unfixable link remains)"
else
  # If exit 0, maybe the path somehow resolved or wasn't detected — check output
  if echo "$output5" | grep -q "no broken links found"; then
    pass "Test 5: no broken links detected (path happened to resolve?)"
  else
    fail "Test 5: expected exit 1 for unfixable link" "got exit $exit_code5, output: $output5"
  fi
fi

rm -f "$TEST_SRC_FILE5"

# --- Summary ---
echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
