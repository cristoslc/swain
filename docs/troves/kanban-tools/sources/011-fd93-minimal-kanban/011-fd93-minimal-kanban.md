---
source-id: "011"
title: "fd93 — The Most Minimal Kanban (essay on filesystem-as-board)"
type: web
url: "https://fd93.me/minimal-kanban"
fetched: 2026-03-15T02:50:00Z
hash: "pending"
---

# The Most Minimal Kanban

Essay by Frank Davies (August 2025) exploring using the filesystem itself as a kanban board — directories as columns, files as cards, `mv` as the transition operation.

## Key argument

- Existing kanban tools (Trello, Obsidian Kanban, kanban.bash) require context switching from CLI workflows
- Non-portable data formats lock you into specific tools
- The filesystem already has the structure you need: directories = columns, files = work items
- Move files between directories to transition them

## Limitations identified

- **No sort order**: Filesystem has no concept of priority ordering within a directory
- **No metadata**: No way to surface task details from filename alone (unless you add frontmatter, which requires scripting)
- **No WIP limits, no history, no due dates** without structured metadata in files

## Resolution

Author concludes pure filesystem kanban is too minimal for real use. Built [plainban](https://codeberg.org/fd93/plainban) — a tool that uses the filesystem as data store but adds scripting for metadata.

## Relevance to swain

This essay validates daymark's design space. Swain already uses phase subdirectories + frontmatter — it has both the filesystem structure AND the metadata. Daymark gives this a visual face without introducing any new data model. The essay's conclusion (pure filesystem is too minimal, you need metadata) is exactly where daymark starts: files with YAML frontmatter.
