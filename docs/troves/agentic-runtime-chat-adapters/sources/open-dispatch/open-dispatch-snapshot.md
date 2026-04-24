# Open Dispatch Source Snapshot

Repository: https://github.com/bobum/open-dispatch
Cloned: 2026-04-23
Version: 2.2.0 (package.json)
License: MIT (declared in package.json; no top-level LICENSE file found)

## Project Structure Overview

```
open-dispatch/
├── src/
│   ├── bot.js                    # Slack+Claude monolith entry point (legacy)
│   ├── opencode-bot.js           # Slack+OpenCode monolith entry point (legacy)
│   ├── teams-opencode-bot.js     # Teams+OpenCode monolith (legacy, has Adaptive Cards)
│   ├── discord-opencode-bot.js   # Disc+OpenCode using bot-engine (modern)
│   ├── bot-engine.js             # Platform-agnostic bot logic (modern)
│   ├── opencode-core.js          # OpenCode CLI instance manager
│   ├── claude-core.js            # Claude CLI instance manager
│   ├── sprite-core.js            # Fly.io Sprite (ephemeral VM) instance manager
│   ├── sprite-orchestrator.js    # Fly Machine lifecycle management
│   ├── sprite-bot.js             # Provider-agnostic Sprite entry point (modern)
│   ├── job.js                    # Job model for Sprite execution
│   ├── webhook-server.js         # HTTP webhook receiver for Sprite callbacks
│   ├── process-handlers.js       # Fatal error handlers (shared utility)
│   ├── teams-bot.js              # Teams+Claude monolith (legacy)
│   ├── discord-bot.js            # Discord+Claude monolith (legacy)
│   └── providers/
│       ├── chat-provider.js       # Abstract base class + provider registry
│       ├── index.js               # Re-exports all providers
│       ├── slack-provider.js      # Slack provider (@slack/bolt, Socket Mode)
│       ├── teams-provider.js      # Teams provider (botbuilder, restify HTTP)
│       └── discord-provider.js    # Discord provider (discord.js, slash commands)
├── sidecar/
│   ├── output-relay.js           # Pipes agent stdout → webhook (runs inside Sprite)
│   ├── sprite-reporter.sh        # Shell reporter for Sprite VMs
│   └── formatters/
│       └── opencode.js            # Filters OpenCode CLI output for relay
├── teams-manifest/
│   ├── manifest.json              # Teams app manifest
│   └── README.md
├── tests/                         # Node test runner files
├── .env.example                   # All config vars documented
├── Dockerfile                     # Container build
├── fly.toml                       # Fly.io deployment config
└── package.json
```

**Two architecture generations exist side-by-side:**

1. **Legacy monoliths** (`bot.js`, `opencode-bot.js`, `teams-opencode-bot.js`) — each file is a self-contained Slack/Teams+AI bot with inline platform logic.
2. **Modern modular** (`bot-engine.js` + `providers/` + `*-core.js`) — a factory pattern where `createBotEngine()` accepts any `ChatProvider` + any AI backend, composing them at runtime.

The `sprite-bot.js` entry point is the canonical modern pattern: read `CHAT_PROVIDER` env var, instantiate the right provider via the registry, create AI backend, and wire them into `createBotEngine()`.

## How the Chat Bridge Works

### Platforms Supported
- **Slack** — via `@slack/bolt` in Socket Mode (no public endpoint needed)
- **Microsoft Teams** — via `botbuilder` + `restify` HTTPS server (requires public endpoint, ngrok for dev)
- **Discord** — via `discord.js` with slash commands + text command fallback

### ChatProvider Abstraction

The bridge is built on `ChatProvider` (abstract base class in `providers/chat-provider.js`). Each platform implements:

| Method | Purpose |
|--------|---------|
| `initialize()` | Load SDK, validate config |
| `start()` / `stop()` | Connect/disconnect |
| `sendMessage(channelId, text)` | Send text, auto-chunked |
| `sendLongMessage(channelId, text)` | Chunk + send |
| `sendCard(channelId, cardData)` | Rich cards (Teams Adaptive Cards, Discord Embeds) |
| `sendTypingIndicator(channelId)` | "Thinking..." indicator |
| `deleteMessage(channelId, messageId)` | Remove a message |
| `editMessage(channelId, messageId, text)` | Edit a message |
| `onMessage(handler)` | Register handler for free-text messages |
| `onCommand(handler)` | Register handler for slash/prefix commands |
| `onError(handler)` | Register error handler |

Properties declare capabilities: `supportsCards`, `supportsEphemeral`, `supportsThreads`, `maxMessageLength`.

