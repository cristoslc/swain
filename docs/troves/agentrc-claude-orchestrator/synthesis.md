# agent.rc — Synthesis

## Key Findings

agent.rc is a tmux-native multi-agent orchestration system for Claude Code. It runs
full Claude Code instances (not API calls) as parallel workers, each in its own git
worktree and tmux pane. A Rust CLI handles all deterministic mechanics; a skill file
tells the LLM orchestrator what to do. The human approves the task DAG before any
workers launch.

## The Two-Layer Architecture

The cleanest design decision in agent.rc is the hard separation between *what* and
*how*:

- **Skill layer** (`SKILL.md`) — prose directives for the orchestrator. It describes the
  four-phase workflow, constraints, and decision rules. The LLM reads this and decides
  what to build, how to decompose it, and when to escalate.
- **Ops binary** (`agentrc`) — a Rust CLI handling everything deterministic: spawning
  tmux panes, creating git worktrees, aggregating worker status, merging branches in
  dependency order, auditing TDD commit patterns, checkpoint/restore.

This split avoids the failure mode where an LLM tries to manage tmux escaping or git
merge strategies — it delegates those to reliable code. It also avoids the failure mode
where a rigid CLI tries to make judgment calls about task decomposition.

## Worktree Isolation as a First-Class Invariant

Every task gets its own branch and worktree under `orc/<task-id>`. Workers are
explicitly forbidden from touching files outside their assigned worktree. The
orchestrator owns all merges; workers cannot push. This prevents the most common
multi-agent failure mode: concurrent writes to the same file.

Merges happen in dependency order — as soon as a task's dependencies resolve, `agentrc
integrate` runs test gates and merges. This is reactive, not batch, which means
completed work unblocks downstream tasks immediately.

## TDD as a Workflow Invariant

Red-green-refactor is enforced structurally, not by suggestion. `agentrc audit
<task-id>` reads commit history and flags branches that skipped tests. Branches that
fail the audit get redispatched. This removes the "just write the tests later" escape
hatch that most LLM coding systems leave open.

## Human-in-the-Loop Gate

The orchestrator does not spawn any workers until the full task DAG — dependencies,
reader/writer classifications, test plans — has been presented to and approved by the
operator. This is a hard block, not a soft suggestion. It is the primary mechanism for
keeping the human aligned with what the AI is about to do.

## Sub-Team Model

Workers are not just Claude Code sessions — they can dispatch their own specialist
subagents (implementation, testing, security review, architecture). The `CLAUDE.md`
worker directives mandate subagent dispatch for all implementation work, typed by role
(e.g., `voltagent-lang:rust-engineer`, `voltagent-qa-sec:test-automator`). All
subagents run the strongest available model. This builds review panels into every
unit of work.

## Comparison with CRISPY Agents

Both agent.rc and CRISPY enforce TDD and use role-separated agents. The key
differences:

| Dimension | agent.rc | CRISPY |
|-----------|----------|--------|
| Execution model | Parallel task DAG | Sequential pipeline |
| Worker isolation | Git worktrees + tmux panes | Single context, instruction budget |
| Coordination layer | Rust CLI binary | LLM skill directives only |
| Runtime | Claude Code (full instances) | OpenCode |
| Human gate | Plan approval before dispatch | Structure + plan review |
| TDD enforcement | Commit audit + redispatch | Mandatory in coder prompt |

CRISPY optimizes for instruction budget and model diversity. agent.rc optimizes for
parallelism, isolation, and deterministic coordination mechanics.

## Gaps (resolved)

### Merge conflict handling

When a merge fails, `integrate` runs a fixed detect → abort → log sequence:

1. Call `git.conflicting_files()` to identify files with unresolved conflicts.
2. Cross-reference those files against other tasks' changed files to find the
   overlapping task IDs.
3. Call `git.merge_abort()` to clean up the attempted merge.
4. Write conflict diagnostics to the integration log and surface them to the operator.

There is **no retry, re-queue, or automatic escalation.** The hard stop is the entire
recovery model. See `src/commands/integrate.rs:292-416` and `src/git/wrapper.rs:105-116`.

### Worker observability

The event model (`src/model/event.rs:4-42`) defines 19 named event types including
`StaleHeartbeat`, `NeedsInput`, `RateLimited`, `MergeConflict`, `TddViolation`, and
`VoltagentViolation`. These are written to an `events.jsonl` log.

The `watch` command monitors two streams: status file changes (state transitions) and
heartbeat file mtimes. The staleness threshold is **120 seconds**, hardcoded at
`src/commands/watch.rs:14`. The `dashboard` TUI refreshes every 3 seconds and shows
stale heartbeat warnings inline. All alerting is **console/TUI-only** — no external
notifications, webhooks, or escalation paths.

### Cost tracking

There is **token counting but no cost tracking.** `TaskStatus` carries an optional
`token_usage: Option<u64>` field (`src/model/task.rs:83`). The `worker status` command
accepts a `--tokens` parameter, and the status formatter aggregates and displays a
total across tasks (`src/commands/status.rs:185-192`). There are no dollar-cost fields,
no per-worker breakdowns, no phase-level granularity, and no budget limits or alerts.

### voltagent-* subagent namespace

`voltagent-*` is an **undocumented placeholder** — present in `CLAUDE.md`, the
`worker-seed.txt`, and the default `CLAUDE.md` template emitted by `agentrc init`, but
not implemented anywhere in the codebase. No struct, routing logic, or external
integration exists for it. A `VoltagentViolation` event type is defined
(`src/model/event.rs:32`) but never emitted. The names (e.g.,
`voltagent-lang:rust-engineer`, `voltagent-qa-sec:test-automator`) appear to be an
aspirational naming convention for specialized subagents — the workers are instructed
to use them, but agentrc itself does not enforce or validate the dispatch.
