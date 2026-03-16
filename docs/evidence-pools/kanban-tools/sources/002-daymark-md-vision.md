---
source-id: "002"
title: "daymark-md — Vision"
type: local
path: "docs/evidence-pools/kanban-tools/files.zip#VISION.md"
fetched: 2026-03-15T02:30:00Z
hash: "pending"
---

# Daymark Vision

Built as a visual companion to swain. Swain produces structured markdown artifacts (Visions, Epics, Specs, Spikes, ADRs) that move through lifecycle phases tracked in YAML frontmatter and phase subdirectories. The artifacts are inspectable and diffable, but reading a directory tree to understand project state is tedious. Daymark gives that tree a face.

## Principles

- **Your files are the source of truth.** No database, no sync layer, no shadow state.
- **Configuration lives in one file.** A single `daymark.tracks.yml`.
- **Transitions are the user's responsibility.** Daymark can enforce forward-only phase ordering but does not run hooks, scripts, or validation.
- **Local-first, single-user, zero-network.**

## Non-goals

- Multiplayer / collaboration features
- Cloud sync or hosted mode
- Replacing your text editor
- Running lifecycle hooks or enforcing workflow rules beyond column ordering
- Supporting non-markdown file formats
