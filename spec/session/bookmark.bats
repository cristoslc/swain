#!/usr/bin/env bats
# Bookmark management behavioral specs
#
# Bookmarks are the primary state-continuity mechanism across sessions.
# They must be atomic, overwrite silently, and handle both context notes
# and worktree tracking.

load '../support/setup'

setup_file() {
  export TEST_SANDBOX
  TEST_SANDBOX="$(create_test_sandbox)"
  scaffold_swain_project "$TEST_SANDBOX"
}

teardown_file() {
  destroy_test_sandbox "$TEST_SANDBOX"
}

setup() {
  cd "$TEST_SANDBOX" || fail "cannot cd to sandbox"
  # Reset session.json before each test
  echo '{}' > .agents/session.json
}

# ─── Context bookmarks ───

@test "sets a context bookmark with note" {
  run bash "$AGENTS_BIN/swain-bookmark.sh" "Working on SPEC-194"
  assert_success

  note=$(jq -r '.bookmark.note' .agents/session.json)
  [ "$note" = "Working on SPEC-194" ]
}

@test "bookmark includes ISO 8601 timestamp" {
  run bash "$AGENTS_BIN/swain-bookmark.sh" "test note"
  assert_success

  ts=$(jq -r '.bookmark.timestamp' .agents/session.json)
  # Should match YYYY-MM-DDTHH:MM:SSZ
  [[ "$ts" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$ ]]
}

@test "bookmark with --files includes file list" {
  run bash "$AGENTS_BIN/swain-bookmark.sh" "editing things" --files SKILL.md README.md
  assert_success

  count=$(jq '.bookmark.files | length' .agents/session.json)
  [ "$count" -eq 2 ]

  first=$(jq -r '.bookmark.files[0]' .agents/session.json)
  [ "$first" = "SKILL.md" ]
}

@test "setting bookmark overwrites previous bookmark silently" {
  bash "$AGENTS_BIN/swain-bookmark.sh" "first bookmark"
  bash "$AGENTS_BIN/swain-bookmark.sh" "second bookmark"

  note=$(jq -r '.bookmark.note' .agents/session.json)
  [ "$note" = "second bookmark" ]

  # Should only have one bookmark field, not an array
  count=$(jq '.bookmark | length' .agents/session.json)
  [ "$count" -ge 2 ]  # note + timestamp at minimum
}

@test "clearing bookmark removes the field" {
  bash "$AGENTS_BIN/swain-bookmark.sh" "temp note"
  run bash "$AGENTS_BIN/swain-bookmark.sh" --clear
  assert_success

  has_bookmark=$(jq 'has("bookmark")' .agents/session.json)
  [ "$has_bookmark" = "false" ]
}

@test "clearing non-existent bookmark succeeds silently" {
  run bash "$AGENTS_BIN/swain-bookmark.sh" --clear
  assert_success
}

@test "bookmark preserves other session.json fields" {
  echo '{"focus_lane": "VISION-001", "preferences": {"verbosity": "concise"}}' > .agents/session.json
  run bash "$AGENTS_BIN/swain-bookmark.sh" "test note"
  assert_success

  focus=$(jq -r '.focus_lane' .agents/session.json)
  [ "$focus" = "VISION-001" ]
}

# ─── Session.json migration ───

@test "creates session.json if missing" {
  rm -f .agents/session.json
  run bash "$AGENTS_BIN/swain-bookmark.sh" "new project"
  assert_success

  assert_file_exists .agents/session.json
  note=$(jq -r '.bookmark.note' .agents/session.json)
  [ "$note" = "new project" ]
}

# ─── Worktree bookmarks ───

@test "worktree add creates structured entry" {
  run bash "$AGENTS_BIN/swain-bookmark.sh" worktree add "/tmp/wt-test" "feature-branch"
  assert_success

  path=$(jq -r '.worktrees[0].path' .agents/session.json)
  branch=$(jq -r '.worktrees[0].branch' .agents/session.json)
  [ "$path" = "/tmp/wt-test" ]
  [ "$branch" = "feature-branch" ]
}

