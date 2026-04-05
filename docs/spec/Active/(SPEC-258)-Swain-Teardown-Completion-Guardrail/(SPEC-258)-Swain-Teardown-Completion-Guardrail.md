---
title: "swain-teardown Completion Guardrail"
artifact: SPEC-258
track: implementable
status: Active
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
priority-weight: high
type: feature
parent-epic: EPIC-059
parent-initiative: ""
linked-artifacts:
  - DESIGN-018
  - SPEC-257
depends-on-artifacts:
  - SPEC-257
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# swain-teardown Completion Guardrail

## Problem Statement

Teardown checks for orphan worktrees, dirty state, and ticket sync — but not whether BDD, smoke, and retro ran. If a session crashed or the user skipped the chain, teardown syncs the work with no warning.

## Desired Outcomes

Teardown becomes the safety net. If steps were missed, it runs them — not just warns. The user never syncs work that was not checked.

## External Behavior

**Trigger:** Teardown runs (session close, manual call, or pre-sync check).

**New check before sync:**

1. Look for `.agents/completion-state.json`
2. If found, find steps that are `pending` or `failed`
3. If any exist, show them and run each in order (BDD → smoke → retro)
4. If all steps are `passed` or `skipped`, go to sync
5. If the file is missing and the worktree has closed tasks, create it and run all steps

**On failure:** Ask "retry, skip, or abort?" Abort halts teardown with no sync.

**Force bypass:** "teardown --force" marks all pending steps `skipped` with "forced bypass" and syncs.

## Acceptance Criteria

**AC-1:** If `bdd_tests` is `pending`, teardown runs BDD before sync.

**AC-2:** If `retro` is `pending` and other steps passed, teardown runs retro before sync.

**AC-3:** If the state file is missing and tasks are closed, teardown creates it and runs all steps.

**AC-4:** If all steps are `passed`, teardown goes straight to sync.

**AC-5:** On step failure, "skip" marks the step `skipped` and moves on.

**AC-6:** "teardown --force" marks all pending steps `skipped` with "forced bypass" and syncs.

**AC-7:** If `smoke_test` is `failed`, teardown re-runs smoke (not BDD, which passed).

**AC-8:** Steps that swain-do marked `skipped` stay skipped — teardown does not re-run them.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Changes swain-teardown's SKILL.md — adds a step before swain-sync
- All existing checks stay (orphan worktrees, dirty state, ticket sync)
- Order: orphan check → dirty state → **completion pipeline** → ticket sync → sync
- If swain-test is not ready, BDD/smoke steps warn instead of blocking
- `--force` must be explicit and recorded — no silent skips

## Implementation Approach

1. Add state file check to teardown's pre-sync path
2. Add step runner that picks up where swain-do left off
3. Add retry/skip/abort for failures
4. Add `--force` bypass
5. Place it between dirty-state check and ticket sync

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-04 | 683a04e6 | Initial creation — operator requested |
