# Kimaki Source Code Snapshot

> Repository: https://github.com/remorses/kimaki  
> Cloned: 2026-04-23  
> License: MIT (Copyright 2025 Kimaki)

## Project Structure Overview

Kimaki is a monorepo (pnpm workspace) with ~10 packages. The core architecture is a **Discord bot** that bridges Discord threads to **OpenCode** coding-agent sessions, with a Slack bridge as a secondary channel.

```
kimaki/
├── cli/                     # Main bot + CLI entrypoint (the heart of the system)
│   ├── src/
│   │   ├── cli.ts           # CLI/setup entrypoint (OAuth, slash command registration)
│   │   ├── discord-bot.ts   # Core Discord event handler (MessageCreate, ThreadCreate)
│   │   ├── interaction-handler.ts  # Slash command + button/modal router
│   │   ├── opencode.ts      # OpenCode server manager (spawn, healthcheck, SDK client)
│   │   ├── session-handler/
│   │   │   ├── thread-session-runtime.ts  # Per-thread session orchestrator
│   │   │   ├── thread-runtime-state.ts    # Per-thread state (Zustand store)
│   │   │   ├── event-stream-state.ts      # SSE event derivation (busy/idle detection)
│   │   │   ├── model-utils.ts             # Model resolution, session startup context
│   │   │   └── agent-utils.ts             # Agent preference resolution
│   │   ├── database.ts      # LibSQL/Prisma persistence layer
│   │   ├── store.ts         # Zustand global state store
│   │   ├── message-formatting.ts      # Markdown ↔ Discord formatting
│   │   ├── message-preprocessing.ts   # Voice transcription, attachment handling
│   │   ├── channel-management.ts       # Discord channel/category creation
│   │   ├── system-message.ts           # System prompt assembly
│   │   ├── discord-utils.ts           # Discord API helpers (send, react, split)
│   │   └── commands/                  # Slash command implementations (~30 commands)
├── discord-digital-twin/    # Fake Discord server for E2E testing (REST + Gateway)
├── discord-slack-bridge/    # Discord ↔ Slack message bridge
├── slack-digital-twin/      # Fake Slack server for E2E testing
├── opencode-cached-provider/ # Model provider caching layer
├── opencode-deterministic-provider/ # Deterministic model responses for testing
├── libsqlproxy/             # LibSQL proxy (Cloudflare D1 compatibility)
├── db/                      # Shared Prisma schema package
└── skills/                  # Agent skills (Markdown-based)
```

## How the Discord Adapter Works

### Message Routing

The adapter in `discord-bot.ts` is the central message router. It listens to three Discord.js events:

1. **`Events.MessageCreate`** — Main ingress point. Two paths:
   - **Thread messages**: If the message arrives in a thread that has a known session (or was bot-created), it resolves the project directory, gets or creates a `ThreadSessionRuntime`, and calls `runtime.enqueueIncoming()`. This queues the message for serialized processing.
   - **Text channel messages**: If the channel has a project directory configured, it creates a new Discord thread, optionally creates a git worktree, then creates a runtime and enqueues the first prompt.

2. **`Events.ThreadCreate`** — Handles bot-initiated threads (via `kimaki send`). Parses a YAML embed footer marker (`ThreadStartMarker`) to extract prompt, agent, model, and worktree config. Creates runtime and starts a session.

3. **`Events.ThreadDelete`** / **`Events.ChannelDelete`** — Disposes runtimes and cleans up DB entries.

### Session Mapping

Each **Discord thread** maps 1:1 to an **OpenCode session**. The mapping is stored in the `thread_sessions` DB table. Key flow:

- `getOrCreateRuntime({ threadId, thread, projectDirectory, sdkDirectory })` looks up or creates a `ThreadSessionRuntime` in an in-memory `Map<string, ThreadSessionRuntime>`.
- The runtime holds: the Discord `ThreadChannel` object, project directory path, SDK directory (may differ for worktrees), and all session state.
- `getThreadSession(threadId)` in the DB provides persistence for recovery after bot restarts.

### Preprocessing Chain

Messages don't go directly to OpenCode. The runtime has a **preprocess chain** (`preprocessChain`) that serializes expensive async work (voice transcription, attachment download, context assembly) without blocking the event stream. The `IngressInput.preprocess` callback is awaited in arrival order, then the resolved prompt is dispatched.

### Event Stream → Discord Output

Once OpenCode processes a prompt, it emits SSE events via `client.event.subscribe()`. The runtime's `startEventListener()` runs a persistent loop that:

1. Subscribes to the OpenCode event stream with exponential backoff.
2. Feeds each event through `dispatchAction()` (a serialized action queue that prevents interleaving).
3. Routes events by type: `message.updated`, `message.part.updated`, `session.idle`, `session.error`, `permission.asked`, `question.asked`, etc.
4. Formats output parts (text, tool calls, tool results) into Discord messages via `formatPart()`.

