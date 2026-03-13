---
title: "Skill Context Footprint Audit"
artifact: SPIKE-010
status: Planned
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
question: "Which swain skills consume the most context, what content categories drive their size, and where is the waste?"
gate: Pre-EPIC-006-specs
risks-addressed:
  - Optimizing the wrong skills first — audit ensures effort targets highest-impact areas
  - Content that looks redundant may actually be load-bearing for agent behavior
depends-on: []
linked-artifacts:
  - EPIC-006
evidence-pool: ""
---

# Skill Context Footprint Audit

## Question

Which swain skills consume the most context, what content categories drive their size, and where is the waste?

## Go / No-Go Criteria

**Go:** Audit produces a ranked list of skills by token count, with each skill's content broken down by category (runtime instructions, reference tables, examples, prose). At least one clear over-specification pattern is identified.

**No-Go:** Skills are uniformly sized and all content is necessary — no meaningful reduction is possible without feature removal.

## Pivot Recommendation

If no-go: accept current footprint and close EPIC-006. If skills are large but all content is necessary, file an ADR proposing a lazy-loading mechanism instead of content trimming.

## Findings

(Populated during Active phase.)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-13 | — | Initial creation |
