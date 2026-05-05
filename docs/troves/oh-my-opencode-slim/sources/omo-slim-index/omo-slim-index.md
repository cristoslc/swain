---
source-id: omo-slim-index
title: oh-my-opencode-slim — Plugin Bootstrap (src/index.ts)
url: https://github.com/alvinunreal/oh-my-opencode-slim/blob/master/src/index.ts
fetched: 2026-05-05
type: repository
---

# Plugin Bootstrap: src/index.ts

The central composition root of the entire plugin. This is the main entrypoint loaded by OpenCode's plugin system.

## Architecture

A single async function export (`OhMyOpenCodeLite`) that receives the OpenCode plugin context and returns a plugin definition with: `agent`, `tool`, `mcp`, `config`, `event`, `tool.execute.before`, `tool.execute.after`, `command.execute.before`, `chat.headers`, `chat.message`, `experimental.chat.system.transform`, `experimental.chat.messages.transform`.

## Initialization Sequence

1. Load and normalize plugin config via `loadPluginConfig()`
2. Apply runtime preset override if `/preset` was used
3. Resolve disabled agents via `getDisabledAgents()`
4. Create display-name mention rewriter
5. Create agent definitions via `createAgents()` and `getAgentConfigs()`
6. Build runtime fallback chains from `_modelArray` + `fallback.chains` config
7. Parse multiplexer config and detect if inside tmux/zellij
8. Initialize `SubagentDepthTracker`
9. Create council tools if `config.council` exists
10. Create built-in MCPs and webfetch tool
11. Initialize all subsystem managers:
    - `MultiplexerSessionManager` — tmux/zellij pane lifecycle
    - `AutoUpdateChecker` — background update detection
    - `PhaseReminderHook` — workflow phase compliance
    - `FilterAvailableSkillsHook` — per-agent skill filtering
    - `PostFileToolNudgeHook` — delegation-aware nudge after file reads
    - `ChatHeadersHook` — session metadata
    - `DelegateTaskRetryHook` — retry guidance for failed delegation
    - `ApplyPatchHook` — patch rescue and validation
    - `JsonErrorRecoveryHook` — malformed JSON recovery
    - `ForegroundFallbackManager` — runtime model failover on rate limits
    - `TodoContinuationHook` — auto-continue on incomplete todos
    - `TaskSessionManagerHook` — resumable child session tracking
    - `InterviewManager` — /interview feature
    - `PresetManager` — /preset runtime switching
    - `DivoomManager` — Bluetooth display integration

## Health Check

After init, validates `minAgents: 5`, `minTools: 5`, `minMcps: 1`. If below thresholds, logs a warning with a link to the GitHub issue.

## jsdom Probe

Async non-blocking probe of jsdom; warns if webfetch won't work.

## Key Integration Points

### `config()` hook
- Sets `default_agent` to `orchestrator` if not user-configured
- Merges agent configs from plugin into opencodeConfig
- Resolves model arrays: picks first model from `_modelArray` + `fallback.chains` combined
- Applies runtime preset overrides for model/variant/temperature
- Creates MCP permission rules per agent based on `mcps` array
- Registers `/auto-continue` command handler

### `event()` handler
- `message.updated` → records TUI agent model info
- `session.created` → registers child in depth tracker
- Handles foreground fallback for rate limits
- Handles todo-continuation, auto-update, multiplexer session mirroring
- Handles interview events
- Handles Divoom display state changes
- Cleans up depth tracker and session agent map on `session.deleted`

### `experimental.chat.system.transform`
- Injects orchestrator prompt for serve-mode sessions
- Collapses multiple system messages into one for provider compatibility

### `experimental.chat.messages.transform`
- Rewrites display name mentions in user messages
- Strips image parts from orchestrator messages when @observer available
- Applies todo-continuation, task-session-manager, phase-reminder, and skill-filter transforms

### `tool.execute.before`
- apply_patch rescue
- Task session management injection
- Divoom task-start notification

### `tool.execute.after`
Post-tool hooks run in sequence with individual try/catch per hook (fail-open semantics):
- Delegate task retry guidance
- JSON error recovery
- Todo continuation tracking
- Post-file-tool nudge
- Task session manager cleanup
- Divoom task-end notification

### `command.execute.before`
- `/auto-continue` — direct interception, bypasses LLM round-trip
- `/interview` — interview flow
- `/preset` — runtime preset switching
