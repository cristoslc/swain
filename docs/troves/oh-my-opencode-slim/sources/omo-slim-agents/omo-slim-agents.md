---
source-id: omo-slim-agents
title: oh-my-opencode-slim — AGENTS.md (Agent Coding Guidelines)
url: https://github.com/alvinunreal/oh-my-opencode-slim/blob/master/AGENTS.md
fetched: 2026-05-05
type: repository
---

# AGENTS.md — Coding & Workflow Guidelines

## Commands

| Command | Description |
|---------|-------------|
| `bun run build` | Build TypeScript to `dist/` |
| `bun run typecheck` | Type checking without emitting |
| `bun test` | Run all tests |
| `bun run lint` | Biome linter |
| `bun run format` | Biome formatter |
| `bun run check` | Biome check with auto-fix |
| `bun run check:ci` | Biome check without auto-fix (CI mode) |
| `bun run dev` | Build and run with OpenCode |

**Single test:** `bun test -t "pattern"`

## Code Style

- Biome configured in `biome.json`
- Line width: 80 chars, indent: 2 spaces, LF line endings
- Single quotes, trailing commas always
- TypeScript strict mode, no explicit `any` (warning only; disabled for tests)
- Module resolution: `bundler`, generate `.d.ts` in `dist/`
- camelCase for variables/functions, PascalCase for classes/interfaces, SCREAMING_SNAKE_CASE for constants
- kebab-case for files, PascalCase for React components
- Biome auto-organizes imports
- Zod for runtime validation

## Project Structure

```
src/
├── agents/       # Agent factories per specialist
├── cli/          # Installer CLI entry
├── config/       # Constants, schemas, MCP defaults
├── council/      # Multi-LLM session orchestration
├── hooks/        # OpenCode lifecycle hooks
├── mcp/          # MCP server definitions
├── multiplexer/  # Tmux/Zellij pane integration
├── skills/       # Bundled skill definitions
├── tools/        # Tool definitions (council, webfetch, AST-grep)
└── utils/        # Shared utilities
```

## Key Dependencies

- `@modelcontextprotocol/sdk` — MCP protocol
- `@opencode-ai/sdk` — OpenCode SDK
- `zod` — Runtime validation

## Tmux Session Lifecycle

1. Graceful shutdown: always `Ctrl+C` before `kill-pane` with 250ms delay
2. Session abort AFTER extracting task results
3. Event handlers wired for `session.deleted` cleanup

## Pre-Push Workflow

1. Stage changes: `git add .`
2. Run `/review` (OpenCode built-in command)
3. Address issues
4. `bun run check:ci && bun test`
5. Commit and push

## Repository Stats

- 468 tests across 35 files
- Full codemap at `codemap.md`
