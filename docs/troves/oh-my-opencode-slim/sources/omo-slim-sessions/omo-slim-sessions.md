---
source-id: omo-slim-sessions
title: oh-my-opencode-slim — Session Management
url: https://github.com/alvinunreal/oh-my-opencode-slim/blob/master/docs/session-management.md
fetched: 2026-05-05
type: documentation
---

# Session Management

Lets the orchestrator remember recent delegated child sessions so follow-up work continues in the right specialist context instead of starting fresh.

## Default Behavior

Remembers **2 recent child sessions per specialist type**. Works without any config entries — runtime falls back to built-in defaults.

## How It Works

When a child task runs, the plugin remembers it under a short alias (`exp-1`, `ora-1`, `fix-2`). The orchestrator sees a compact reminder in its system context:

```
### Resumable Sessions
- explorer: exp-1 Search routing files
  Context read by exp-1: src/router.ts (120 lines), src/routes/api.ts (74 lines)
- oracle: ora-1 Review auth architecture
```

Read context only shows files where at least 10 lines were read (configurable), includes line counts, caps at most recent 8 files per session (configurable).

## Scope and Safety

- Only applies to orchestrator-managed `task` delegations
- Scoped to current parent orchestrator session
- In-memory only; disappears on restart
- Does not change manual `@agent` calls
- Keeps only a few recent sessions per specialist
- Missing/deleted sessions cleaned up automatically
- Read context tracks normal `read` tool usage, not shell commands or MCP tools

## Configuration

```jsonc
{
  "sessionManager": {
    "maxSessionsPerAgent": 2,
    "readContextMinLines": 10,
    "readContextMaxFiles": 8
  }
}
```

| Option | Type | Default | Range | Description |
|--------|------|---------|-------|-------------|
| `maxSessionsPerAgent` | integer | `2` | 1–10 | Remembered sessions per specialist |
| `readContextMinLines` | integer | `10` | 0–1000 | Min lines read before file appears |
| `readContextMaxFiles` | integer | `8` | 0–50 | Max read-context files per session |
