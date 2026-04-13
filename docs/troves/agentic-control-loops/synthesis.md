# Agentic Control Loops — Synthesis

**Sources:** ghuntley-ralph-technique, open-ralph-wiggum, ralph-loop-quickstart, openclaw-daemon
**Related troves:** `claude-code-source-leak-2026` (KAIROS/PROACTIVE/COORDINATOR_MODE), `agentic-runtime-chat-adapters` (OpenClaw as messaging adapter), `platform-hooks-validation` (hook systems), `claude-code-auto-mode` (permission tiers)
**Last updated:** 2026-04-06

---

## What this covers

Two distinct patterns for autonomous agent runtime control loops:

1. **Iterative loops** (Ralph Wiggum) — the same prompt fed to a coding agent repeatedly until a completion token appears. Agent sees previous work via the filesystem and git history. Used for greenfield development and POC work.
2. **Daemon/reactive loops** (OpenClaw) — an always-on process that responds to incoming events (messages, webhooks). Used for personal AI assistants that need to be continuously available.

The Claude Code source leak (covered in `claude-code-source-leak-2026`) reveals a third pattern in development: **platform-level autonomous loops** (KAIROS daemon mode, PROACTIVE tick prompts, COORDINATOR_MODE orchestration) that absorb both patterns into the coding agent platform itself.

---

## Key findings

### The Ralph Wiggum technique: iterative loops via repeated prompting

The core mechanism (`ghuntley-ralph-technique`) is as simple as:

```bash
while :; do cat PROMPT.md | claude-code ; done
```

The AI does not communicate between iterations. It receives the same prompt every loop, but the codebase has changed — files, git history, test output — so it self-corrects incrementally. The "loop controller" is just a bash script checking for a completion token (e.g., `<promise>COMPLETE</promise>`).

This is **not** the agent reasoning about its own progress. It's the agent seeing the results of its previous actions via the filesystem and deciding what to do next based on the same prompt.

### Context window strategy is load-bearing

Two schools of thought exist, and the sources conflict on this:

- **Huntley's original**: single context window with disciplined allocation (~170k tokens). Uses `@fix_plan.md` and `@specs/*` to steer the agent across iterations.
- **ralph-loop-quickstart** explicitly calls the single-context approach a "fundamental flaw." Advocates for fresh context per iteration to prevent context bloat, hallucination, and the need for manual compaction.

The open-ralph-wiggum implementation follows the fresh-context-per-iteration model (separate process invocation each loop). The quickstart guide documents why this matters at scale for longer-running tasks.

### Completion tokens are the control primitive

The loop terminates on a specific token in the agent's output (`<promise>COMPLETE</promise>`, `<promise>DONE</promise>`, etc.). This is the primary control mechanism — not an external evaluator or supervisor. The operator defines success by writing the token into the prompt.

Variants:
- **Task completion tokens** (`<promise>READY_FOR_NEXT_TASK</promise>`) for multi-task flows.
- **Abort tokens** (`--abort-promise`) for early exit on precondition failure.
- **JSON feature flags** (`"passes": true`) for structured verification without token scanning.

### Permission management is the main friction point

All sources address the approval problem differently:

- `open-ralph-wiggum` defaults to `--allow-all` — auto-approves all tool permissions.
- `ralph-loop-quickstart` uses `.claude/settings.json` with explicit allow-lists per CLI tool.
- `openclaw-daemon` integrates with farmer's trust tier system (paranoid / standard / autonomous).
- The leaked `TRANSCRIPT_CLASSIFIER` feature would automate this at the platform level.

This is the primary usability bottleneck for unattended autonomous loops. Fully autonomous runs require either pre-approved allow-lists or a remote approval dashboard (farmer).

### OpenClaw is a different loop topology

OpenClaw (`openclaw-daemon`) runs a daemon process that responds to incoming channel messages. This is reactive, not iterative. The control loop is:

```
incoming message → Gateway → AI model → tool calls → response to channel
```

The daemon stays alive between messages; the loop is triggered by events, not a bash script. OpenClaw's "agent harness" capabilities are explicitly listed as a next priority in VISION.md, suggesting the iterative-loop pattern will be integrated into the platform alongside the reactive one.

### The platform is moving toward absorbing the loop

The Claude Code source leak (`claude-code-source-leak-2026`) reveals three feature flags that internalize the control loop at the platform level:

- **KAIROS** — daemon mode with background sessions and dream memory consolidation. This is the always-on pattern, built into Claude Code itself.
- **PROACTIVE** — "tick" prompts where the model decides what to do on each wake-up. This is the iterative loop pattern, also built in.
- **COORDINATOR_MODE** — spawns parallel worker agents. This is the multi-agent orchestration pattern.

If these ship, the bash loop wrappers become unnecessary for many use cases. The Ralph Wiggum pattern may be transitional infrastructure.

---

## Points of agreement

- Ralph Wiggum works best for greenfield projects with verifiable success criteria. All sources say: do not use it in legacy codebases.
- Human expertise is still required. "Engineers are still needed" (Huntley). The operator must write the prompt, define success criteria, and tune the loop when it fails.
- PRD / specification quality determines loop quality. Poor prompts produce wasted iterations.
- Max iterations is always required. Runaway loops are real.
- The filesystem (and git history) is the agent's working memory across iterations. This is the mechanism that makes repeated prompting effective.

---

## Points of disagreement / tension

- **Single context vs. fresh context**: Huntley favors single context with disciplined allocation; the quickstart guide advocates fresh context per iteration. The right answer likely depends on task length and token budget.
- **Permission philosophy**: auto-approve-all (open-ralph-wiggum default) vs. explicit allow-lists (quickstart) vs. remote approval dashboard (farmer/openclaw). These represent different points on the autonomy-oversight tradeoff.
- **Agent neutrality**: open-ralph-wiggum supports Claude Code, Codex, Copilot CLI, and OpenCode interchangeably. This implies the loop controller is model-agnostic; the technique is not Claude-specific.

---

## Gaps

- No evidence on how loop controllers handle agent crashes, context errors, or API rate limits mid-loop. The sources describe happy-path operation.
- No coverage of cost tracking across iterations. Huntley mentions $297 total for a $50k contract but no per-iteration breakdown.
- No coverage of security implications of `--allow-all` in production environments.
- The "fresh context vs. accumulated context" debate lacks empirical benchmarks comparing both approaches on the same tasks.
- OpenClaw's "computer-use and agent harness capabilities" listed as a next priority — no details yet on what this means for iterative-loop integration.

---

## Relevance to swain

| Loop pattern | Swain analog | Implication |
|---|---|---|
| Ralph loop (same prompt, repeated) | swain-do worktree execution | Swain's agent dispatching could adopt loop mechanics for long-running SPEC implementation |
| Fresh context per iteration | Worktree isolation | Per-worktree isolation already provides fresh context semantics |
| Completion token | SPEC AC validation | ACs are the swain equivalent of the completion token |
| PRD quality determines loop quality | SPEC quality determines implementation quality | Swain's brainstorming + writing-plans chain is the PRD-quality gate |
| `--allow-all` / trust tiers | Permission presets in AGENTS.md | Farmer as an operator-sustainability tool worth evaluating for long swain sessions |
| KAIROS (platform daemon) | swain-session lifecycle | If KAIROS ships, swain session management may need to layer on top of it rather than around Claude Code |

The Ralph Wiggum ecosystem is essentially a community-built version of what Anthropic is building into Claude Code via KAIROS and PROACTIVE mode. The community patterns validate the direction; the platform features will eventually replace them.
