---
source: https://opencode.ai/docs/custom-tools/
type: web
title: "OpenCode Custom Tools Documentation"
fetched: 2026-04-30
proxy-used: none
---

# OpenCode Custom Tools Documentation

Custom tools are TypeScript/JavaScript functions the LLM can call during conversations.

## Key Mechanics for Replacing Built-in Tools

1. **Location**: `.opencode/tools/` (project) or `~/.config/opencode/tools/` (global).
2. **Filename becomes tool name**: A file named `todowrite.ts` creates a `todowrite` tool.
3. **Name collision = replacement**: If a custom tool uses the same name as a built-in tool, the custom tool takes precedence.
4. **Use `tool()` helper** from `@opencode-ai/plugin` for type-safety and Zod schema validation.
5. **Context**: Tools receive `{ agent, sessionID, messageID, directory, worktree }`.

## Multiple Tools Per File

Named exports create tools as `<filename>_<exportname>`. Default exports use just the filename.

## Python Interop

Tools can invoke external scripts via `Bun.$`\`python3 ...\``.

## Dependencies

Add a `.opencode/package.json` with external npm dependencies; OpenCode runs `bun install` at startup.
