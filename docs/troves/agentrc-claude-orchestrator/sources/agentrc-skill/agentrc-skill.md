---
source-id: agentrc-skill
type: repository
url: "https://github.com/ericsmithhh/agent.rc/blob/master/skill/agentrc/SKILL.md"
fetched: 2026-04-13
title: "agentrc SKILL.md — Orchestrator workflow directives"
author: ericsmithhh
---

# agentrc — Orchestrator Skill

The agentrc skill enables you to coordinate multiple Claude Code worker sessions in
tmux panes using the `agentrc` CLI binary.

## Initial Setup

When this skill activates, execute:

1. Rename the current tmux window: `tmux rename-window 'agent.rc'`
2. Launch a dashboard pane (if not already running): `tmux split-window -h -l 45% 'agentrc dashboard'`
3. Initialize `.orchestrator/` if it doesn't exist: `agentrc init`

## Four-Phase Workflow

**Phase 1 (PLAN):** Classify the goal, gather context, create a task dependency graph,
then present the plan to the user before spawning any workers.

**Phase 2 (DISPATCH):** Create the run and spawn workers for tasks with resolved
dependencies.

**Phase 3 (MONITOR + INTEGRATE):** Continuously check status using `agentrc status`,
review and merge completed tasks as their dependencies finish, then spawn newly
unblocked tasks.

**Phase 4 (REPORT):** Summarize results and offer cleanup.

## Critical Git Rules

The orchestrator exclusively handles merges, pushes, and remote operations — never
committing directly to main. Workers may only use `git add`, `commit`, `status`,
`diff`, and `log`. Subagents cannot run any git commands. All changes require
branching, review, and merge with `--no-ff`.

## Key Constraints

- Never write directly to worker worktrees.
- Redispatches require explicit user approval.
- Do not assume slow progress indicates failure (workers may spend 10–20 minutes
  planning or reading).
- Practice atomic commits: complete all changes, verify tests pass, then commit once.
- Maximum two redispatches per task before escalating to the user.
