# opencode-telegram-bot — Code Snapshot

**Repository:** https://github.com/grinev/opencode-telegram-bot  
**Version:** 0.18.0  
**License:** MIT (Copyright 2026 Ruslan Grinev)  
**Language:** TypeScript (Node.js >=20)  
**Key dependencies:** grammy (Telegram Bot framework), @opencode-ai/sdk (OpenCode client), better-sqlite3

---

## Project Structure Overview

```
src/
├── agent/          # Agent selection/management
├── app/            # Bot startup and lifecycle
├── attach/         # Session attach/detach service
├── bot/            # Telegram Bot layer — commands, handlers, streaming, middleware
│   ├── commands/   # Slash commands (/start, /new, /sessions, /status, /abort, etc.)
│   ├── handlers/   # Message handlers (prompt, voice, document, question, permission, agent, model, variant)
│   ├── middleware/  # Auth guard, interaction guard, unknown-command fallback
│   ├── streaming/   # ResponseStreamer + ToolCallStreamer (throttled message editing)
│   └── utils/      # Telegram text rendering, keyboard, file download, TTS, markdown
├── config.ts       # Environment config (Telegram token, OpenCode URL, model, etc.)
├── external-input/  # External user input suppression (dedup from parallel channels)
├── git/            # Worktree management
├── i18n/           # Internationalization (en, de, es, fr, ru, zh)
├── interaction/    # Busy-state guard (prevents concurrent interactions)
├── keyboard/       # Reply keyboard manager (agent, model, context buttons)
├── model/          # Model/variant selection and capability checks
├── opencode/       # OpenCode SDK client, SSE event stream, process management
│   ├── client.ts   # createOpencodeClient (HTTP client)
│   ├── events.ts   # SSE event subscription with auto-reconnect
│   └── process.ts  # Find/kill local OpenCode server process
├── permission/     # Permission request handling (file writes, shell commands)
├── pinned/         # Pinned message manager (context/token display)
├── project/        # Multi-project support (switch between worktrees)
├── question/       # Question tool (interactive polls from agent)
├── rename/         # Session rename
├── runtime/        # Runtime mode detection, paths (XDG-style)
├── scheduled-task/ # Cron-like scheduled prompt execution
├── service/        # Service/daemon mode (child process management)
├── session/        # Session management (thin wrapper over settings)
├── settings/       # Persistent settings (project, session, model, TTS)
├── stt/            # Speech-to-text (Whisper API)
├── summary/        # Event aggregator — processes SSE events into Telegram messages
├── telegram/       # Markdown rendering pipeline (block parser, chunker, validator)
├── tts/            # Text-to-speech client
├── utils/          # Logger, error formatting, rate-limit retry, background tasks
└── variant/        # Model variant selection
```

---

## How the Telegram Adapter Works

### Architecture: Bot ↔ SSE Events ↔ OpenCode Server

The bot is a **long-polling Telegram bot** built on **grammy** that communicates with a locally-running **opencode serve** instance via the **@opencode-ai/sdk** HTTP client (v2 API).

**Connection flow:**

1. **Startup** (`src/app/start-bot-app.ts`): Loads settings, creates bot, subscribes to events.
2. **OpenCode Client** (`src/opencode/client.ts`): Creates an SDK client pointed at `OPENCODE_API_URL` (default `http://localhost:4096`) with optional Basic Auth.
3. **Event Stream** (`src/opencode/events.ts`): Subscribes to SSE events from `opencodeClient.event.subscribe()`. Handles reconnection with exponential backoff (1s–15s). Uses `setImmediate()` to yield to grammY's event loop between events (critical for not blocking Telegram getUpdates).
4. **Event Processing** (`src/summary/aggregator.ts`): The `SummaryAggregator` processes events (`message.updated`, `message.part.updated`, `message.part.delta`, `session.idle`, `session.error`, `question.asked`, `permission.asked`, etc.) and routes them to Telegram message callbacks.
5. **Streaming** (`src/bot/streaming/`): `ResponseStreamer` handles throttled Telegram message editing (500ms default). Messages are chunked, sent, and then edited in-place as new content arrives.
6. **Auth** (`src/bot/middleware/auth.ts`): Single-user auth — only `TELEGRAM_ALLOWED_USER_ID` can interact. Unauthorized users get their commands silently wiped.

### Key Design Patterns for the Chat Adapter Layer

