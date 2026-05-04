# opencode-telegram-bot — Trove Source

> Telegram bot client for OpenCode — run and monitor coding tasks from chat.
> Upstream: <https://github.com/grinev/opencode-telegram-bot>

## What was captured

20 source files covering the core chat-adapter architecture, selected for their
relevance to building a Zulip-to-OpenCode bridge (swain-helm).

### Entry point & config

| File | Why |
|------|-----|
| `src/index.ts` | Module entry, exports the public API. |
| `src/cli.ts` | CLI entry point, argument parsing and bootstrapping. |
| `src/config.ts` | Environment/config loading — shows what env vars the bot needs. |

### OpenCode API client & SSE handler

| File | Why |
|------|-----|
| `src/opencode/client.ts` | OpenCode SDK client wrapper — how the bot talks to OpenCode. |
| `src/opencode/events.ts` | SSE event types and parsing — the streaming protocol from OpenCode. |
| `src/opencode/process.ts` | Process lifecycle management — spawning and supervising OpenCode sessions. |

### Telegram bot core & message routing

| File | Why |
|------|-----|
| `src/bot/index.ts` | Main bot setup — Grammy bot initialization, command registration, middleware pipeline. |
| `src/bot/assistant-run-state.ts` | State machine for an assistant run — tracks streaming/response lifecycle. |
| `src/bot/message-patterns.ts` | Message pattern matching — how incoming text is routed to handlers. |
| `src/bot/handlers/prompt.ts` | Prompt handler — the main user-to-assistant message flow. |
| `src/bot/handlers/agent.ts` | Agent handler — manages agent/subagent interactions. |
| `src/bot/handlers/context.ts` | Context middleware — builds per-request context objects. |

### Streaming & response rendering

| File | Why |
|------|-----|
| `src/bot/streaming/response-streamer.ts` | Core streaming response handler — SSE events to Telegram messages, the key adapter pattern. |
| `src/bot/streaming/tool-call-streamer.ts` | Tool call streaming — renders tool invocations in real time. |

### Middleware (auth & guards)

| File | Why |
|------|-----|
| `src/bot/middleware/auth.ts` | Authentication middleware — which users are allowed. |
| `src/bot/middleware/interaction-guard.ts` | Interaction guard — prevents conflicting concurrent operations. |

### Session & state management

| File | Why |
|------|-----|
| `src/session/manager.ts` | Session manager — creates, tracks, and switches OpenCode sessions. |
| `src/session/cache-manager.ts` | Session cache — SQLite-backed cache for conversation history and state. |

### Interaction & permission model

| File | Why |
|------|-----|
| `src/interaction/manager.ts` | Interaction manager — coordinates multi-turn conversations. |
| `src/interaction/types.ts` | Interaction types — the data model for conversations. |
| `src/permission/manager.ts` | Permission manager — approval flow for dangerous operations. |
| `src/permission/types.ts` | Permission types — data model for permission requests. |

### Project context

| File | Why |
|------|-----|
| `src/project/manager.ts` | Project manager — multi-project support, directory mapping. |

### Agent subsystem

| File | Why |
|------|-----|
| `src/agent/manager.ts` | Agent manager — orchestrates agent (subagent) runs. |
| `src/agent/types.ts` | Agent types — data model for agent configuration. |

### Metadata

| File | Why |
|------|-----|
| `package.json` | Dependencies and scripts — shows grammy, @opencode-ai/sdk, better-sqlite3, etc. |
| `LICENSE` | MIT license. |

## What was excluded

- **Command implementations** (start, help, new, sessions, etc.) — Telegram-specific UX, not adapter-relevant.
- **Telegram rendering pipeline** (markdown-normalizer, block-parser, chunker, etc.) — Zulip has different formatting constraints.
- **i18n** — Not relevant to adapter architecture.
- **TTS/STT** — Voice features outside the bridge scope.
- **Scheduled tasks** — Cron-like features, not core adapter logic.
- **Tests, scripts, .github, docs/** — Not source logic.
- **Utility helpers** (logger, error-format, rate-limit-retry, etc.) — Standard plumbing.
- **Variant, pinned, rename, model, keyboard, attach** — Telegram-specific features.