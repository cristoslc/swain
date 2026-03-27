---
title: "TDD Coverage Self-Critique Gate"
artifact: SPEC-173
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
  - SPEC-172
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# TDD Coverage Self-Critique Gate

## Problem Statement

After writing tests and seeing them pass (GREEN), the agent declares completion without examining what it *didn't* test. In [SPEC-172](../(SPEC-172)-Session-Bootstrap-Script-Consolidation/(SPEC-172)-Session-Bootstrap-Script-Consolidation.md), 14/14 tests passed but 6 dimensions were untested (flag coverage, write side-effects, fallback paths, degraded-mode behavior, idempotency, integration). The agent identified all gaps immediately when the operator asked "what did you miss?" — the knowledge was available, the self-check wasn't happening. One untested path (broken jq fallback) was a real production bug.

The test-driven-development skill's Verification Checklist has "Edge cases and errors covered" but this is too vague to trigger the specific self-critique behavior needed.

## Desired Outcomes

Agents using the TDD skill pause after GREEN to enumerate untested dimensions before moving to REFACTOR or declaring completion. The operator no longer needs to prompt "what did you miss?" — the skill instructions make the agent do it unprompted.

## External Behavior

After all tests pass (Verify GREEN), and before REFACTOR, the agent runs through a structured self-critique checklist. If gaps are found, the agent surfaces them to the operator: "Tests pass, but I haven't covered: X, Y, Z. Want me to add tests for these before proceeding?"

## Acceptance Criteria

1. **Given** the TDD skill's Verification Checklist, **when** read by an agent, **then** it includes a concrete self-critique step that enumerates untested dimensions: flags/args, write side-effects, fallback/degraded paths, error cases, idempotency, and integration (does this test the user's actual goal?).
2. **Given** the Verify GREEN section, **when** all tests pass, **then** the instructions direct the agent to ask "what dimensions are untested?" before proceeding to REFACTOR.
3. **Given** the self-critique finds gaps, **when** the agent surfaces them, **then** it presents them as a concrete list with the option to add tests or proceed.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Changes are limited to `skills/test-driven-development/SKILL.md`. No script changes, no new files.
- The self-critique is a prompt/checklist addition, not a tool or automated scan.
- Keep the addition concise — the TDD skill is deliberately terse and direct.

## Implementation Approach

1. Add a "Coverage self-critique" subsection after "Verify GREEN" and before "REFACTOR" in the TDD skill.
2. Expand the Verification Checklist with specific untested-dimension prompts.
3. Keep the tone consistent with the skill's existing voice (imperative, no fluff).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-27 | — | Initial creation, from SPEC-172 retro learning |
