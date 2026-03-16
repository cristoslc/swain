---
source-id: "012"
title: "taskell — CLI kanban board with markdown storage"
type: web
url: "https://github.com/smallhadroncollider/taskell"
fetched: 2026-03-15T02:50:00Z
hash: "pending"
---

# taskell

CLI kanban board/task manager for Mac and Linux, written in Haskell. Stores data as a single markdown file.

## Key characteristics

- **Single markdown file**: Board state stored in one `.md` file (headings = columns, list items = tasks)
- **vim-style key-bindings**: Terminal UI with vim navigation
- **Clean diffs**: Markdown storage enables version control
- **Sub-tasks and due dates**: Task metadata within the markdown structure
- **Trello/GitHub imports**: Can import from external boards
- **Appears unmaintained**: Last significant activity several years ago

## How it differs from daymark

- **Single-file board**: All tasks live in one markdown file. Not a filesystem scanner.
- **Board-centric, not file-centric**: Like Obsidian Kanban, the board IS the file, not a view over many files.
- **TUI only**: No web UI, no browser-based board.
- **No frontmatter**: Uses markdown structure (headings, lists), not YAML frontmatter.

## Relevance to swain

taskell stores its board in a single file. It doesn't read a folder of existing files with frontmatter. Completely different data model from swain's artifact tree. Not a viable alternative.
