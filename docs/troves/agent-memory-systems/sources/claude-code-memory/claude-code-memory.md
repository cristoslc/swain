---
source-id: "claude-code-memory"
title: "How Claude Remembers Your Project — Claude Code Docs"
type: web
url: "https://code.claude.com/docs/en/memory"
fetched: 2026-03-23T00:00:00Z
hash: "b320714b266f4b1254520258279197cf071fc08cd7cf54fde7bc2c51b97b55fe"
---

# How Claude Remembers Your Project

Each Claude Code session begins with a fresh context window. Two mechanisms carry knowledge across sessions:

- **CLAUDE.md files**: instructions you write to give Claude persistent context
- **Auto memory**: notes Claude writes itself based on your corrections and preferences

## CLAUDE.md vs Auto Memory

Claude Code has two complementary memory systems. Both are loaded at the start of every conversation. Claude treats them as context, not enforced configuration.

|  | CLAUDE.md files | Auto memory |
| --- | --- | --- |
| **Who writes it** | You | Claude |
| **What it contains** | Instructions and rules | Learnings and patterns |
| **Scope** | Project, user, or org | Per working tree |
| **Loaded into** | Every session | Every session (first 200 lines) |
| **Use for** | Coding standards, workflows, project architecture | Build commands, debugging insights, preferences Claude discovers |

## CLAUDE.md Files

CLAUDE.md files are markdown files that give Claude persistent instructions for a project, your personal workflow, or your entire organization.

### Scope Hierarchy

| Scope | Location | Purpose |
| --- | --- | --- |
| **Managed policy** | `/Library/Application Support/ClaudeCode/CLAUDE.md` (macOS) | Organization-wide instructions managed by IT/DevOps |
| **Project instructions** | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Team-shared instructions for the project |
| **User instructions** | `~/.claude/CLAUDE.md` | Personal preferences for all projects |

### Import Syntax

CLAUDE.md files can import additional files using `@path/to/import` syntax. Imported files are expanded and loaded into context at launch. Both relative and absolute paths are allowed, with a maximum depth of five hops.

### Loading Behavior

Claude Code reads CLAUDE.md files by walking up the directory tree from the current working directory. Files in subdirectories are included when Claude reads files in those subdirectories (lazy loading).

### Rules Directory (`.claude/rules/`)

For larger projects, instructions can be organized into `.claude/rules/` as individual markdown files. Rules can be scoped to specific file paths using YAML frontmatter with a `paths` field and glob patterns.

```yaml
---
paths:
  - "src/api/**/*.ts"
---
# API Development Rules
- All API endpoints must include input validation
```

Rules without a `paths` field are loaded unconditionally at launch.

## Auto Memory

Auto memory lets Claude accumulate knowledge across sessions without the user writing anything. Claude saves notes for itself as it works: build commands, debugging insights, architecture notes, code style preferences, and workflow habits.

### Storage Location

Each project gets its own memory directory at `~/.claude/projects/<project>/memory/`. The `<project>` path is derived from the git repository, so all worktrees and subdirectories within the same repo share one auto memory directory.

```
~/.claude/projects/<project>/memory/
├── MEMORY.md          # Concise index, loaded into every session
├── debugging.md       # Detailed notes on debugging patterns
├── api-conventions.md # API design decisions
└── ...                # Any other topic files Claude creates
```

### How It Works

- The first 200 lines of `MEMORY.md` are loaded at the start of every conversation
- Content beyond line 200 is not loaded at session start
- Claude keeps `MEMORY.md` concise by moving detailed notes into separate topic files
- Topic files are not loaded at startup — Claude reads them on demand
- Auto memory is machine-local; not shared across machines or cloud environments

### Subagent Memory

Subagents can also maintain their own auto memory, configured via subagent configuration.

### Configuration

Auto memory is on by default (requires Claude Code v2.1.59+). Toggle via `/memory` in a session or set `autoMemoryEnabled: false` in project settings. Environment variable: `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`.

## Memory Design Principles

- CLAUDE.md content is delivered as a user message after the system prompt, not as part of it
- No guarantee of strict compliance — more specific/concise instructions work better
- CLAUDE.md fully survives compaction (`/compact` re-reads from disk)
- Target under 200 lines per CLAUDE.md file
- Use markdown headers and bullets for structure
- Write concrete, verifiable instructions
