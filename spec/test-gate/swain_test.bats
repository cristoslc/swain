#!/usr/bin/env bats
# swain-test.sh behavioral specs (SPEC-220)
#
# The test gate script detects project test commands, runs them,
# and emits structured output for agent consumption.

load '../support/setup'

setup() {
  export TEST_SANDBOX
  TEST_SANDBOX="$(create_test_sandbox)"
  scaffold_swain_project "$TEST_SANDBOX"
  cd "$TEST_SANDBOX" || fail "cannot cd to sandbox"
}

teardown() {
  destroy_test_sandbox "$TEST_SANDBOX"
}

# ─── Test command detection ───

@test "detects npm test from package.json" {
  echo '{"name":"test","scripts":{"test":"echo tests-passed"}}' > package.json
  git add -A && git commit -q -m "add package.json"
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_success
  assert_output --partial "command: npm test"
  assert_output --partial "status: PASS"
}

@test "uses testing.json command over convention detection" {
  # Both package.json and testing.json present — testing.json wins
  echo '{"name":"test","scripts":{"test":"echo wrong"}}' > package.json
  mkdir -p .agents
  echo '{"integration":{"command":"echo custom-pass","timeout":300}}' > .agents/testing.json
  git add -A && git commit -q -m "add both"
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_success
  assert_output --partial "command: echo custom-pass"
  assert_output --partial "status: PASS"
}

@test "detects make test from Makefile with test target" {
  printf 'test:\n\t@echo make-tests-passed\n' > Makefile
  git add -A && git commit -q -m "add Makefile"
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_success
  assert_output --partial "command: make test"
  assert_output --partial "status: PASS"
}

@test "skips integration when no test command detected" {
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_success
  assert_output --partial "status: SKIP"
}

# ─── Exit codes ───

@test "exits 0 when tests pass" {
  echo '{"name":"test","scripts":{"test":"echo ok"}}' > package.json
  git add -A && git commit -q -m "add"
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_success
}

@test "exits 1 when tests fail" {
  echo '{"name":"test","scripts":{"test":"exit 1"}}' > package.json
  git add -A && git commit -q -m "add"
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_failure
  assert_output --partial "status: FAIL"
}

@test "exits 0 when no tests detected (skip is not failure)" {
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_success
}

# ─── Structured output sections ───

@test "always emits ## INTEGRATION section" {
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_success
  assert_output --partial "## INTEGRATION"
}

@test "FAIL output includes last lines of test output" {
  echo '{"name":"test","scripts":{"test":"echo failure-details && exit 1"}}' > package.json
  git add -A && git commit -q -m "add"
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_failure
  assert_output --partial "failure-details"
}

@test "emits ## FALLBACK when no artifacts, skills, or smoke detected" {
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_success
  assert_output --partial "## FALLBACK"
  assert_output --partial "exercise the happy path"
}

# ─── Artifact resolution ───

@test "--artifacts flag resolves spec paths in output" {
  create_artifact "." "spec" "SPEC-215" "Consumer Harness"
  git add -A && git commit -q -m "add spec"
  run bash "$AGENTS_BIN/swain-test.sh" --artifacts SPEC-215
  assert_success
  assert_output --partial "## ARTIFACTS"
  assert_output --partial "SPEC-215"
}

@test "--artifacts with unknown ID still succeeds" {
  run bash "$AGENTS_BIN/swain-test.sh" --artifacts SPEC-999
  assert_success
  # Should not crash, just skip that artifact
}

# ─── Skill change detection ───

@test "detects changed files under skills/" {
  mkdir -p skills/swain-test
  echo "# changed" > skills/swain-test/SKILL.md
  git add -A && git commit -q -m "change skill"
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_success
  assert_output --partial "## SKILLS"
  assert_output --partial "detected: true"
}

@test "no SKILLS section when no skill files changed" {
  echo "unrelated" > somefile.txt
  git add -A && git commit -q -m "unrelated change"
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_success
  # Should NOT contain ## SKILLS
  ! echo "$output" | grep -q "## SKILLS"
}

# ─── Smoke section ───

@test "emits SMOKE section from testing.json smoke entries" {
  mkdir -p .agents
  echo '{"smoke":["check health endpoint","verify login flow"]}' > .agents/testing.json
  git add -A && git commit -q -m "add smoke"
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_success
  assert_output --partial "## SMOKE"
  assert_output --partial "check health endpoint"
  assert_output --partial "verify login flow"
}

@test "no SMOKE section when testing.json has no smoke entries" {
  mkdir -p .agents
  echo '{"integration":{"command":"echo ok"}}' > .agents/testing.json
  git add -A && git commit -q -m "add testing.json"
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_success
  ! echo "$output" | grep -q "## SMOKE"
}

# ─── Integration duration ───

@test "reports duration in output" {
  echo '{"name":"test","scripts":{"test":"echo ok"}}' > package.json
  git add -A && git commit -q -m "add"
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_success
  assert_output --partial "duration:"
}
