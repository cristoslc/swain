#!/usr/bin/env bash
# test-renumber-collision.sh — tests for SPEC-204
# Verifies that renumber-artifact.sh does not over-rewrite keeper references
# during collision resolution.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
RENUMBER="$REPO_ROOT/skills/swain-design/scripts/renumber-artifact.sh"

PASS=0
FAIL=0
TOTAL=0

assert() {
  local desc="$1"
  local result="$2"
  TOTAL=$((TOTAL + 1))
  if [[ "$result" == "0" ]]; then
    PASS=$((PASS + 1))
    echo "  PASS: $desc"
  else
    FAIL=$((FAIL + 1))
    echo "  FAIL: $desc"
  fi
}

assert_contains() {
  local desc="$1"
  local file="$2"
  local pattern="$3"
  TOTAL=$((TOTAL + 1))
  if grep -q "$pattern" "$file" 2>/dev/null; then
    PASS=$((PASS + 1))
    echo "  PASS: $desc"
  else
    FAIL=$((FAIL + 1))
    echo "  FAIL: $desc — expected '$pattern' in $(basename "$file")"
  fi
}

assert_not_contains() {
  local desc="$1"
  local file="$2"
  local pattern="$3"
  TOTAL=$((TOTAL + 1))
  if ! grep -q "$pattern" "$file" 2>/dev/null; then
    PASS=$((PASS + 1))
    echo "  PASS: $desc"
  else
    FAIL=$((FAIL + 1))
    echo "  FAIL: $desc — found '$pattern' in $(basename "$file") but expected it absent"
  fi
}

# --- Setup: create a temp git repo with collision scenario ---
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

setup_collision_repo() {
  cd "$TMPDIR"
  git init -q
  git config user.email "test@test.com"
  git config user.name "Test"

  # Create the keeper artifact (SPEC-050) — predates the collision
  mkdir -p docs/spec/Active/"(SPEC-050)-Keeper-Feature"
  cat > docs/spec/Active/"(SPEC-050)-Keeper-Feature"/"(SPEC-050)-Keeper-Feature.md" <<'KEEPER'
---
title: "Keeper Feature"
artifact: SPEC-050
status: Active
created: 2026-01-01
parent-epic: EPIC-010
linked-artifacts:
  - ADR-005
---

# Keeper Feature

This is the keeper artifact for SPEC-050.
KEEPER

  # Create another doc that references the keeper
  mkdir -p docs/adr/Accepted/"(ADR-005)-Some-Decision"
  cat > docs/adr/Accepted/"(ADR-005)-Some-Decision"/"(ADR-005)-Some-Decision.md" <<'ADR'
---
title: "Some Decision"
artifact: ADR-005
status: Accepted
created: 2026-01-01
linked-artifacts:
  - SPEC-050
---

# Some Decision

This decision was made for SPEC-050 (Keeper Feature).
ADR

  # Create an epic that references the keeper
  mkdir -p docs/epic/Active/"(EPIC-010)-Parent-Epic"
  cat > docs/epic/Active/"(EPIC-010)-Parent-Epic"/"(EPIC-010)-Parent-Epic.md" <<'EPIC'
---
title: "Parent Epic"
artifact: EPIC-010
status: Active
created: 2026-01-01
---

# Parent Epic

Contains SPEC-050 as a child spec.
EPIC

  # Commit the keeper and its references
  git add -A
  git commit -q -m "Add keeper SPEC-050 and references"

  # Now create the collision artifact — same ID, newer date
  mkdir -p docs/spec/Active/"(SPEC-050)-Collision-Feature"
  cat > docs/spec/Active/"(SPEC-050)-Collision-Feature"/"(SPEC-050)-Collision-Feature.md" <<'COLLISION'
---
title: "Collision Feature"
artifact: SPEC-050
status: Active
created: 2026-03-15
parent-epic: ""
linked-artifacts: []
---

# Collision Feature

This is the collision artifact that accidentally got SPEC-050.
COLLISION

  # Create a doc that references the collision
  mkdir -p docs/design/Active/"(DESIGN-001)-Collision-Design"
  cat > docs/design/Active/"(DESIGN-001)-Collision-Design"/"(DESIGN-001)-Collision-Design.md" <<'DESIGN'
---
title: "Collision Design"
artifact: DESIGN-001
status: Active
created: 2026-03-15
linked-artifacts:
  - SPEC-050
---

# Collision Design

This design doc was created alongside the collision and references SPEC-050
meaning the collision feature, not the keeper.
DESIGN

  git add -A
  git commit -q -m "Add collision SPEC-050 and its design doc"

  # Copy the scripts we need into this repo
  mkdir -p skills/swain-design/scripts
  cp "$RENUMBER" skills/swain-design/scripts/
  cp "$REPO_ROOT/skills/swain-design/scripts/next-artifact-number.sh" skills/swain-design/scripts/
  cp "$REPO_ROOT/skills/swain-design/scripts/detect-duplicate-numbers.sh" skills/swain-design/scripts/
  git add -A
  git commit -q -m "Add scripts"
}

