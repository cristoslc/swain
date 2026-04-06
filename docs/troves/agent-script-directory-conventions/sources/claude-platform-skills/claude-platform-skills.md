---
source-type: web-page
title: "Agent Skills Overview — Claude Platform Docs"
url: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
fetched: 2026-04-06
---

# Claude Platform Agent Skills

Anthropic's native implementation of Agent Skills across Claude.ai, Claude API, Claude Code, and Claude Agent SDK.

## Skill structure

```
pdf-skill/
├── SKILL.md        (main instructions)
├── FORMS.md        (form-filling guide)
├── REFERENCE.md    (detailed API reference)
└── scripts/
    └── fill_form.py (utility script)
```

## Discovery paths (Claude Code)

- Personal: `~/.claude/skills/`
- Project: `.claude/skills/`
- Also reads `.agents/skills/` as agent-compatible path.

## Key conventions

- Scripts live in `scripts/` within each skill directory.
- Progressive disclosure: metadata always loaded (~100 tokens), SKILL.md on trigger, resources as needed.
- Claude reads SKILL.md via bash from the filesystem.
- Scripts run via bash; script code never enters context window — only output does.
- No concept of a top-level `bin/` directory.
- Skills are filesystem-based directories, not installed executables.

## Claude Code specifics

- Claude Code also reads AGENTS.md as a fallback if no CLAUDE.md is found.
- Skills can bundle deterministic scripts for operations better handled by code than LLM generation.
- Custom skills shared via Claude Code Plugins.
