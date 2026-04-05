#!/usr/bin/env bats
# Focus lane behavioral specs
#
# Focus lanes scope status recommendations to a vision or initiative.
# They persist in session.json and survive session boundaries.

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
  echo '{}' > .agents/session.json
}

# ─── Setting focus ───

@test "set focus writes to session.json" {
  run bash "$AGENTS_BIN/swain-focus.sh" set VISION-001
  assert_success

  focus=$(jq -r '.focus_lane' .agents/session.json)
  [ "$focus" = "VISION-001" ]
}

@test "set focus outputs confirmation" {
  run bash "$AGENTS_BIN/swain-focus.sh" set INITIATIVE-002
  assert_success
  assert_output --partial "INITIATIVE-002"
}

@test "set focus overwrites previous focus" {
  bash "$AGENTS_BIN/swain-focus.sh" set VISION-001
  bash "$AGENTS_BIN/swain-focus.sh" set VISION-002

  focus=$(jq -r '.focus_lane' .agents/session.json)
  [ "$focus" = "VISION-002" ]
}

@test "set focus preserves other session.json fields" {
  echo '{"bookmark": {"note": "test"}, "preferences": {}}' > .agents/session.json
  run bash "$AGENTS_BIN/swain-focus.sh" set VISION-001
  assert_success

  note=$(jq -r '.bookmark.note' .agents/session.json)
  [ "$note" = "test" ]
}

# ─── Clearing focus ───

@test "clear focus removes focus_lane field" {
  bash "$AGENTS_BIN/swain-focus.sh" set VISION-001
  run bash "$AGENTS_BIN/swain-focus.sh" clear
  assert_success

  has_focus=$(jq 'has("focus_lane")' .agents/session.json)
  [ "$has_focus" = "false" ]
}

@test "clear focus on empty session succeeds" {
  run bash "$AGENTS_BIN/swain-focus.sh" clear
  assert_success
}

# ─── Showing focus ───

@test "shows current focus when set" {
  bash "$AGENTS_BIN/swain-focus.sh" set VISION-001
  run bash "$AGENTS_BIN/swain-focus.sh"
  assert_success
  assert_output --partial "VISION-001"
}

@test "shows 'none' when no focus is set" {
  run bash "$AGENTS_BIN/swain-focus.sh"
  assert_success
  assert_output --partial "none"
}

# ─── Error handling ───

@test "set without ID fails" {
  run bash "$AGENTS_BIN/swain-focus.sh" set
  assert_failure
  assert_output --partial "Usage"
}

@test "creates session.json if missing" {
  rm -f .agents/session.json
  run bash "$AGENTS_BIN/swain-focus.sh" set VISION-001
  assert_success

  assert_file_exists .agents/session.json
  focus=$(jq -r '.focus_lane' .agents/session.json)
  [ "$focus" = "VISION-001" ]
}
