#!/usr/bin/env bash
# RED tests for SPEC-251: Artifact-Aware Worktree Naming
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SCRIPT="$REPO_ROOT/.agents/bin/swain-worktree-name.sh"
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

echo "=== SPEC-251: Artifact-Aware Worktree Naming Tests ==="

# --- AC1: Extracts artifact ID from purpose text ---
echo ""
echo "--- AC1: Artifact ID extraction ---"

NAME1=$(bash "$SCRIPT" "implement SPEC-054 lockfile schema" 2>/dev/null)
assert "SPEC ID extracted" "$(echo "$NAME1" | grep -qi "spec-054" && echo true || echo false)"

NAME2=$(bash "$SCRIPT" "EPIC-012 migration work" 2>/dev/null)
assert "EPIC ID extracted" "$(echo "$NAME2" | grep -qi "epic-012" && echo true || echo false)"

NAME3=$(bash "$SCRIPT" "work on spec-054 stuff" 2>/dev/null)
assert "case insensitive extraction" "$(echo "$NAME3" | grep -qi "spec-054" && echo true || echo false)"

# --- AC2: Implementable naming ---
echo ""
echo "--- AC2: Implementable naming (SPEC, SPIKE) ---"

# SPEC should produce: spec-NNN-<title-slug>
NAME_IMPL=$(bash "$SCRIPT" "implement SPEC-054" 2>/dev/null)
assert "implementable uses ID-title pattern" "$(echo "$NAME_IMPL" | grep -qE '^spec-054-' && echo true || echo false)"
assert "implementable has no timestamp" "$(echo "$NAME_IMPL" | grep -qvE '[0-9]{8}-[0-9]{6}' && echo true || echo false)"

# --- AC3: Container naming ---
echo ""
echo "--- AC3: Container naming (EPIC, INITIATIVE) ---"

NAME_CONT=$(bash "$SCRIPT" "migration EPIC-012" 2>/dev/null)
assert "container includes timestamp" "$(echo "$NAME_CONT" | grep -qE '[0-9]{8}' && echo true || echo false)"
assert "container includes epic ID" "$(echo "$NAME_CONT" | grep -qi "epic-012" && echo true || echo false)"

# --- AC4: Standing naming ---
echo ""
echo "--- AC4: Standing naming (ADR, VISION, etc.) ---"

NAME_STAND=$(bash "$SCRIPT" "update ADR-025" 2>/dev/null)
assert "standing uses ID-title pattern" "$(echo "$NAME_STAND" | grep -qE '^adr-025-' && echo true || echo false)"

# --- AC5: Fallback naming ---
echo ""
echo "--- AC5: Fallback (no artifact ID) ---"

NAME_FALL=$(bash "$SCRIPT" "fix some random bug" 2>/dev/null)
assert "fallback has session prefix" "$(echo "$NAME_FALL" | grep -qE '^session-' && echo true || echo false)"
assert "fallback has timestamp" "$(echo "$NAME_FALL" | grep -qE '[0-9]{8}-[0-9]{6}' && echo true || echo false)"

# No args at all
NAME_EMPTY=$(bash "$SCRIPT" 2>/dev/null)
assert "no args produces session fallback" "$(echo "$NAME_EMPTY" | grep -qE '^session-' && echo true || echo false)"

# --- AC6: Title lookup from frontmatter ---
echo ""
echo "--- AC6: Title from frontmatter ---"

# Use a known artifact that exists in this repo
NAME_LOOKUP=$(bash "$SCRIPT" "implement SPEC-244" 2>/dev/null)
assert "title slug included for known artifact" "$(echo "$NAME_LOOKUP" | grep -qi "lockfile" && echo true || echo false)"

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
