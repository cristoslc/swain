---
source-id: "010"
title: "Tasks.md — Self-hosted, file-based task management board"
type: web
url: "https://github.com/BaldissaraMatheus/Tasks.md"
fetched: 2026-03-15T02:45:00Z
hash: "pending"
---

# Tasks.md

A self-hosted, markdown file-based task management board. Docker container serving a web UI.

## Key characteristics

- **Each task is a markdown file**: Cards are individual .md files in lane directories
- **Lane = directory**: Files live in directories that map to kanban columns
- **Docker deployment**: Single container, self-hosted
- **Sub-directory projects**: Subdirectories can be opened as separate projects
- **Intentionally minimal**: "Low maintenance project. The scope of features and support are purposefully kept narrow."
- **No frontmatter integration**: Cards are files in directories — the directory determines the column, not file metadata

## How it differs from daymark

- **Directory-based columns**: Like md-board, columns come from directory names, not frontmatter fields
- **Task manager, not artifact visualizer**: Creates its own task files in its own directory structure
- **Docker/self-hosted**: Heavier deployment model than a local `uvx` command
- **No lifecycle awareness**: No tracks, no phase ordering, no terminal states, no enforce-order
- **No filesystem watching for external changes**: Designed as the sole interface to the files

## Relevance to swain

Tasks.md is a simple task board that uses markdown files in directories. It doesn't read frontmatter, can't handle multiple tracks, and has no lifecycle awareness. Not suitable for visualizing swain's artifact tree.