A **provider registry** (`registerProvider`/`createProvider`) allows runtime lookup by name (`'slack'`, `'teams'`, `'discord'`).

### Message Routing Flow

1. **Incoming message** arrives via platform SDK event
2. Provider creates a `MessageContext` (`channelId`, `userId`, `userName`, `messageId`, `raw`, `reply`)
3. If it matches a slash command pattern → `_emitCommand(ctx, command, args)` → `bot-engine` handles it
4. If it's free text → `_emitMessage(ctx, text)` → `bot-engine` looks up an AI instance bound to that channel
5. If an instance exists → message is forwarded to the AI backend
6. AI backend response streams back through `onMessage` callback → provider sends to chat

### Smart Routing (Channel Binding)

`bot-engine.js` line ~770:

```js
chatProvider.onMessage(async (ctx, text) => {
  const found = aiBackend.getInstanceByChannel(ctx.channelId);
  if (found) {
    await sendMessageToInstance(ctx, found.instanceId, text);
  }
});
```

Each AI instance records its `channelId` at creation. Free-text messages in a bound channel are automatically routed to the matching instance. No command prefix needed.

Commands (`od-start`, `od-stop`, `od-list`, `od-send`, `od-run`, `od-jobs`) are explicitly parsed and dispatched regardless of channel binding.

### Streaming and Rate-Limit Protection

`bot-engine.js` includes a `createMessageBatcher(channelId)` that:
- Buffers output lines
- Flushes every 500ms or every 5 lines
- Enforces 200ms minimum between sends
- Wraps output in code blocks for readability

## Session Persistence and Resume

### Claude Backend (`claude-core.js`)
- **First message**: spawns `claude --session-id <uuid> --output-format stream-json`
- **Subsequent messages**: spawns `claude --resume <sessionId> --output-format stream-json`
- Each invocation is a **separate process** — no long-running daemon
- Session ID stored in the in-memory `instances` Map
- **No disk persistence** — sessions are lost on bot restart

### OpenCode Backend (`opencode-core.js`)
- **First message**: `opencode run --format json -- <message>` (no session flag)
- **Subsequent messages**: `opencode run --format json --session <sessionId> -- <message>`
- Captures session ID from response JSON (`sessionID`, `sessionId`, or `session_id` fields)
- Also in-memory only

### Sprite Backend (`sprite-core.js`)
- Ephemeral Fly Machines for one-shot jobs
- Persistent mode available via `--image` flag
- Webhook-driven completion (not process exit)
- `job.js` tracks state transitions: `queued → running → completed/failed`
- Stale reaper runs every 60s to timeout orphaned jobs

### Key Insight: No Durable Persistence

All session state lives in process-memory `Map` objects. A bot restart loses all instance bindings. The Teams bot has an explicit comment in `teams-opencode-bot.js:51`:

> "This Map is in-memory only. All selections will be lost if the bot process restarts. For production use, consider backing this with persistent storage."

## License Type

**MIT** — declared in `package.json` (`"license": "MIT"`). No dedicated LICENSE file found in the repository.

## Key Files for Borrowing the Chat Bridge Layer

These are the files most relevant to adapting the chat bridge for swain-helm:

| File | Why It Matters |
|------|---------------|
| `src/providers/chat-provider.js` | Abstract base class + registry — the contract any new provider must implement |
| `src/providers/slack-provider.js` | Full Slack implementation with Socket Mode, slash commands, message chunking |
| `src/providers/teams-provider.js` | Full Teams implementation with Bot Framework, Adaptive Cards, proactive messaging |
| `src/providers/discord-provider.js` | Full Discord implementation with slash commands, embeds, threading |
| `src/providers/index.js` | Provider registry and factory — `createProvider('slack', config)` |
| `src/bot-engine.js` | Platform-agnostic orchestrator: command parsing, instance routing, message batcher |
| `src/webhook-server.js` | HTTP callback receiver for async agent responses (relevant for Zulip webhook) |
| `src/opencode-core.js` | Instance lifecycle: start, session management, send with streaming callback |
| `.env.example` | Complete configuration reference for all providers |

### What's Missing for Zulip Adaptation

The existing providers handle Slack, Teams, and Discord. A Zulip provider would need to:
1. Extend `ChatProvider`
2. Implement `sendMessage`, `sendCard` (Zulip has limited card support), `sendTypingIndicator`
3. Use the Zulip API (likely via `zulip` npm package) for both receiving messages (via event queue long-polling) and sending
4. Handle Zulip's stream/topic model instead of flat channel IDs
5. Map Zulip PMs and stream messages to commands vs free-text routing