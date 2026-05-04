---
title: "Chat Bridge Architecture Comparison: swain-helm vs golembot vs kimaki vs open-dispatch"
artifact: SPIKE-073
track: container
status: Active
author: cristos
created: 2026-04-24
last-updated: 2026-04-24
parent-initiative: INITIATIVE-018
parent-vision: VISION-006
question: "Should swain-helm's Python-native chat bridge be replaced with or influenced by an existing multi-channel/multi-runtime agent gateway (golembot, kimaki, or open-dispatch)?"
gate: Pre-MVP
risks-addressed:
  - Reinventing solved patterns (channel abstraction, engine abstraction, session persistence) if comparable tools already exist.
  - Locking into a Python-only stack that cannot reach platforms with TS/JS-only SDKs (Slack Bolt, Discord.js, Grammy).
  - Committing to swain-helm's current supervisor protocol before validating it against alternative designs.
trove: agentic-runtime-chat-adapters
linked-artifacts:
  - INITIATIVE-018
  - VISION-006
depends-on-artifacts: []
---

# Chat Bridge Architecture Comparison

## Summary

<!-- Populated at Active → Complete transition. Leave empty during research. -->

## Question

Should swain-helm's Python-native chat bridge be replaced with or influenced by an existing multi-channel/multi-runtime agent gateway? Three candidates are captured in the [agentic-runtime-chat-adapters](../../../troves/agentic-runtime-chat-adapters/) trove (collected 2026-04-24):

- **golembot** — TS/Node, multi-channel + multi-engine gateway. MIT. Active.
- **kimaki** — TS/Node, Discord + OpenCode only, with native worktree management. MIT. Active.
- **open-dispatch** — JS/Node, Slack/Teams/Discord + OpenCode/Claude. MIT. Simpler surface.

The current swain-helm architecture is Python supervisor-first: `watchdog.py` manages plugin subprocesses via a line protocol, with adapters for Zulip, Claude Code, OpenCode, and tmux panes.

## Go / No-Go Criteria

The spike produces a decision matrix across the dimensions listed in *Investigation Plan*. The recommendation must be one of:

- **Go (adopt)** — replace swain-helm's chat bridge layer with one of the three candidates. Requires:
  - A concrete LOC estimate for the swap (adapter writes, protocol rewrites, config migration).
  - A named operational owner for the new runtime (Node version pinning, dependency updates).
  - An upstream-coupling plan (fork vs patch vs vendor).
- **No-Go (retain)** — keep swain-helm's Python stack. Requires:
  - A named pattern from each candidate that swain-helm should absorb (abstraction shape, event model, session keying).
  - Issue references on the swain-helm backlog for each absorbed pattern.
- **Hybrid** — adopt one candidate as a sibling service. Keep swain-helm for specific surfaces. Example: keep Python for Zulip and the supervisor, delegate Slack and Discord to a candidate. Requires:
  - A named process-boundary contract between swain-helm and the sibling service.
  - An operational cost estimate for running both runtimes.

## Pivot Recommendation

If all three candidates fail the fit test, keep swain-helm as-is. File follow-up specs for the concrete capability gaps — multi-channel, richer StreamEvent, provider failover, fleet coordination.

## Findings

### Context: the three candidates

Full source captured in `docs/troves/agentic-runtime-chat-adapters/sources/` for golembot, kimaki, and open-dispatch.

- **golembot** (`0xranx/golembot`, v0.46.0). Architecture: `ChannelAdapter` + `AgentEngine` + `Gateway`. One gateway process binds to one workspace dir at boot. Channels: Slack, Telegram, Discord, Feishu, DingTalk, WeCom, WeChat. Engines: claude-code, codex, cursor, opencode. Fleet registry for peer discovery. Rich `StreamEvent` union carries tool calls, cost, and turn counts. `KeyedMutex` guards per-session concurrency. Provider config supports failover to a backup LLM.

- **kimaki** (`remorses/kimaki`). Discord-only, OpenCode-only. Runtime is thread-per-session with event-sourced state. **Channel topic XML tags** bind each Discord channel to a directory: `<kimaki><directory>/path/to/project</directory></kimaki>`. This is the routing primitive golembot would need a patch for. Worktree management is a **first-class chat command surface** — `/new-worktree`, `/merge-worktree`, `/worktrees`, `/add-dir`. Session state lives in SQLite. Lock port enforces single-instance. SIGUSR2 triggers graceful restart.

- **open-dispatch** (`nichochar/open-dispatch`). `ChatProvider` base class backs Slack, Teams, and Discord. Runtime adapters: `opencode-core`, `claude-core`. Central `bot-engine` routes messages. No worktree commands. No topic routing. No Zulip. Simpler than the other two.

### Current swain-helm architecture

Python supervisor-first:

| Module | LOC | Role |
|--------|-----|------|
| `watchdog.py` | 477 | Supervisor loop: spawn, health-check, restart plugin subprocesses. |
| `protocol.py` | 590 | Line-protocol message types (ConfigMessage, Command, Event) and encode/decode. |
| `bridges/project.py` | 580 | Per-project bridge — coordinates runtime + chat adapters for one project. |
| `plugin_process.py` | 170 | Subprocess lifecycle (fork, stdin/stdout wiring, shutdown). |
| `provision.py` | 177 | First-time setup. |
| `session_registry.py` | 126 | Cross-project session tracking. |
| `worktree_scanner.py` | 162 | Discovers worktrees and maps them to bridges. |
| `adapters/zulip_chat.py` | 253 | Zulip `ChannelAdapter` plugin. |
| `adapters/claude_code.py` | 289 | Claude Code CLI runtime plugin. |
| `adapters/opencode.py` | 170 | OpenCode CLI runtime plugin. |
| `adapters/opencode_server.py` | 825 | OpenCode server runtime plugin. |
| `adapters/tmux_pane.py` | 311 | Tmux pane runtime plugin. |

