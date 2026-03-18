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

## Test Plan

### T1 — "What should happen next?" query
- Set up state: one SPEC in Active with ready tasks (tk), one pending unprocessed event (subscription match), one EPIC with all child SPECs complete (transition candidate)
- Run the query and verify all three appear in the result, ranked by priority-weight
- Verify each result item includes provenance (which source contributed it: specgraph, tk, or event bus)

### T2 — "What happened recently?" query
- Emit 5 events spanning two different artifacts over the last hour
- Run the query and verify all 5 appear with human-readable context (artifact title, event type, relative time)
- Verify session-scoped default: only events from the current session appear unless `--all` is passed

### T3 — "What's blocked and why?" query
- Create a task in tk that depends on another incomplete task
- Create a SPEC that depends on an unresolved EPIC
- Run the query and verify both blocked items appear with their specific blockers identified
- Verify the dependency graph context includes the blocker's current status

### T4 — Source aggregation correctness
- Create a work item that appears in all three sources (artifact in specgraph, tasks in tk, events in event bus)
- Run the unified query and verify the item appears once (merged), not three times
- Verify the merged result contains data from all three sources with correct provenance

### T5 — Priority merge rules
- Create items with conflicting priority signals: high priority-weight in specgraph but low priority in tk, and a stale event vs a recent event
- Verify the merge follows the documented order: artifact priority-weight > tk priority > event recency

### T6 — Graceful degradation
- Run queries with the event bus empty (no events.jsonl) — verify specgraph + tk results still return correctly
- Run queries with tk returning no tasks — verify specgraph + event bus results return
- Run queries with specgraph unavailable (missing or erroring) — verify the query layer reports the degraded source and returns partial results from the available sources

### T7 — JSON output contract
- Run each query type and pipe output through `jq`
- Verify the output is valid JSON with a stable schema (consistent field names, types, and structure across runs)
- Verify the schema includes a top-level `sources` array indicating which backends were consulted and their status

### T8 — Caching behavior
- Run an expensive cross-source query twice in succession
- Verify the second call is faster (cache hit) and returns identical results
- Mutate state (emit a new event) and verify the next query reflects the change (cache invalidation)

## Child Specs

None yet — specs to be decomposed when this EPIC transitions to Active.

## Key Dependencies

- **EPIC-025 (Event Bus)** — the event bus must exist before the query layer can consume it

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-17 | — | Initial creation as part of INITIATIVE-009 |
