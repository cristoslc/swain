---
source-id: "005"
title: "Obsidian Kanban — Markdown-backed Kanban boards in Obsidian"
type: web
url: "https://github.com/obsidian-community/obsidian-kanban"
fetched: 2026-03-15T02:35:00Z
hash: "pending"
---

# Obsidian Kanban

Create markdown-backed Kanban boards in Obsidian. One of the most popular Obsidian plugins.

## Key characteristics

- **Boards are special markdown files**: Each board is a single `.md` file using Obsidian-specific markdown syntax (headings = columns, list items = cards).
- **Locked to Obsidian**: Board files won't render as kanban without the plugin. Requires Obsidian as the host application.
- **Board-centric, not file-centric**: A board file _contains_ cards as list items. It does not render _a folder of existing files_ as a kanban board.
- **No YAML frontmatter integration**: Cards are markdown list items within the board file, not external files with frontmatter fields.
- **Rich card features**: Due dates, tags, checkboxes, links to other notes.

## How it differs from daymark

- **Requires Obsidian**: Not a standalone tool. Can't be used in a swain/terminal workflow.
- **Board _is_ the file**: You create a kanban.md that defines the board. Daymark reads _existing_ files and derives the board from their frontmatter.
- **No lifecycle awareness**: No concept of tracks, phase sequences, or enforce-order. Just freeform columns.
- **No filesystem watching**: It's an editor plugin, not a filesystem tool.

## Relevance to swain

Obsidian Kanban is the most popular markdown kanban tool but operates in a fundamentally different model. It requires adopting Obsidian as your workspace and creating board-specific files. It cannot read swain's existing artifact tree and derive a board from frontmatter fields. Not a viable alternative.
