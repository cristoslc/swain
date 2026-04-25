---
title: "Kimaki Extensibility and Python Rewrite Viability"
artifact: SPIKE-074
track: container
status: Complete
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

**Verdict: Refactor Required (B) — Recommend Hybrid approach (steal patterns, extend swain-helm).**

Kimaki does not have a `ChannelAdapter` or `AgentEngine` interface. `ThreadSessionRuntime` holds a Discord `ThreadChannel` directly and imports Discord.js types throughout. The Slack bridge works by *impersonating the Discord API*, not via a shared abstraction. Extending kimaki to Zulip requires either (a) building another API-impersonation bridge (~3,500 LOC TS, high maintenance) or (b) extracting adapter interfaces from the runtime (~1,500 LOC refactor before any extension work). The full Python port would cost ~8,300 LOC (1.5× current swain-helm), breaching the self-imposed ceiling. The recommended path is **steal kimaki patterns into swain-helm** — port the channel-topic→directory parser, worktree command patterns, and event-sourced session state model, while keeping swain-helm's existing Zulip adapter, NDJSON protocol, and multi-engine bridge architecture.

## Question

This spike assumes [SPIKE-073](../../Active/(SPIKE-073)-Chat-Bridge-Architecture-Comparison/(SPIKE-073)-Chat-Bridge-Architecture-Comparison.md) picks kimaki. Two concrete questions follow.

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

### Refined module-by-module mapping — swain-helm → kimaki equivalent

| swain-helm module | LOC | Kimaki equivalent | Port decision |
|-------------------|-----|-------------------|---------------|
| `watchdog.py` | 502 | (external — lock port + SIGUSR2) | **Retain** swain-helm |
| `protocol.py` | 608 | (in-process runtime eliminates this) | **Retain** (essential for subprocess plugin model) |
| `bridges/project.py` | 611 | `ThreadSessionRuntime` + `channel-management.ts` | **Steal patterns** (state machine, turn interruption) |
| `plugin_process.py` | 170 | (in-process — not needed in kimaki) | **Retain** (needed for subprocess plugin model) |
| `provision.py` | 199 | (no direct equivalent) | **Retain** swain-helm |
| `session_registry.py` | 126 | SQLite `discord-sessions.db` via Prisma | **Retain** (simpler, adequate) |
| `worktree_scanner.py` | 162 | kimaki's worktree commands | **Retain** + steal pattern |
| `adapters/zulip_chat.py` | 600+304 | Would become a kimaki ChannelAdapter | **Retain** (already works) |
| `adapters/claude_code.py` | 289 | Would become a kimaki AgentEngine | **Retain** (already works) |
| `adapters/opencode.py` | 170 | kimaki's `opencode.ts` | **Steal SSE client pattern** |
| `adapters/opencode_server.py` | 825 | kimaki's `opencode.ts` server lifecycle | **Steal session lifecycle pattern** |
| `adapters/tmux_pane.py` | 311 | (no equivalent — kimaki is chat-only) | **Retain** (unique capability) |
| `config.py` | 140 | kimaki's `config.ts` | **Retain** (1Password integration) |
| `opencode_discovery.py` | 325 | kimaki's `opencode.ts` health checks | **Retain** (port scanning already works) |

