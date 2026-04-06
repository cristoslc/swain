---
source-type: web-page
title: "CLAUDE.md, AGENTS.md, and Every AI Config File Explained"
url: https://www.deployhq.com/blog/ai-coding-config-files-guide
fetched: 2026-04-06
---

# AI Config Files Guide

Comprehensive comparison of all agent configuration file conventions.

## Cross-tool project layout

```
your-project/
├── AGENTS.md          ← Universal instructions (Codex, Cursor, Claude Code)
├── CLAUDE.md          ← Claude-specific additions (if needed)
├── .github/
│   └── copilot-instructions.md ← Copilot-specific
├── .cursor/
│   └── rules/         ← Cursor-specific scoped rules
└── ...
```

## Tool-specific directories

| Tool | Config Directory | Skills Path |
|------|-----------------|-------------|
| Claude Code | `.claude/` | `.claude/skills/` |
| Cursor | `.cursor/` | `.cursor/rules/` |
| Codex | `.agents/` | `.agents/skills/` |
| Copilot | `.github/` | N/A |
| Windsurf | N/A (uses Memories) | N/A |

## Key observations

- AGENTS.md is "the closest thing to a universal standard."
- Claude Code also reads AGENTS.md as fallback.
- No tool defines a `.agents/bin/` or `.agents/scripts/` directory.
- Scripts live within skills, not in a separate top-level directory.
- The ecosystem is converging on `.agents/skills/` for portable skill packages.
