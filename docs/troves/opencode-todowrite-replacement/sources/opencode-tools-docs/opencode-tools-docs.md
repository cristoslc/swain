---
source: https://opencode.ai/docs/tools/
type: web
title: "OpenCode Tools Documentation"
fetched: 2026-04-30
proxy-used: none
---

# OpenCode Tools Documentation

OpenCode's built-in tools include: bash, edit, write, read, grep, glob, lsp (experimental), apply_patch, skill, todowrite, webfetch, websearch, question.

## The `todowrite` Tool

- **Purpose**: Manage todo lists during coding sessions.
- **Permission config**: `todowrite: "allow"` in `opencode.json`.
- **Disabled for subagents by default**, but can be enabled manually.
- **Session-bound**: Stored in-memory, lost on session end.

## Tool Name Collision

Custom tools that use the same name as a built-in tool take precedence. This is the primary mechanism for replacing the `todowrite` tool entirely.

## Disabling

Individual tools can be disabled via permissions without overriding them.
