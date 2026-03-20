---
source-id: drift-guard-cli
type: web
url: https://news.ycombinator.com/item?id=47380526
fetched: 2026-03-19
---

# drift-guard: Protect Your UI from AI Agents' Design Drift

Source: Hacker News Show HN (2026)

## What It Is

A pure CLI tool that snapshots design tokens and DOM structure, then checks for "drift" at the code level. Zero token overhead, no MCP server.

## How It Works

1. `init` — scans CSS/HTML and snapshots all design tokens (colors, fonts, spacing, shadows, radius, layout, effects) + structural fingerprint of DOM
2. `rules` — generates rule files for 5 AI tools (.cursorrules, CLAUDE.md, AGENTS.md, copilot-instructions.md, .clinerules)
3. `check` — compares current state against the snapshot; exits with code 1 if drift exceeds threshold

## Design Decisions

- **Zero token overhead** — pure CLI, no AI involvement in the checking
- **Static analysis** — uses css-tree and cheerio (no headless browser, < 1 second)
- **Stale snapshot warning** — warns if baseline is older than 7 days
- **Structure + Style** — monitors both CSS tokens and DOM hierarchy
- **Pre-commit hook** — blocks drifted commits before they land

## Relevance to Swain

This tool addresses the specific problem of AI coding agents changing UI without the developer noticing. The "snapshot + check" pattern is analogous to what swain needs for DESIGN artifacts: snapshot the intended design state, then check if implementation has drifted.

Key difference: drift-guard works at the *code* level (CSS/DOM), while swain's DESIGN artifacts work at the *document* level (markdown descriptions of interaction design). Swain would need to bridge from document-level intent to code-level verification.
