---
source-id: "001"
title: "daymark-md — README"
type: local
path: "docs/evidence-pools/kanban-tools/files.zip#README.md"
fetched: 2026-03-15T02:30:00Z
hash: "pending"
---

# daymark-md

**A kanban board for your markdown files.**

Daymark reads a folder of markdown files, groups them into columns by a YAML frontmatter field, and renders an interactive kanban board in your browser. Drag a card to a new column and Daymark updates the frontmatter on disk. Edit a file in your text editor and the board updates in real time.

No database. No sync service. No account. Your files are the board.

## Key capabilities

- Reads `daymark.tracks.yml` config to know which frontmatter field drives columns
- Supports multiple lifecycle tracks with different phase sequences
- Optionally enforces forward-only transitions per track
- Watches filesystem and live-updates the board when files change externally
- Opens files for viewing rendered markdown and editing frontmatter
- Supports phase subdirectories (auto-detects and moves files between subdirs)
- Distributed as a Python package on PyPI: `uvx daymark-md`
- Static HTML + vanilla JS + CSS frontend, no build step

## What it doesn't do

- Replace your text editor — Daymark is for triage and navigation
- Run hooks, scripts, or CI on transitions
- Store anything outside your existing files — no database, no dotfile state
- Make network requests — fully local, fully offline
