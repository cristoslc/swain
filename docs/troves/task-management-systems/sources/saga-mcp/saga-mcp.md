---
source-id: "saga-mcp"
title: "saga-mcp — A Jira-like project tracker MCP server for AI agents"
type: web
url: "https://github.com/spranab/saga-mcp"
fetched: 2026-03-22T00:00:00Z
hash: "6109eb4d83c362a3a62f242e3c435d2d796fc291396a5407676d28a583c7d33f"
---

# saga-mcp

A Jira-like project tracker MCP server for AI agents. SQLite-backed, per-project scoped, with full hierarchy and activity logging.

## Features

- Full hierarchy: Projects > Epics > Tasks > Subtasks
- Task dependencies with auto-block/unblock
- Comments (threaded)
- Templates with variable substitution
- Dashboard with natural language summary
- SQLite self-contained `.tracker.db` per project
- Activity log with old/new values
- Notes system (decisions, context, meeting notes, blockers)
- Batch operations
- 31 focused tools with MCP safety annotations
- Import/export as JSON
- Source references
- Auto time tracking
- Cross-platform

## Quick Start

```bash
npx -y saga-mcp
```

Set `DB_PATH` environment variable to control where the `.tracker.db` file is created.

## Tools (31)

### Getting Started

| Tool | Description |
|------|-------------|
| `get_started` | Get instructions on how to use the tracker |
| `get_dashboard` | Get a comprehensive project dashboard with natural language summary |

### Projects

| Tool | Description |
|------|-------------|
| `create_project` | Create a new project |
| `list_projects` | List all projects |
| `update_project` | Update a project |
| `delete_project` | Delete a project |

### Epics

| Tool | Description |
|------|-------------|
| `create_epic` | Create an epic within a project |
| `list_epics` | List epics in a project |
| `update_epic` | Update an epic |
| `delete_epic` | Delete an epic |

### Tasks

| Tool | Description |
|------|-------------|
| `create_task` | Create a task within an epic |
| `list_tasks` | List tasks in an epic |
| `update_task` | Update a task |
| `delete_task` | Delete a task |
| `add_dependency` | Add a dependency between tasks |
| `remove_dependency` | Remove a dependency between tasks |
| `batch_create_tasks` | Create multiple tasks at once |
| `batch_update_tasks` | Update multiple tasks at once |

### Subtasks

| Tool | Description |
|------|-------------|
| `create_subtask` | Create a subtask within a task |
| `list_subtasks` | List subtasks of a task |
| `update_subtask` | Update a subtask |
| `delete_subtask` | Delete a subtask |

### Comments

| Tool | Description |
|------|-------------|
| `add_comment` | Add a comment to a task |
| `list_comments` | List comments on a task |

### Templates

| Tool | Description |
|------|-------------|
| `create_template` | Create a reusable task template |
| `use_template` | Create a task from a template with variable substitution |

### Notes

| Tool | Description |
|------|-------------|
| `add_note` | Add a note (decision, context, meeting, etc.) |
| `list_notes` | List notes with optional filtering |

### Intelligence

| Tool | Description |
|------|-------------|
| `get_activity_log` | Get activity history with filtering |

### Import/Export

| Tool | Description |
|------|-------------|
| `export_project` | Export project data as JSON |
| `import_project` | Import project data from JSON |

## How It Works

- Uses SQLite as a single file per project (`.tracker.db`)
- Schema is auto-created on first use
- All operations go through MCP tool calls
- Activity log tracks every change with old/new values

## Hierarchy

```
Project
  └── Epic
        └── Task
              ├── Subtask
              ├── Comments
              └── Dependencies (to other tasks)
```

## Task Dependencies

- Tasks can depend on other tasks within the same project
- When all dependencies of a blocked task are completed, the task is automatically unblocked
- Circular dependency detection prevents invalid states

## Note Types

- `general` — General notes
- `decision` — Decision records
- `context` — Context/background information
- `meeting` — Meeting notes
- `technical` — Technical notes
- `blocker` — Blockers and impediments
- `progress` — Progress updates
- `release` — Release notes

## Activity Log

Every change is recorded with:
- Timestamp
- Entity type and ID
- Action performed
- Old and new values
- Filterable by entity, action, and time range

## Privacy

- Fully local — all data stays on your machine
- Works offline
- No telemetry or analytics
- No cloud dependencies

## Project Info

- 17 stars, 3 forks
- MIT license
- TypeScript
- Version 1.5.3
