# Synthesis: subtask2 — opencode Command Orchestration Plugin

## What It Is

subtask2 is a TypeScript plugin for opencode that adds deterministic control flow to opencode's `/commands` system. It replaces opencode's default "summarize the task tool output" behavior with an explicit chaining, looping, and parallelization model. The plugin intercepts five opencode lifecycle hooks (command execution, tool execution before/after, message transformation, and session idle) to orchestrate multi-step agent workflows from command frontmatter and inline syntax.

## Key Findings

### Chaining via `return`

The `return` field in command frontmatter defines a sequence of actions to execute after a subtask completes. Items can be prompts (injected as real user messages), `/command` invocations (executed immediately), or inline subtasks. This is the core mechanism — everything else builds on it. The plugin removes opencode's generic synthetic message entirely, giving the user full visibility and control over what happens next.

### Orchestrator-Decides Loop Pattern

Loops use a novel "orchestrator-decides" pattern: after a subtask iteration completes, the main session receives an evaluation prompt asking it to check a human-readable condition. The main LLM reads files, runs tests, inspects git state, and responds with `<subtask2 loop="break"/>` or `<subtask2 loop="continue"/>`. This avoids brittle regex-based completion markers and leverages the LLM's existing code-reading capability. Max iterations serve as a safety net.

### Centralized Session State via Module-Scoped Maps

All state (~70 getter/setter functions in `state.ts`) uses module-scoped Maps keyed by session ID. This covers return chains, loop state, named results, model/agent overrides, parent session mapping, and dedup tracking. There is no cleanup mechanism for ended sessions — noted as a memory leak concern in the project's TODO.

### Three-Layer Configuration Priority

Configuration cascades: inline overrides (`{model:...}`) > command frontmatter > plugin defaults (`subtask2.jsonc`). This lets users set defaults globally, override per-command, and fine-tune per-invocation without editing files.

### Context Passing: `$TURN` and `$RESULT`

Two context-passing mechanisms bridge the subtask isolation gap:
- `$TURN[n]` injects previous session messages into subtask prompts, formatted as USER/ASSISTANT blocks
- `$RESULT[name]` captures subtask output and substitutes it into later return chain items

### Auto Mode (Experimental)

An opt-in feature where the LLM generates its own subtask2 workflow. The plugin injects the full README documentation as context, the LLM outputs a `/subtask {...}` command inside `<subtask2 auto>` tags, and the plugin parses and executes it. This is a meta-level capability — using agentic output to generate agentic workflows.

## Points of Agreement

Both sources agree on the core feature set: return chaining, loops, parallel execution, `$TURN`, `$RESULT`, and inline overrides. The README provides user-facing documentation and examples; the source code confirms the implementation architecture and reveals internal state management, hook lifecycle, and parsing details.

## Points of Disagreement

The README marks `parallel` as "pending PR" (requiring sst/opencode#6478), but the source code includes a full parallel implementation (`parallel.ts`, `flattenParallels()`). This suggests the feature was implemented in anticipation of the upstream PR being merged, not that the code is missing.

The README doesn't mention the auto mode feature prominently — it's documented in the source code and TODO but not in the main feature list. The source confirms it's experimental.

## Gaps

- **No session cleanup** — Memory grows unbounded for long-running instances. The TODO acknowledges this.
- **Race conditions** — The plugin uses prompt-content-based matching for parent session mapping (`pendingParentByPrompt`), which could collide if two subtasks have identical prompts.
- **No error recovery** — If a subtask fails mid-chain, the remaining returns still execute. No rollback or conditional branching on failure.
- **Single-model evaluation for loops** — The loop evaluation happens in whatever model the main session uses. No option to use a different model for evaluation vs. execution.
- **Parallel requires upstream PR** — The `parallel` feature needs sst/opencode#6478 for true concurrent subtask spawning. Currently, only the plugin-side orchestration code exists.

## Relevance to Related Troves

- **opencode-crush-cli** — Covers opencode itself (TUI, headless mode). subtask2 extends opencode's command system.
- **agentic-control-loops** — Covers general agentic loop patterns. subtask2's orchestrator-decides loop is a concrete implementation.
- **process-supervision-patterns** — Covers how to supervise long-running processes. subtask2's loop evaluation pattern is a form of process supervision where the main session acts as supervisor.