---
source: https://github.com/anomalyco/opencode/issues/18071
type: forum
title: "OpenCode Issue #18071: Add persistent todo list"
fetched: 2026-04-30
proxy-used: none
---

# OpenCode Issue #18071: Persistent Todo List Feature Request

**Opened**: Mar 18, 2026
**Status**: Open
**Assigned**: rekram1-node
**Labels**: core, discussion

## Problem Description

OpenCode's todo list (managed via TodoWrite tool) is stored only in memory and associated with individual sessions. When a session reaches its context limit and a new session is created, all todo tasks are lost.

Key issues:
1. Context limits on large projects cause task loss.
2. Lost progress when starting new sessions.
3. Users must manually reconstruct todo lists.
4. Poor UX — users expect persistence across sessions.

## Proposed Solution

Persist todo list to disk as `.opencode/todo.json`:
- Save on create/update.
- Load on session start.
- Auto-save enabled by default.
- Configurable via `opencode.json`.

## Proposed File Format

```json
{
  "version": "1.0",
  "todos": [
    {
      "id": "uuid",
      "content": "Task description",
      "status": "pending|in_progress|completed",
      "priority": "high|medium|low",
      "createdAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-01-01T00:00:00Z",
      "sessionId": "optional-session-id"
    }
  ]
}
```

## Relevance to Swain

This feature request validates the persistent-todo need but proposes yet another custom file format. Swain's approach (tk tickets in `.tickets/` dir) provides:
- Markdown files (human-readable, git-diffable).
- Dependency tracking (dep/undep).
- Priority levels (0-4).
- Tag support.
- Existing tooling already in PATH.
- Cross-session persistence natively.
