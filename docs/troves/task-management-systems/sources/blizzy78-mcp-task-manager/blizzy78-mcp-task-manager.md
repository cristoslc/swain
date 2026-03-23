---
source-id: "blizzy78-mcp-task-manager"
title: "blizzy78/mcp-task-manager — Task Manager MCP Server with critical path tracking"
type: web
url: "https://github.com/blizzy78/mcp-task-manager"
fetched: 2026-03-22T00:00:00Z
hash: "e6e81b33f892334d3e8a6ef8297baed8e4d8bbb6d216da177af6629d6b717e69"
---

# blizzy78/mcp-task-manager

An MCP server for agents to orchestrate task workflows through exploration.

## Overview

- Create and organize tasks in hierarchical structures with dependencies
- Decompose complex tasks into smaller subtasks with sequence ordering
- Track task progression through defined states: `todo`, `in-progress`, `done`, `failed`
- Orchestrate workflows with proper dependency validation and critical path tracking

## Tested Compatibility

- GitHub Copilot in VS Code with Claude Sonnet 4
- GPT-4.1 and GPT-5 don't work well with this server

## Tools (5)

| Tool | Description |
|------|-------------|
| `create_task` | Create a new top-level task |
| `decompose_task` | Break a task into subtasks with sequence ordering |
| `update_task` | Update task status (todo → in-progress → done/failed) |
| `task_info` | Get detailed info about a task including dependencies and critical path |
| `current_task` | Get the current task to work on (single agent mode only) |

## Single Agent Mode

Set `SINGLE_AGENT=true` environment variable to enable `current_task` tool. This is designed for context recovery after history compaction — the agent can ask "what should I be working on?" and get a deterministic answer.

## Persistence

In-memory only. No persistence across sessions. All task state is lost when the server process ends.

## Installation

```bash
npx -y @blizzy/mcp-task-manager
```

## Recommended Agent Prompt

The repository includes recommended prompt snippets for instructing the agent how to use the task manager effectively, including guidelines for task decomposition, status updates, and workflow orchestration.

## Project Info

- 4 stars
- MIT license
- TypeScript