@test "worktree add includes timestamp" {
  run bash "$AGENTS_BIN/swain-bookmark.sh" worktree add "/tmp/wt-test" "feature-branch"
  assert_success

  ts=$(jq -r '.worktrees[0].last_active' .agents/session.json)
  [[ "$ts" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T ]]
}

@test "worktree add replaces existing entry for same path" {
  bash "$AGENTS_BIN/swain-bookmark.sh" worktree add "/tmp/wt-test" "old-branch"
  bash "$AGENTS_BIN/swain-bookmark.sh" worktree add "/tmp/wt-test" "new-branch"

  count=$(jq '.worktrees | length' .agents/session.json)
  [ "$count" -eq 1 ]

  branch=$(jq -r '.worktrees[0].branch' .agents/session.json)
  [ "$branch" = "new-branch" ]
}

@test "worktree add skips trunk path" {
  # Use git rev-parse to get the canonical path (handles macOS /tmp -> /private/var symlinks)
  local canonical_root
  canonical_root="$(git rev-parse --show-toplevel)"
  run bash "$AGENTS_BIN/swain-bookmark.sh" worktree add "$canonical_root" "trunk"
  assert_success
  assert_output --partial "Skipping trunk"
}

@test "worktree remove deletes entry by path" {
  bash "$AGENTS_BIN/swain-bookmark.sh" worktree add "/tmp/wt-a" "branch-a"
  bash "$AGENTS_BIN/swain-bookmark.sh" worktree add "/tmp/wt-b" "branch-b"
  run bash "$AGENTS_BIN/swain-bookmark.sh" worktree remove "/tmp/wt-a"
  assert_success

  count=$(jq '.worktrees | length' .agents/session.json)
  [ "$count" -eq 1 ]

  remaining=$(jq -r '.worktrees[0].path' .agents/session.json)
  [ "$remaining" = "/tmp/wt-b" ]
}

@test "worktree list shows all entries" {
  bash "$AGENTS_BIN/swain-bookmark.sh" worktree add "/tmp/wt-a" "branch-a"
  bash "$AGENTS_BIN/swain-bookmark.sh" worktree add "/tmp/wt-b" "branch-b"
  run bash "$AGENTS_BIN/swain-bookmark.sh" worktree list
  assert_success
  assert_output --partial "/tmp/wt-a"
  assert_output --partial "/tmp/wt-b"
}

@test "worktree list reports empty when no bookmarks" {
  run bash "$AGENTS_BIN/swain-bookmark.sh" worktree list
  assert_success
  assert_output --partial "No worktree bookmarks"
}

@test "worktree prune removes entries for nonexistent directories" {
  bash "$AGENTS_BIN/swain-bookmark.sh" worktree add "/nonexistent/path/abc" "dead-branch"
  run bash "$AGENTS_BIN/swain-bookmark.sh" worktree prune
  assert_success
  assert_output --partial "Pruned"

  count=$(jq '.worktrees | length' .agents/session.json)
  [ "$count" -eq 0 ]
}

@test "worktree prune keeps entries for existing directories" {
  local real_dir
  real_dir="$(mktemp -d)"
  bash "$AGENTS_BIN/swain-bookmark.sh" worktree add "$real_dir" "real-branch"
  run bash "$AGENTS_BIN/swain-bookmark.sh" worktree prune
  assert_success

  count=$(jq '.worktrees | length' .agents/session.json)
  [ "$count" -eq 1 ]
  rm -rf "$real_dir"
}

# ─── Error handling ───

@test "bookmark with no args prints usage and fails" {
  run bash "$AGENTS_BIN/swain-bookmark.sh"
  assert_failure
  assert_output --partial "Usage"
}

@test "worktree add with missing args fails" {
  run bash "$AGENTS_BIN/swain-bookmark.sh" worktree add
  assert_failure
  assert_output --partial "Error"
}