- **Fire-and-forget prompt dispatch**: `session.prompt()` is called in a background task (`safeBackgroundTask`) so the grammY handler returns immediately, allowing `getUpdates` polling to continue.
- **Streaming message assembly**: Text deltas accumulate in `SummaryAggregator.textMessageStates`, then stream out via `ResponseStreamer` which manages send/edit/delete of Telegram messages.
- **Tool call batching**: `ToolMessageBatcher` and `ToolCallStreamer` batch tool notifications to avoid flooding the chat.
- **Pinned message**: A pinned message in the chat shows context usage, cost, and file changes — updated on token events.
- **Subagent tracking**: The aggregator tracks child sessions spawned by the `task` tool and renders subagent progress cards.

---

## How Sessions Are Managed from Mobile

### Session Lifecycle

1. **Creating sessions**: `/new` command or auto-create on first prompt (`processUserPrompt` in `handlers/prompt.ts`). Calls `opencodeClient.session.create({ directory })`.
2. **Switching sessions**: `/sessions` lists sessions with pagination, user taps inline keyboard button → callback handler loads session, subscribes to events.
3. **Attaching to sessions**: `attachToSession()` in `attach/service.ts` subscribes to SSE events, restores pending questions/permissions, syncs pinned message state.
4. **Detaching**: On session switch or reset, `stopEventListening()` kills the SSE stream, `summaryAggregator.clear()` resets state.

### Monitoring & Control from Phone

- **Task commands**: `/task <prompt>` runs a one-shot task, `/tasklist` shows scheduled tasks
- **Abort**: `/abort` cancels a running session
- **Status**: `/status` shows current session and project info
- **OpenCode lifecycle**: `/opencode_start` spawns `opencode serve` as a detached child process; `/opencode_stop` finds and kills it by PID
- **Questions**: Agent questions appear as inline keyboard polls; answers are sent back via `opencodeClient.question.reply()`
- **Permissions**: Permission requests show approval/denial inline keyboards, sent back via `opencodeClient.permission.reply()`
- **Voice input**: Voice messages are transcribed via Whisper API and sent as text prompts
- **Photo/document upload**: Photos and documents are attached as file parts to prompts

---

## License

**MIT License** — Copyright (c) 2026 Ruslan Grinev. Free for commercial and personal use with attribution.

---

## Key Files for Borrowing the Chat Adapter Layer

The most important files for adapting this pattern to a Zulip (or other) chat bridge:

| File | Purpose |
|------|---------|
| `src/opencode/client.ts` | SDK client instantiation — how to connect to OpenCode |
| `src/opencode/events.ts` | SSE event subscription with reconnection — the bridge's event backbone |
| `src/summary/aggregator.ts` | Event → message routing logic — the heart of the adapter |
| `src/bot/streaming/response-streamer.ts` | Throttled message streaming pattern |
| `src/bot/streaming/tool-call-streamer.ts` | Batching pattern for tool call notifications |
| `src/bot/handlers/prompt.ts` | How prompts are dispatched (fire-and-forget pattern) |
| `src/bot/index.ts` | Full bot wiring — events, commands, callbacks, streaming setup |
| `src/attach/service.ts` | Session attach/detach lifecycle |
| `src/config.ts` | Configuration pattern (env vars, defaults) |
| `src/session/manager.ts` | Session state management |
| `src/interaction/guard.ts` | Preventing concurrent interactions |
| `src/bot/middleware/auth.ts` | Auth gate pattern |
| `src/bot/assistant-run-state.ts` | Tracking active assistant runs |
| `src/bot/utils/finalize-assistant-response.ts` | Post-completion message finalization |
| `.env.example` | Full configuration reference |

### What to keep vs. replace for Zulip

**Keep (adapter-neutral):**
- `opencode/client.ts` — SDK client
- `opencode/events.ts` — SSE subscription (the core bridge mechanism)
- `summary/aggregator.ts` — Event processing logic (strip Telegram-specific callbacks)
- `session/manager.ts` — Session state
- `config.ts` — Config pattern (add Zulip keys)
- `interaction/` — Busy-state guard
- `attach/service.ts` — Attach lifecycle

**Replace (Telegram-specific):**
- `bot/` → Zulip message sending (grammy → zulip SDK)
- `telegram/` → Zulip markdown rendering
- `keyboard/` → Zulip doesn't have reply keyboards (use topics/streams instead)
- `pinned/` → Zulip topic pins
- `stt/`, `tts/` → Can be reused as-is