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

## Gaps

- No documented model for handling merge conflicts when tasks have undetected write
  overlap (only "reader/writer classifications" at plan time).
- The `agentrc dashboard` TUI and `watch` command suggest observability is important,
  but no detail on what signals workers emit or how alerting works.
- No mention of cost tracking across parallel workers (each full Claude Code session
  generates independent usage).
- The `voltagent-*` subagent namespace in CLAUDE.md is undocumented — it's unclear
  if this is a public framework or project-specific naming.
