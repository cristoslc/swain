---
source-id: "copilot-cli-session-state"
title: "GitHub Copilot CLI Session State and Lifecycle Management"
type: web
url: "https://deepwiki.com/github/copilot-cli/6.2-session-state-and-lifecycle-management"
fetched: 2026-03-28T08:00:00Z
hash: "--"
---

# GitHub Copilot CLI Session State and Lifecycle Management

## Storage Architecture

Dual-format storage design that decouples storage representation from timeline display:

```
~/.copilot/
├── session-state/           # Active sessions (JSON, v0.0.342+)
├── history-session-state/   # Legacy sessions (migrated on resume)
├── session-store.db         # SQLite database for /chronicle queries
├── events.jsonl             # Per-session metrics (requests, tokens, changes)
├── config.json              # Global configuration
├── mcp-config.json          # MCP server configuration
└── lsp-config.json          # Language server configuration
```

## Session State Directory

Every Copilot CLI session is persisted as a set of files in `~/.copilot/session-state/`. Each session gets its own subdirectory containing:
- Prompts and responses
- Tools used
- Files modified
- Complete session records

## SQLite Session Store

`~/.copilot/session-store.db` contains a subset of the full session data. Powers the `/chronicle` command for querying past work across sessions. Populated incrementally during sessions and flushed on completion.

## Session Lifecycle

1. **Creation**: UUID generated, empty timeline and context initialized
2. **Active**: Conversation tracked with tool calls and file modifications
3. **Persistence**: State written to storage on termination
4. **Resumption**: Load via `--resume <UUID>` or `--resume <task-id>`

## Session Identification

- Primary: UUID generated at session creation
- Resume by UUID: `--resume <id>`
- Resume by task ID: `--resume <task-id>`
- Interactive picker: `--resume` without arguments

## Crash Recovery

- Session history preserved during `/quit` and Ctrl+C
- If session terminates unexpectedly before in-memory data flushes to session store, users can recover via reindexing from session files
- Corruption handling improved — sessions from pre-1.0.6 no longer break resume

## Cross-Session Memory

- Repository memory: remembers conventions, patterns, preferences across sessions
- Cross-session queries: ask about past work, files, PRs via `/chronicle`
- All data stored locally in `~/.copilot/` — only accessible to user account

## Compaction

- Automatic at 95% token consumption
- Tool call sequences, extended thinking, and skills preserved
- `preCompact` hook fires before summarization
- Timeline includes checkpoint summaries

## What Survives a Crash

- Session files in `session-state/` (written incrementally)
- SQLite session store (up to last flush)
- Events log
- Configuration

## What's Lost

- In-memory data not yet flushed to session store
- Metrics for the final incomplete session segment
