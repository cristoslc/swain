---
title: "Kimaki Extensibility and Python Rewrite Viability"
artifact: SPIKE-074
track: container
status: Active
author: cristos
created: 2026-04-24
last-updated: 2026-04-24
parent-initiative: INITIATIVE-018
parent-vision: VISION-006
question: "If SPIKE-073 concludes kimaki is the closest architectural fit, (1) how much effort does it take to extend kimaki to Zulip and Claude Code, and (2) is it worth discarding swain-helm's Python code to reimplement kimaki's architecture in Python instead of adopting its TS runtime?"
gate: Pre-MVP
risks-addressed:
  - Kimaki's wins (channel-topic→directory routing, worktree commands, event-sourced session runtime) may be tightly coupled to Discord and OpenCode, forcing a ground-up rewrite to extend it.
  - Adopting kimaki's Node runtime creates a permanent dual-language stack (Python supervisor + Node chat bridge) with long-term maintenance cost.
  - A Python port loses upstream's bug fixes and pattern evolution; adopting upstream accepts Node runtime and upstream coupling.
trove: agentic-runtime-chat-adapters
linked-artifacts:
  - SPIKE-073
  - INITIATIVE-018
  - VISION-006
depends-on-artifacts:
  - SPIKE-073
---

# Kimaki Extensibility and Python Rewrite Viability

## Summary

<!-- Populated at Active → Complete transition. Leave empty during research. -->

## Question

This spike assumes [SPIKE-073](../(SPIKE-073)-Chat-Bridge-Architecture-Comparison/(SPIKE-073)-Chat-Bridge-Architecture-Comparison.md) picks kimaki. Two concrete questions follow.

1. **Extensibility.** What does kimaki need to support Zulip as a second channel and Claude Code as a second engine? Does its current design extend cleanly? Or does it need a new abstraction class first?

2. **Port vs adopt.** Is it worth throwing out swain-helm's Python code and porting kimaki's design into Python instead of adopting kimaki's TS runtime? Kimaki's design wins are: thread-per-session runtime, event-sourcing, channel-topic routing, and worktree commands.

## Go / No-Go Criteria

**Extensibility result** (question 1):

- **Clean extension** — kimaki already abstracts the channel and engine boundaries. Adding Zulip is ~300 LOC TS. Adding Claude Code is ~300 LOC TS. No new abstraction class needed.
- **Refactor required** — kimaki hardcodes Discord and OpenCode. A refactor must land first. Example: introduce a `ChannelAdapter` base class. Today's code references Discord.js types directly. Estimate refactor LOC before any extension work.
- **Rewrite required** — the hardcoding runs too deep. Core modules must be rewritten. Name which modules and why.

**Port vs adopt result** (question 2):

- **Adopt** — keep kimaki TS. Extend in-tree or upstream. Requires: acceptable Node runtime cost, an upstream patch plan, and a clear channel and engine extension path.
- **Port** — drop swain-helm's Python code. Rebuild kimaki's design in Python. Requires: port LOC at or below 1.5× current swain-helm (~7,000 LOC ceiling). Also requires a clear win over adopt — examples: tight Python integration with other swain tools, avoided dual-runtime tax.
- **Hybrid** — port only key patterns. Targets: channel-topic routing, worktree command surface. Keep the rest of swain-helm. Useful when extension is "refactor required" and refactor cost ≈ port cost.

## Pivot Recommendation

If kimaki needs a rewrite to extend, and the port cost exceeds 1.5× current swain-helm LOC, pivot back. Revisit the golembot or swain-helm paths in SPIKE-073. Kimaki becomes a pattern source, not a runtime choice.

## Findings

### Investigation plan — Question 1: Extensibility

Read kimaki's captured source in `docs/troves/agentic-runtime-chat-adapters/sources/kimaki/` end-to-end, with focus on the following files listed in its README:

**Session runtime (abstraction candidate):**
- `cli/src/session-handler/thread-session-runtime.ts` — is `ThreadSessionRuntime` Discord-specific, or does it take a generic thread/channel interface?
- `cli/src/session-handler/thread-runtime-state.ts` — state transitions. Are they tied to Discord event shapes?
- `cli/src/session-handler/event-stream-state.ts` — SSE event serialization into Discord messages. Is the SSE source OpenCode-specific?

**Discord adapter (what would become the "channel adapter" layer):**
- `cli/src/discord-bot.ts` — Discord event loop. What percentage of this file is Discord.js API calls vs runtime glue?
- `cli/src/discord-utils.ts` — formatting helpers. Reusable?
- `cli/src/discord-command-registration.ts` — slash command registration. Platform-coupled?
- `cli/src/channel-management.ts` — **XML topic parser for channel→directory routing**. Is this reusable across platforms, or does it assume Discord's topic/description field shape?

