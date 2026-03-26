---
source-id: "gemini-cli-memory"
title: "Gemini CLI Memory Management and save_memory Tool"
type: web
url: "https://geminicli.com/docs/cli/tutorials/memory-management/"
fetched: 2026-03-23T00:00:00Z
hash: "c18f9d45e8ed2ae81c87d4dd58d686c26bf202361af64a9680c995bf6521d0b2"
---

# Gemini CLI Memory System

Gemini CLI uses two complementary mechanisms for persistent context: GEMINI.md instruction files and a `save_memory` tool for fact persistence.

## GEMINI.md — Project-Wide Rules

The primary way to control the agent's behavior is through `GEMINI.md` files. These are Markdown files containing instructions that are automatically loaded into every conversation.

### Hierarchy

1. **Global**: `~/.gemini/GEMINI.md` — rules for every project
2. **Project Root**: `./GEMINI.md` — rules for the current repository
3. **Subdirectory**: `./src/GEMINI.md` — rules specific to that folder

Context is loaded hierarchically. More specific files take precedence over broader ones.

### Usage

```markdown
# Project Instructions
- **Framework:** We use React with Vite.
- **Styling:** Use Tailwind CSS for all styling. Do not write custom CSS.
- **Testing:** All new components must include a Vitest unit test.
- **Tone:** Be concise. Don't explain basic React concepts.
```

## save_memory Tool — Fact Persistence

The `save_memory` tool allows the Gemini agent to persist specific facts, user preferences, and project details across sessions.

### Technical Reference

- **Arguments**: `fact` (string, required) — a clear, self-contained statement in natural language
- **Storage**: Appends to the `## Gemini Added Memories` section of the global `GEMINI.md` file (`~/.gemini/GEMINI.md`)
- **Loading**: Stored facts are automatically included in the hierarchical context system for all future sessions
- **Format**: Saves data as a bulleted list item within a dedicated Markdown section

### Invocation

Natural language triggers — user says "Remember that..." or "Save the fact that..." and the agent calls `save_memory` automatically.

### Use Cases

- Persisting user preferences ("I prefer functional programming")
- Saving project-wide architectural decisions
- Storing frequently used aliases or system configurations

## Memory Management Commands

- `/memory show` — displays the full concatenated set of instructions currently loaded (all GEMINI.md files + saved memories)
- `/memory reload` — forces a reload if GEMINI.md was edited during a session

## Key Design Characteristics

- **Simple append model**: save_memory only appends facts; no update, consolidation, or deletion mechanism
- **Global scope only**: saved memories go to the global GEMINI.md, not project-specific files
- **No automatic extraction**: unlike Claude Code and Codex, Gemini CLI does not autonomously extract memories from conversations — the user must explicitly ask the agent to remember something
- **Hierarchical context loading**: GEMINI.md files load in a cascade from global to subdirectory
- **Plain markdown**: all context is stored as human-readable, editable markdown
