---
source-id: "mcp-server-taskwarrior"
title: "awwaiid/mcp-server-taskwarrior — MCP Server for TaskWarrior"
type: web
url: "https://github.com/awwaiid/mcp-server-taskwarrior"
fetched: 2026-03-22T00:00:00Z
hash: "a07647e2e86cadafea7a9c6c9c77516f0fa150ac3d69a0d347e2726c51e57041"
---

# awwaiid/mcp-server-taskwarrior

A Node.js server implementing MCP (Model Context Protocol) for TaskWarrior operations.

## Features

- View pending tasks
- Filter tasks by project and tags
- Add new tasks with descriptions, due dates, priorities, projects, and tags
- Mark tasks as complete

## Warning

Uses `task id` which is unstable — TaskWarrior renumbers IDs as tasks are completed or deleted. Should use UUID instead for reliable task references.

## Tools (3)

| Tool | Description |
|------|-------------|
| `get_next_tasks` | Get pending tasks, optionally filtered by project/tags |
| `add_task` | Add a new task with description, due date, priority, project, and tags |
| `mark_task_done` | Mark a task as complete |

## Requirements

- TaskWarrior (`task`) must be installed locally

## Installation

```bash
npx -y mcp-server-taskwarrior
```

## Project Info

- 44 stars, 11 forks
- MIT license
- JavaScript
