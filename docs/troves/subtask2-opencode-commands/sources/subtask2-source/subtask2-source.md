---
source-id: subtask2-source
source-type: repository
title: "subtask2 Source Code Analysis"
url: https://github.com/spoons-and-mirrors/subtask2
fetched: 2026-04-19
content-hash: --
selective: true
highlights:
  - src/core/plugin.ts
  - src/core/state.ts
  - src/types.ts
  - src/loop.ts
  - src/features/returns.ts
  - src/features/parallel.ts
  - src/features/inline-subtasks.ts
  - src/features/auto.ts
  - src/hooks/command-hooks.ts
  - src/hooks/session-idle-hook.ts
  - src/hooks/tool-hooks.ts
  - src/hooks/message-hooks.ts
  - src/parsing/frontmatter.ts
  - src/parsing/overrides.ts
  - src/parsing/commands.ts
  - src/parsing/parallel.ts
  - package.json
---

# subtask2 Source Code Analysis

## Architecture

subtask2 is a TypeScript plugin for opencode that hooks into opencode's plugin lifecycle to intercept command execution, tool calls, and message transformations. The codebase is organized into four layers:

1. **Core** (`src/core/`) — Plugin entry point, centralized state management
2. **Features** (`src/features/`) — Return execution, parallel subtasks, inline subtasks, results, turn context, auto mode
3. **Hooks** (`src/hooks/`) — Command hooks, tool hooks, message hooks, session idle handler
4. **Parsing** (`src/parsing/`) — Frontmatter, overrides, commands, parallel config, turn references, auto workflow parsing

## Plugin Entry Point (`src/core/plugin.ts`)

The plugin registers five hooks via the `createPlugin` factory:

- `command.execute.before` — Intercepts command execution to handle subtask configuration, parallel spawning, return chains, and model/agent overrides
- `tool.execute.before` — Maps subtask sessions to parent sessions, resolves `$RESULT` and `$TURN` references
- `tool.execute.after` — Captures subtask results into named stores
- `experimental.chat.messages.transform` — Removes opencode's generic "Summarize..." message and injects pending prompt returns
- `config` — Registers the `/subtask` command for inline subtask creation
- `event` — Handles `session.idle` events for return chain processing, loop evaluation, and non-subtask return handling

## State Management (`src/core/state.ts`)

All plugin state is centralized in `state.ts` using module-scoped Maps keyed by session ID. Key state categories:

- **Command configs** — Loaded from command manifest
- **Plugin config** — User preferences (`replace_generic`, `generic_return`)
- **Return state** — Return chains, stacks for nested returns, pending prompt returns, deferred returns
- **Session tracking** — Main command, parent session mapping, processed messages
- **Loop state** — Active loops, pending evaluations
- **Result capture** — Named results (`$RESULT`), pending captures by session or prompt
- **Override state** — Pending model/agent overrides per session

The state module exports ~70 getter/setter functions. No cleanup mechanism exists for ended sessions (noted in TODO.md as a memory leak concern).

## Types (`src/types.ts`)

```typescript
interface LoopConfig {
  max: number;
  until: string;
}

interface ParallelCommand {
  command: string;
  arguments?: string;
  prompt?: string;
  model?: string;
  agent?: string;
  loop?: LoopConfig;
  as?: string;
  inline?: boolean;
}

interface CommandConfig {
  return: string[];
  parallel: ParallelCommand[];
  agent?: string;
  description?: string;
  template?: string;
  loop?: LoopConfig;
  model?: string;
  auto?: boolean;
}

interface Subtask2Config {
  replace_generic: boolean;
  generic_return?: string;
}
```

## Loop System (`src/loop.ts`)

The loop system uses an "orchestrator-decides" pattern:

1. Subtask runs and completes
2. Main session receives an evaluation prompt with the condition
3. Main LLM evaluates against the condition (reading files, running tests, etc.)
4. LLM responds with `<subtask2 loop="break"/>` or `<subtask2 loop="continue"/>`
5. If continue, loop re-runs. If break, proceeds to next return
6. Max iterations serves as safety net

State tracking: `activeLoops` map (session → LoopState), `pendingLoopEvaluation` map for sessions awaiting LLM evaluation.

## Feature: Returns (`src/features/returns.ts`)

The return system is the core orchestration mechanism. It handles:

- **Command returns** (`/command args`) — Executes via `client.session.command()`
- **Prompt returns** — Injects as real user messages via `client.session.promptAsync()`
- **Inline subtask returns** (`/subtask {overrides} prompt`) — Spawns as subtask
- **Auto workflow parse** (`__subtask2_auto_parse__`) — Parses LLM-generated workflow from `<subtask2 auto>` tags
- **Dedup** — Prevents double execution via `executedReturns` set
- **Loop integration** — Starts loops when loop config is present in return commands
- **Result capture** — Registers `{as:name}` captures for both subtask and non-subtask commands
- **Piped args** — Processes `||` pipe-delimited arguments

## Feature: Parallel (`src/features/parallel.ts`)

`flattenParallels()` recursively expands parallel command trees:

1. For each parallel command, load its command file
2. Parse frontmatter and resolve `$ARGUMENTS` and `$TURN` references
3. Build `SubtaskPart` objects with agent, model, description, prompt
4. Recursively expand nested parallels (max depth 5, cycle detection via `visited` set)
5. Argument priority: piped args > frontmatter args > main args

Parallel commands are forced into subtask mode regardless of their own `subtask:` setting. Their `return` is ignored — only the parent's return applies.

