---
source-id: omo-deepwiki-overview
type: web
url: "https://deepwiki.com/code-yeongyu/oh-my-openagent"
fetched: 2026-04-19T12:00:00Z
title: "Oh My OpenAgent — DeepWiki Architecture Overview"
---

# Oh My OpenAgent — DeepWiki Architecture Overview

## Plugin Architecture

The plugin follows a strict initialization order defined in `src/index.ts`:

1. **Config loading** — JSONC parsing, Zod v4 validation, project/user merge, migration
2. **Manager creation** — TmuxSessionManager, BackgroundManager, SkillMcpManager, ConfigHandler
3. **Tool registration** — SkillContext, AvailableCategories, ToolRegistry (26 tools)
4. **Hook composition** — 3-tier: Core(43) + Continuation(7) + Skill(2) = 52 hooks
5. **Interface assembly** — 10 OpenCode hook handlers → PluginInterface

## Configuration Merging

User config (`~/.config/opencode/`) merges with project config (`.opencode/`):
- `agents`, `categories`, `claude_code`: deep merged recursively (prototype-pollution-safe)
- `disabled_*` arrays: set union (concatenated + deduplicated)
- All other fields: override replaces base value

## Three-Tier MCP System

| Tier | Source | Mechanism |
|------|--------|-----------|
| Built-in | `src/mcp/` | 3 remote HTTP: websearch (Exa/Tavily), context7, grep_app |
| Claude Code | `.mcp.json` | `${VAR}` env expansion via claude-code-mcp-loader |
| Skill-embedded | SKILL.md YAML | Managed by SkillMcpManager (stdio + HTTP) |

Skills load from `.opencode/skills/*/SKILL.md` (project), `~/.config/opencode/skills/*/SKILL.md` (user). Higher priority overrides lower.

## Hook Execution Flow

The plugin composes 52 hooks into 5 execution tiers. Each hook follows the `createXXXHook` factory pattern. Hooks intercept tool calls, transform messages, manage session lifecycle, and enforce quality constraints.

## Tool Categories

- **Task Management**: `task_create`, `task_list`, `task_get`, `task_update` with file-based persistence in `.sisyphus/tasks/`
- **Delegation**: `task` (delegate by category or agent type), `call_omo_agent` (spawn subagents with background support)
- **LSP Refactoring**: `lsp_goto_definition`, `lsp_diagnostics`, `lsp_rename`, `lsp_find_references`, `lsp_symbols`
- **Code Search**: `ast_grep_search`, `ast_grep_replace`, `grep`, `glob`
- **System**: `interactive_bash` (tmux), `look_at` (vision), `skill`, `hashline_edit` (hash-anchored editing), `background_output`, `background_cancel`
- **Session**: `session_list`, `session_read`, `session_search`, `session_info`

## Key Design Patterns

- **Factory pattern**: All tools, hooks, agents created via `createXXX()` functions
- **Barrel exports**: 104 index.ts files establish module boundaries
- **Runtime fallback**: Two separate systems — `model-fallback` (proactive, at chat.params) vs `runtime-fallback` (reactive, at session.error)
- **Dual package publishing**: `oh-my-opencode` + `oh-my-openagent` in transition period
- **Zod v4 validation**: All config validated at load time with safeParse fallback