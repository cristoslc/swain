---
title: "Orchestrator Integration"
artifact: EPIC-027
track: container
status: Proposed
author: cristos
created: 2026-03-17
last-updated: 2026-03-17
parent-initiative: INITIATIVE-009
depends-on:
  - EPIC-026
success-criteria:
  - subscriptions.json fully replaces the AGENTS.md "Superpowers skill chaining" prose table
  - Gradual adoption protocol works — LLM checks AGENTS.md table first, then runs orchestrator for event-driven dispatch
  - As skills migrate to subscriptions.json, corresponding AGENTS.md table rows are removed
  - Third-party skills can register subscriptions without modifying governance files
  - Interactive vs delegable dispatch modes work with model routing and prompt seeds
  - Superpowers skills chain correctly via subscriptions.json
linked-artifacts:
  - INITIATIVE-009
  - EPIC-026
---

# Orchestrator Integration

## Goal / Objective

Migrate governance from the AGENTS.md prose chaining table to subscriptions.json, enabling machine-readable, extensible skill coordination. Implement a gradual adoption protocol where the LLM checks AGENTS.md first (for not-yet-migrated chains) then runs the orchestrator for event-driven dispatch. As skills migrate, table rows are removed until the prose table is empty and can be deleted.

## Scope Boundaries

**In scope:**
- Governance migration plan: map each row of the current AGENTS.md chaining table to a subscriptions.json entry
- Gradual adoption protocol: dual-path dispatch (prose table fallback + orchestrator)
- Interactive vs delegable dispatch modes — interactive chains require operator presence, delegable chains can run in background agents
- Model routing via subscription metadata (model_hint field)
- Prompt seed templates for dispatched handlers
- Superpowers skill subscription entries (brainstorming, writing-plans, test-driven-development, etc.)
- Third-party skill registration — skills add entries to subscriptions.json without editing AGENTS.md
- Migration completion gate: when all rows are migrated, remove the prose table from AGENTS.md

**Out of scope:**
- Event bus implementation (EPIC-025)
- Query layer implementation (EPIC-026)
- Status dashboard changes (EPIC-028)
- Runtime model selection implementation — subscriptions carry hints, but routing is the runtime's responsibility

## Design Decisions

1. **Gradual migration** — no big-bang cutover; both dispatch paths coexist during transition
2. **Subscriptions own the chain definition** — AGENTS.md becomes documentation-only once migration completes
3. **Mode field enables safe delegation** — `interactive` chains wait for operator; `delegable` chains can be dispatched to background agents via swain-dispatch
4. **Orchestrator is a recommender, not a dispatcher** — The orchestrator outputs text instructions that any agent runtime can follow (e.g., "ACTION: transition SPEC-012 to Complete / CONTEXT: All tasks in plan closed / MODE: delegable"). The runtime decides how to execute — Claude Code uses skill invocations + subagents, OpenCode follows the text directly, Copilot uses /fleet, etc. This makes the orchestrator portable across all AGENTS.md-compatible tools.
5. **Cross-runtime portability** — Research showed 5 of 7 major agent runtimes (Codex CLI, OpenCode, Copilot CLI, Cursor, Windsurf) now support subagent dispatch with parallelism. AGENTS.md is a Linux Foundation standard. The subscription registry's mode/model/prompt_seed metadata is portable — most runtimes can spawn a subagent with a prompt. The runtime-specific adapter layer is thin: "spawn a subagent with this prompt" works nearly everywhere.
6. **Subscription registry dispatch hints** — The `mode: interactive|delegable` distinction maps across runtimes. "Delegable" means "can run without user interaction" — in Claude Code that's a subagent, in Codex that's a spawned agent, in Cursor that's a background agent. The `prompt_seed` is the portability mechanism — it's not "invoke skill X" but "here's what to do, as a prompt any LLM can follow."

## Migration Map (Current Table)

| Current Trigger | Current Chain | Target Subscription Event |
|----------------|---------------|--------------------------|
| Creating Vision/Initiative/Persona | swain-design -> brainstorming | `artifact.created` with filter on type |
| SPEC implementation | swain-design -> brainstorming -> writing-plans -> swain-do | `artifact.phase_transition` to Active for SPEC |
| Executing implementation tasks | swain-do -> test-driven-development | `task.claimed` |
| Dispatching parallel work | swain-do -> subagent-driven-development | `task.dispatch_requested` |
| EPIC terminal state | swain-design -> swain-retro | `artifact.phase_transition` to Complete for EPIC |
| Claiming work complete | verification-before-completion | `task.completion_claimed` |

## Child Specs

None yet — specs to be decomposed when this EPIC transitions to Active.

## Key Dependencies

- **EPIC-026 (Query Layer)** — the orchestrator uses the query layer to determine current state when evaluating subscriptions

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-17 | — | Initial creation as part of INITIATIVE-009 |
