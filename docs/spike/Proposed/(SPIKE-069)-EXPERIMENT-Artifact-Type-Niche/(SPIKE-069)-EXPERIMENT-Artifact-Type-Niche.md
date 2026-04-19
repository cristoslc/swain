---
title: "EXPERIMENT Artifact Type Niche"
artifact: SPIKE-069
track: container
status: Proposed
author: cristos
created: 2026-04-18
last-updated: 2026-04-18
question: "Does the EXPERIMENT artifact type fill a niche not covered by existing types (SPIKE, SPEC + outcome tracking, retroactive creation), or does it add type proliferation without sufficient justification?"
gate: Pre-Implementation
risks-addressed:
  - Artifact type proliferation — too many types dilute the value of the type system
  - Lifecycle confusion — EXPERIMENT's deployed-first model may conflict with Swain's plan-first conventions
  - Overlap with SPEC + outcome tracking — retroactive SPECs with measured outcomes may cover the same ground
evidence-pool: ""
---

# EXPERIMENT Artifact Type Niche

## Summary

<!-- Populated on transition to Complete. -->

## Question

Does the EXPERIMENT artifact type fill a niche not covered by existing types (SPIKE, SPEC + outcome tracking, retroactive creation), or does it add type proliferation without sufficient justification?

The proposed EXPERIMENT type has three distinguishing features:
1. A deployed-first lifecycle (Proposed → Running → Resolved, no In Progress or Needs Manual Test)
2. Resolution states (Confirmed, Refuted, Inconclusive)
3. Hypothesis and success metric as required fields

The core question is whether these features justify a new type, or whether the same value can be achieved by:
- A SPEC with `outcome:` tracking (already proposed for EPIC-086)
- A retroactive SPEC placed directly in Complete (EPIC-086)
- A SPIKE re-scoped to cover post-deployment measurement (stretch)

## Go / No-Go Criteria

- **Go** if: there are at least 3 real scenarios from the Boswell research or operator experience where an EXPERIMENT artifact would capture information that existing types fundamentally cannot — not just "it would be convenient."
- **No-Go** if: all proposed scenarios can be covered by existing types with minor extensions (SPEC + outcome field, retroactive creation, SPIKE re-scoping).

## Pivot Recommendation

If No-Go: extend SPEC with an optional `hypothesis:` + `success-metric:` frontmatter field pair and a `resolution:` field. Any SPEC can be marked as experimental without creating a new type. The deployed-first lifecycle is handled by retroactive creation (EPIC-086) — the work is already done, so the SPEC starts in Complete.

## Findings

<!-- Populated during Active phase. -->

Key angles to investigate:

1. **What does EXPERIMENT capture that SPEC doesn't?** SPEC tracks implementation evidence (tests pass). EXPERIMENT would track outcome evidence (metric moved). But can `outcome:` on SPEC + a link to external metrics cover this? Is the separation of "evidence of building correctly" vs. "evidence of building the right thing" worth a type boundary?

2. **What does EXPERIMENT capture that SPIKE doesn't?** SPIKE answers "Should we build X?" before building. EXPERIMENT would answer "Did X work?" after deploying. These are different questions — but SPIKE could be extended to cover both with a `kind: pre-build | post-deploy` field.

3. **Is the deployed-first lifecycle necessary?** A retroactive SPEC starts in Complete — same functional result. The EXPERIMENT lifecycle adds an intermediate "Running" state (data collection in progress). Is this state worth a separate lifecycle, or can a SPEC in Complete with `resolution: pending` achieve the same thing?

4. **Cost of type proliferation.** Each artifact type adds: a definition file, a template, folder structure conventions, lifecycle rules, swain-design creation logic, specwatch checks, chart.sh integration, index entries, and operator cognitive load. Is EXPERIMENT worth that cost?

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-18 | — | Decomposed from EPIC-083 Abandoned |