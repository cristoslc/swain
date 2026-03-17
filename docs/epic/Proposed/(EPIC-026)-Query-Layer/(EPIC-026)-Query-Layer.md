---
title: "Query Layer"
artifact: EPIC-026
track: container
status: Proposed
author: cristos
created: 2026-03-17
last-updated: 2026-03-17
parent-initiative: INITIATIVE-009
depends-on:
  - EPIC-025
success-criteria:
  - A unified query interface exposes combined state from specgraph, tk, and the event bus
  - A first-class "what should happen next?" query returns prioritized actionable items combining artifact state, task state, and pending reactions
  - Consumers (orchestrator, swain-status) program against the query layer instead of directly reading three separate state stores
  - Query results include provenance — which source(s) contributed each item
linked-artifacts:
  - INITIATIVE-009
  - EPIC-025
  - EPIC-027
  - EPIC-028
---

# Query Layer

## Goal / Objective

Build a unified interface over specgraph, tk, and the event bus that abstracts away the three separate state stores. The key deliverable is a first-class "what should happen next?" query that combines artifact state (what phase is each artifact in?), task state (what's blocked, ready, or in-progress?), and pending reactions (what events haven't been handled yet?) into a single prioritized answer.

## Scope Boundaries

**In scope:**
- Query interface (CLI and/or importable module) that aggregates specgraph, tk, and event bus
- "What should happen next?" query: combines ready tasks, pending event reactions, and artifact transitions needing decisions
- "What happened recently?" query: recent events with context from artifact and task state
- "What's blocked and why?" query: blocked tasks with dependency graph context
- Provenance in query results — each item indicates which source(s) contributed it
- Caching strategy for expensive cross-source joins

**Out of scope:**
- Modifying specgraph or tk internals — this layer reads from them, doesn't change them
- Orchestrator dispatch logic (EPIC-027)
- Status dashboard formatting (EPIC-028)
- GraphQL or REST API — CLI-first

## Design Decisions

1. **Reads, not writes** — the query layer is read-only; mutations go through specgraph, tk, or event emission directly
2. **CLI-first** — primary interface is a command that outputs JSON; other consumers parse that output
3. **Priority merge** — when the same work item appears in multiple sources, priority-weight from the artifact hierarchy takes precedence, then tk priority, then event recency

## Child Specs

None yet — specs to be decomposed when this EPIC transitions to Active.

## Key Dependencies

- **EPIC-025 (Event Bus)** — the event bus must exist before the query layer can consume it

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-17 | — | Initial creation as part of INITIATIVE-009 |