### Slash Commands

`interaction-handler.ts` routes ~30 slash commands and their autocomplete, plus buttons, select menus, and modals. Key commands:
- `/new-session` — Start a new conversation in a thread
- `/resume` — Resume a previous session
- `/fork` — Fork a conversation into a new thread
- `/model` — Switch model mid-conversation
- `/abort` — Cancel the current run
- `/queue` — Queue follow-up messages
- `/new-worktree` — Create an isolated git worktree
- `/merge-worktree` — Merge a worktree back

## How Sessions Are Managed

### Start

1. A message arrives in a thread (or a new thread is created from a text channel message).
2. `getOrCreateRuntime()` creates a `ThreadSessionRuntime` if one doesn't exist.
3. `runtime.enqueueIncoming()` pushes the message into a serialized queue.
4. On first dispatch, `ensureSession()` creates an OpenCode session via `client.session.create()`.
5. The event listener (`startEventListener()`) subscribes to SSE events for that session.

### Stop/Dispose

- `disposeRuntime(threadId)` is called on `ThreadDelete` or by the idle sweeper.
- It aborts the event listener, clears pending UI state (permissions, questions, action buttons), rejects unprocessed actions, and removes the runtime from the in-memory map.
- The idle sweeper (`runtime-idle-sweeper.ts`) disposes runtimes idle for >1 hour.

### Attach/Resume

- When a user sends a message in a thread that already has a session, `enqueueIncoming()` queues it behind any active run.
- If the OpenCode server process died, `subscribeOpencodeServerLifecycle` detects restarts and reconnects the SSE listener.
- The runtime reconciles worktree directory changes via `handleDirectoryChanged()`, which clears the old session and reconnects.

### Key State Management

- **Global Zustand store** (`store.ts`): Holds all per-thread `ThreadRunState` objects.
- **Per-thread state** (`thread-runtime-state.ts`): Session ID, queue items, sent part IDs for dedup, listener controller, typing state, etc.
- **Event buffer**: In-memory ring buffer of 1000 SSE events, used for busy/idle derivation and `waitForEvent()` polling.
- **Serialized action queue** (`actionQueue`): All mutations flow through `dispatchAction()` which serializes them to prevent race conditions.

## Key Files for Borrowing the Chat Adapter Layer

| File | Purpose |
|------|---------|
| `cli/src/discord-bot.ts` | Main Discord event loop — message ingress, thread lifecycle, permission checks |
| `cli/src/session-handler/thread-session-runtime.ts` | Per-thread runtime: session creation, event stream, message dispatch, abort |
| `cli/src/session-handler/thread-runtime-state.ts` | Thread state type + transitions (session ID, queue, part dedup) |
| `cli/src/session-handler/event-stream-state.ts` | SSE event derivation (busy/idle detection, completion detection) |
| `cli/src/interaction-handler.ts` | Slash command router (demonstrates how to wire Discord interactions) |
| `cli/src/opencode.ts` | OpenCode server process manager + SDK client factory |
| `cli/src/message-formatting.ts` | Markdown ↔ Discord formatting, part rendering |
| `cli/src/message-preprocessing.ts` | Voice transcription, attachment download, context assembly |
| `cli/src/system-message.ts` | System prompt construction (agent, model, worktree context) |
| `cli/src/channel-management.ts` | Discord channel/category creation and project directory mapping |
| `cli/src/database.ts` | LibSQL/Prisma persistence (thread_sessions, channel_directories, etc.) |
| `discord-digital-twin/src/index.ts` | Fake Discord server for testing (REST API + Gateway WebSocket) |
| `discord-digital-twin/src/server.ts` | HTTP server implementing Discord REST API routes |
| `discord-digital-twin/src/gateway.ts` | WebSocket Gateway implementing Discord Gateway protocol |
| `discord-slack-bridge/src/node-bridge.ts` | Slack ↔ Discord bridge runtime (bridges messages in both directions) |

## License

**MIT License** — Copyright (c) 2025 Kimaki. Full text available in `LICENSE` file.

## Architecture Notes

- **OpenCode SDK**: The bot uses `@opencode-ai/sdk` to communicate with an OpenCode server process. The SDK provides `client.session.create()`, `client.session.promptAsync()`, `client.event.subscribe()`, `client.permission.reply()`, etc.
- **One OpenCode server per bot**: A single `opencode serve` process is shared across all project directories, scoped via the `x-opencode-directory` header.
- **Git worktrees**: Each thread can optionally create a git worktree for isolation. Worktree creation is async; the preprocess chain awaits the worktree promise before resolving.
- **Digital Twin testing**: The `discord-digital-twin` package implements a fake Discord server (REST + Gateway WebSocket) backed by SQLite/Prisma, enabling full E2E testing without real Discord API calls.
- **Slack bridge**: The `discord-slack-bridge` package provides bidirectional message bridging between Discord and Slack, with format conversion, typing indicator bridging, and component translation.