---
title: "Agent Runtime Efficiency"
artifact: INITIATIVE-003
track: container
status: Active
author: cristos
created: 2026-03-15
last-updated: 2026-03-30
parent-vision: VISION-001
success-criteria:
  - Skill context footprint ≤5% of context window
  - Each skill operation routed to appropriate model tier
  - Superpowers integration assessed and coexistence path established
linked-artifacts:
  - EPIC-004
  - EPIC-006
  - EPIC-007
  - EPIC-048
  - SPEC-026
  - SPIKE-026
  - EPIC-068
---

# Agent Runtime Efficiency

## Strategic Focus

Keep agents fast, cheap, and correctly routed. This initiative focuses on reducing the token cost of swain's skill system and ensuring operations are dispatched to the right model tier — heavy reasoning for design work, lightweight for routing and tab naming.

## Scope Boundaries

**In scope:** Context footprint reduction, model routing annotations, runtime model routing enforcement, superpowers interop assessment.

**Out of scope:** Prompt caching strategies.

## Child Epics

- EPIC-004: Superpowers Integration Assessment (Complete)
- EPIC-006: Skill Context Footprint Reduction (Complete)
- EPIC-007: Agent Model Routing and Reasoning Effort Steering (Complete)
- [EPIC-048](../../../epic/Active/(EPIC-048)-Session-Startup-Fast-Path/(EPIC-048)-Session-Startup-Fast-Path.md): Session Startup Fast Path (Active)

## Research Spikes

- SPIKE-026: Context Fork as Model Routing Implementation Path (Active)

## Small Work (Epic-less Specs)

None.

## Key Dependencies

EPIC-006 needed to complete before EPIC-007 to offset added annotation content.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Complete | 2026-03-15 | -- | Retroactive creation during initiative migration; all child epics already complete |
| Active | 2026-03-16 | -- | Reopened: SPEC-026 implemented advisory annotations but not runtime enforcement; "routed" success criterion unmet. SPIKE-026 investigates context fork as implementation path |
