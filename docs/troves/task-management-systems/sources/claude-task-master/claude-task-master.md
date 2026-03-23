---
source-id: "claude-task-master"
title: "Claude Task Master (task-master-ai) — AI-powered task management for development"
type: web
url: "https://github.com/eyaltoledano/claude-task-master"
fetched: 2026-03-22T00:00:00Z
hash: "c4f7fc32393e68dc75632138b80a1d282994569b525e934620c694992158b5e8"
---

# Claude Task Master (task-master-ai)

An AI-powered task management system for Cursor, Lovable, Windsurf, Roo, and others.

By @eyaltoledano & @RalphEcom.

## Project Stats

- 26.1k stars, 2.5k forks, 153 watching
- 1,212 commits, 91 releases
- Latest version: 0.43.0

## Requirements

At least one of:

- An API key from a supported provider: Anthropic, OpenAI, Google, Perplexity, xAI, OpenRouter, or others
- Claude Code CLI (no API key needed)
- Codex CLI (OAuth)

### 3 Model Types

- **Main model** — primary task generation and management
- **Research model** — used for analysis and complexity scoring
- **Fallback model** — used when main model is unavailable

## Quick Start

### Via MCP (Recommended)

MCP configuration available for:
- Cursor
- Windsurf
- VS Code
- Q CLI

### Claude Code Quick Install

```bash
claude mcp add taskmaster-ai -- npx -y task-master-ai
```

## Tool Loading Configuration

Task Master supports different tool loading profiles to manage context window usage:

| Profile | Tools | Token Cost |
|---------|-------|------------|
| `all` | 36 tools | ~21k tokens |
| `standard` | 15 tools | ~10k tokens |
| `core` / `lean` | 7 tools | ~5k tokens |
| `custom` | User-defined | Varies |

### Core Tools (7)

- `get_tasks` — List all tasks
- `next_task` — Get the next task to work on (respects dependencies)
- `get_task` — Get details of a specific task
- `set_task_status` — Update task status
- `update_subtask` — Update a subtask
- `parse_prd` — Parse a PRD document into tasks
- `expand_task` — Expand a task into subtasks

### Standard Tools (15)

Includes all core tools plus:
- `initialize_project` — Set up a new project
- `analyze_project_complexity` — Analyze complexity of all tasks
- `expand_all` — Expand all tasks into subtasks
- `add_subtask` — Add a subtask to a task
- `remove_task` — Remove a task
- `generate` — Generate task files
- `add_task` — Add a new task
- `complexity_report` — Generate a complexity report

## PRD-Driven Workflow

1. Write a PRD (Product Requirements Document)
2. Parse the PRD into structured tasks
3. Tasks are generated with dependencies and complexity scores
4. AI-driven decomposition breaks tasks into subtasks
5. `next_task` respects dependency ordering

## Claude Code Support

- Uses `claude-code/opus` and `claude-code/sonnet` model identifiers
- No API key needed when using Claude Code CLI
- Tasks are stored as project-local JSON files

## License

MIT License with Commons Clause — you can use Task Master commercially in your own projects, but you cannot sell Task Master itself as a product or service.
