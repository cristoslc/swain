---
source: https://opencode.ai/docs/plugins/
type: web
title: "OpenCode Plugins Documentation"
fetched: 2026-04-30
proxy-used: none
---

# OpenCode Plugins Documentation

Plugins extend OpenCode via hooks and custom tools. Two loading modes:

1. **Local files**: `.opencode/plugins/` (project) or `~/.config/opencode/plugins/` (global).
2. **npm packages**: Listed in `opencode.json` under `plugin` array.

## Custom Tools via Plugins

Plugins can expose tools using the `tool` helper:

```ts
export const CustomToolsPlugin: Plugin = async (ctx) => {
  return {
    tool: {
      mytool: tool({
        description: "This is a custom tool",
        args: { foo: tool.schema.string() },
        async execute(args, context) {
          return `Hello ${args.foo}`;
        },
      }),
    },
  };
};
```

Note: "If a plugin tool uses the same name as a built-in tool, the plugin tool takes precedence."

## Relevant Hooks

- `tool.execute.before` / `tool.execute.after` — intercept tool execution.
- `todo.updated` — fires when the todo list changes (can sync to external storage).
- `session.compacted` — fires before context compaction.
- `experimental.session.compacting` — customize compaction prompts.

## Dependencies

Add `.opencode/package.json` with dependencies for local plugins.
