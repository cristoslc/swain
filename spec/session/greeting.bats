#!/usr/bin/env bats
# Session greeting behavioral specs (SPEC-194)
#
# The greeting script is the first thing that runs in every swain session.
# It must be fast, produce valid JSON, and correctly detect project state.

load '../support/setup'

# Each test gets a fresh sandbox — greeting tests modify state
# (removing .agents, adding lock files) that would pollute siblings.
setup() {
  export TEST_SANDBOX
  TEST_SANDBOX="$(create_test_sandbox)"
  scaffold_swain_project "$TEST_SANDBOX"
  cd "$TEST_SANDBOX" || fail "cannot cd to sandbox"
}

teardown() {
  destroy_test_sandbox "$TEST_SANDBOX"
}

# ─── JSON output contract ───

@test "greeting --json emits valid JSON" {
  run bash "$AGENTS_BIN/swain-session-greeting.sh" --json
  assert_success
  # Must be parseable by jq
  echo "$output" | jq . >/dev/null 2>&1
  assert_success
}

@test "greeting --json includes all required fields" {
  run bash "$AGENTS_BIN/swain-session-greeting.sh" --json
  assert_success

  echo "$output" | jq -e '.greeting' >/dev/null
  echo "$output" | jq -e '.branch' >/dev/null
  echo "$output" | jq -e 'has("dirty")' >/dev/null
  echo "$output" | jq -e 'has("isolated")' >/dev/null
  echo "$output" | jq -e 'has("bookmark")' >/dev/null
  echo "$output" | jq -e 'has("warnings")' >/dev/null
}

@test "greeting field is always true" {
  run bash "$AGENTS_BIN/swain-session-greeting.sh" --json
  assert_success

  result=$(echo "$output" | jq -r '.greeting')
  [ "$result" = "true" ]
}

@test "warnings is always an array" {
  run bash "$AGENTS_BIN/swain-session-greeting.sh" --json
  assert_success

  type=$(echo "$output" | jq -r '.warnings | type')
  [ "$type" = "array" ]
}

# ─── Dirty state detection ───

@test "reports dirty=true on nominally clean tree (bootstrap writes session.json)" {
  # The greeting/bootstrap script writes to .agents/session.json,
  # which means a freshly-scaffolded tree is always dirty AFTER
  # the greeting runs. This is expected — the greeting reports the
  # state it observes, which includes its own bootstrap writes.
  run bash "$AGENTS_BIN/swain-session-greeting.sh" --json
  assert_success

  dirty=$(echo "$output" | jq -r '.dirty')
  [ "$dirty" = "true" ]
}

@test "reports dirty=true when files are modified" {
  echo "changed" >> README.md
  run bash "$AGENTS_BIN/swain-session-greeting.sh" --json
  assert_success

  dirty=$(echo "$output" | jq -r '.dirty')
  [ "$dirty" = "true" ]

  # Restore
  git checkout -- README.md
}

@test "reports dirty=true when untracked files exist" {
  touch untracked-file.txt
  run bash "$AGENTS_BIN/swain-session-greeting.sh" --json
  assert_success

  dirty=$(echo "$output" | jq -r '.dirty')
  [ "$dirty" = "true" ]

  rm -f untracked-file.txt
}

# ─── Branch detection ───

@test "reports current branch name" {
  run bash "$AGENTS_BIN/swain-session-greeting.sh" --json
  assert_success

  branch=$(echo "$output" | jq -r '.branch')
  expected=$(git rev-parse --abbrev-ref HEAD)
  [ "$branch" = "$expected" ]
}

# ─── Bookmark passthrough ───

@test "reports null bookmark when no bookmark is set" {
  echo '{}' > .agents/session.json
  run bash "$AGENTS_BIN/swain-session-greeting.sh" --json
  assert_success

  bookmark=$(echo "$output" | jq -r '.bookmark')
  [ "$bookmark" = "null" ]
}

# ─── Warning: stale git lock ───

@test "warns about stale git index.lock" {
  touch .git/index.lock
  run bash "$AGENTS_BIN/swain-session-greeting.sh" --json
  assert_success

  echo "$output" | jq -e '.warnings[] | select(contains("index.lock"))' >/dev/null
  rm -f .git/index.lock
}

# ─── Warning: missing .agents directory ───

@test "creates missing .agents directory and warns" {
  rm -rf .agents
  run bash "$AGENTS_BIN/swain-session-greeting.sh" --json
  assert_success

  assert_dir_exists .agents
  echo "$output" | jq -e '.warnings[] | select(contains(".agents"))' >/dev/null
}

# ─── Human-readable output ───

@test "human-readable output includes branch name" {
  run bash "$AGENTS_BIN/swain-session-greeting.sh"
  assert_success
  assert_output --partial "Branch:"
}

@test "human-readable output shows [dirty] after bootstrap (session.json written)" {
  run bash "$AGENTS_BIN/swain-session-greeting.sh"
  assert_success
  assert_output --partial "[dirty]"
}

@test "human-readable output shows [dirty] for modified tree" {
  echo "changed" >> README.md
  run bash "$AGENTS_BIN/swain-session-greeting.sh"
  assert_success
  assert_output --partial "[dirty]"
  git checkout -- README.md
}
