---
source-id: cline-kanban
type: repository
url: https://github.com/cline/kanban
title: "cline/kanban — Browser-based kanban for parallel agent orchestration"
fetched: 2026-03-27T00:00:00Z
---

# cline/kanban

> A replacement for your IDE better suited for running many agents in parallel and reviewing diffs

## Overview

cline/kanban is a browser-based kanban board purpose-built for orchestrating parallel coding agents. Run it with `npx kanban` from any git repo — no install required. Apache 2.0 licensed, v0.1.50, by Cline Bot Inc (2026). Labeled as "Research Preview" — experimental, bypasses permissions for more autonomy.

## Key features

- **Worktree-per-task isolation**: Each task card gets its own ephemeral git worktree with symlinked node_modules (and other gitignored files)
- **Per-card terminal sessions**: Each card runs its own terminal session with a CLI agent (Claude Code, Codex, Gemini, OpenCode, Droid)
- **Hook-based reactive status**: Real-time status tracking via hooks — displays latest message/tool call on each card
- **Hook state machine**: `in_progress` <-> `review` transitions via hook events (`to_in_progress`, `to_review`)
- **Hook environment variables**: `KANBAN_HOOK_TASK_ID`, `KANBAN_HOOK_WORKSPACE_ID`, `KANBAN_HOOK_PORT`
- **Dependency chains**: Link cards so completion of one auto-starts the next
- **Auto-commit**: Built-in checkpointing, diff review, commit/PR creation for autonomous work
- **Multi-agent support**: Supports Claude, Codex, Gemini, OpenCode, Droid via hooks

## Architecture

### Source layout

```
src/
  cli.ts           — CLI entry point
  cline-sdk/       — Cline SDK integration
  commands/        — CLI command handlers
  config/          — Configuration management
  core/            — Core board/task logic
  fs/              — Filesystem operations
  projects/        — Project management
  prompts/         — Prompt templates
  server/          — HTTP server
  state/           — State management
  telemetry/       — Usage telemetry
  terminal/        — Terminal session management (node-pty)
  trpc/            — tRPC API layer
  update/          — Self-update mechanism
  workspace/       — Worktree/workspace management
web-ui/            — React frontend
```

### Key dependencies

- `@clinebot/agents`, `@clinebot/core`, `@clinebot/llms` — Cline agent framework
- `@modelcontextprotocol/sdk` — MCP integration
- `node-pty` — Terminal management for per-card agent sessions
- tRPC — Client-server communication between web UI and backend

### Technology stack

- TypeScript + React (web UI)
- tRPC for API communication
- node-pty for terminal management
- Git worktrees for task isolation

## Design model

cline/kanban falls into **Model 1: Board-owns-the-data** — it creates and manages its own task state rather than reading existing markdown artifacts with frontmatter. Tasks are board-native entities, not projections of external files.

However, it has a distinctive twist absent from other Model 1 tools: **integrated worktree-per-task agent orchestration with hooks-based status tracking**. The board is not just a task manager — it is an agent execution environment where each card is a live agent session with its own isolated workspace.

## Relevance to swain

1. **Worktree-per-task pattern**: Validates the same pattern swain already uses for worktree isolation during spec implementation. cline/kanban automates worktree creation/teardown per card, with symlinked node_modules to avoid redundant installs.

2. **Hook-based reactive status**: The `to_in_progress` / `to_review` hook state machine is a concrete implementation of reactive status tracking. Swain's synthesis theorized about a reactive loop (filesystem watcher -> frontmatter diff -> transition event); cline/kanban solves the same problem via explicit hook callbacks rather than filesystem polling.

3. **Dependency chain automation**: Card linking with auto-start on completion is the pattern swain-do aspires to — when one spec completes, the next dependent spec should be ready for work.

4. **Multi-agent orchestration**: Running multiple agents in parallel with per-agent worktrees is directly relevant to swain's subagent-driven-development skill and EPIC-045's multi-runtime goals.