**Total retainable: ~3,716 LOC** (retained as-is or with stolen patterns layered in)
**Total steal-only: ~0 LOC new** (patterns ported into existing modules, not new files)
**Total discardable only if fully adopting kimaki: ~1,801 LOC** (protocol, plugin_process, provision — but these are *essential* to swain-helm's architecture, not replaceable by kimaki)

### Findings — Question 1: Extensibility

**Answer: Refactor Required (B).**

**1. No `ChannelAdapter` interface exists.**

Kimaki's Slack integration (`discord-slack-bridge`) does NOT use a shared abstraction. It works by *impersonating the Discord API* — a translation proxy that receives Slack webhooks, translates them into Discord gateway events, and feeds them to an unmodified `discord.js` client. The `ThreadSessionRuntime` only ever sees Discord-shaped objects.

Key evidence:
- `thread-session-runtime.ts` line 9: `import { ChannelType, type ThreadChannel } from 'discord.js'` — the runtime holds a `ThreadChannel` directly as a readonly field.
- `RuntimeOptions` (line 180-185) takes `thread: ThreadChannel` — a Discord.js type.
- All message output flows through `sendThreadMessage` from `discord-utils.ts`, which calls Discord REST APIs.
- `discord-bot.ts` (1,368 lines) is deeply intertwined with Discord.js event types (`Events.MessageCreate`, `Events.ThreadCreate`, `Events.ThreadDelete`).
- The Slack bridge (~3,500 LOC) reimplements Discord's REST API and Gateway protocol to make discord.js think it's talking to Discord when it's actually talking to Slack.

**2. No `AgentEngine` interface exists.**

The OpenCode integration (`opencode.ts`, 1,250 LOC) is directly embedded. The `ThreadSessionRuntime` calls `getOpencodeClient()`, `client.session.create()`, `client.event.subscribe()`, etc. There is no abstraction layer that would let you swap in Claude Code or another engine.

**3. Minimum files to modify for Zulip support:**

*Bridge approach* (impersonating Discord API, like Slack bridge):
- New package: `discord-zulip-bridge` (~3,000–3,500 LOC TS)
- Zero changes to `ThreadSessionRuntime`
- Requires running a fake Discord API server alongside Zulip event polling
- High maintenance cost: must track every Discord API change

*Adapter extraction approach* (clean refactoring):
- Extract interface from `ThreadSessionRuntime`: `ChannelAdapter` (~300 LOC TS for interface)
- Implement `DiscordChannelAdapter`: move Discord-specific code from `ThreadSessionRuntime` and `discord-bot.ts` (~800 LOC moved, ~200 LOC new)
- Implement `ZulipChannelAdapter`: ~500 LOC TS new
- Modify: `discord-bot.ts`, `thread-session-runtime.ts`, `discord-utils.ts`
- Total: ~1,500 LOC refactor before any extension, then ~500 LOC per new channel

**4. Minimum files to modify for Claude Code engine support:**

- Extract `AgentEngine` interface from `opencode.ts`: ~200 LOC TS for interface
- Implement `OpenCodeEngine`: move code from `opencode.ts` (~600 LOC moved, ~100 LOC new)
- Implement `ClaudeCodeEngine`: ~400 LOC TS new (subprocess management + stream-json parsing)
- Modify: `opencode.ts`, `thread-session-runtime.ts`, session startup flow
- Total: ~700 LOC refactor before engine extension, then ~400 LOC per new engine

**5. Slash command dispatch is Discord-coupled.**

`interaction-handler.ts` routes ~30 slash commands registered via Discord's application command API. Commands like `/new-worktree` and `/merge-worktree` dispatch through Discord interaction objects. Adding Zulip would require either:
- A Zulip custom command handler that translates to the same command surface (moderate effort, duplicated dispatch)
- Extracting a platform-agnostic command registry (significant refactor)

### Findings — Question 2: Port vs Adopt

**Adopt (extend kimaki TS runtime):**

| Cost Item | Estimate |
|-----------|----------|
| Node ≥ 20 runtime in ops stack | Low (one-time) |
| Upstream coupling (fork, patch, vendor) | Ongoing maintenance |
| Adapter extraction refactor | ~1,500 LOC |
| Zulip ChannelAdapter | ~500 LOC |
| Claude Code engine | ~400 LOC |
| Migrate swain-helm Zulip logic | ~900 LOC moved to TS |
| Operational cost (npm/pnpm in CI, Node SBOM) | Ongoing |
| Discard swain-helm Python code (~5,500 LOC) | Total loss of tested infrastructure |
| **Total estimated TS effort** | **~3,300 LOC new + 1,500 LOC refactor** |

**Port (rebuild kimaki architecture in Python):**

| Module | Estimated LOC |
|--------|--------------|
| Event-sourced session runtime (replaces `bridges/project.py`) | ~800 |
| Channel→directory routing (XML topic parser equivalent) | ~200 |
| Worktree command surface | ~400 |
| SQLite session store (replaces `session_registry.py`) | ~150 |
| Thread-per-session lifecycle manager | ~600 |
| SSE streaming client (replace `opencode_server.py` patterns) | ~500 |
| Message formatting, typing indicators, text batching | ~350 |
| Slash command dispatch | ~300 |
| Remaining adapter wiring | ~500 |
| **Total estimated new Python LOC** | **~3,800** |
| **Plus retained swain-helm LOC** | **~3,700** |
| **Combined total** | **~7,500** (exceeds 1.5× current swain-helm ≈ 7,000 LOC ceiling) |

A full Python port breaches the 7,000 LOC ceiling. The port also loses upstream bug fixes, pattern evolution, and the extensive kimaki test suite.

**Hybrid (steal patterns into swain-helm):**

| Pattern to steal | Source in kimaki | swain-helm target | Estimated effort |
|-------------------|-------------------|-------------------|-------------------|
| Event-sourced state model (busy/idle/completion detection from SSE events) | `event-stream-state.ts`, `thread-runtime-state.ts` | `bridges/project.py` session state machine | ~400 LOC |
| Channel→directory metadata (topic-based project directory mapping) | `channel-management.ts` (SQLite-based) | `adapters/zulip_chat.py` topic registration | ~200 LOC |
| Preprocess chain (serialized async preprocessing before dispatch) | `thread-session-runtime.ts` `preprocessChain` | `bridges/project.py` turn handling | ~150 LOC |
| Worktree command patterns (create, merge, status from chat) | `commands/new-worktree.ts`, `merge-worktree.ts` | `bridges/project.py` worktree commands (already partially present via `worktree_scanner.py`) | ~200 LOC |
| Permission/approval flow (interactive permission prompts in chat) | `commands/permissions.ts`, `thread-session-runtime.ts` approval handling | `bridges/project.py` approval relay (partially implemented) | ~200 LOC |
| **Total estimated new/modified LOC** | | | **~1,150 LOC** |

This stays well within budget and preserves all working swain-helm infrastructure.

### Decision

**Recommendation: Hybrid (steal patterns, keep swain-helm).**

Rationale:
1. **Extensibility answer is B (refactor required).** Kimaki is not plug-and-play for new channels. Adding Zulip would require ~1,500 LOC of adapter extraction before any extension work, or ~3,500 LOC of API-impersonation bridge code (high maintenance).
2. **The hybrid path costs ~1,150 LOC** — porting only the patterns that matter — against the adopt path's ~3,300 LOC new + 1,500 LOC refactor, and the port path's ~7,500 LOC total.
3. **Swain-helm already has working Zulip and Claude Code adapters.** Discarding 5,500 LOC of tested Python to rewrite in TypeScript serves no purpose when the hybrid path gives us the architectural wins (event-sourced state, preprocess chains, approval flows) without the dual-runtime tax.
4. **The NDJSON subprocess plugin model** (`protocol.py` + `plugin_process.py`) is a strength, not a weakness — it's how swain-helm achieves multi-engine support (OpenCode, Claude Code, tmux) without in-process coupling. Kimaki's in-process model is simpler for one engine but less flexible for multi-engine orchestration.
5. **Upstream coupling risk** is real: kimaki is actively developed. A port would drift; an adopt would create a permanent fork-or-patch decision. Stealing specific patterns avoids both.

The next step is to create a SPEC that enumerates which kimaki patterns to port into swain-helm and in what order, starting with the event-sourced state model (highest impact on session reliability).

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
| Complete | 2026-04-24 | — | Findings complete. Verdict: Refactor Required (B). Recommendation: Hybrid — steal patterns into swain-helm. |
