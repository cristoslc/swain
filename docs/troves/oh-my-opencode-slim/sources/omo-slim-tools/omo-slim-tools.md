---
source-id: omo-slim-tools
title: oh-my-opencode-slim — Tools & Capabilities
url: https://github.com/alvinunreal/oh-my-opencode-slim/blob/master/docs/tools.md
fetched: 2026-05-05
type: documentation
---

# Tools & Capabilities

## apply_patch Rescue

Intercepts `apply_patch` before native execution. Rewrites stale patches, canonizes tolerant matches against real files, preserves EOL/final-newline state, uses bounded LCS fallback, blocks patches outside allowed root/worktree, fails on ambiguity.

## Web Fetch (`webfetch`)

Fetches remote pages with content extraction for docs/static sites. Blocks cross-origin redirects. Falls back to raw content when secondary-model summarization unavailable.

## Code Search Tools

| Tool | Description |
|------|-------------|
| `grep` | Fast content search (ripgrep) |
| `ast_grep_search` | AST-aware code pattern matching across 25 languages |
| `ast_grep_replace` | AST-aware code refactoring with dry-run support |

`ast_grep` understands code structure for structural queries like "all arrow functions returning JSX."

## Formatters

OpenCode auto-formats files on write/edit using language-specific formatters (Prettier, Biome, gofmt, rustfmt, ruff, 20+ others).

## Todo Continuation

Auto-continue feature with configurable cooldowns, max continuations, and auto-enable thresholds. See dedicated [Todo Continuation](todo-continuation.md) doc.
