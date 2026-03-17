---
title: "Event Bus"
artifact: EPIC-025
track: container
status: Proposed
author: cristos
created: 2026-03-17
last-updated: 2026-03-17
parent-initiative: INITIATIVE-009
depends-on:
  - EPIC-029
success-criteria:
  - Events are appended to per-worktree files (.agents/events/<id>.events.jsonl) with a consistent schema (timestamp, event type, source skill, payload, unique event ID)
  - Orchestrator compiles per-worktree event files into trunk .agents/events.jsonl with deduplication by event ID
  - Emission helpers are available as shell functions that skill scripts can source
  - Existing skill scripts (specwatch, tk close, lifecycle stamping) emit events as side effects without agent intervention
  - A subscriptions.json registry maps event types to handlers with metadata (handler, mode, model hint, prompt seed)
  - An orchestrator script processes pending events by matching against subscriptions
  - Preflight triggers event compilation and checks for unprocessed events at session start
  - Compile mode fails with a shaped error when run from a worktree; recommend mode fails with a shaped error when emitting from trunk
  - Compilation is triggered at preflight (session start) and swain-sync (worktree merge) — no daemon required
  - All trunk branch references are parameterized via swain.settings.json git.trunk (EPIC-029)
  - State-derivation fallback cross-references tk and specgraph to synthesize events for transitions that occurred without emission
linked-artifacts:
  - INITIATIVE-009
  - EPIC-026
  - EPIC-029
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
- Worktree enforcement guards: compile mode restricted to trunk, recommend mode restricted to worktrees, with shaped errors guiding agents to the correct context
- Compilation triggered at two sync points: preflight (session start) and swain-sync (worktree merge back to trunk)

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
8. **Worktree enforcement guards** — the orchestrator script has two modes that run in different contexts:
   - **Compile mode** (trunk only): merges per-worktree event files into trunk `events.jsonl`. Fails with a shaped error if run from a worktree.
   - **Recommend mode** (worktree): reads trunk log, checks subscriptions, outputs next actions. Fails with a shaped error if emitting from trunk, prompting the agent to use a worktree.
   Compilation is triggered at two natural sync points — preflight (session start, before the agent enters a worktree) and swain-sync (when merging a worktree back to trunk). No daemon or launchctl agent is needed. The trunk branch is not hardcoded — it is read from `swain.settings.json` `git.trunk` (see EPIC-029).
9. **Parameterized trunk reference** — all references to the trunk branch (compilation target, merge base, event file paths) use the configurable `git.trunk` setting from `swain.settings.json` rather than hardcoding "main". See EPIC-029 for the cross-cutting parameterization.

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

## Test Plan

### T1 — Event schema validation
- Emit an event via `swain-emit` and verify the JSONL line contains all required fields: `ts`, `event`, `source`, `artifact`, `session`, `id`, `payload`
- Verify `ts` is ISO-8601 UTC, `id` is unique across repeated calls, and the line is valid JSON parseable by `jq`

### T2 — Per-worktree isolation
- From two separate worktree contexts, emit events concurrently (background subshells)
- Verify each writes to its own `events/<worktree-id>.events.jsonl` and neither file contains the other's events
- Verify a non-worktree session on main writes to `events/<session-id>.events.jsonl`

### T3 — Compilation and deduplication
- Seed two per-worktree event files with overlapping event IDs
- Run the orchestrator compile step
- Verify trunk `events.jsonl` contains each event ID exactly once, in chronological order
- Verify per-worktree inbox files are truncated/archived after compilation

### T4 — Emission from existing skill scripts
- Run `specwatch` on a phase transition (e.g., SPEC Proposed → Active) and verify an `artifact.phase_transition` event is emitted
- Run `tk close` on a task and verify a `task.completed` event is emitted
- Run lifecycle stamping and verify the corresponding event appears
- In all cases, verify the agent did not need to explicitly emit — the script did it as a side effect

### T5 — Subscription registry loading
- Create a valid `subscriptions.json` with two entries (one interactive, one delegable)
- Run the orchestrator and verify it loads both subscriptions, matching event types and filters correctly
- Add a malformed entry (missing `handler`) and verify the orchestrator rejects it with a clear error, processing valid entries

### T6 — Orchestrator dispatch
- Seed `events.jsonl` with an unprocessed event matching a subscription
- Run the orchestrator and verify it outputs the correct recommendation text (handler, mode, model_hint, prompt_seed)
- Verify the event is marked as processed (not re-dispatched on next run)
- Seed an event that matches no subscription and verify it is skipped without error

### T7 — State-derivation fallback
- Create a state mismatch: advance a SPEC to Complete in specgraph and close its tasks in tk, but emit no events
- Run the state-derivation fallback
- Verify it synthesizes the missing `artifact.phase_transition` event with correct payload and a `source: "state-derivation"` marker
- Verify deduplication — run fallback again and confirm no duplicate events

### T8 — Preflight integration
- Start a fresh session with pending per-worktree event files and unprocessed events
- Run `swain-preflight.sh` and verify it triggers compilation, then reports unprocessed event count
- Start a session with no pending events and verify preflight exits cleanly

### T9 — Rotation and compaction
- Append 1000+ events to trunk `events.jsonl`
- Trigger rotation and verify older events are archived (e.g., moved to `events/archive/`) and the active file stays under the configured threshold
- Verify archived events are still queryable by the orchestrator when needed

## Key Dependencies

- **EPIC-029** (Configurable Trunk Branch) — the event bus must use `git.trunk` for compilation target and worktree enforcement, not hardcoded "main"

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-17 | — | Initial creation as part of INITIATIVE-009 |
