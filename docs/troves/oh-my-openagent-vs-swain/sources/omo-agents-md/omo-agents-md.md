---
source-id: omo-agents-md
type: repository
url: "https://github.com/code-yeongyu/oh-my-openagent/blob/dev/AGENTS.md"
fetched: 2026-04-19T12:00:00Z
title: "Oh My OpenAgent — AGENTS.md (Architecture Reference)"
highlights:
  - omo-agents-md.md
selective: true
---

# oh-my-opencode — OpenCode Plugin AGENTS.md

## OVERVIEW

OpenCode plugin (npm: `oh-my-opencode`, dual-published as `oh-my-openagent`) extending Claude Code with 11 agents, 52 lifecycle hooks, 26 tools, 3-tier MCP system (built-in + .mcp.json + skill-embedded), Hashline LINE#ID edit tool, IntentGate classifier, and Claude Code compatibility. 1766 TypeScript source files, 377k LOC, 104 barrel index.ts files.

## Structure

```
oh-my-opencode/
├── src/
│   ├── index.ts              # Plugin entry
│   ├── plugin-config.ts      # JSONC multi-level config (Zod v4)
│   ├── agents/               # 11 agents
│   ├── hooks/                # 52 lifecycle hooks
│   ├── tools/                # 26 tools across 16 directories
│   ├── features/             # 19 feature modules
│   ├── shared/               # 170+ utility files (barrel-exported)
│   ├── config/               # Zod v4 schema system (32 files)
│   ├── cli/                  # CLI: install, run, doctor, mcp-oauth
│   ├── mcp/                  # 3 built-in remote MCPs
│   ├── plugin/               # 10 OpenCode hook handlers
│   ├── plugin-handlers/      # 6-phase config loading
│   └── openclaw/             # Bidirectional integration (Discord/Telegram/webhook)
├── packages/                 # 11 platform-specific binaries
├── script/                  # Build/publish automation
├── .sisyphus/               # AI agent workspace
└── .local-ignore/            # Dev-only test fixtures
```

## Initialization Flow

```
pluginModule.server(input, options)
  ├─→ loadPluginConfig()         # JSONC → project/user merge → Zod validate → migrate
  ├─→ createManagers()           # TmuxSessionManager, BackgroundManager, SkillMcpManager, ConfigHandler
  ├─→ createTools()              # SkillContext + AvailableCategories + ToolRegistry (26 tools)
  ├─→ createHooks()              # 3-tier: Core(43) + Continuation(7) + Skill(2) = 52 hooks
  └─→ createPluginInterface()    # 10 OpenCode hook handlers → PluginInterface
```

## 10 OpenCode Hook Handlers

| Handler | Purpose |
|---------|---------|
| `config` | 6-phase: provider → plugin-components → agents → tools → MCPs → commands |
| `tool` | 26 registered tools |
| `chat.message` | First-message variant, session setup, keyword detection |
| `chat.params` | Anthropic effort level, think mode, runtime fallback override |
| `chat.headers` | Copilot x-initiator header injection |
| `event` | Session lifecycle, openclaw dispatch, runtime fallback |
| `tool.execute.before` | Pre-tool hooks (file guard, label truncator, rules injector) |
| `tool.execute.after` | Post-tool hooks (output truncation, comment checker, hashline) |
| `experimental.chat.messages.transform` | Context injection, thinking block validation, tool pair validation |
| `experimental.session.compacting` | Context + todo preservation during compaction |

## Three-Tier MCP System

| Tier | Source | Mechanism |
|------|--------|-----------|
| Built-in | `src/mcp/` | 3 remote HTTP: websearch (Exa/Tavily), context7, grep_app |
| Claude Code | `.mcp.json` | `${VAR}` env expansion via claude-code-mcp-loader |
| Skill-embedded | SKILL.md YAML | Managed by SkillMcpManager (stdio + HTTP) |

## Agent Model Resolution

4-step resolution chain: override → category-default → provider-fallback → system-default. Agents have three modes: `primary` (respects UI model), `subagent` (own fallback chain), `all`.

## Hook Execution Order

Session (24) → Tool-Guard (14) → Transform (5) → Continuation (7) → Skill (2)

## Conventions

- **Runtime**: Bun only (1.3.11 in CI)
- **TypeScript**: strict mode, ESNext, bundler moduleResolution, `bun-types`
- **Test pattern**: Bun test with given/when/then style
- **Factory pattern**: `createXXX()` for all tools, hooks, agents
- **Config format**: JSONC with comments, Zod v4 validation, snake_case keys
- **File naming**: kebab-case for all files/directories
- **Module structure**: index.ts barrel exports, no catch-all files, 200 LOC soft limit
- **No path aliases**: relative imports only
- **Dual package**: `oh-my-opencode` + `oh-my-openagent` published simultaneously