---
title: "swain-test skill"
artifact: SPEC-221
track: implementable
author: operator
created: 2026-03-31
last-updated: 2026-04-12
priority-weight: high
type: feature
status: Complete
parent-epic: EPIC-052
parent-initiative: ""
linked-artifacts:
  - EPIC-052
  - SPEC-220
depends-on-artifacts:
  - SPEC-220
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# swain-test skill

## Problem Statement

The `swain-test.sh` script handles deterministic integration testing but the smoke phase requires agent judgment — reading spec ACs, exercising components, dispatching subagents for behavioral verification. That orchestration logic needs a skill file so agents know exactly what to do.

## Desired Outcomes

A `skills/swain-test/SKILL.md` that agents can invoke to run the full two-phase gate. The skill handles: invoking the script, reading its output, executing smoke instructions, handling failures, and escalating when needed.

## External Behavior

**Skill file location:** `skills/swain-test/SKILL.md`

**Invocation trigger:** swain-sync and swain-release invoke this skill at their respective insertion points. Agents can also invoke it directly.

**Phase 1 — Integration tests (script-driven):**
1. Invoke `.agents/bin/swain-test.sh [--artifacts <IDs>]` with any artifact IDs the agent considers relevant to the current work.
2. If script exits 1 (integration failure): report the failure output, fix the issue, re-stage, and re-invoke the full gate from step 1. Do not proceed to Phase 2.
3. If script exits 0: read stdout and proceed to Phase 2.

**Phase 2 — Smoke tests (agent-executed):**
Execute the instructions from the script's stdout in this order:
1. **Spec-derived verification** — for each path in `## ARTIFACTS`, read the spec file and identify its acceptance criteria. Exercise each AC as a verification step. Report what was done and what was observed.
2. **Behavioral verification** — if `## SKILLS` shows `detected: true`, dispatch a subagent (haiku model recommended for cost) with a representative prompt for each changed skill. Verify the skill activates and produces expected output. Report: prompt used, activation confirmed (yes/no), output summary.
3. **Standing smoke tests** — execute each item in `## SMOKE` as an agentic task. Report result.
4. **Fallback** — if `## ARTIFACTS`, `## SKILLS`, and `## SMOKE` were all empty or skipped, follow the `## FALLBACK` instruction: describe what changed, stand up the affected component, exercise the happy path, report what was observed.

**Failure handling:**
- On any Phase 2 failure: fix the issue, re-stage, and re-invoke the full gate from Phase 1.
- After 2 failed full-gate attempts: escalate to operator. Report all failures with evidence: what was attempted, what failed, what was tried to fix it.
- **Operator escape hatch:** operator can override by stating the reason. Record in the verification log and commit message as `operator override: <reason>`.

**Gate output:**
After successful completion, the skill produces a structured evidence summary for use in evidence recording (SPEC-226).

## Acceptance Criteria

**Given** swain-sync invokes swain-test with `--artifacts SPEC-220`,
**When** integration tests pass and SPEC-220's ACs are verifiable,
**Then** the agent reads SPEC-220's file, exercises the ACs, and produces a written evidence summary.

**Given** the script detects skill file changes,
**When** Phase 2 runs,
**Then** the agent dispatches a subagent with a representative prompt and reports activation and output.

**Given** integration tests fail,
**When** the agent fixes the issue and re-invokes the gate,
**Then** the gate re-runs from Phase 1 (not from Phase 2).

**Given** the gate fails twice in a row,
**When** the second failure is detected,
**Then** the agent escalates to the operator with full failure evidence and does not attempt a third fix.

**Given** the operator states an override reason,
**When** the gate is bypassed,
**Then** the override reason is captured in the evidence summary.

**Given** no test command is detected and `## ARTIFACTS`, `## SKILLS`, `## SMOKE` are all empty,
**When** the gate runs,
**Then** the agent follows `## FALLBACK` and produces generic evidence (what changed, what was exercised, what was observed).

## Scope & Constraints

- Phase 2 is non-deterministic and token-expensive. It only runs after Phase 1 passes.
- The skill does not modify spec files or artifact indexes — it only reads and produces evidence.
- Behavioral verification model choice is the agent's; haiku is recommended for cost, not required.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | — | Initial creation |
| Complete | 2026-04-12 | — | SKILL.md implemented; 34/34 BDD tests pass; smoke test confirms skill activates; readability 8.5 |
