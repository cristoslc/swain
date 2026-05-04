#!/usr/bin/env bats
# swain-test SKILL.md structural specs (SPEC-221)
#
# The swain-test skill orchestrates the two-phase test gate:
# Phase 1 is deterministic (script-driven); Phase 2 is agentic.
# These tests verify the SKILL.md file encodes the external
# behavior required by SPEC-221 so regressions in the orchestration
# doc are caught before they reach trunk.

load '../support/setup'

SKILL_FILE="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)/skills/swain-test/SKILL.md"

# ─── File presence and frontmatter ───

@test "SKILL.md exists at skills/swain-test/SKILL.md" {
  [ -f "$SKILL_FILE" ]
}

@test "SKILL.md has YAML frontmatter with name, description, version" {
  run head -10 "$SKILL_FILE"
  assert_success
  assert_output --partial "name: swain-test"
  assert_output --partial "description:"
  assert_output --partial "version:"
}

@test "frontmatter description mentions test gate role" {
  run head -10 "$SKILL_FILE"
  assert_success
  assert_output --partial "test gate"
}

# ─── Phase 1 (integration, script-driven) ───

@test "instructs agent to invoke swain-test.sh" {
  run cat "$SKILL_FILE"
  assert_success
  assert_output --partial "swain-test.sh"
}

@test "documents --artifacts flag usage" {
  run cat "$SKILL_FILE"
  assert_success
  assert_output --partial "--artifacts"
}

@test "documents Phase 1 exit-code handling (0 vs 1)" {
  run cat "$SKILL_FILE"
  assert_success
  assert_output --partial "exit"
}

@test "instructs to NOT proceed to Phase 2 when Phase 1 fails" {
  run grep -iE "do not proceed|not proceed|skip phase 2|stop" "$SKILL_FILE"
  assert_success
}

# ─── Phase 2 (smoke, agent-executed) ───

@test "documents Phase 2 step for ARTIFACTS (spec AC verification)" {
  run cat "$SKILL_FILE"
  assert_success
  assert_output --partial "## ARTIFACTS"
  assert_output --partial "acceptance criteria"
}

@test "documents Phase 2 step for SKILLS (subagent dispatch)" {
  run cat "$SKILL_FILE"
  assert_success
  assert_output --partial "## SKILLS"
  assert_output --partial "subagent"
}

@test "recommends haiku model for behavioral verification" {
  run grep -iE "haiku" "$SKILL_FILE"
  assert_success
}

@test "documents Phase 2 step for SMOKE (standing smoke tests)" {
  run cat "$SKILL_FILE"
  assert_success
  assert_output --partial "## SMOKE"
}

@test "documents FALLBACK handling when all other sections empty" {
  run cat "$SKILL_FILE"
  assert_success
  assert_output --partial "## FALLBACK"
}

# ─── Failure handling ───

@test "documents retry from Phase 1 after any failure" {
  run grep -iE "re-invoke|re-run from phase 1|restart from phase 1|re-stage" "$SKILL_FILE"
  assert_success
}

@test "documents 2-strike escalation rule" {
  run grep -iE "two failed|2 failed|twice|two attempts|second failure" "$SKILL_FILE"
  assert_success
}

@test "documents operator override escape hatch" {
  run grep -iE "operator override" "$SKILL_FILE"
  assert_success
}

# ─── Evidence summary ───

@test "documents production of evidence summary for downstream consumption" {
  run grep -iE "evidence" "$SKILL_FILE"
  assert_success
}

# ─── Invocation context ───

@test "notes swain-sync and swain-release invoke this skill" {
  run cat "$SKILL_FILE"
  assert_success
  assert_output --partial "swain-sync"
  assert_output --partial "swain-release"
}
