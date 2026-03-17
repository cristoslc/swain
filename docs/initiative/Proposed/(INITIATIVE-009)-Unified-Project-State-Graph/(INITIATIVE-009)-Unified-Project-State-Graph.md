---
title: "Unified Project State Graph"
artifact: INITIATIVE-009
track: container
status: Proposed
author: cristos
created: 2026-03-17
last-updated: 2026-03-17
parent-vision: VISION-001
priority-weight: medium
success-criteria:
  - Skill transitions emit structured events to .agents/events.jsonl with consistent schema
  - A subscriptions.json registry maps events to handlers with mode (interactive|delegable), model hint, and prompt seed
  - A unified query interface answers "what should happen next?" by combining specgraph, tk, and event bus state
  - swain-status consumes the event bus as a third input source alongside specgraph and tk
  - The AGENTS.md prose chaining table is fully replaced by subscriptions.json entries
  - Third-party skills can register event subscriptions without modifying governance files
linked-artifacts:
  - EPIC-025
  - EPIC-026
  - EPIC-027
  - EPIC-028
  - VISION-001
depends-on-artifacts: []
---

# Unified Project State Graph

## Strategic Focus

Replace swain's prose-based skill chaining table with a machine-readable, event-driven coordination layer. Unify the three existing state sources (specgraph for artifact state, tk for task state, and a new event bus for transition state) behind a common query interface that the orchestrator and swain-status consume.

## Why This Initiative

The current chaining table in AGENTS.md is a static dispatch map that:

- **Mixes concerns** — superpowers chains and swain-internal chains live in the same prose table
- **Doesn't handle cross-session handoffs** — dispatched agents completing work have no way to signal the orchestrator
- **Requires governance hash churn** — every new chain means editing AGENTS.md and re-stamping the lifecycle hash
- **Can't be extended by third-party skills** — adding a subscription requires editing a prose table in a governance file

The fragmentation across specgraph, tk, and manual prose coordination creates blind spots. swain-status can't answer "what happened recently" or "what reactions are pending" because transition events aren't recorded anywhere.

## Scope Boundaries

**In scope:**
- Event log format and emission helpers
- Subscription registry (subscriptions.json)
- Orchestrator script with state-derivation fallback
- Unified query interface over specgraph + tk + event bus
- Migration of AGENTS.md chaining table to subscriptions.json
- swain-status event bus integration

**Out of scope:**
- Real-time push notifications (webhooks, SSE)
- Distributed event bus across repos
- Agent-to-agent direct messaging
- UI/frontend for event visualization

## Child Epics

| Epic | Title | Status | Depends On |
|------|-------|--------|------------|
| EPIC-025 | Event Bus | Proposed | — |
| EPIC-026 | Query Layer | Proposed | EPIC-025 |
| EPIC-027 | Orchestrator Integration | Proposed | EPIC-026 |
| EPIC-028 | Status Integration | Proposed | EPIC-026 |

## Dependency Graph

```
EPIC-025 (Event Bus)
    └── EPIC-026 (Query Layer)
            ├── EPIC-027 (Orchestrator Integration)
            └── EPIC-028 (Status Integration)
```

EPIC-027 and EPIC-028 are independent of each other; both depend on EPIC-026.

## Small Work (Epic-less Specs)

None.

## Key Dependencies

- **specgraph** — must expose artifact state in a format the query layer can consume (already exists as Python CLI)
- **tk** — must expose task state via ticket-query plugin (already exists)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-17 | — | Initial creation with 4 child EPICs |
