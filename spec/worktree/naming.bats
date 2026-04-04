#!/usr/bin/env bats
# Worktree naming behavioral specs
#
# Worktree names must be unique, predictable in format, and safe for
# use as git branch names.

load '../support/setup'

# ─── Format contract ───

@test "generates name in format: context-YYYYMMDD-HHmmss-XXXX" {
  run bash "$AGENTS_BIN/swain-worktree-name.sh" "test-context"
  assert_success

  # Match: test-context-YYYYMMDD-HHMMSS-XXXX (4 hex chars)
  [[ "$output" =~ ^test-context-[0-9]{8}-[0-9]{6}-[0-9a-f]{4}$ ]]
}

@test "defaults context to 'session' when no argument given" {
  run bash "$AGENTS_BIN/swain-worktree-name.sh"
  assert_success
  [[ "$output" =~ ^session-[0-9]{8}-[0-9]{6}-[0-9a-f]{4}$ ]]
}

@test "custom context prefix is used" {
  run bash "$AGENTS_BIN/swain-worktree-name.sh" "spec-194"
  assert_success
  [[ "$output" =~ ^spec-194- ]]
}

# ─── Uniqueness ───

@test "two consecutive calls produce different names" {
  name1=$(bash "$AGENTS_BIN/swain-worktree-name.sh" "uniq")
  name2=$(bash "$AGENTS_BIN/swain-worktree-name.sh" "uniq")

  [ "$name1" != "$name2" ]
}

# ─── Git branch safety ───

@test "output is safe for use as a git branch name" {
  run bash "$AGENTS_BIN/swain-worktree-name.sh" "my-feature"
  assert_success

  # No spaces, no special chars that git dislikes
  [[ ! "$output" =~ [[:space:]] ]]
  [[ ! "$output" =~ \.\. ]]
  [[ ! "$output" =~ [~^:?*\[] ]]
}
