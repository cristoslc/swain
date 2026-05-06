---
title: AGENTS.md - Simple Open Format for Guiding Coding Agents
url: https://agents.md/
source-type: web-page
fetched: 2026-05-05
transcript-source: web-page
---

# AGENTS.md

## Overview

AGENTS.md is a simple, open format for guiding coding agents.

## Philosophy

> "Think of AGENTS.md as a README for agents: a dedicated, predictable place to provide context and instructions to help AI coding agents work on your project."

## Key Principles

- **Single file**: One file per directory
- **Plain markdown**: Standard Markdown syntax
- **Optional metadata**: Simple frontmatter support
- **Human-first**: Readable by humans and agents
- **Tool-agnostic**: Works across different AI tools

## Governance

AGENTS.md is now stewarded by the **Agentic AI Foundation (AAIF)** under the Linux Foundation.

> "AGENTS.md emerged from collaborative efforts across the AI software development ecosystem, including OpenAI Codex, Amp, Jules from Google, Cursor, and Factory."

## How It Works

### Hierarchical Structure

Place AGENTS.md files throughout your repository:
- Root level for project-wide guidance
- Nested directories for package/module-specific instructions
- Agents read the nearest file in the directory tree

Example from OpenAI: main repo has 88 AGENTS.md files.

### Precedence

More specific files take precedence over general ones:
1. `AGENTS.override.md` (highest priority)
2. `AGENTS.md`
3. `TEAM_GUIDE.md`
4. `.agents.md` (lowest priority)

### Configuration Discovery

Agents read AGENTS.md files before doing any work. By layering:
- Global guidance (home directory)
- Project-specific overrides
- Directory-specific instructions

Agents start each task with consistent expectations.

## Format

Standard Markdown with optional frontmatter:

```markdown
---
tools: ["eslint", "jest", "typescript"]
---

# Project Guidelines

## Build Commands
- Run `npm run build` for production builds
- Run `npm test` for unit tests
```

## Supported Tools

- OpenAI Codex
- GitHub Copilot
- Google Jules
- Cursor
- Factory
- Amp
- Many others

## Global Configuration

### Current State (Fragmented)
Each tool uses different global config paths:
- Claude Code: `~/.claude/CLAUDE.md`
- Codex: `~/.codex/AGENTS.md`
- droid: `~/.factory/AGENTS.md`
- Amp: `~/.config/AGENTS.md`

### Proposed Standard
Issue #91 proposes: `~/.config/agents/AGENTS.md`

## Comparison to Other Standards

| Tool | Configuration |
|------|--------------|
| Cursor | `.cursor/rules/` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Claude | `.claude/skills/` |
| AGENTS.md | `AGENTS.md` (standard markdown) |

## Benefits

1. **No proprietary format**: Standard markdown
2. **Hierarchical**: Directory-level specificity
3. **Portable**: Works across tools
4. **Version controlled**: Lives in repo
5. **Human readable**: Not just for agents

## Example Content

```markdown
# AGENTS.md

## Repository Expectations
- Run `npm run lint` before opening a pull request
- Document public utilities in `docs/` when you change behavior
- Add overrides in nested directories when specific teams need different rules

## Dev Environment Tips
- Use `pnpm dlx turbo run where <project_name>` to jump to a package
- Run `pnpm install --filter <project_name>` to add packages
```

## Relationship to README.md

> "README.md files are for humans: quick starts, project descriptions, and contribution guidelines. AGENTS.md complements this by containing the extra, sometimes detailed context coding agents need: build steps, tests, and conventions that might clutter a README or aren't relevant to human contributors."

---

Sources:
- https://agents.md/
- https://github.com/agentsmd/agents.md
- https://developers.openai.com/codex/guides/agents-md
- https://github.com/openai/codex/blob/main/AGENTS.md
