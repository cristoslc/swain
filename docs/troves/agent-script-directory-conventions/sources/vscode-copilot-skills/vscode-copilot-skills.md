---
source-type: web-page
title: "Use Agent Skills in VS Code — GitHub Copilot"
url: https://code.visualstudio.com/docs/copilot/customization/agent-skills
fetched: 2026-04-06
---

# VS Code / GitHub Copilot Agent Skills

GitHub Copilot's implementation of Agent Skills in VS Code.

## Key features

- `/create-skill` command generates SKILL.md with directory structure.
- Skills are portable across skills-compatible agents.
- Skills from installed plugins appear alongside locally defined skills.
- Terminal tool provides controls for script execution (auto-approve, allow-lists).

## Directory conventions

- Standard layout: `SKILL.md`, `scripts/`, `references/`, `assets/`.
- Skills are "packages" vs commands which are "single files."
- Personal skills in `~/.claude/skills/` (Claude Code compatible).

## Key observation

VS Code explicitly uses `scripts/` within skills, not `bin/`. The convention is consistent across all Agent Skills implementations.
