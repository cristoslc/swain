---
title: "Claude Code Skills vs MCP vs Plugins: Complete Guide 2026"
source-url: "https://www.morphllm.com/claude-code-skills-mcp-plugins"
fetch-date: "2026-05-01"
type: web-page
publisher: "MorphLLM"
---

# Claude Code Skills vs MCP vs Plugins: Complete Guide 2026

## Key Distinctions

Claude Code has five extension types:

| Type | Purpose | Token Cost | Best For |
|------|---------|-----------|----------|
| Skills | Teach procedures | 30-50 tokens/skill | Domain expertise |
| MCP | Connect tools | Varies (can be 50k+) | External integrations |
| Plugins | Bundle & share | Sum of contents | Team standardization |
| Hooks | Automate actions | Minimal | Workflow triggers |
| Commands | Prompt shortcuts | Minimal | Frequent operations |

## Skills Architecture

Skills use progressive disclosure:
1. Metadata scan — Claude loads only names and descriptions (~30-50 tokens per skill).
2. Relevance match — if a skill matches the current task, full instructions load.
3. Resource loading — scripts and files load only when executed.

You can have 100+ skills installed without impacting context.

## MCP Token Problem

A five-server setup with 58 tools can use 55,000+ tokens before any conversation starts. Anthropic's Tool Search feature reduces this by ~85% through on-demand tool discovery.

## Skills vs MCP Decision Framework

- Skills = procedural knowledge (30-50 tokens each, loaded on-demand).
- MCP = external tool connections (can use 50k+ tokens).
- Hooks = actions that *must* happen.
- Skills = guidance that *should* be followed.

## Plugins as Bundles

Plugins package commands, agents, skills, hooks, and MCP configs into distributable units. Installed via `/plugin install github.com/username/my-plugin`.
