---
source-id: "003"
title: "daymark-md — Architecture"
type: local
path: "docs/evidence-pools/kanban-tools/files.zip#ARCHITECTURE.md"
fetched: 2026-03-15T02:30:00Z
hash: "pending"
---

# Daymark Architecture

Single Python process: uvicorn/starlette serving a local web UI and watching the filesystem.

## Components

- **Scanner**: Walks configured `scan_paths`, parses YAML frontmatter, builds in-memory card index. Re-indexes only changed files on watch events.
- **Tracks config**: Single YAML file defining column_field, scan_paths, track_field, tracks with phases/terminal/enforce_order, match rules, defaults.
- **Mutator**: Updates frontmatter on disk (atomic write-to-temp + rename). Moves files between phase subdirectories if applicable.
- **Watcher**: Uses `watchfiles`/`watchdog`, debounces events (100ms), pushes WebSocket deltas.
- **Frontend**: Static HTML + vanilla JS + CSS. Board view with columns, card detail panel (rendered markdown, inline frontmatter editor), filter/search bar.

## Data flow

- Startup: load config → walk scan_paths → build card index → start watcher → serve HTTP + WS
- Drag-and-drop: POST /api/cards/{id}/move → validate transition → update frontmatter → move file → watcher picks up → WS push
- External edit: watcher detects → scanner re-parses → index updated → WS push → board re-renders

## Future considerations (not planned)

- Git integration (show lifecycle commit hashes on cards)
- Relationship graph (render depends-on-artifacts as edges)
- Multiple boards (tabs or board picker)
- Plugin hooks (pre/post-move validation)
