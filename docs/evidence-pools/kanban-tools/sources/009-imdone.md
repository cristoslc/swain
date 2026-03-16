---
source-id: "009"
title: "Imdone — Markdown kanban board (local-first)"
type: web
url: "https://imdone.io/markdown-kanban-board"
fetched: 2026-03-15T02:45:00Z
hash: "pending"
---

# Imdone

Local-first kanban board that turns markdown blocks in your notes and code into cards. Desktop app + CLI + npm package.

## Key characteristics

- **Token-based card detection**: Recognizes TODO, DOING, DONE, FIXME, HACK, etc. in markdown files and code comments
- **In-file markers**: Cards are inline tokens (`#TODO: description`) within existing files, not separate files
- **Jira/GitHub sync**: Bidirectional sync with external issue trackers via imdone-cli
- **Rich metadata**: Tags, contexts, due dates, custom ordering — stored as HTML comments in the source file
- **Real-time file watching**: Changes appear on the board instantly
- **Drag-and-drop**: Moving cards updates the source file token
- **Desktop app + CLI + npm**: Multiple interfaces

## How it differs from daymark

- **Token-based, not frontmatter-based**: Imdone reads inline TODO/DOING/DONE markers within files. Daymark reads YAML frontmatter fields.
- **Card = inline marker, not file**: An imdone card is a comment/heading inside a file. A daymark card is an entire file.
- **No lifecycle tracks**: Single board with token-based columns. No concept of multiple artifact types following different phase sequences.
- **No phase subdirectory support**: Doesn't understand file location as a lifecycle signal.

## Relevance to swain

Imdone is designed for TODO tracking within code and notes, not for visualizing a tree of structured artifacts with lifecycle frontmatter. It reads inline markers, not YAML frontmatter fields. Swain's artifact model (one file = one artifact, frontmatter drives lifecycle) is fundamentally different from imdone's model (one file contains many inline cards). Not a viable alternative.
