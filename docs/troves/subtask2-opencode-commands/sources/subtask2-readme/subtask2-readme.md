---
source-id: subtask2-readme
source-type: web
title: "subtask2: A Better opencode /command Handler"
url: https://github.com/spoons-and-mirrors/subtask2
fetched: 2026-04-19
content-hash: fa57b4a6bd2b37fca685a1701b3c61480d6033a8dc5f0ad9f3a9d7ee5be926d3
---

# subtask2: A Better opencode `/command` Handler

## Overview

subtask2 is an opencode plugin that enhances opencode's `/commands` system with chaining, looping, parallelization, and context-passing capabilities. Its tagline is "Lower session entropy with a more deterministic agentic loop."

**Install:** Add to opencode config:

```json
{
  "plugins": ["@spoons-and-mirrors/subtask2@latest"]
}
```

**Package:** `@spoons-and-mirrors/subtask2` (npm)  
**License:** PolyForm Noncommercial 1.0.0  
**Requires:** opencode with `@opencode-ai/plugin` >= 1.0.216

---

## Key Features

1. **`return`** — Chain prompts, `/commands`, and subagents after command completion
2. **`loop`** — Repeat subtask execution until a condition is met (or fixed N iterations)
3. **`parallel`** — Run subtasks concurrently (pending upstream PR)
4. **`$TURN[n]`** — Inject previous conversation turns into command prompts
5. **`{as:name}` + `$RESULT[name]`** — Capture and reference named subtask outputs
6. **Inline syntax** — Override model, agent, and create ad-hoc subtasks without command files

---

## 1. `return` — Chaining Prompts and Commands

Use `return` to tell the main agent what to do after a command completes. Supports prompts, `/commands`, and chaining.

### Single return

```yaml
subtask: true
return: Look again, challenge the findings, then implement the valid fixes.
---
Review the PR# $ARGUMENTS for bugs.
```

### Array of sequential returns

```yaml
subtask: true
return:
  - Implement the fix
  - Run the tests
---
Find the bug in auth.ts
```

### Trigger `/commands` in return

```yaml
subtask: true
return:
  - /revise-plan make the UX as horribly impractical as imaginable
  - /implement-plan
  - Send this to my mother in law
---
Design the auth system for $ARGUMENTS
```

### How return prompts work

When `subtask: true` completes, OpenCode injects a hidden synthetic user message asking the model to "summarize the task tool output..." Subtask2 completely removes this message and handles returns differently:

- **Prompt returns** fire as **real user messages** visible in conversation
- **Command returns** (starting with `/`) execute immediately

When no `return` is defined and `replace_generic` is enabled (default), subtask2 removes the synthetic message and fires a fallback prompt:

> Review, challenge and verify the task tool output above against the codebase. Then validate or revise it, before continuing with the next logical step.

Priority: `return` param > config `generic_return` > built-in default > opencode original

---

## 2. `loop` — Repeat Until Condition is Met

### Unconditional loop (fixed iterations)

```bash
/generate-tests {loop:5} generate unit tests for auth module
```

### Conditional loop (with evaluation)

```bash
/fix-tests {loop:10 && until:all tests pass with good coverage}
```

### Frontmatter syntax

```yaml
---
loop:
  max: 10
  until: "all features implemented correctly"
---
Implement the auth system.
```

### In return chains

```yaml
return:
  - /implement-feature
  - /fix-tests {loop:5 && until:tests are green}
  - /commit
```

### How loop evaluation works (orchestrator-decides pattern)

1. Subtask runs and completes
2. Main session receives evaluation prompt with the condition
3. Main LLM evaluates: reads files, checks git, runs tests if needed
4. Responds with `<subtask2 loop="break"/>` (satisfied) or `<subtask2 loop="continue"/>` (more work needed)
5. If continue → loop again. If break → proceed to next step
6. Max iterations is a safety net

---

## 3. `parallel` — Run Subtasks Concurrently

Spawn additional command subtasks alongside the main one:

```yaml
subtask: true
parallel:
  - /plan-gemini
  - /plan-opus
return:
  - Compare and challenge the plans, keep the best bits and make a unified proposal
  - Critically review the plan directly against what reddit has to say about it
---
Plan a trip to $ARGUMENTS.
```

