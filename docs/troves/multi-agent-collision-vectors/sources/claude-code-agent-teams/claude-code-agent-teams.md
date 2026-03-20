---
source-id: claude-code-agent-teams
type: documentation
title: "Orchestrate teams of Claude Code sessions"
url: "https://code.claude.com/docs/en/agent-teams"
fetched: 2026-03-20
content-hash: "--"
---

# Orchestrate Teams of Claude Code Sessions

## Architecture

An agent team consists of:
- **Team lead**: the main Claude Code session that creates the team, spawns teammates, and coordinates work
- **Teammates**: separate Claude Code instances that each work on assigned tasks
- **Task list**: shared list of work items that teammates claim and complete
- **Mailbox**: messaging system for communication between agents

Task claiming uses file locking to prevent race conditions when multiple teammates try to claim the same task simultaneously.

## Worktree Integration

Teams without worktrees coordinate tasks but share the same filesystem — works when teammates edit different files. Teams with worktrees give each teammate its own worktree isolation — used when teammates might edit overlapping files.

## Conflict Avoidance Strategy

The documentation explicitly recommends: "Two teammates editing the same file leads to overwrites. Break the work so each teammate owns a different set of files."

Agent teams are not recommended for "same-file edits, or work with many dependencies" — these should use a single session or subagents.

## Coordination Mechanisms

- **Automatic message delivery**: messages delivered automatically to recipients without polling
- **Idle notifications**: teammates notify the lead when they finish
- **Shared task list**: all agents can see task status and claim available work
- **Task dependencies**: blocked tasks cannot be claimed until dependencies complete

## Quality Gates

Hooks enforce rules:
- `TeammateIdle`: runs when a teammate is about to go idle; exit code 2 keeps them working
- `TaskCompleted`: runs when a task is marked complete; exit code 2 prevents completion

## Known Limitations

- No session resumption with in-process teammates
- Task status can lag (teammates sometimes fail to mark tasks complete)
- One team per session; no nested teams
- All teammates start with lead's permission mode
- No explicit merge queue or integration verification mechanism

## Key Gap

The documentation describes task-level coordination and filesystem-level isolation but does not address semantic integration verification — there is no mechanism to ensure that independently-correct changes from different teammates are semantically compatible when merged. The merge strategy is left to standard git workflows.
