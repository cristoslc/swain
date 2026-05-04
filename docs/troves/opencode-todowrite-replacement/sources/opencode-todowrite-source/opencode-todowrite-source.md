---
source: https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/tool/todowrite.txt
type: web
title: "OpenCode todowrite Tool Source (prompt text)"
fetched: 2026-04-30
proxy-used: none
---

# OpenCode todowrite Tool Source

The `todowrite.txt` file is the system prompt text injected into sessions to describe the todowrite tool to the LLM.

## Schema (inferred from issues + docs)

The todowrite tool accepts a single parameter `todos` which is an array of objects:

```json
{
  "todos": [
    {
      "content": "Task description",
      "status": "pending | in_progress | completed | cancelled",
      "priority": "high | medium | low"
    }
  ]
}
```

No id field is required by the schema — the tool manages that internally.

## Known Failure Modes with Open-Weight Models

1. **Stringified JSON**: Models send `todos` as a string instead of an actual array. Error: `"expected array, received string"`. (Issue #7512, #1373, #10813)
2. **Wrong tool name**: Models try `todowrite`, `TodoWrite`, `update_plan`, `TodoRead` instead of `todowrite`. (Issue #234, #12938, obra/superpowers#654)
3. **Capitalization mismatch**: Qwen models generate `Write` instead of `write`. (Issue #234)
4. **Empty parameters**: Models call with `{}` causing strict-mode validation failures. (Issue #11357)
5. **Missing description**: The `bash` tool requires a `description` parameter that some models don't send. (Issue #13146) — illustrative of systemic tool-calling brittleness with open-weight models.
6. **Subagent denial**: Even when enabled in agent config, subagents can't use todowrite. (Issue #12938)

## System Prompt Guidance

The tool description includes extensive examples and reasoning about when to use/not use the todowrite tool. The prompt emphasizes marking tasks completed immediately, not batching.

The Anthropic-specific system prompt at `packages/opencode/src/session/prompt/anthropic.txt` says: "IMPORTANT: Always use the TodoWrite tool to plan and track tasks throughout the conversation."
