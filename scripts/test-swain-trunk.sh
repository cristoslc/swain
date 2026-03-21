#!/usr/bin/env bash
# Tests for swain-trunk.sh
# Run: bash scripts/test-swain-trunk.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SWAIN_TRUNK="$SCRIPT_DIR/swain-trunk.sh"
PASS=0
FAIL=0
TMPDIR_BASE=""

cleanup() {
  if [ -n "$TMPDIR_BASE" ] && [ -d "$TMPDIR_BASE" ]; then
    rm -rf "$TMPDIR_BASE"
  fi
}
trap cleanup EXIT

assert_eq() {
  local desc="$1" expected="$2" actual="$3"
  if [ "$expected" = "$actual" ]; then
    echo "  PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $desc (expected '$expected', got '$actual')"
    FAIL=$((FAIL + 1))
  fi
}

TMPDIR_BASE="$(mktemp -d)"

# ─── T1: Normal repo (not worktree) returns current branch ───
echo "T1: Auto-detection on current branch"
T1_DIR="$TMPDIR_BASE/t1"
mkdir -p "$T1_DIR"
(
  cd "$T1_DIR"
  git init -b develop . >/dev/null 2>&1
  git commit --allow-empty -m "init" >/dev/null 2>&1
  result=$(bash "$SWAIN_TRUNK")
  assert_eq "returns 'develop' when on develop" "develop" "$result"
)

# ─── T2: Settings override ───
echo "T2: Settings override"
T2_DIR="$TMPDIR_BASE/t2"
mkdir -p "$T2_DIR"
(
  cd "$T2_DIR"
  git init -b main . >/dev/null 2>&1
  git commit --allow-empty -m "init" >/dev/null 2>&1
  echo '{"git": {"trunk": "custom-trunk"}}' > swain.settings.json
  result=$(bash "$SWAIN_TRUNK")
  assert_eq "returns 'custom-trunk' from settings override" "custom-trunk" "$result"
)

# ─── T3: Settings override empty string is ignored ───
echo "T3: Empty settings override falls through to auto-detect"
T3_DIR="$TMPDIR_BASE/t3"
mkdir -p "$T3_DIR"
(
  cd "$T3_DIR"
  git init -b main . >/dev/null 2>&1
  git commit --allow-empty -m "init" >/dev/null 2>&1
  echo '{"git": {"trunk": ""}}' > swain.settings.json
  result=$(bash "$SWAIN_TRUNK")
  assert_eq "returns 'main' when override is empty" "main" "$result"
)

# ─── T4: No settings file falls through to auto-detect ───
echo "T4: No settings file"
T4_DIR="$TMPDIR_BASE/t4"
mkdir -p "$T4_DIR"
(
  cd "$T4_DIR"
  git init -b trunk . >/dev/null 2>&1
  git commit --allow-empty -m "init" >/dev/null 2>&1
  result=$(bash "$SWAIN_TRUNK")
  assert_eq "returns 'trunk' when no settings file" "trunk" "$result"
)

# ─── T5: From inside a worktree, returns main worktree's branch ───
echo "T5: Detection from inside a worktree"
T5_DIR="$TMPDIR_BASE/t5"
mkdir -p "$T5_DIR"
(
  cd "$T5_DIR"
  git init -b develop . >/dev/null 2>&1
  git commit --allow-empty -m "init" >/dev/null 2>&1
  git worktree add "$T5_DIR/wt" -b feature-x >/dev/null 2>&1
  cd "$T5_DIR/wt"
  result=$(bash "$SWAIN_TRUNK")
  assert_eq "returns 'develop' from worktree (not 'feature-x')" "develop" "$result"
  cd "$T5_DIR"
  git worktree remove "$T5_DIR/wt" 2>/dev/null || true
)

# ─── T6: Settings override from worktree ───
echo "T6: Settings override from worktree"
T6_DIR="$TMPDIR_BASE/t6"
mkdir -p "$T6_DIR"
(
  cd "$T6_DIR"
  git init -b main . >/dev/null 2>&1
  git commit --allow-empty -m "init" >/dev/null 2>&1
  echo '{"git": {"trunk": "release"}}' > swain.settings.json
  git add . && git commit -m "settings" >/dev/null 2>&1
  git worktree add "$T6_DIR/wt" -b feature-y >/dev/null 2>&1
  cd "$T6_DIR/wt"
  result=$(bash "$SWAIN_TRUNK")
  assert_eq "returns 'release' override from worktree" "release" "$result"
  cd "$T6_DIR"
  git worktree remove "$T6_DIR/wt" 2>/dev/null || true
)

# ─── Summary ───
echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
