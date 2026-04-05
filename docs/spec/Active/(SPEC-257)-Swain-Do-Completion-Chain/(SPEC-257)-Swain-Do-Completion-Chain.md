---
title: "swain-do Completion Chain"
artifact: SPEC-257
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
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# swain-do Completion Chain

## Problem Statement

When swain-do closes all tasks for a SPEC, it moves the phase and offers a merge — but skips BDD, smoke, and retro. The user runs those by hand each time.

## Desired Outcomes

"All tasks done" means the gates and retro run too. The user never types the BDD → smoke → retro steps again. It stops only on failure or when it needs input.

## External Behavior

**Trigger:** All tasks for a SPEC close (`OPEN_COUNT == 0`).

**Steps:**
1. Create `.agents/completion-state.json` per [DESIGN-018](../../design/Active/(DESIGN-018)-Completion-Pipeline-State-Tracking/(DESIGN-018)-Completion-Pipeline-State-Tracking.md)
2. Run swain-test for BDD, update `bdd_tests`
3. If BDD passes, run smoke test, update `smoke_test`
4. If smoke passes, run swain-retro, update `retro`
5. Move SPEC to next phase (gated on the above)
6. Offer merge

**On failure:** Stop and report. The user says "retry" or "skip."

**On skip:** BDD and smoke can be skipped. Retro cannot.

## Acceptance Criteria

**AC-1:** On plan done, swain-do creates `completion-state.json` with all steps `pending`.

**AC-2:** It runs swain-test for BDD and sets the step to `passed` or `failed`.

**AC-3:** After BDD passes, it runs smoke and updates the step.

**AC-4:** After smoke passes, it runs swain-retro and updates the step.

**AC-5:** On failure, "retry" resumes from the failed step, not from the start.

**AC-6:** "skip BDD" or "skip smoke" sets the step to `skipped` and moves on.

**AC-7:** "skip retro" is refused — retro always runs.

**AC-8:** Once all steps are `passed` or `skipped`, SPEC moves to next phase and merge is offered.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Changes swain-do's SKILL.md — adds the chain to the plan completion handler
- SPEC transition and merge-offer still happen after the pipeline
- If swain-test is not yet ready, BDD and smoke steps warn instead of blocking
- The chain only fires on SPEC plan completion, not single task closes

## Implementation Approach

1. Add state file creation to plan done handler
2. Add step-by-step run with state writes per DESIGN-018
3. Add skip handling for user overrides
4. Add resume from failed step
5. Gate SPEC phase move on all steps done

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-04 | 683a04e6 | Initial creation — operator requested |
