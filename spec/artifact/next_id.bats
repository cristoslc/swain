#!/usr/bin/env bats
# Artifact ID generation behavioral specs (SPEC-193)
#
# Artifact IDs must be globally unique across all branches.
# The next-artifact-id script scans all local branches and the
# working tree to prevent collisions in parallel worktree workflows.

load '../support/setup'

# Each test gets a fresh sandbox because artifact tests accumulate state
setup() {
  export TEST_SANDBOX
  TEST_SANDBOX="$(create_test_sandbox)"
  scaffold_swain_project "$TEST_SANDBOX"
  cd "$TEST_SANDBOX" || fail "cannot cd to sandbox"
}

teardown() {
  destroy_test_sandbox "$TEST_SANDBOX"
}

# ─── Basic contract ───

@test "returns a positive integer" {
  run bash "$AGENTS_BIN/next-artifact-id.sh" SPEC
  assert_success
  [[ "$output" =~ ^[0-9]+$ ]]
  [ "$output" -gt 0 ]
}

@test "returns 1 when no artifacts exist" {
  run bash "$AGENTS_BIN/next-artifact-id.sh" SPEC
  assert_success
  [ "$output" -eq 1 ]
}

# ─── Sequential allocation ───

@test "returns N+1 when SPEC-N exists on disk" {
  create_artifact "." "spec" "SPEC-005" "Test Spec"
  git add -A && git commit -q -m "add spec"

  run bash "$AGENTS_BIN/next-artifact-id.sh" SPEC
  assert_success
  [ "$output" -eq 6 ]
}

@test "finds highest ID across lifecycle phases" {
  mkdir -p docs/spec/Complete
  cat > docs/spec/Complete/SPEC-010.md <<'EOF'
---
id: SPEC-010
title: Old spec
status: Complete
---
EOF
  create_artifact "." "spec" "SPEC-003" "Active spec"
  git add -A && git commit -q -m "add specs in phases"

  run bash "$AGENTS_BIN/next-artifact-id.sh" SPEC
  assert_success
  [ "$output" -eq 11 ]
}

# ─── Type isolation ───

@test "SPEC and EPIC IDs are independent" {
  create_artifact "." "spec" "SPEC-020" "High Spec"
  create_artifact "." "epic" "EPIC-005" "Low Epic"
  git add -A && git commit -q -m "add mixed artifacts"

  run bash "$AGENTS_BIN/next-artifact-id.sh" SPEC
  assert_success
  [ "$output" -eq 21 ]

  run bash "$AGENTS_BIN/next-artifact-id.sh" EPIC
  assert_success
  [ "$output" -eq 6 ]
}

# ─── All supported prefixes ───

@test "supports all artifact type prefixes" {
  local prefixes=(SPEC EPIC INITIATIVE VISION SPIKE ADR PERSONA RUNBOOK DESIGN JOURNEY TRAIN)
  for prefix in "${prefixes[@]}"; do
    run bash "$AGENTS_BIN/next-artifact-id.sh" "$prefix"
    assert_success
    [[ "$output" =~ ^[0-9]+$ ]]
  done
}

# ─── Cross-branch scanning ───

@test "detects artifacts on other branches" {
  create_artifact "." "spec" "SPEC-015" "Branch artifact"
  git add -A && git commit -q -m "artifact on feature branch"

  # Create artifact on a different branch
  git checkout -b feature-branch
  create_artifact "." "spec" "SPEC-025" "Feature artifact"
  git add -A && git commit -q -m "higher artifact on feature"
  git checkout -

  run bash "$AGENTS_BIN/next-artifact-id.sh" SPEC
  assert_success
  [ "$output" -eq 26 ]
}

@test "detects uncommitted artifacts in working tree" {
  create_artifact "." "spec" "SPEC-030" "Uncommitted spec"
  # Deliberately NOT committing

  run bash "$AGENTS_BIN/next-artifact-id.sh" SPEC
  assert_success
  [ "$output" -eq 31 ]
}

# ─── Error handling ───

@test "fails with usage when no prefix given" {
  run bash "$AGENTS_BIN/next-artifact-id.sh"
  assert_failure
  assert_output --partial "Usage"
}

# ─── Zero-padded IDs ───

@test "handles zero-padded artifact numbers (SPEC-007)" {
  create_artifact "." "spec" "SPEC-007" "Padded spec"
  git add -A && git commit -q -m "padded spec"

  run bash "$AGENTS_BIN/next-artifact-id.sh" SPEC
  assert_success
  [ "$output" -eq 8 ]
}
