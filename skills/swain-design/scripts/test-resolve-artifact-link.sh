#!/bin/bash
# TDD tests for resolve-artifact-link.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RESOLVE="$SCRIPT_DIR/resolve-artifact-link.sh"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

PASS=0
FAIL=0

pass() { echo "  PASS: $1"; ((PASS++)); }
fail() { echo "  FAIL: $1"; [ -n "${2:-}" ] && echo "    $2"; ((FAIL++)); }

echo "=== resolve-artifact-link.sh tests ==="

# Test 1: Resolve a known artifact ID (absolute path)
echo "--- Test 1: resolve known artifact ID ---"
result=$(bash "$RESOLVE" SPEC-103 2>/dev/null) || result=""
if [ -n "$result" ]; then pass "returns a path"; else fail "returns a path" "got empty"; fi
case "$result" in *SPEC-103.md) pass "path ends with SPEC-103.md" ;; *) fail "path ends with SPEC-103.md" "got: $result" ;; esac

# Test 2: Relative path from source file
echo "--- Test 2: relative path from source ---"
result=$(bash "$RESOLVE" SPEC-103 "docs/epic/Active/(EPIC-031)-Skill-Audit-Remediation/(EPIC-031)-Skill-Audit-Remediation.md" 2>/dev/null) || result=""
if [ -n "$result" ]; then pass "returns a path"; else fail "returns a path" "got empty"; fi
case "$result" in /*) fail "path is relative" "got absolute: $result" ;; *) pass "path is relative" ;; esac
case "$result" in *SPEC-103*) pass "path contains SPEC-103" ;; *) fail "path contains SPEC-103" "got: $result" ;; esac

# Test 3: Nonexistent artifact
echo "--- Test 3: nonexistent artifact ---"
bash "$RESOLVE" SPEC-99999 >/dev/null 2>&1 && fail "SPEC-99999 should exit non-zero" || pass "SPEC-99999 exits non-zero"

# Test 4: No args
echo "--- Test 4: no args ---"
bash "$RESOLVE" >/dev/null 2>&1 && fail "no args should exit non-zero" || pass "no args exits non-zero"

# Test 5: Invalid format
echo "--- Test 5: invalid format ---"
bash "$RESOLVE" "not-an-artifact" >/dev/null 2>&1 && fail "invalid format should exit non-zero" || pass "invalid format exits non-zero"

# Test 6: Multiple artifact types resolve
echo "--- Test 6: type prefixes ---"
for id in EPIC-031 VISION-001 INITIATIVE-003; do
  result=$(bash "$RESOLVE" "$id" 2>/dev/null) || result=""
  if [ -n "$result" ]; then pass "$id resolves"; else fail "$id resolves"; fi
done

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
