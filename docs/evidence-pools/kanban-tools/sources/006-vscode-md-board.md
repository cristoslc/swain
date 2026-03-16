---
source-id: "006"
title: "VS Code Markdown Board (md-board) — Frontmatter-powered kanban in VS Code"
type: web
url: "https://marketplace.visualstudio.com/items?itemName=iketiunn.md-board"
fetched: 2026-03-15T02:40:00Z
hash: "pending"
---

# VS Code Markdown Board (md-board)

VS Code extension that visualizes a folder of markdown files as a kanban board powered by frontmatter. Version 0.0.5 (February 2026). **8 installs.**

## Key characteristics

- **Directory-based columns**: Root-level files go to "Inbox", subdirectory names become column names. Does NOT use a frontmatter field for column assignment.
- **Optional frontmatter**: `title` and `summary` fields for card display. No status/phase field.
- **Drag-and-drop**: Moving cards moves files between directories.
- **File watching**: Detects external changes in real time.
- **Very early stage**: 8 installs, version 0.0.5. Minimal feature set.

## How it differs from daymark

- **Directory-based, not frontmatter-field-based**: Columns come from subdirectory names, not from a configurable frontmatter field value.
- **No multi-track support**: Single flat board, no concept of different artifact types.
- **No tracks configuration**: No equivalent of daymark.tracks.yml — no phase ordering, no terminal states, no enforce-order.
- **VS Code only**: Requires VS Code as the host application.

## Relevance to swain

Closest existing tool to daymark's concept — it reads a folder of markdown files and renders a board. But its directory-based column model is simpler than daymark's frontmatter-field-driven approach. It cannot handle swain's multi-track lifecycle and has no concept of phase ordering. Too early-stage and limited to be a replacement.
