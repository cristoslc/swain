---
source-type: web-page
title: "everything-claude-code AGENTS.md — Community Plugin"
url: https://github.com/affaan-m/everything-claude-code/blob/main/AGENTS.md
fetched: 2026-04-06
---

# everything-claude-code Directory Layout

A production community plugin with 38 agents, 156 skills, 72 commands. Shows real-world directory conventions at scale.

## Directory structure

```
agents/     — 38 specialized subagents
skills/     — 156 workflow skills and domain knowledge
commands/   — 72 slash commands
hooks/      — Trigger-based automations
rules/      — Always-follow guidelines (common + per-language)
scripts/    — Cross-platform Node.js utilities
mcp-configs/ — 14 MCP server configurations
tests/      — Test suite
```

## Key observation

This project uses **`scripts/`** (not `bin/`) for cross-cutting utility scripts. Skills contain their own scripts internally. The top-level `scripts/` holds shared utilities that aren't tied to a specific skill — the same role swain's `.agents/bin/` serves, but named `scripts/`.
