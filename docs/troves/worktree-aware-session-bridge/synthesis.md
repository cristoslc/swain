# Synthesis: Worktree-Aware Session Bridge

Prior art for building a worktree-aware chat bridge that lets an operator control agent sessions from any device. This trove covers session management, worktree isolation, process supervision, notification, and memory — the components needed to compose or build swain-helm.

## Key findings

### No single project combines chat bridge + worktree awareness + watchdog supervision

The landscape has strong individual pieces but no complete composition:

- **Agent of Empires** comes closest — it combines tmux session management with git worktree integration and Docker sandboxing. But it has no chat bridge (it's a local TUI) and no persistent watchdog.
- **Kimaki** and **GolemBot** provide the chat-to-agent routing layer, but neither discovers git worktrees or maps chat topics to branches.
- **opencode-pilot** is the closest to a watchdog pattern — it's a daemon that polls for work and spawns sessions. But it polls GitHub/Linear, not git worktrees.
- **hcom** provides inter-agent messaging with collision detection, but agents communicate with each other, not with a chat app.

### The worktree → topic → session mapping is unique to swain-helm

No existing project polls `git worktree list --porcelain` every 15s and maps each branch to a chat topic + agent session. This is the core novelty. The closest analogs are:

- **Agent of Empires** manages worktrees but maps them to tmux panes, not chat topics.
- **opencode-pilot** creates worktrees per GitHub issue but doesn't map them to chat channels.
- **Micode** uses worktree isolation in its brainstorm-plan-implement flow but has no chat dimension.

### Chat adapter patterns are well-established and composable

Three distinct adapter architectures emerged:

1. **Platform SDK adapters (GolemBot)** — Implement a `ChannelAdapter` interface per platform (Feishu, Slack, Telegram, Discord, DingTalk, WeCom, WeChat). Each adapter handles platform-specific message formatting, threading, and event subscription. The gateway routes messages through a pluggable engine. This is the most modular approach.

2. **Single-platform bots (Kimaki, opencode-telegram-bot)** — One adapter per platform, deeply integrated with platform features (Discord threads, Telegram inline keyboards). These are more complete for their platform but harder to reuse across protocols. Kimaki's Discord thread-per-session model is particularly close to swain-helm's topic-per-worktree pattern.

3. **Multi-protocol bridges (Open Dispatch)** — `ChatProvider` abstract class with implementations for Slack, Teams, and Discord. Uses Socket Mode (Slack), Bot Framework (Teams), and discord.js. Session persistence is in-memory only — sessions are lost on restart.

### The borrow-vs-build decision for chat adapters

**Borrow GolemBot's adapter interface** if going multi-platform. Its `ChannelAdapter` abstraction is clean and well-documented. The engine abstraction (claude-code, codex, cursor, opencode) maps to swain-helm's runtime adapter concept. License: MIT.

**Borrow Kimaki's thread-session mapping** if going Zulip. Kimaki creates a Discord thread per session — structurally identical to swain-helm's topic-per-worktree pattern. The `thread-session-runtime.ts` and `thread-runtime-state.ts` files are the most relevant. License: BUSL-1.1 (commercial use requires license).

**Borrow Open Dispatch's provider pattern** for quick Slack/Teams integration. The `ChatProvider` base class is simple and protocol-agnostic. License: MIT.

**Build the Zulip adapter from scratch** using the python-zulip-api. None of these projects target Zulip. The Zulip adapter will need: event queue subscription, topic-based threading (Zulip topics map directly to worktree branches), and stream management (one stream per project). The `agentic-runtime-chat-adapters` trove has Zulip-specific research in `chat-server-features`.

### Session management patterns

**opencode-sessions** provides a minimal `session` tool with 4 modes (message, new, compact, fork). It runs inside the opencode plugin lifecycle with no daemon. Good reference for the session protocol layer. License: MIT.

**opencode-agent-tmux** auto-spawns tmux panes per agent session, manages lifecycle (idle detection, cleanup), and includes a zombie reaper for orphaned processes. This maps to swain-helm's watchdog bridge supervision. The smart wrapper (`opentmux`) provides multi-port detection. License: MIT.

**Pilot** is the best reference for the watchdog pattern. It's a Node.js daemon that polls for work, evaluates readiness, spawns sessions via HTTP API, and persists state. Its config layering (presets < defaults < repo < source) is worth borrowing. License: MIT.

### Notification patterns

**opencode-notify** uses event-driven notifications (session.idle, session.error, session.permission) with deduplication and terminal focus detection. Good pattern for the "task complete" notification that swain-helm needs. License: MIT.

**opencode-ntfy.sh** uses push notifications via ntfy.sh, which would work for the mobile use case swain-helm targets. The SDK-based backend (`opencode-notification-sdk`) provides event routing and suppression. License: MIT.

### Memory and handoff patterns

**opencode-agent-memory** uses Letta-style editable memory blocks (global + project scope) with YAML frontmatter, injected into the system prompt. Three tools (list, set, replace). This maps to swain-helm's artifact-on-disk philosophy — the bridge doesn't need to manage memory if swain skills already do it. License: MIT.

**opencode-mem** uses SQLite + USearch vector store with auto-capture on idle, profile-based memory scopes, and compaction recovery. More sophisticated than what swain-helm needs (swain skills already handle artifact persistence). License: MIT.

**Handoff** creates focused continuation prompts for new sessions. This bridges the "what was I working on?" gap between chat sessions. The `read_session` tool accesses the previous transcript. Directly relevant to swain-helm's session continuity across bridge disconnections. License: MIT.

## Points of agreement

- All projects assume a running agent process (opencode serve, Claude Code, Codex, etc.) — the bridge connects to it rather than replacing it.
- File-based session state (JSON, SQLite) is the common persistence mechanism. No project uses a database server.
- Git worktree awareness is emerging but not yet universal. Agent of Empires, Micode, and Pilot all use worktrees but for different purposes.
- The "one session per unit-of-work" pattern is standard — whether that unit is a GitHub issue (Pilot), a Discord thread (Kimaki), or a git worktree (swain-helm).

## Points of disagreement

- **Daemon vs. plugin:** Pilot is a standalone daemon. opencode-sessions, opencode-agent-tmux, and opencode-notify run as opencode plugins inside the agent lifecycle. swain-helm needs to be a daemon (it manages processes outside the agent).
- **Session persistence:** Open Dispatch uses in-memory sessions (lost on restart). Kimaki uses SQLite. Agent of Empires uses TOML config. swain-helm uses JSON per-project files.
- **Threading model:** Kimaki uses Discord threads (one thread per session). GolemBot uses smart mode (mention-only when idle, always respond when active). swain-helm uses Zulip topics (one topic per worktree branch). These are different mappings but structurally similar.

## Gaps

- **No project bridges chat topics to git worktrees.** This is swain-helm's unique contribution.
- **No project provides a watchdog that reconciles desired state against running processes** (except Pilot, which reconciles work queues, not process states). swain-helm's watchdog fills this gap.
- **Approval flows for async remote operation remain unsolved.** No project provides a general "route this approval request to a chat surface and wait for a response" mechanism.
- **Zulip-specific adapter code doesn't exist in the ecosystem.** The Zulip adapter must be built from scratch using python-zulip-api.

## License summary

| Project | License | Notes |
|---------|---------|-------|
| Kimaki | BUSL-1.1 | Commercial use requires license. Cannot borrow code directly for MIT project. |
| GolemBot | MIT | Fully permissive. Adapter interface is borrowable. |
| Open Dispatch | MIT | Fully permissive. Provider pattern is borrowable. |
| hcom | MIT | Fully permissive. Messaging patterns are borrowable. |
| opencode-telegram-bot | MIT | Fully permissive. SSE/event pattern is borrowable. |
| Agent of Empires | MIT | Fully permissive. Worktree + tmux patterns are borrowable. |
| opencode-worktree | MIT | Fully permissive. |
| Micode | MIT | Fully permissive. |
| Pocket Universe | MIT | Fully permissive. |
| opencode-sessions | MIT | Fully permissive. |
| opencode-agent-tmux | MIT | Fully permissive. |
| Pilot | MIT | Fully permissive. |
| opencode-notify | MIT | Fully permissive. |
| opencode-ntfy.sh | MIT | Fully permissive. |
| opencode-agent-memory | MIT | Fully permissive. |
| opencode-mem | MIT | Fully permissive. |
| opencode-handoff | MIT | Fully permissive. |