# Kimaki Source Reference

**License: MIT** — See LICENSE file in this directory.

**Source:** https://github.com/remorses/kimaki  
**Captured:** 2026-04-24

## What was included

Curated selection of Kimaki's most architecturally significant files for the swain-helm bridge design. Focuses on session runtime, Discord adapter, and worktree management patterns.

### Session runtime (thread-per-session model)

- `cli/src/session-handler/thread-session-runtime.ts` — Core orchestrator. One `ThreadSessionRuntime` per active Discord thread. Owns resource handles, delegates state to the global store.
- `cli/src/session-handler/thread-runtime-state.ts` — State transitions for thread runtime (event sourcing pattern).
- `cli/src/session-handler/event-stream-state.ts` — Event stream state machine for serializing SSE events into Discord messages.
- `cli/src/session-handler.ts` — Re-export barrel for session handler modules.

### Discord channel adapter

- `cli/src/discord-bot.ts` — Main Discord bot entry point. Bridges Discord events to OpenCode sessions, manages voice connections, orchestrates the event loop.
- `cli/src/discord-utils.ts` — Discord utility functions for message formatting, channel operations, and embeds.
- `cli/src/discord-command-registration.ts` — Slash command and interaction registration with Discord's API.
- `cli/src/channel-management.ts` — Channel-to-directory mapping and metadata management (XML topic parsing).

### OpenCode integration

- `cli/src/opencode.ts` — OpenCode server lifecycle: spawn, connect, and manage coding agent processes.
- `cli/src/opencode-command.ts` — OpenCode command construction and dispatch.
- `cli/src/opencode-interrupt-plugin.ts` — Plugin for interrupting running OpenCode sessions.

### Worktree management

- `cli/src/worktree-utils.ts` — Low-level git worktree helpers.
- `cli/src/commands/new-worktree.ts` — Create worktrees from Discord.
- `cli/src/commands/merge-worktree.ts` — Merge worktrees back.
- `cli/src/commands/worktrees.ts` — Worktree listing and management command.
- `cli/src/commands/worktree-settings.ts` — Per-project worktree configuration.
- `cli/src/commands/add-dir.ts` — Add project directories to channel mapping.

### Session lifecycle

- `cli/src/runtime-idle-sweeper.ts` — Sweeps idle sessions to free resources.
- `cli/src/startup-service.ts` — Bot startup and initialization orchestration.
- `cli/src/config.ts` — Configuration loading and defaults.

### Persistence

- `cli/src/database.ts` — SQLite database layer (Prisma + libSQL). Stores session state, channel mappings, and credentials.

### Documentation

- `internals.md` — How Kimaki works under the hood (SQLite, lock port, channel metadata, voice processing).
- `event-sourcing-for-application-state.md` — Design rationale for event-sourced state over mutable fields.

### Metadata

- `package.json` — CLI package manifest with dependencies (discord.js, opencode SDK, Prisma, etc.).
- `LICENSE` — MIT license.

## What was excluded

- `discord-digital-twin/` — Separate package providing a Discord API-compatible mock server.
- `discord-slack-bridge/` — Slack-to-Discord bridge (separate concern).
- `libsqlproxy/`, `errore/`, `traforo/`, `sigillo/`, `fly-admin/` — Supporting packages not directly relevant.
- Test files, e2e fixtures, scripts, skills, voice handling, GenAI worker, image/voice processing, subagent plugins.
- `node_modules/`, `dist/`, `pnpm-lock.yaml`, `tsconfig.json`, build config.

## Why these files matter for swain-helm

Kimaki's `ThreadSessionRuntime` is the closest existing pattern to what swain-helm needs: a per-session runtime that bridges a chat platform (Discord) to an agentic coding tool (OpenCode), with worktree isolation per session and idle session cleanup. The channel-management pattern (XML metadata in channel topics for directory mapping) and the event-sourcing state model are both worth studying as reference architectures.