# ============================================================
echo "=== SPEC-204: Collision reference rewrite tests ==="
echo ""

# --- Test 1: Keeper references in pre-collision files are preserved ---
echo "Test 1: Keeper references in pre-collision files are NOT rewritten"
setup_collision_repo

COLLISION_DIR="$TMPDIR/docs/spec/Active/(SPEC-050)-Collision-Feature"
bash "$RENUMBER" SPEC-050 SPEC-099 --source-dir "$COLLISION_DIR"

# The ADR was committed BEFORE the collision — its SPEC-050 reference is to the keeper
assert_contains "ADR still references keeper SPEC-050" \
  "$TMPDIR/docs/adr/Accepted/(ADR-005)-Some-Decision/(ADR-005)-Some-Decision.md" \
  "SPEC-050"
assert_not_contains "ADR does NOT reference SPEC-099" \
  "$TMPDIR/docs/adr/Accepted/(ADR-005)-Some-Decision/(ADR-005)-Some-Decision.md" \
  "SPEC-099"

# The EPIC was committed BEFORE the collision — its SPEC-050 reference is to the keeper
assert_contains "EPIC still references keeper SPEC-050" \
  "$TMPDIR/docs/epic/Active/(EPIC-010)-Parent-Epic/(EPIC-010)-Parent-Epic.md" \
  "SPEC-050"
assert_not_contains "EPIC does NOT reference SPEC-099" \
  "$TMPDIR/docs/epic/Active/(EPIC-010)-Parent-Epic/(EPIC-010)-Parent-Epic.md" \
  "SPEC-099"

echo ""

# --- Test 2: Collision artifact's own files ARE rewritten ---
echo "Test 2: Collision artifact's own files ARE rewritten"

# The collision artifact should have been renamed and its references updated
NEW_COLLISION_MD="$TMPDIR/docs/spec/Active/(SPEC-099)-Collision-Feature/(SPEC-099)-Collision-Feature.md"
assert_contains "collision artifact renamed to SPEC-099" "$NEW_COLLISION_MD" "artifact: SPEC-099"
assert_not_contains "collision artifact no longer says SPEC-050" "$NEW_COLLISION_MD" "SPEC-050"

echo ""

# --- Test 3: Post-collision references ARE rewritten ---
echo "Test 3: Post-collision file references ARE rewritten"

# The design doc was committed AFTER the collision — its SPEC-050 reference is to the collision
assert_contains "design doc references SPEC-099" \
  "$TMPDIR/docs/design/Active/(DESIGN-001)-Collision-Design/(DESIGN-001)-Collision-Design.md" \
  "SPEC-099"
assert_not_contains "design doc no longer references SPEC-050" \
  "$TMPDIR/docs/design/Active/(DESIGN-001)-Collision-Design/(DESIGN-001)-Collision-Design.md" \
  "SPEC-050"

echo ""

# --- Test 4: Keeper artifact's own files are preserved ---
echo "Test 4: Keeper artifact's own files are preserved"

KEEPER_MD="$TMPDIR/docs/spec/Active/(SPEC-050)-Keeper-Feature/(SPEC-050)-Keeper-Feature.md"
assert_contains "keeper frontmatter still SPEC-050" "$KEEPER_MD" "artifact: SPEC-050"
assert_contains "keeper body still SPEC-050" "$KEEPER_MD" "keeper artifact for SPEC-050"
assert_not_contains "keeper has no SPEC-099" "$KEEPER_MD" "SPEC-099"

echo ""

# --- Test 5: Dry-run shows which refs would be skipped ---
echo "Test 5: Dry-run distinguishes keeper vs collision references"

# Reset the repo for a fresh dry-run test
rm -rf "$TMPDIR"
TMPDIR=$(mktemp -d)
setup_collision_repo

COLLISION_DIR="$TMPDIR/docs/spec/Active/(SPEC-050)-Collision-Feature"
DRY_OUTPUT=$(bash "$RENUMBER" SPEC-050 SPEC-099 --source-dir "$COLLISION_DIR" --dry-run 2>&1)

# Dry-run should mention skipping keeper references
TOTAL=$((TOTAL + 1))
if echo "$DRY_OUTPUT" | grep -qi "skip"; then
  PASS=$((PASS + 1))
  echo "  PASS: dry-run mentions skipping keeper references"
else
  FAIL=$((FAIL + 1))
  echo "  FAIL: dry-run does not mention skipping — output:"
  echo "$DRY_OUTPUT" | sed 's/^/    /'
fi

# Dry-run should mention rewriting collision references
TOTAL=$((TOTAL + 1))
if echo "$DRY_OUTPUT" | grep -qi "rewrite"; then
  PASS=$((PASS + 1))
  echo "  PASS: dry-run mentions rewriting collision references"
else
  FAIL=$((FAIL + 1))
  echo "  FAIL: dry-run does not mention rewriting"
fi

echo ""

# --- Summary ---
echo "=== Results: $PASS/$TOTAL passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
