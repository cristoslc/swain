---
source-id: omo-slim-config
title: oh-my-opencode-slim — Configuration Reference
url: https://github.com/alvinunreal/oh-my-opencode-slim/blob/master/docs/configuration.md
fetched: 2026-05-05
type: documentation
---

# Configuration Reference

## Config Files

| File | Purpose |
|------|---------|
| `~/.config/opencode/opencode.json` | OpenCode core settings (plugin registration, providers) |
| `~/.config/opencode/oh-my-opencode-slim.json` | Plugin settings — agents, multiplexer, MCPs, council |
| `~/.config/opencode/oh-my-opencode-slim.jsonc` | Same with JSONC (comments + trailing commas). Takes precedence if both exist |
| `.opencode/oh-my-opencode-slim.json` | Project-local overrides (checked first) |

## Prompt Overriding

Markdown files in `~/.config/opencode/oh-my-opencode-slim/`:
- `{agent}.md` — Replaces agent's default prompt entirely
- `{agent}_append.md` — Appends custom instructions to default prompt

When a `preset` is active, checks `~/.config/opencode/oh-my-opencode-slim/{preset}/` first, then root fallback.

## Full Option Reference

### Top-level
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `preset` | string | — | Active preset name |
| `presets` | object | — | Named preset configurations |
| `disabled_agents` | string[] | `["observer"]` | Agent names to disable globally |
| `autoUpdate` | boolean | `true` | Auto-install updates in background |
| `disabled_mcps` | string[] | `[]` | MCP servers to disable globally |

### Preset Agent Overrides
Each `presets.<name>.<agent>` supports: `model`, `temperature`, `variant`, `displayName`, `skills`, `mcps`, `options`.

### Custom Agents
Unknown keys under `agents` are treated as custom subagents requiring: `model`, `prompt`, optional `orchestratorPrompt`.

### Multiplexer
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `multiplexer.type` | string | `"none"` | `auto`, `tmux`, `zellij`, or `none` |
| `multiplexer.layout` | string | `"main-vertical"` | Layout preset for tmux |
| `multiplexer.main_pane_size` | number | `60` | Main pane size % (20–80) |

Legacy `tmux.*` keys auto-convert to `multiplexer.*`.

### Council
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `council.presets` | object | — | Required if using council |
| `council.default_preset` | string | `"default"` | Default preset |
| `council.timeout` | number | `180000` | Per-councillor timeout (ms) |
| `council.councillor_execution_mode` | string | `"parallel"` | `parallel` or `serial` |
| `council.councillor_retries` | number | `3` | Retries on empty provider response |

### Fallback
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `fallback.enabled` | boolean | `false` | Enable model failover |
| `fallback.timeoutMs` | number | `15000` | Time before trying next model |
| `fallback.chains.<agent>` | string[] | — | Ordered fallback model IDs |

### Session Management
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `sessionManager.maxSessionsPerAgent` | integer | `2` | Remembered sessions per specialist (1–10) |
| `sessionManager.readContextMinLines` | integer | `10` | Min lines read before file appears in context |
| `sessionManager.readContextMaxFiles` | integer | `8` | Max read-context files per session |

### Todo Continuation
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `todoContinuation.maxContinuations` | integer | `5` | Max consecutive auto-continuations |
| `todoContinuation.cooldownMs` | integer | `3000` | Delay before auto-continuing |
| `todoContinuation.autoEnable` | boolean | `false` | Auto-enable at session start |
| `todoContinuation.autoEnableThreshold` | integer | `4` | Todo count triggering auto-enable |

### Interview
`interview.maxQuestions` (2), `interview.outputFolder` ("interview"), `interview.autoOpenBrowser` (true), `interview.port` (0), `interview.dashboard` (false)

### Divoom Display
`divoom.enabled` (false) plus various tuning params for the Divoom MiniToo Bluetooth display integration.

### Agent Display Names
`agents.<agent>.displayName` for user-facing aliases (e.g., `"oracle"` → `"advisor"`). Names must be unique, can't conflict with internal names.
