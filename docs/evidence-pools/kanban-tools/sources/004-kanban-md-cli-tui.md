---
source-id: "004"
title: "kanban-md — File-based kanban CLI/TUI for multi-agent workflows"
type: web
url: "https://github.com/antopolskiy/kanban-md"
fetched: 2026-03-15T02:35:00Z
hash: "pending"
---

# kanban-md

File-based kanban board CLI and TUI for multi-agent workflows. Written in Go, distributed as a single static binary.

## Key characteristics

- **Every task is a Markdown file** with YAML frontmatter (status, priority, assignee, tags, due date)
- **CLI-first**: `kanban-md init`, `kanban-md create`, `kanban-md list`, `kanban-md move`
- **TUI for observation**: Interactive terminal interface with keyboard navigation, auto-refreshes on file changes
- **Agent-optimized**: Designed for AI coding agents to coordinate work. Multiple agents can work simultaneously without conflicts.
- **Zero dependencies at runtime**: No database, no server, no config service, no API tokens
- **Skills included**: Pre-written Claude Code skills for CLI usage and multi-agent workflows. Installable via `kanban-md skill install`.

## How it differs from daymark

- **Task-centric, not artifact-centric**: kanban-md creates and manages its own task files. It doesn't visualize _existing_ markdown files with frontmatter — it _is_ the task system.
- **No multi-track support**: Single board with standard kanban columns (todo, in-progress, done). No concept of different artifact types following different lifecycles.
- **No web UI**: TUI only (terminal). No browser-based board view.
- **No frontmatter-field-driven columns**: Columns are fixed statuses, not configurable from arbitrary frontmatter fields.

## Relevance to swain

kanban-md is a task tracker (competes with tk/ticket), not a document lifecycle visualizer. It creates its own files rather than reading existing artifacts. It cannot render swain's multi-track lifecycle (implementable/container/standing) from existing frontmatter.
