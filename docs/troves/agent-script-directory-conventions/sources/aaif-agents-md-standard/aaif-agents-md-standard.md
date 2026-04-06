---
source-type: web-page
title: "Linux Foundation Announces AAIF — AGENTS.md, MCP, Goose"
url: https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation
fetched: 2026-04-06
---

# Agentic AI Foundation (AAIF)

Formed December 2025 under the Linux Foundation. Three founding contributions:

1. **Model Context Protocol (MCP)** — donated by Anthropic.
2. **AGENTS.md** — donated by OpenAI. Simple, universal standard for giving AI coding agents project-specific guidance.
3. **Goose** — donated by Block. Open source agent framework.

## AGENTS.md adoption

- Introduced January 2025 by OpenAI for Codex.
- 60,000+ open-source repositories adopted as of early 2026.
- Supported by: Codex, Cursor, Windsurf, GitHub Copilot, Gemini CLI, Jules, Factory A, OpenCode.
- Claude Code reads AGENTS.md as fallback when no CLAUDE.md found.
- 4.7% of 10,000 surveyed repos contain agent config files; AGENTS.md in 1.6% overall (33% among AI-configured projects).

## Directory conventions established

- AGENTS.md at project root for instructions.
- `.agents/skills/` for agent skills (Codex convention, adopted by OpenCode and others).
- No standard for `.agents/bin/` — the spec doesn't define a top-level executable aggregation point.
