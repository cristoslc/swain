---
source-type: web-page
title: "Agent Skills — Kiro IDE Docs"
url: https://kiro.dev/docs/skills/
fetched: 2026-04-06
---

# Kiro IDE Skills

Amazon's Kiro IDE implements the Agent Skills standard.

## Directory structure

```
my-skill/
├── SKILL.md           # Required
├── scripts/           # Optional executable code
├── references/        # Optional documentation
└── assets/            # Optional templates
```

## Discovery paths

- Workspace: `.kiro/skills/`
- Global: `~/.kiro/skills/`

## Key conventions

- Scripts in `scripts/` within each skill — "deterministic tasks" work better as scripts than LLM-generated alternatives.
- Skill folder name must match `name` field in frontmatter.
- Skills can be imported from GitHub repositories.
- No mention of `bin/` directories.