This runs 3 subtasks in parallel: main command, `plan-gemini`, `plan-opus`. When ALL complete, the main session receives the `return` prompt.

### Piped arguments with `||`

```bash
/mycommand main args || pipe1 || pipe2 || pipe3
```

Pipe segments map in chronological order: main → parallels → return `/commands`

Priority: pipe args > frontmatter args > inherit main args

Parallel commands are forced into subtasks regardless of their own `subtask` setting. Their `return` is ignored — only the parent's `return` applies. Nested parallels are automatically flattened with a maximum depth of 5.

---

## 4. Context & Results

### `$TURN[n]` — Reference conversation turns

Inject previous conversation turns into command prompts:

- `$TURN[6]` — last 6 messages
- `$TURN[:3]` — just the 3rd message from the end
- `$TURN[:2:5:8]` — specific messages at indices 2, 5, 8
- `$TURN[*]` — all messages in the session

Works in command body templates, arguments, parallel command prompts, and piped arguments.

Format:

```
--- USER ---
What's the best way to implement auth?

--- ASSISTANT ---
I'd recommend using JWT tokens with...

--- USER ---
Can you show me an example?
...
```

### `{as:name}` and `$RESULT[name]` — Named results

Capture command outputs and reference them later in return chains:

```yaml
subtask: true
parallel:
  - /plan {model:anthropic/claude-sonnet-4 && as:claude-plan}
  - /plan {model:openai/gpt-4o && as:gpt-plan}
return:
  - /deep-analysis {as:analysis}
  - "Compare $RESULT[claude-plan] vs $RESULT[gpt-plan] using insights from $RESULT[analysis]"
```

If a result isn't found, it's replaced with `[Result 'name' not found]`.

---

## 5. Inline Syntax — Overrides and Ad-hoc Subtasks

### `{model:...}` — Model override

```bash
/plan {model:anthropic/claude-sonnet-4} design auth system
```

### `{agent:...}` — Agent override

```bash
/research {agent:explore} find auth patterns
```

### Combining overrides

```bash
/plan {model:openai/gpt-4o && agent:build} implement the feature
```

### `/subtask {...} prompt` — Ad-hoc subtasks

Create subtasks directly without command files:

```yaml
return:
  - /subtask {loop:10 && until:tests pass} Fix failing tests and run the suite
  - /subtask {model:openai/gpt-4o && agent:build} Implement the feature
  - Summarize what was done
```

The space between `/subtask` and `{` is required for instant execution.

### Inline returns

```yaml
return:
  - /subtask {return:validate the output || run tests || deploy} implement the feature
```

---

## 6. OpenCode's Generic Message Handling

Subtask2 completely removes opencode's synthetic "Summarize the task tool output" message when `subtask: true` commands complete.

- **With `return`:** Synthetic message removed; return prompts fire as real user messages
- **Without `return`:** If `replace_generic` is enabled (default), a fallback prompt replaces the generic message
- **Custom fallback:** Via `generic_return` in `~/.config/opencode/subtask2.jsonc`

---

## Configuration

`~/.config/opencode/subtask2.jsonc`:

```jsonc
{
  "replace_generic": true,
  // "generic_return": "custom return prompt"
}
```

---

## Notable Examples

### Multi-model ensemble planning

```yaml
---
description: multi-model ensemble, 3 models plan in parallel, best ideas unified
model: github-copilot/claude-opus-4.5
subtask: true
parallel: /plan-gemini, /plan-gpt
return:
  - Compare all 3 plans and validate each directly against the codebase. Pick the best ideas from each and create a unified implementation plan.
  - /review-plan focus on simplicity and correctness
---
Plan the implementation for the following feature
> $ARGUMENTS
```

### Fix-until-pass loop

```bash
/fix-tests {loop:10 && until:all tests pass with good coverage}
```

### Full orchestration

```yaml
subtask: true
parallel:
  - /research-docs {as:docs} authentication flow
  - /research-codebase {as:code} auth middleware implementation
  - /security-audit
return:
  - Synthesize all findings into an implementation plan.
```