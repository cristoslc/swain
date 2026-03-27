---
title: "TDD Coverage Self-Critique Gate"
artifact: SPEC-176
track: implementable
status: Active
author: cristos
created: 2026-03-27
last-updated: 2026-03-27
priority-weight: ""
type: enhancement
parent-epic: ""
parent-initiative: ""
linked-artifacts:
  - SPEC-175
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# TDD Coverage Self-Critique Gate

## Problem Statement

After writing tests and seeing them pass (GREEN), the agent declares completion without examining what it *didn't* test. In [SPEC-175](../(SPEC-175)-Session-Bootstrap-Script-Consolidation/(SPEC-175)-Session-Bootstrap-Script-Consolidation.md), 14/14 tests passed but 6 dimensions were untested (flag coverage, write side-effects, fallback paths, degraded-mode behavior, idempotency, integration). The agent identified all gaps immediately when the operator asked "what did you miss?" — the knowledge was available, the self-check wasn't happening. One untested path (broken jq fallback) was a real production bug.

The superpowers test-driven-development skill's Verification Checklist has "Edge cases and errors covered" but this is too vague to trigger the specific self-critique behavior needed. Superpowers skills cannot be modified (they're overwritten on update), so the gate must live in swain-do's TDD enforcement, which wraps the TDD skill and controls the execution flow around it.

## Desired Outcomes

Agents pause after GREEN to enumerate untested dimensions before moving to REFACTOR or declaring completion. The operator no longer needs to prompt "what did you miss?" — swain-do's enforcement makes the agent do it unprompted, regardless of which TDD skill is installed.

## External Behavior

After all tests pass (Verify GREEN), and before REFACTOR, the agent runs through a structured self-critique checklist defined in swain-do's TDD enforcement. If gaps are found, the agent surfaces them to the operator: "Tests pass, but I haven't covered: X, Y, Z. Want me to add tests for these before proceeding?"

## Acceptance Criteria

1. **Given** swain-do's TDD enforcement (`skills/swain-do/references/tdd-enforcement.md`), **when** read by an agent, **then** it includes a post-GREEN self-critique step that enumerates untested dimensions: flags/args, write side-effects, fallback/degraded paths, error cases, idempotency, and integration (does this test the user's actual goal?).
2. **Given** a task reaches GREEN (all tests pass), **when** swain-do's enforcement applies, **then** the agent asks "what dimensions are untested?" before proceeding to REFACTOR.
3. **Given** the self-critique finds gaps, **when** the agent surfaces them, **then** it presents them as a concrete list with the option to add tests or proceed.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Changes are limited to `skills/swain-do/references/tdd-enforcement.md`. No changes to superpowers skills (they may be overwritten).
- The self-critique is a checklist addition to swain-do's enforcement, not a tool or automated scan.
- Keep the addition concise and consistent with the existing enforcement tone.

## Implementation Approach

1. Add a "Post-GREEN coverage self-critique" section to `tdd-enforcement.md` between the existing "Task ordering" and "Completion verification" sections.
2. Define the self-critique checklist with specific dimensions (flags, side-effects, fallbacks, idempotency, integration).
3. Include the operator-facing output format ("Tests pass, but I haven't covered: ...").

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-27 | — | Initial creation, from SPEC-175 retro learning |
