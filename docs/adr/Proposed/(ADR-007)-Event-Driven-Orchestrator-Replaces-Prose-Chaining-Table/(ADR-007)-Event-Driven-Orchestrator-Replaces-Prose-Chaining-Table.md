---
title: "Event-Driven Orchestrator Replaces Prose Chaining Table"
artifact: ADR-007
track: standing
status: Proposed
author: cristos
created: 2026-03-17
last-updated: 2026-03-17
linked-artifacts:
  - INITIATIVE-009
  - EPIC-025
  - EPIC-026
  - EPIC-027
  - ADR-001
depends-on-artifacts: []
---

# ADR-007: Event-Driven Orchestrator Replaces Prose Chaining Table

## Context

The AGENTS.md governance template contains a "Superpowers skill chaining" table — a static dispatch map telling agents which skill to invoke after which trigger. After trimming the governance template from 220 to 58 lines, the chaining table was updated to 8 rows mixing superpowers chains (conditional on installation) and swain-internal chains (always apply), some spanning 4 skills deep.

This table has three structural problems:

1. **Governance hash churn.** Every new chain requires editing AGENTS.md, which changes the governance hash. This creates friction disproportionate to the change.
2. **No cross-session handoffs.** Dispatched agents (via swain-dispatch or subagent-driven-development) write results to disk, but the next session has no mechanism to discover what happened and what chains should fire next. The table assumes a single continuous session.
3. **No third-party extensibility.** External skills cannot subscribe to events without editing the governance file. The table is a closed dispatch map.

The catalyst was auditing the chaining table for completeness: the full lifecycle of a SPEC (plan completion → SPEC transition → EPIC rollup check → retro trigger) required chains that weren't represented. Adding them revealed the table was encoding a dependency graph that it couldn't adequately express — cascading completions, cross-skill handoffs, and conditional dispatch based on runtime capabilities.

Separately, swain already has three state sources — specgraph (artifact state), tk (task state), and now the proposed event bus (transition state) — that are queried independently. swain-status already consults specgraph and tk to answer "what's next?" but can't answer "what happened recently" or "what reactions are pending." The event bus is the missing third input, and a unified query layer over all three is the architectural goal (EPIC-026).

Research across 7 major agent runtimes showed that 5 (Codex CLI, OpenCode, Copilot, Cursor, Windsurf) now support subagent dispatch with parallelism. AGENTS.md is a Linux Foundation standard. Multiple runtimes (Cursor, Windsurf, Copilot) already use git worktrees for agent isolation. Subagent dispatch is table stakes, not Claude Code-specific — the orchestration layer must be runtime-portable.

This ADR evolves the integration mechanism that ADR-001 established. ADR-001 defined the three-layer model (swain-only / overlap / superpowers-only) and placed skill chaining in the governance layer. This decision moves chaining from static prose into a machine-readable event system while preserving the layered ownership model.

## Decision

Replace the prose chaining table with an event-driven orchestrator. Seven design decisions define the architecture:

### 1. Event bus — file-based, JSONL, append-only

Events are recorded in `.agents/events.jsonl` using JSONL format (one JSON object per line). The log is append-only within a session. Events carry a type, timestamp, source skill, and payload. This is the canonical coordination medium.

### 2. Per-worktree event files — no contention, no locks

Each worktree or session writes to `events/<id>.events.jsonl`. The orchestrator in main compiles worktree event files into the trunk `events.jsonl`. This eliminates write contention across parallel agents without requiring file locks or coordination protocols.

### 3. Emission via scripts, not prose

Skill scripts — which already run deterministic operations (specwatch, tk close, lifecycle stamping) — emit events as a side effect. The agent doesn't have to remember to emit; the tool does it. This addresses emission reliability at the source. If a skill has a bash script that closes a ticket, that script appends the event. The LLM never writes to the event log directly.

### 4. State derivation as reliability fallback

The orchestrator cross-references tk (ticket state) and specgraph (artifact phase transitions) to synthesize events for transitions that occurred without emission. The event log is the fast path for coordination; state derivation is the consistency layer. This means the system is eventually consistent even when a skill script fails to emit or the agent bypasses the script.

### 5. Subscription registry — machine-readable dispatch

`subscriptions.json` maps event types to handlers with metadata:

- `handler` — the skill or script to invoke
- `mode` — `interactive` (requires operator) or `delegable` (safe for subagent)
- `model` — cognitive tier hint (opus/sonnet/haiku)
- `prompt_seed` — context to include when invoking the handler

This replaces the prose table with a format that tools can parse, skills can register into, and third parties can extend without editing governance.

### 6. Orchestrator is a recommender, not a dispatcher

The orchestrator reads the event log, evaluates subscriptions, and outputs text instructions describing what should happen next. It does not invoke skills directly. The agent runtime decides how to execute (inline, subagent, deferred). This makes the orchestrator portable across all AGENTS.md-compatible tools — all it requires is bash and the ability to read text recommendations.

### 7. Gradual adoption — prose table coexists with subscriptions

During migration, the AGENTS.md prose table and `subscriptions.json` coexist. The agent checks the prose table first and runs the orchestrator second. Skills migrate individually from table rows to subscription entries; the table shrinks over time. When the table is empty, it is removed. This avoids a big-bang migration and lets each skill validate its subscription independently.

## Alternatives Considered

**Keep the static table.** The table works at current scale (8 rows) and is immediately readable by any LLM. However, it cannot handle cross-session handoffs, cannot be extended by third-party skills, and requires governance edits for every new chain. Rejected because the complexity trajectory is upward — the table will only grow as skills multiply.

**Full event bus replacing table immediately (big bang).** Architecturally cleaner but operationally riskier. Every skill must emit events correctly from day one, and any missed emission breaks coordination with no fallback. Rejected in favor of gradual adoption where the prose table serves as a safety net during migration.

**Orchestrator dispatches directly** (runtime-specific invocations). The orchestrator could invoke skills using Claude Code's skill system or similar runtime APIs. Rejected because it would tie the architecture to a single runtime's invocation mechanism. The recommender pattern is portable: any runtime that can read text and invoke commands can follow orchestrator output.

**Prose-level event descriptions** (skills describe events in SKILL.md, agent mentally reconstructs graph). Each skill's SKILL.md would document what events it emits and consumes, and the agent would mentally assemble the dispatch graph. Rejected because it scatters the dispatch table across 10+ files, makes the full graph invisible, complicates debugging, and the "dispatcher" is still an LLM interpreting prose — gaining no machine-readability benefits.

## Consequences

**Positive:**

- Cross-session handoffs work: dispatched agents write events, the next session's orchestrator picks them up and recommends follow-on actions
- Third-party skills subscribe to events without editing governance files
- Machine-readable coordination enables tooling: swain-status can show pending events, audit trails are automatic, event replay is possible
- Portable across agent runtimes — the orchestrator needs only AGENTS.md support and bash
- State derivation fallback means the system is eventually consistent even when event emission is missed
- Governance hash churn is eliminated for new chains — they go into subscriptions.json, not AGENTS.md

**Negative / Trade-offs:**

- More infrastructure to maintain: event log format, subscription registry schema, orchestrator script, per-worktree event compilation
- Mixed period during gradual adoption where some chains live in the prose table and others in subscriptions.json — agents must check both
- Emission reliability depends on skill scripts remembering to write events; state derivation catches misses but adds latency
- The subscription registry schema is a new contract that all participating skills must conform to
- The recommender pattern adds a layer of indirection compared to direct dispatch — the agent must interpret and act on recommendations

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-17 | — | Initial creation from INITIATIVE-009 design session |
