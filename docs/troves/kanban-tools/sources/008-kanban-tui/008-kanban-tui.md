---
source-id: "008"
title: "kanban-tui — Python TUI task manager with multiple backends"
type: web
url: "https://github.com/Zaloog/kanban-tui"
fetched: 2026-03-15T02:45:00Z
hash: "pending"
---

# kanban-tui

A customizable terminal-based task manager powered by Textual with multiple backends. 222 GitHub stars.

## Key characteristics

- **SQLite backend** (default): Tasks stored in a database, not as markdown files
- **Multiple backends**: sqlite (full features), jira (API integration), claude (reads ~/.claude/tasks/ JSON)
- **TUI + CLI + MCP server**: Interactive terminal UI, CLI for agents (`ktui task list/create/update/move/delete`), MCP server for tool exposure
- **Agent-friendly**: Claude Code skills, CLI interface for agentic use, MCP server
- **Customizable columns**: Default Ready/Doing/Done/Archive, but configurable via Settings tab
- **Task dependencies**: Blocking prevention, circular detection, visual indicators
- **Audit trail**: Tracks creation/update/deletion with timestamps
- **Charts**: Bar charts showing task activity over time (monthly/weekly/daily)
- **Web mode**: `--web` flag serves the TUI in a browser via textual-serve
- **Multi-board support**: Multiple boards with board picker

## How it differs from daymark

- **Database-backed, not file-backed**: Uses SQLite, not markdown files on disk. Tasks are not human-readable markdown.
- **Task manager, not document visualizer**: Creates/manages its own tasks. Does not read existing markdown files with frontmatter.
- **No frontmatter awareness**: No concept of reading YAML frontmatter from external files.
- **No multi-track lifecycle**: Boards have columns but no concept of different artifact types following different phase sequences.

## Relevance to swain

kanban-tui is a polished task management TUI but operates in a completely different data model. It stores tasks in SQLite, not as markdown files. It cannot read swain's artifact tree. The Claude backend reads Claude's own JSON tasks, not arbitrary markdown. Not a viable alternative for visualizing swain's lifecycle.
