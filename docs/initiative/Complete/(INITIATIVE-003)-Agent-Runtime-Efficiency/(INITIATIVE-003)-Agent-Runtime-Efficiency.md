---
title: "Agent Runtime Efficiency"
artifact: INITIATIVE-003
track: container
status: Complete
author: cristos
created: 2026-03-15
last-updated: 2026-03-15
parent-vision: VISION-001
success-criteria:
  - Skill context footprint ≤5% of context window
  - Each skill operation routed to appropriate model tier
  - Superpowers integration assessed and coexistence path established
linked-artifacts:
  - EPIC-004
  - EPIC-006
  - EPIC-007
---

# Agent Runtime Efficiency

## Strategic Focus

Keep agents fast, cheap, and correctly routed. This initiative focuses on reducing the token cost of swain's skill system and ensuring operations are dispatched to the right model tier — heavy reasoning for design work, lightweight for routing and tab naming.

## Scope Boundaries

**In scope:** Context footprint reduction, model routing annotations, superpowers interop assessment.

**Out of scope:** Agent runtime implementation details (Claude Code, Cursor, etc.), model selection APIs, prompt caching strategies.

## Child Epics

- EPIC-004: Superpowers Integration Assessment (Complete)
- EPIC-006: Skill Context Footprint Reduction (Complete)
- EPIC-007: Agent Model Routing and Reasoning Effort Steering (Complete)

## Small Work (Epic-less Specs)

None.

## Key Dependencies

EPIC-006 needed to complete before EPIC-007 to offset added annotation content.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Complete | 2026-03-15 | — | Retroactive creation during initiative migration; all child epics already complete |
