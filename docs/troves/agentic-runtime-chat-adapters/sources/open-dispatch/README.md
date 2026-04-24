# Open Dispatch — Source Trove

**Source:** [https://github.com/nichochar/open-dispatch](https://github.com/nichochar/open-dispatch)
**License:** MIT (per package.json)
**Date collected:** 2026-04-24

## What is Open Dispatch?

Open Dispatch bridges Slack, Microsoft Teams, and Discord to OpenCode/Claude using a `ChatProvider` abstraction. It provides a unified bot engine that routes messages between chat platforms and AI agent runtimes.

## Files Included

### ChatProvider interface and adapters

| File | Purpose |
|------|---------|
| `src/providers/chat-provider.js` | Core `ChatProvider` base class defining the adapter interface (send, update, delete, react, typing, etc.) |
| `src/providers/slack-provider.js` | Slack adapter implementing ChatProvider |
| `src/providers/teams-provider.js` | Microsoft Teams adapter implementing ChatProvider |
| `src/providers/discord-provider.js` | Discord adapter implementing ChatProvider |
| `src/providers/index.js` | Provider registry and factory |

### Bot engine and orchestrator

| File | Purpose |
|------|---------|
| `src/bot-engine.js` | Central orchestrator: receives messages from providers, manages conversation state, dispatches to agent runtimes |
| `src/bot.js` | Entry point / bot bootstrap wiring |
| `src/job.js` | Async job management for long-running agent tasks |

### Agent runtime adapters

| File | Purpose |
|------|---------|
| `src/opencode-core.js` | OpenCode runtime adapter (subprocess communication with opencode serve) |
| `src/claude-core.js` | Claude API runtime adapter (direct API calls) |
| `src/opencode-bot.js` | OpenCode-specific bot logic and message formatting |

### Infrastructure

| File | Purpose |
|------|---------|
| `src/webhook-server.js` | HTTP webhook receiver for platform events |
| `package.json` | Dependencies and project metadata |
| `.env.example` | Environment variable template for configuration |

## What was skipped

- `src/sprite-*` — Sprite orchestration subsystem (separate concern from chat adapters)
- `src/teams-bot.js`, `src/teams-opencode-bot.js`, `src/discord-bot.js`, `src/discord-opencode-bot.js` — Platform-specific entry points that delegate to the generic bot-engine/opencode-core layer already captured
- `src/process-handlers.js` — Minor utility for process signal handling
- `sidecar/` — Sidecar container for output relay (separate deployment concern)
- `tests/` — Test fixtures
- `Dockerfile`, `fly.toml` — Deployment config
- `.github/` — CI workflows
- `teams-manifest/` — Teams app manifest
- `*-SETUP.md` — Per-platform setup guides