## Feature: Inline Subtasks (`src/features/inline-subtasks.ts`)

Two paths:

1. `buildInlineSubtaskPart()` — Used by command hooks to modify the output parts of the current prompt
2. `executeInlineSubtask()` — Used by return chains to spawn a new subtask

Both resolve `$TURN` references, register parent sessions for race-safe mapping, register result captures, and start loops if configured. The `buildInlineSubtaskPart` path also supports inline parallel commands.

## Feature: Results (`src/features/results.ts`)

`$RESULT[name]` resolution:

- Named results stored per-session in `state.ts` (`subtaskResults` map)
- `resolveResultReferences()` replaces `$RESULT[name]` patterns with stored values
- Falls back to `[Result 'name' not found]` when name is missing
- Works in return prompt chains and command arguments

## Feature: Turns (`src/features/turns.ts`)

`$TURN[n]` resolution fetches session messages via opencode SDK:

- `$TURN[5]` — last 5 messages
- `$TURN[:3]` — 3rd from end
- `$TURN[:2:5:8]` — specific indices
- `$TURN[*]` — all messages

Messages are formatted as `--- USER ---` / `--- ASSISTANT ---` blocks. Resolution happens before command execution and in parallel/inline subtask prompts.

## Feature: Auto Mode (`src/features/auto.ts`)

Experimental feature that lets LLMs generate subtask2 workflows on the fly:

1. User runs `/command` with `auto: true` in frontmatter
2. Plugin replaces command prompt with auto-workflow generation prompt
3. LLM generates a `/subtask {...}` command inside `<subtask2 auto="true">` tags
4. On completion, the generated workflow is parsed and executed
5. The auto prompt template includes the full README documentation so LLM knows the syntax

## Hook: Command Hooks (`src/hooks/command-hooks.ts`)

Intercepts `command.execute.before` to:

1. Match command name to loaded configs (handling subfolder paths)
2. Parse frontmatter from command file
3. Resolve `$TURN` references in prompt template
4. Handle return chains, parallel subtasks, loop configuration
5. Apply inline overrides (`{model:...}`, `{agent:...}`)
6. Replace `output.parts` with subtask configuration

## Hook: Tool Hooks (`src/hooks/tool-hooks.ts`)

Two phases:

- **`tool.execute.before`** — Maps subtask sessions to parent sessions, resolves `$RESULT` and `$TURN` in tool call arguments, captures named results from main session
- **`tool.execute.after`** — Stores named results from subtask completions

## Hook: Message Hooks (`src/hooks/message-hooks.ts`)

Intercepts `experimental.chat.messages.transform` to:

1. Remove opencode's generic "Summarize the task tool output..." message from conversations where subtask2 handles returns
2. Inject pending prompt returns as real user messages (set by session.idle)

## Hook: Session Idle (`src/hooks/session-idle-hook.ts`)

The central orchestrator for post-subtask processing:

1. Processes return chains (popping from return stack)
2. Executes return items (commands, prompts, inline subtasks)
3. Processes pending prompt returns
4. Handles loop evaluation and iteration
5. Captures subtask results
6. Processes non-subtask command returns
7. Sets pending prompt returns for message-hooks to inject

## Parsing System

- **Frontmatter** (`parsing/frontmatter.ts`) — YAML frontmatter extraction from command files, with support for `return`, `parallel`, `loop`, `model`, `agent`, `as`, and `auto` fields
- **Overrides** (`parsing/overrides.ts`) — Inline syntax parsing for `{model:...}`, `{agent:...}`, `{loop:N}`, `{until:...}`, `{as:...}`, `{parallel:...}`, `{return:...}`
- **Commands** (`parsing/commands.ts`) — Command name resolution, path matching, `$ARGUMENTS` substitution
- **Parallel** (`parsing/parallel.ts`) — Parallel config parsing from various formats (YAML array, comma-separated, object arrays)
- **Turns** (`parsing/turns.ts`) — `$TURN[n]` syntax parsing for various index patterns

## Session Flow

A typical subtask2 session flows:

1. User invokes `/command args` → `command.execute.before` intercepts
2. Plugin parses frontmatter, resolves `$TURN` and `$ARGUMENTS`
3. If `subtask: true`, modifies output.parts to spawn subtask
4. If `parallel`, flattens and adds parallel subtask parts
5. If `loop`, registers loop state
6. If `return`, stores return chain in session state
7. Subtask completes → `session.idle` fires
8. Idle handler processes return chain, loops, named results
9. If prompt return → injected as real user message via `promptAsync()`
10. If command return → executed via `client.session.command()`
11. If loop → evaluation prompt injected, LLM decides break/continue

## Configuration

- `~/.config/opencode/subtask2.jsonc` — User config (`replace_generic`, `generic_return`)
- Command frontmatter — Per-command config (`return`, `parallel`, `loop`, `model`, `agent`, `subtask`, `auto`)
- Inline overrides — Per-invocation config (`{model:...}`, `{agent:...}`, `{loop:...}`)

Priority: inline overrides > command frontmatter > plugin config defaults

## Dependencies

- `@opencode-ai/plugin` >= 1.0.216 (peer dependency)
- `@opencode-ai/sdk` (latest)
- `yaml` ^2.8.2

## Known Issues / TODO

- No session state cleanup — Maps grow unbounded for long-running instances
- `auto` mode is experimental
- `parallel` feature requires upstream PR (sst/opencode#6478)
- Model aliases planned (`{model:opus}` instead of `{model:github-copilot/claude-opus-4.5}`)
- `--` syntax for inline overrides under consideration