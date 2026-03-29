---
source-id: "crush-opencode-session-storage"
title: "Crush (OpenCode) Session Storage"
type: web
url: "https://github.com/opencode-ai/opencode"
fetched: 2026-03-28T08:00:00Z
hash: "--"
---

# Crush (formerly OpenCode) Session Storage

## Storage Location

OpenCode stores session data in `~/.local/share/opencode/` using SQLite.

```
~/.local/share/opencode/
├── opencode.db             # SQLite database (sessions, conversations, tool results)
└── ...
~/.config/opencode/
└── opencode.json           # Configuration (providers, MCP, settings)
```

## Session Persistence

- SQLite database persists session data across terminal restarts
- Sessions can be closed and resumed later
- Multiple concurrent sessions supported, each with independent conversation history and context

## Context Management

- Automatic context compaction for long sessions
- Summarizes older conversation history to free context window
- Configurable compaction aggressiveness based on model context size

## Persistent Memory

- Remembers user preferences, previous sessions, coding context
- Enables building on prior work across days or weeks

## Project Mapping

Not explicitly documented. Sessions appear to be stored globally in the SQLite database. Project association likely via working directory metadata in session records.

## Crash Recovery

No explicit crash recovery documentation found. SQLite provides transactional writes, so committed data survives crashes. Uncommitted transactions are rolled back on recovery.

## What Survives a Crash

- All committed session data in SQLite (transactional — ACID guarantees)
- Configuration
- Persistent memory store

## What's Lost

- Current uncommitted transaction (rolled back by SQLite)
- In-flight tool execution results not yet committed
- Active context compaction state
