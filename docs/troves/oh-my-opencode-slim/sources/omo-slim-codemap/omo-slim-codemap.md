---
source-id: omo-slim-codemap
title: oh-my-opencode-slim — Repository Atlas (codemap.md)
url: https://github.com/alvinunreal/oh-my-opencode-slim/blob/master/codemap.md
fetched: 2026-05-05
type: repository
---

# Repository Atlas

## Core Responsibility

An OpenCode plugin that adds a specialist-agent operating model on top of the host runtime: define orchestrator and specialist agents, load layered plugin configuration and per-agent permissions, expose additional tools and MCP integrations, manage delegated/resumable session orchestration and terminal multiplexer visualization, inject workflow-enforcement hooks plus runtime command handlers, ship install-time skills and a bootstrap CLI.

## System Entry Points

| Path | Role |
|------|------|
| `package.json` | Package manifest, dependency graph, release scripts |
| `src/index.ts` | Main plugin bootstrap — wires agents, tools, MCPs, hooks, council/session managers |
| `src/cli/index.ts` | CLI entrypoint for installation/bootstrap |
| `src/config/schema.ts` | Source-of-truth runtime config schema (Zod) |
| `scripts/generate-schema.ts` | Generates JSON schema from Zod config |

## Directory Map

| Directory | Responsibility |
|-----------|---------------|
| `src/` | Plugin bootstrap, runtime model chains, hook orchestration, task-session aliasing |
| `src/agents/` | Agent factory layer — prompt/model overrides, display names, MCP assignment, permission shaping |
| `src/cli/` | Installer, config editing, provider preset generation, skill installation |
| `src/config/` | Config schema, layered loaders, preset merging, compatibility migrations |
| `src/council/` | Multi-model council orchestration — preset resolution, execution modes, retries, timeouts |
| `src/hooks/` | Aggregated runtime hooks — prompt transforms, recovery, session aliasing, nudges, lifecycle |
| `src/mcp/` | Built-in MCP registry and per-provider definitions |
| `src/multiplexer/` | Terminal multiplexer abstraction — backend selection, session mirroring, shutdown |
| `src/skills/` | Bundled install-time OpenCode skills |
| `src/tools/` | Tool exports — AST-grep, smartfetch, council orchestration, /preset switching |
| `src/utils/` | Cross-cutting helpers — logging, session metadata, task aliases, system-message normalization |

## Runtime Control Flow

1. **Plugin startup** — OpenCode loads `src/index.ts`; config normalized; agents, tools, MCPs, hooks registered; delegation/council/multiplexer/session-tracking initialized
2. **Interactive request handling** — Orchestrator prompt drives routing; tool calls resolve through exports; hooks transform prompts/messages or intercept commands
3. **Delegated execution** — OpenCode child sessions created by delegation/council flows; tracked by session utilities; optionally mirrored to tmux/zellij panes; results flow back via notifications/output polling
4. **Install/release path** — CLI configures host OpenCode; skills copied; scripts validate schema and host-load behavior

## Recommended Reading Order

1. `codemap.md` (this file)
2. `src/codemap.md`
3. `src/agents/codemap.md` or `src/multiplexer/codemap.md` or `src/tools/codemap.md` or `src/hooks/codemap.md`
