---
title: "Decision-Only Artifact Type Classification"
artifact: SPIKE-012
status: Planned
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
question: "Which artifact types are decision-only across their entire lifecycle, what does 'no meaningful implementation phase' mean for each, and what is the correct swain-status treatment at each phase?"
gate: Pre-SPEC-010-implementation
risks-addressed:
  - Misclassifying a type as decision-only when some of its phases are legitimately agent-implementable
  - Hiding artifacts that do need attention from the operator (over-filtering)
depends-on: []
linked-artifacts:
  - SPEC-010
  - EPIC-006
evidence-pool: ""
---

# Decision-Only Artifact Type Classification

## Question

Which artifact types are decision-only across their entire lifecycle, what does "no meaningful implementation phase" mean for each, and what is the correct swain-status treatment at each phase?

## Go / No-Go Criteria

**Go:** A definitive classification table is produced that maps each artifact type to: (a) decision-only vs. implementation-capable, and (b) the correct swain-status action hint and bucket (Decisions / Implementation / Omit) for each lifecycle phase.

**No-Go:** Some types are ambiguous — their phases mix human and agent work. In that case, produce a per-phase table and recommend a conservative classification (prefer Decisions over Implementation for ambiguous phases).

## Pivot Recommendation

If no-go: use the per-phase conservative table to fix SPEC-010. Accept some over-classification into Decisions as preferable to false Implementation signals.

## Findings

(Populated during Active phase.)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-13 | — | Initial creation |
