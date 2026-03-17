---
title: "Status Integration"
artifact: EPIC-028
track: container
status: Proposed
author: cristos
created: 2026-03-17
last-updated: 2026-03-17
parent-initiative: INITIATIVE-009
depends-on:
  - EPIC-026
success-criteria:
  - swain-status consumes the event bus as a third input source alongside specgraph and tk
  - Status output transitions from state snapshot to narrative with temporal context
  - Recent events are surfaced with human-readable descriptions (e.g., "SPEC-012 completed 20 minutes ago by dispatched agent")
  - Pending reactions from subscriptions.json are surfaced as actionable items
  - Event-enriched status provides better decision support than the current state-only snapshot
linked-artifacts:
  - INITIATIVE-009
  - EPIC-026
---

# Status Integration

## Goal / Objective

Evolve swain-status from a state snapshot to a narrative-aware status dashboard by consuming the event bus as a third input source. Instead of "SPEC-012 is Complete," status should report "SPEC-012 was completed 20 minutes ago by a dispatched agent, EPIC rollup check pending." The event bus provides the temporal dimension — what happened, when, and what reactions are still pending.

## Scope Boundaries

**In scope:**
- swain-status integration with event bus via the query layer (EPIC-026)
- Temporal context in status output — when things happened, not just current state
- Pending reaction surfacing — "EPIC-014 rollup check pending" when a child SPEC completion event hasn't triggered its subscription yet
- Cross-session handoff visibility — events from dispatched agents appear in status
- Narrative formatting — human-readable event summaries, not raw JSON

**Out of scope:**
- Event bus implementation (EPIC-025)
- Query layer implementation (EPIC-026)
- Orchestrator/dispatch changes (EPIC-027)
- Real-time status updates (push-based)
- UI/frontend visualization (daymark integration is a separate concern)

## Design Decisions

1. **Query layer as sole data source** — swain-status reads from the query layer, not directly from events.jsonl; this ensures consistent state merging
2. **Narrative over table** — event-enriched output uses prose sentences, not additional table columns; tables are for current state, narrative is for recent activity
3. **Recency window** — status shows events from the current session by default, with a flag for broader time ranges

## Child Specs

None yet — specs to be decomposed when this EPIC transitions to Active.

## Key Dependencies

- **EPIC-026 (Query Layer)** — status consumes events through the unified query interface, not directly

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-17 | — | Initial creation as part of INITIATIVE-009 |
