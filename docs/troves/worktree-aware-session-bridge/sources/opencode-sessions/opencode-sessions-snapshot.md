# OpenCode Sessions - Code Snapshot

**Repository**: https://github.com/malhashemi/opencode-sessions
**Author**: M. Adel Alhashemi
**License**: MIT
**Version**: 1.0.0
**Snapshot Date**: 2026-04-23

---

## Project Overview

OpenCode Sessions is an OpenCode plugin for **multi-agent collaboration and workflow orchestration** across sessions. It provides a single `session` tool with four operational modes that enable agents to collaborate, hand off work, compress context, and explore alternatives in parallel.

## Project Structure

```
opencode-sessions/
├── index.ts          # Main plugin entry point (~503 lines, single-file architecture)
├── package.json      # NPM package config (opencode-sessions v1.0.0)
├── tsconfig.json     # TypeScript config
├── AGENTS.md         # Agent guidelines for AI contributors
├── README.md         # Full documentation with examples
├── LICENSE           # MIT License
├── CHANGELOG.md
├── CONTRIBUTING.md
├── .prettierrc       # { "semi": false }
└── .github/
    └── workflows/
        └── release-please.yml
```

## Session/Agent Management Code

### Core Architecture (`index.ts`)

The entire plugin is a single file implementing the `Plugin` interface from `@opencode-ai/plugin`.

**Agent Discovery** (`discoverAgents`, lines 47-149):
- Scans `~/.config/opencode/agent/` and `.opencode/agent/` directories for `.md` files
- Parses YAML frontmatter via `gray-matter` to find agents with `mode: "primary"` or `mode: "all"`
- Adds built-in agents (`build`, `plan`) if not overridden by `.md` files
- Reads `opencode.json` files for disabled agents and filters them out

**Session Tool** (lines 294-501):
Four modes exposed as a single tool:

| Mode | Creates New Session | Agent Switching | Context Preserved | Use Case |
|------|-------------------|-----------------|-------------------|----------|
| `message` | No | Yes | Yes | Agent collaboration |
| `new` | Yes | Yes | No | Phase transitions |
| `compact` | No | Yes | Compressed | Token optimization |
| `fork` | Yes (child) | Yes | Yes | Parallel exploration |

**Event-Driven Hooks**:
- `tool.execute.before` (lines 186-205): Intercepts `session` tool calls, stores pending messages for message mode and pending compaction requests
- `event` handler (lines 208-291): Listens for `session.idle` (sends queued messages, triggers compaction) and `session.compacted` (sends post-compaction messages)

**Agent Relay Pattern** (message mode):
1. Tool stores message in `pendingMessages` map
2. Current agent finishes its turn
3. `session.idle` event fires after session unlocks
4. Plugin sends queued message to target agent via `ctx.client.session.prompt()`

**Compaction Flow** (compact mode):
1. Gets last assistant message to extract `providerID`/`modelID`
2. Injects context marker via `noReply: true` prompt
3. Stores compaction request in `pendingCompactions` map
4. On `session.idle`: calls `ctx.client.session.summarize()`
5. On `session.compacted`: waits 100ms, then sends handoff message

**New Session Flow**:
- Creates session via `ctx.client.session.create()` with optional title
- Sends initial message with specified agent via `ctx.client.session.prompt()`

**Fork Flow**:
- Uses `ctx.client.session.fork()` to copy message history
- Sends new message in forked session with specified agent

## Key Files

| File | Purpose |
|------|---------|
| `index.ts` | Complete plugin implementation (503 lines) |
| `package.json` | Package metadata, deps: `@opencode-ai/sdk`, `gray-matter` |
| `AGENTS.md` | Code style: no semicolons, async/await, JSDoc, conventional commits |
| `README.md` | Comprehensive docs: API reference, mermaid diagrams, examples |

## Dependencies

- `@opencode-ai/sdk` ^0.15.18 (peer dependency)
- `@opencode-ai/plugin` ^0.15.18 (dev dependency)
- `gray-matter` ^4.0.3 (YAML frontmatter parser)
- TypeScript ^5.9.3
- `@types/bun`, `bun-types` ^1.3.0

## Key Design Decisions

1. **Single-file architecture**: Entire plugin is one TypeScript file
2. **Event-driven relay**: Uses OpenCode's hook system (`tool.execute.before`, `event`) instead of direct agent-to-agent calls
3. **No external state**: All state held in-memory maps (`pendingMessages`, `pendingCompactions`, `activeCompactions`)
4. **Agent discovery from filesystem**: Discovers agents dynamically from `.md` files, not hardcoded
5. **Turn-based collaboration**: Agents don't interrupt each other - each gets a complete turn