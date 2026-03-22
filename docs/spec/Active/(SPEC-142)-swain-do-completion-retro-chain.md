---
title: "swain-do isn't consistently capturing retros on completion"
artifact: SPEC-142
track: implementable
status: Active
author: cristos
created: 2026-03-21
last-updated: 2026-03-21
type: bug
parent-epic: ""
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts: []
addresses: []
source-issue: "gh#86"
swain-do: required
---

# swain-do isn't consistently capturing retros on completion

## Problem Statement

swain-do's completion flow (SKILL.md line 182) says "When all tasks in the plan complete, or when the operator requests, call `ExitWorktree`" — but it doesn't specify the full completion chain. The documented chain in AGENTS.md requires: all tasks complete → swain-do invokes swain-design (transition SPEC) → swain-design checks parent EPIC → if EPIC reaches terminal state → swain-retro. Because swain-do lacks explicit plan completion detection and the handoff to swain-design, retros are never triggered.

## Reproduction Steps

1. Implement a SPEC via swain-do (plan creation, task execution)
2. Close all tasks in the plan
3. Observe that swain-do offers to exit the worktree but does NOT:
   - Invoke swain-design to transition the SPEC
   - Trigger the EPIC terminal transition → retro chain

## Severity

high

## Expected vs. Actual Behavior

**Expected:** When all tasks in a plan close, swain-do should: (1) detect plan completion, (2) invoke swain-design to transition the SPEC to its next phase, (3) offer to merge the worktree branch and clean up. The swain-design transition handles the downstream EPIC→retro chain.

**Actual:** swain-do just says "call ExitWorktree" with no plan completion detection, no SPEC transition handoff, and no merge/cleanup offer. The retro chain is never triggered.

## Acceptance Criteria

- Given all tasks in a plan are closed, when swain-do detects completion, then it must invoke swain-design to transition the SPEC forward
- Given swain-do detects plan completion, when the SPEC has a parent EPIC, then swain-design checks whether the EPIC should also transition (existing behavior once invoked)
- Given swain-do detects plan completion in a worktree, then it offers to merge the worktree branch and clean up after the SPEC transition
- Given the completion chain runs, when the EPIC reaches a terminal state, then swain-retro is invoked (existing behavior in swain-design once the chain fires)

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| All tasks closed → invoke swain-design | SKILL.md lines 199-214: Step 2 invokes swain-design for SPEC transition | PASS |
| Parent EPIC cascade check | SKILL.md lines 212-214: swain-design checks EPIC and invokes retro | PASS |
| Worktree → offer merge/cleanup | SKILL.md lines 216-227: Step 3 offers merge with ExitWorktree | PASS |
| EPIC terminal → swain-retro fires | SKILL.md line 214: retro chain documented via swain-design | PASS |

## Scope & Constraints

- The fix is in swain-do's SKILL.md — adding a "Plan completion" section between the worktree isolation preamble and the fallback section
- swain-design's phase-transitions.md already handles the EPIC→retro chain correctly; it just needs to be invoked
- No script changes needed — this is a skill instruction fix

## Implementation Approach

1. Add a "Plan completion and handoff" section to `skills/swain-do/SKILL.md` that:
   - Defines plan completion detection (all tasks under the plan epic are closed)
   - Specifies the handoff to swain-design for SPEC phase transition
   - Includes the merge/cleanup offer flow
   - References the existing retro chain in swain-design

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-21 | -- | Created from gh#86; bug — swain-do missing completion→retro chain |