**OpenCode integration (what would become the "engine" layer):**
- `cli/src/opencode.ts` — server lifecycle (spawn, connect, manage).
- `cli/src/opencode-command.ts` — command dispatch.
- `cli/src/opencode-interrupt-plugin.ts` — interrupt handling.

**Worktree commands (what must be preserved):**
- `cli/src/worktree-utils.ts`, `cli/src/commands/*.ts` — are these command handlers Discord-coupled, or do they delegate all platform work to an adapter?

**Questions to answer from the reading:**

1. Is there a `ChannelAdapter`-like interface (explicit or implicit) in kimaki?
2. Is there an `AgentEngine`-like interface for the OpenCode integration?
3. What is the **minimum set of files** that must be modified or introduced to add Zulip as a second channel?
4. What is the **minimum set of files** that must be modified or introduced to add Claude Code as a second engine?
5. How does the slash command surface (`/new-worktree`, etc.) dispatch to platform-specific registration? Is it platform-agnostic at the core?

### Investigation plan — Question 2: Port vs adopt

Independent of the extensibility answer, estimate the cost and value of each path.

**Cost estimate: adopt kimaki (TS, upstream)**
- Add Node ≥ 20 runtime to swain's operational stack.
- Add upstream coupling: fork, patch, or vendor decision.
- Write Zulip ChannelAdapter (depends on question 1 answer).
- Write Claude Code engine (depends on question 1 answer).
- Migrate existing swain-helm bridges to kimaki's runtime model.
- Operational changes: Node version pinning, npm/pnpm in CI, Node SBOM.

**Cost estimate: port kimaki architecture to Python**
- LOC estimate per ported module (event-sourced runtime, SQLite session store, channel-topic→directory parser, worktree commands).
- Preserve swain-helm modules that don't need replacing (`watchdog.py`, `worktree_scanner.py`, `provision.py`).
- Discard or rewrite modules that conflict (`bridges/project.py`, `protocol.py`, `plugin_process.py`, the `adapters/` tree).
- Operational benefit: stay Python-only, no dual-runtime tax.
- Operational cost: carry the full architecture's maintenance instead of inheriting upstream fixes.
- **Key risk**: drift from upstream kimaki's design evolution — a 2026 port becomes a 2027 fork with custom patches.

**Value comparison**
- Integration with other swain skills: does swain-do, swain-session, swain-design benefit measurably from a Python-native bridge runtime? Concretely name the integration points and their LOC savings.
- Observability: Python-native gives shared logging, metrics, tracing with the rest of swain. Node adds a second telemetry surface.
- Upstream coupling: adopt accepts coupling, port avoids it. Weigh against kimaki's development velocity and active contributor count.

### Module-by-module mapping — swain-helm → kimaki equivalent

| swain-helm module | Kimaki equivalent | Port decision |
|-------------------|-------------------|---------------|
| `watchdog.py` | (external — kimaki uses lock port + SIGUSR2) | Retain swain-helm |
| `protocol.py` | (not needed — kimaki uses in-process runtime) | Discard on adopt, port on port |
| `bridges/project.py` | `ThreadSessionRuntime` + `channel-management.ts` | Replace |
| `plugin_process.py` | (not needed — in-process) | Discard |
| `provision.py` | (no direct equivalent) | Retain swain-helm |
| `session_registry.py` | SQLite `discord-sessions.db` | Replace |
| `worktree_scanner.py` | kimaki's worktree commands | Both complementary |
| `adapters/zulip_chat.py` | Would become a kimaki ChannelAdapter | Rewrite |
| `adapters/claude_code.py` | Would become a kimaki AgentEngine | Rewrite |
| `adapters/opencode.py` | kimaki's `opencode.ts` | Replace |
| `adapters/opencode_server.py` | kimaki's `opencode.ts` (server lifecycle) | Replace |
| `adapters/tmux_pane.py` | (no equivalent — kimaki is chat-only) | Retain if still needed, else drop |

*This mapping needs refinement after reading kimaki source in depth.*

### Decision criteria summary

Final recommendation lands as one of:

- **Adopt kimaki upstream, extend for Zulip + Claude Code.** Requires clean extension path from question 1.
- **Adopt kimaki upstream, vendor + patch.** Requires refactor-required extension path from question 1, where upstream won't accept the refactor.
- **Port kimaki architecture to Python.** Requires rewrite-required extension path *or* a compelling integration-with-swain argument that outweighs upstream inheritance.
- **Steal patterns from kimaki into swain-helm.** Fallback if neither adopt nor port is cost-effective — port only the channel-topic→directory parser and worktree command surface, keep the rest of swain-helm as-is.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-24 | — | Initial creation (user-requested; skips Proposed). Depends on SPIKE-073. |
