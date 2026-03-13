---
title: "Decision-Only Artifacts Incorrectly Shown as Implementable in swain-status"
artifact: SPEC-010
status: Draft
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
type: bug
parent-epic: EPIC-006
linked-research:
  - SPIKE-012
linked-adrs: []
depends-on:
  - SPIKE-012
addresses: []
evidence-pool: ""
source-issue: github:cristoslc/swain#29
swain-do: required
---

# Decision-Only Artifacts Incorrectly Shown as Implementable in swain-status

## Problem Statement

swain-status classifies ready artifacts into "Decisions Waiting on You" (human judgment needed) and "Implementation" (agent can handle). The `is_decision` guard in `swain-status.sh` only matches decision-only types in specific early phases (e.g., VISION in Draft, ADR in Proposed). Once those artifacts advance past the guarded phase, they fall through to the implementation bucket and receive the action "progress to next phase."

VISION, ADR, PERSONA, and potentially JOURNEY are decision-support artifacts with no agent-implementable work at any lifecycle phase. They should never appear in the Implementation section regardless of status. This has been reported by consumers (GitHub #29, #28).

## Reproduction Steps

1. Have a VISION artifact in Active status.
2. Run `swain-status` or `/swain-status`.
3. Observe VISION appears under "Implementation" with action "progress to next phase."

## Severity

medium

## Expected vs. Actual Behavior

**Expected:** VISION (and other decision-only types) never appear in the Implementation section. At non-Draft phases they either appear in Decisions (if human action is still needed) or are omitted from the actionable lists entirely.

**Actual:** VISION in Active status appears under Implementation with the misleading action "progress to next phase."

## External Behavior

After this spec is implemented:

- VISION, ADR, PERSONA artifacts never appear in the Implementation section at any lifecycle phase.
- JOURNEY artifacts never appear in the Implementation section.
- The `is_decision` logic is replaced or extended with a type-level classification (decision-only vs. implementation-capable) derived from SPIKE-012 findings.
- An Active VISION with no pending human action is either omitted from actionable lists or shown with a contextually correct hint (e.g., "decompose into epics").

## Acceptance Criteria

- **Given** a VISION artifact in any status (Draft, Active, Complete), **when** swain-status runs, **then** it never appears under "Implementation."
- **Given** an ADR in any status other than Proposed, **when** swain-status runs, **then** it never appears under "Implementation."
- **Given** VISION-001 in Active status (current real-world case), **when** swain-status runs, **then** it is either absent from actionable lists or shown under "Decisions" with a correct hint.
- **Given** the fix is applied, **when** swain-status runs on a repo with only implementation-capable artifacts ready, **then** the Implementation section still renders correctly.

## Scope & Constraints

- Fix is scoped to `skills/swain-status/scripts/swain-status.sh` and the specgraph data it reads.
- The classification of which types are decision-only comes from SPIKE-012 — do not hard-code a partial fix before the spike completes.
- Related issue #28 (visions should not block each other) is a separate specgraph concern and is out of scope here.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-13 | — | Initial creation |