Total: ~4,675 LOC Python. Chat surface today: Zulip only, one stream per project, one topic per worktree.

### Investigation plan

Score each candidate on these dimensions:

1. **Workspace/worktree routing model** — can one process serve many workspaces? How is the workspace selected per message? Does it support Zulip's stream-per-project, topic-per-worktree layout, or Slack's channel-per-worktree layout?
2. **Channel abstraction** — what does the `ChannelAdapter` (or equivalent) interface require? What capabilities are pluggable (reply, typing, status updates, history fetch, read receipts)?
3. **Engine abstraction** — what does the agent-engine interface require? What does a new engine need to implement?
4. **Supervisor model** — does the project assume you run one process, or does it expect an external supervisor? What's the restart/health-check story?
5. **Session/state persistence** — where is session state stored? What's the scope (per-chat, per-workspace, global)? How does it handle engine swaps mid-session?
6. **Channel extensibility** — concretely, how many LOC to add Zulip?
7. **Engine extensibility** — concretely, how many LOC to add or change an engine?
8. **Language/runtime** — Node/TS, JS, Rust, Python. Maintenance cost of adding that runtime to swain's stack.
9. **LOC to swap** — how much of swain-helm would be replaced, rewritten, or retained?
10. **Operational cost** — number of processes, upstream coupling risk, dependency surface.

### Decision matrix (to populate)

| Dimension | swain-helm (current) | golembot | kimaki | open-dispatch |
|-----------|---------------------|----------|--------|---------------|
| Workspace routing | Per-project bridge, Python-driven | One dir per process; fleet for multi | **Channel topic → directory (native)** | One bot, no topic-routing |
| Channel abstraction | Subprocess plugin protocol | `ChannelAdapter` interface, ~130 LOC | Discord-specific, not abstracted | `ChatProvider` base class |
| Engine abstraction | Subprocess plugin protocol | `AgentEngine` interface | OpenCode-only, not abstracted | `opencode-core`, `claude-core` |
| Supervisor model | First-class (`watchdog.py`) | External (user runs process) | External, lock-port enforced | External |
| Session persistence | `session_registry.py` (Python) | `.golem/sessions.json` per dir | SQLite per bot | In-memory per bot |
| New channel LOC | Full Python plugin (~250+ LOC) | ~300 LOC TS (Slack/Telegram precedent) | Requires new abstraction layer | ~250 LOC JS (provider precedent) |
| New engine LOC | Full Python plugin (~250+ LOC) | ~300 LOC TS (engine precedent) | Requires new abstraction layer | ~200 LOC JS (core precedent) |
| Language/runtime | Python 3.12 | Node ≥ 20, TS | Node ≥ 20, TS | Node ≥ 18, JS |
| LOC retained from swain-helm | 100% | watchdog, provision, session_registry (~800 LOC) | watchdog, worktree_scanner (~640 LOC) | watchdog, session_registry (~700 LOC) |
| LOC discarded from swain-helm | 0 | adapters/, bridges/, protocol.py, plugin_process.py (~3,800 LOC) | adapters/, bridges/, protocol.py, plugin_process.py (~3,800 LOC) | adapters/, bridges/, protocol.py, plugin_process.py (~3,800 LOC) |
| Upstream coupling | None | Medium (patch needed for `workspaceRouter`) | Low (use as-is until extending) | Low (use as-is) |
| Operational cost | 1 Python process per project | N Node processes (one per workspace, or 1 + patch) | 1 Node process for all channels | 1 Node process for all channels |

*Entries are initial estimates from source reading; each row needs validation against the captured source before concluding.*

### Open questions to resolve in the spike

- **Golembot's `workspaceRouter` patch** — is it ~100 LOC TS as estimated? Does engine invocation have hidden workspace coupling? Read `gateway.ts:966-1150` and `index.ts:258` end-to-end.
- **Kimaki's abstraction extensibility** — is `ThreadSessionRuntime` Discord-specific? Or does it factor out a reusable thread/channel abstraction? See [SPIKE-074](../../Complete/(SPIKE-074)-Kimaki-Extensibility-And-Python-Rewrite/(SPIKE-074)-Kimaki-Extensibility-And-Python-Rewrite.md).
- **Open-dispatch's ChatProvider sufficiency** — does the `ChatProvider` interface expose thread or topic semantics? Would those let Zulip topics map to workspace directories? Read `src/providers/chat-provider.js`.
- **Process-per-workspace scaling** — a user with 10 worktrees would run 10 golembot processes. Is that acceptable? Measure memory per idle golembot. Does each hold an open HTTP server and SSE connection?
- **Fleet coordination cost** — does golembot's fleet registry need an external broker (Redis, etcd)? Or is it filesystem-based? What happens when a peer crashes mid-session?

### Evaluation artifacts to produce

1. **Annotated decision matrix** — each cell backed by a source reference (file:line from the trove).
2. **LOC swap estimate per path** — concrete counts for "adopt + patch golembot", "adopt + extend kimaki", "adopt + extend open-dispatch", "keep swain-helm + absorb patterns".
3. **Capability gap list** — for each candidate, what would still need to be written (e.g., Zulip adapter for golembot; second engine for kimaki).
4. **ADR recommendation** — draft an ADR proposing the chosen direction with alternatives table.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-24 | — | Initial creation (user-requested; skips Proposed). |
