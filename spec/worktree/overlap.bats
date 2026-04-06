#!/usr/bin/env bats
# Worktree overlap detection behavioral specs (SPEC-195)
#
# Before creating a new worktree, swain checks for existing worktrees
# that match the same spec or context. This prevents duplicating work.

load '../support/setup'

setup_file() {
  export TEST_SANDBOX
  TEST_SANDBOX="$(create_test_sandbox)"
}

teardown_file() {
  destroy_test_sandbox "$TEST_SANDBOX"
}

setup() {
  cd "$TEST_SANDBOX" || fail "cannot cd to sandbox"
}

# ─── No-match behavior ───

@test "returns found=false when no worktrees match" {
  run bash "$AGENTS_BIN/swain-worktree-overlap.sh" "nonexistent-spec"
  assert_success

  found=$(echo "$output" | jq -r '.found')
  [ "$found" = "false" ]
}

@test "returns empty worktrees array on no match" {
  run bash "$AGENTS_BIN/swain-worktree-overlap.sh" "nonexistent-spec"
  assert_success

  count=$(echo "$output" | jq '.worktrees | length')
  [ "$count" -eq 0 ]
}

# ─── Input validation ───

@test "returns error when no search term provided" {
  run bash "$AGENTS_BIN/swain-worktree-overlap.sh"
  assert_failure

  echo "$output" | jq -e '.error' >/dev/null
}

# ─── JSON output contract ───

@test "output is always valid JSON" {
  run bash "$AGENTS_BIN/swain-worktree-overlap.sh" "anything"
  # Even on failure, output should be JSON
  echo "$output" | jq . >/dev/null 2>&1
}

@test "output always contains found and worktrees fields" {
  run bash "$AGENTS_BIN/swain-worktree-overlap.sh" "test"
  assert_success

  echo "$output" | jq -e 'has("found")' >/dev/null
  echo "$output" | jq -e 'has("worktrees")' >/dev/null
}

# ─── Case insensitive matching ───

@test "matches are case-insensitive" {
  # Create a worktree with uppercase in branch name
  git worktree add -b "worktree-SPEC-194-test" ".wt-test-upper" 2>/dev/null || skip "cannot create worktree in sandbox"
  run bash "$AGENTS_BIN/swain-worktree-overlap.sh" "spec-194"

  found=$(echo "$output" | jq -r '.found')
  [ "$found" = "true" ]

  git worktree remove ".wt-test-upper" --force 2>/dev/null || true
}

# ─── Match detection with real worktrees ───

@test "detects existing worktree matching search term" {
  git worktree add -b "worktree-spec-200-fast" ".wt-test-match" 2>/dev/null || skip "cannot create worktree in sandbox"
  run bash "$AGENTS_BIN/swain-worktree-overlap.sh" "spec-200"
  assert_success

  found=$(echo "$output" | jq -r '.found')
  [ "$found" = "true" ]

  count=$(echo "$output" | jq '.worktrees | length')
  [ "$count" -ge 1 ]

  git worktree remove ".wt-test-match" --force 2>/dev/null || true
}

@test "matched worktree entry includes path and branch" {
  git worktree add -b "worktree-spec-201-test" ".wt-test-fields" 2>/dev/null || skip "cannot create worktree in sandbox"
  run bash "$AGENTS_BIN/swain-worktree-overlap.sh" "spec-201"
  assert_success

  echo "$output" | jq -e '.worktrees[0].path' >/dev/null
  echo "$output" | jq -e '.worktrees[0].branch' >/dev/null

  git worktree remove ".wt-test-fields" --force 2>/dev/null || true
}
