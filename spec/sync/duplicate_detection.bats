#!/usr/bin/env bats
# Artifact duplicate number detection behavioral specs (SPEC-158)
#
# Before committing, swain-sync checks for duplicate artifact numbers.
# Same number + same title across phases = transition in progress (OK).
# Same number + different titles = real collision (BLOCK).

load '../support/setup'

setup() {
  export TEST_SANDBOX
  TEST_SANDBOX="$(create_test_sandbox)"
  cd "$TEST_SANDBOX" || fail "cannot cd to sandbox"
  mkdir -p docs/spec/Active docs/spec/Complete
}

teardown() {
  destroy_test_sandbox "$TEST_SANDBOX"
}

# ─── No duplicates ───

@test "exits 0 with no output when no duplicates exist" {
  mkdir -p "docs/spec/Active/(SPEC-001)-first-spec"
  mkdir -p "docs/spec/Active/(SPEC-002)-second-spec"
  run bash "$AGENTS_BIN/detect-duplicate-numbers.sh" SPEC
  assert_success
  [ -z "$output" ]
}

@test "exits 0 when no artifact directories exist" {
  run bash "$AGENTS_BIN/detect-duplicate-numbers.sh" SPEC
  assert_success
}

# ─── Phase transition (same title) ───

@test "same number + same title across phases is NOT a duplicate" {
  mkdir -p "docs/spec/Active/(SPEC-001)-my-feature"
  mkdir -p "docs/spec/Complete/(SPEC-001)-my-feature"
  run bash "$AGENTS_BIN/detect-duplicate-numbers.sh" SPEC
  assert_success
  [ -z "$output" ]
}

# ─── Real collision (different titles) ───

@test "same number + different titles IS a duplicate" {
  mkdir -p "docs/spec/Active/(SPEC-001)-first-feature"
  mkdir -p "docs/spec/Active/(SPEC-001)-second-feature"
  run bash "$AGENTS_BIN/detect-duplicate-numbers.sh" SPEC
  assert_failure
  assert_output --partial "DUPLICATE SPEC-001"
}

@test "duplicate report includes paths" {
  mkdir -p "docs/spec/Active/(SPEC-005)-alpha"
  mkdir -p "docs/spec/Complete/(SPEC-005)-beta"
  run bash "$AGENTS_BIN/detect-duplicate-numbers.sh" SPEC
  assert_failure
  assert_output --partial "docs/spec/"
}

# ─── Type filtering ───

@test "only scans requested type" {
  mkdir -p "docs/spec/Active/(SPEC-001)-alpha"
  mkdir -p "docs/spec/Active/(SPEC-001)-beta"
  mkdir -p "docs/epic/Active/(EPIC-001)-gamma"
  mkdir -p "docs/epic/Active/(EPIC-001)-delta"

  # Only check EPIC — should find that dup
  run bash "$AGENTS_BIN/detect-duplicate-numbers.sh" EPIC
  assert_failure
  assert_output --partial "EPIC"

  # SPEC should also fail independently
  run bash "$AGENTS_BIN/detect-duplicate-numbers.sh" SPEC
  assert_failure
  assert_output --partial "SPEC"
}

@test "scans all types when no args given" {
  mkdir -p "docs/spec/Active/(SPEC-001)-alpha"
  mkdir -p "docs/spec/Active/(SPEC-001)-beta"
  run bash "$AGENTS_BIN/detect-duplicate-numbers.sh"
  assert_failure
  assert_output --partial "DUPLICATE"
}

# ─── Error handling ───

@test "rejects unrecognized type" {
  run bash "$AGENTS_BIN/detect-duplicate-numbers.sh" BOGUS
  assert_failure
  assert_output --partial "unrecognized"
}

@test "case-insensitive type argument" {
  mkdir -p "docs/spec/Active/(SPEC-001)-alpha"
  run bash "$AGENTS_BIN/detect-duplicate-numbers.sh" spec
  assert_success
}
