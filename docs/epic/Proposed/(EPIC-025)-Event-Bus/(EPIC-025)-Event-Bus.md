---
title: "Event Bus"
artifact: EPIC-025
track: container
status: Proposed
author: cristos
created: 2026-03-17
last-updated: 2026-03-17
parent-initiative: INITIATIVE-009
depends-on: []
success-criteria:
  - Events are appended to per-worktree files (.agents/events/<id>.events.jsonl) with a consistent schema (timestamp, event type, source skill, payload, unique event ID)
  - Orchestrator compiles per-worktree event files into trunk .agents/events.jsonl with deduplication by event ID
  - Emission helpers are available as shell functions that skill scripts can source
  - Existing skill scripts (specwatch, tk close, lifecycle stamping) emit events as side effects without agent intervention
  - A subscriptions.json registry maps event types to handlers with metadata (handler, mode, model hint, prompt seed)
  - An orchestrator script processes pending events by matching against subscriptions
  - Preflight triggers event compilation and checks for unprocessed events at session start
  - State-derivation fallback cross-references tk and specgraph to synthesize events for transitions that occurred without emission
linked-artifacts:
  - INITIATIVE-009
  - EPIC-026
---

# Event Bus

## Goal / Objective

Establish the foundational event infrastructure for swain's coordination layer. Define the event log format, provide emission helpers for skill scripts, create the subscription registry, and build the orchestrator that processes events — including a state-derivation fallback that can reconstruct missed events from tk and specgraph state.

## Scope Boundaries

**In scope:**
- Event log format: `.agents/events.jsonl` (trunk) — one JSON object per line
- Per-worktree/session event files: `.agents/events/<worktree-id>.events.jsonl` — each writer appends to its own file, avoiding contention
- Event schema: `timestamp`, `event_type`, `source_skill`, `artifact_id`, `session_id`, `id` (unique event ID for deduplication), `payload`
- Shell emission helpers (`swain-emit`) that skill scripts source to append events to the appropriate per-worktree file
- Emission integrated into existing skill scripts (specwatch, tk close, lifecycle stamping) as side effects — agents don't emit directly
- `subscriptions.json` registry: maps event types to handler definitions with `handler`, `mode` (interactive|delegable), `model_hint`, `prompt_seed`
- Orchestrator script: compiles per-worktree event files into trunk (dedup by event ID, append in order), then reads unprocessed events, matches against subscriptions, dispatches handlers
- Preflight compilation hook: at session start, preflight triggers orchestrator compilation of pending worktree event files and checks for unprocessed events
- State-derivation fallback: periodically cross-references tk + specgraph to detect state transitions that weren't emitted as events, and back-fills them
- Event log rotation/compaction strategy (including truncation/archival of per-worktree inbox files after compilation)

**Out of scope:**
- Unified query interface (EPIC-026)
- Migration of AGENTS.md table (EPIC-027)
- swain-status integration (EPIC-028)
- Real-time event streaming

## Design Decisions

1. **JSONL over SQLite** — append-only log is simpler, git-diffable, and requires no runtime dependencies
2. **Shell-first emission** — skill scripts are bash; emission helpers must be sourceable shell functions, not Python
3. **Subscriptions as data** — `subscriptions.json` is declarative configuration, not code; skills register by adding entries
4. **State-derivation as safety net** — the fallback ensures the system is eventually consistent even if skills forget to emit
5. **Per-worktree event files** — each worktree/session writes to its own namespaced event file at `events/<worktree-id>.events.jsonl` (or `events/<session-id>.events.jsonl` for multiple sessions on main). The orchestrator is the only writer to the trunk `events.jsonl` — it compiles per-worktree files by deduplicating by event ID and appending new events in order. Worktree event files are ephemeral (like an inbox) — truncated/archived after compilation. This eliminates write contention and removes the need for file locking.
6. **Preflight as compilation hook** — at session start, preflight compiles any pending worktree/session event files into trunk, then checks for unprocessed events. This ensures dispatched agent events get picked up even if no skill explicitly triggered the orchestrator.
7. **Emission via scripts, not prose** — skill scripts (which already run deterministic operations like specwatch, tk close, lifecycle stamping) emit events as a side effect. The agent never has to remember to emit — the tool does it. This addresses emission reliability at the source.

## Event Schema

```json
{
  "ts": "2026-03-17T14:30:00Z",
  "event": "artifact.phase_transition",
  "source": "swain-design",
  "artifact": "SPEC-042",
  "session": "abc123",
  "payload": {
    "from": "Proposed",
    "to": "Active"
  }
}
```

## Subscription Schema

```json
{
  "subscriptions": [
    {
      "event": "artifact.phase_transition",
      "filter": { "payload.to": "Complete", "artifact": "EPIC-*" },
      "handler": "swain-retro",
      "mode": "interactive",
      "model_hint": "opus",
      "prompt_seed": "EPIC {artifact} reached Complete — run retrospective"
    }
  ]
}
```

## Child Specs

None yet — specs to be decomposed when this EPIC transitions to Active.

## Key Dependencies

None. This is the foundation — no other EPIC can proceed without it.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-17 | — | Initial creation as part of INITIATIVE-009 |
