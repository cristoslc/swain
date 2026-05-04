---
title: OpenCode Integration
url: https://www.getagentcraft.com/docs/integrations/opencode
fetched: 2026-05-04
type: documentation
---

# OpenCode

Integration with the OpenCode AI coding agent.

AgentCraft supports OpenCode as a second AI coding tool alongside Claude Code. OpenCode provides access to 75+ models from multiple providers.

## Setup

If OpenCode is installed, AgentCraft auto-detects it during setup and installs the OpenCode plugin to ~/.config/opencode/plugins/agentcraft.js.

## Two Integration Paths

| Path | How it works | Who drives it |
| --- | --- | --- |
| Passive monitoring | Plugin hooks send events; SQLite scanner discovers sessions | External OpenCode sessions you start in a terminal |
| Internal spawning | AgentCraft spawns opencode run --format json as a subprocess | Heroes spawned from the UI with "OpenCode" selected |

Both paths produce heroes that appear on the map and in the roster.

## Spawning OpenCode Heroes

Press W at the Town Hall (or in the command grid) to spawn an OpenCode hero. The W option is grayed out if OpenCode is not installed.

External OpenCode sessions (started in a separate terminal) are automatically detected and appear on the map as read-only heroes.

## Model Selection

When you select an OpenCode hero, the model dropdown in the Side Panel shows all models available in your OpenCode installation, grouped by provider (Anthropic, OpenAI, Google, Groq, etc.).

AgentCraft discovers these automatically at startup by querying opencode models. If you add a new provider after starting the server, refresh models via:

```
GET /opencode/models?refresh=true
```

## Limitations

Some features are Claude Code-only and not available for OpenCode heroes:

| Feature | Reason |
| --- | --- |
| Manual approval (Y/N) | Requires Claude Code's PreToolUse hook |
| Plan approval workflow | Uses Claude Code's plan mode events |
| Git tab / usage panel | Reads Claude CLI-specific output |
| Agent Teams | Requires Claude Code team configuration |

## External Session Detection

Past OpenCode sessions are discovered from OpenCode's SQLite database at ~/.local/share/opencode/opencode.db. This allows sessions to appear in the roster even without the plugin running.

The better-sqlite3 dependency is optional — if it's not installed, only plugin-based session tracking is used.