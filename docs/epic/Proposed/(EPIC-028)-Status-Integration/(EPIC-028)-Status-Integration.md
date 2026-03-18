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

## Test Plan

### T1 — Event bus as third input source
- Emit events for two artifacts (one phase transition, one task completion)
- Run swain-status and verify both events appear in the output alongside specgraph and tk data
- Remove the event bus (delete events.jsonl) and verify swain-status still works with specgraph + tk only (graceful degradation)

### T2 — Temporal context
- Emit an event 5 minutes ago and another 2 hours ago
- Run swain-status and verify output includes relative timestamps ("5 minutes ago", "2 hours ago") rather than just current state
- Verify the format is "SPEC-012 was completed 5 minutes ago" not "SPEC-012 status: Complete"

### T3 — Pending reaction surfacing
- Create an unprocessed event that matches a subscription (e.g., EPIC completion → retro pending)
- Run swain-status and verify it surfaces "EPIC-014 rollup check pending" as an actionable item
- Process the event (run orchestrator) and verify the pending reaction disappears from status

### T4 — Cross-session handoff visibility
- Emit events from a dispatched agent session (different session_id)
- Run swain-status from the operator's session and verify the dispatched agent's events appear
- Verify the output attributes the action to the dispatched agent ("completed by dispatched agent")

### T5 — Narrative formatting
- Generate status with events and verify the output uses prose sentences for recent activity, not raw JSON or table rows
- Verify current state still uses table format (tables for state, narrative for activity)
- Verify the narrative section is clearly separated from the state section

### T6 — Recency window
- Emit events spanning 3 different sessions over a simulated multi-day period
- Run swain-status with default settings and verify only current-session events appear
- Run swain-status with `--since 48h` (or equivalent flag) and verify events from all sessions within that window appear

### T7 — Decision support quality
- Set up a scenario: EPIC with all child SPECs complete, one pending reaction, two ready tasks
- Run swain-status and verify it produces a ranked recommendation (not just a data dump)
- Verify the recommendation references the event context ("all specs complete as of 10 minutes ago — transition EPIC to Complete?")

### T8 — No direct event bus reads
- Instrument or mock the query layer to track calls
- Run swain-status and verify all event data comes through the query layer API, not by reading events.jsonl directly
- This validates the architectural constraint from Design Decision #1

## Child Specs

None yet — specs to be decomposed when this EPIC transitions to Active.

## Key Dependencies

- **EPIC-026 (Query Layer)** — status consumes events through the unified query interface, not directly

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-17 | — | Initial creation as part of INITIATIVE-009 |
