---
source-id: agentrc-readme
type: repository
url: "https://github.com/ericsmithhh/agent.rc"
fetched: 2026-04-13
title: "agent.rc — Orchestrate parallel Claude Code workers with discipline"
author: ericsmithhh
---

# agent.rc — README

## Summary

agent.rc orchestrates parallel Claude Code workers across tmux panes. Each worker is a full Claude Code session in its own git worktree and tmux pane. A Rust CLI binary (`agentrc`) handles deterministic mechanics — spawning, status tracking, branch merging, TDD auditing. A skill layer (`SKILL.md`) tells the orchestrator what to do in prose directives.

## Core design principles

- **Human-in-the-loop** — you approve the full task DAG before any workers launch.
- **TDD enforced** — red-green-refactor is a workflow invariant. Commit history is audited. Branches that skip tests are redispatched.
- **Maximal models** — every worker and subagent runs the strongest available model.
- **Sub-team orchestration** — each worker can dispatch its own specialist subagents (implementation, testing, security review, architecture, code quality).
- **Full Claude Code instances** — workers are not sandboxed API calls. Full skills, full MCP servers, full tool access.
- **Multi-agent review panels** — every chunk of work is reviewed by a stack specialist, code quality reviewer, and security auditor before merge.
- **Git worktree isolation** — every task gets its own branch and worktree. Merges happen in dependency order with test gates.
- **Active steering** — attach to any worker's tmux pane mid-task and redirect it in natural language.
- **Tmux-native** — no Electron, no web UI, no containers.

## Architecture

Two layers, cleanly separated:

- **Skill layer** (`skill/agentrc/SKILL.md`) — prose directives the orchestrator follows: plan, decompose, dispatch, monitor, integrate, report. The LLM decides *what* to build.
- **Ops binary** (`agentrc`) — a single Rust binary handling deterministic mechanics: tmux panes, git worktrees, status aggregation, branch merging, TDD auditing, checkpoint/restore. The binary handles *how*.

```
┌────────────────────────────────────────────────┐
│ Terminal (tmux)                                │
│                                                │
│ ┌──────────────┐ ┌───────────┐ ┌───────────┐   │
│ │ Orchestrator │ │ Worker 1  │ │ Worker 2  │   │
│ │ Claude Code  │ │ Claude    │ │ Claude    │   │
│ │ agentrc skill│ │ MCP       │ │ MCP       │   │
│ │ plans, gates │ │ skills    │ │ skills    │   │
│ │ dispatches   │ │ subagents │ │ subagents │   │
│ └──────┬───────┘ └─────┬─────┘ └─────┬─────┘   │
│        │               │             │         │
│        └───────agentrc CLI───────────┘         │
│          spawn, status, integrate,             │
│          teardown, checkpoint                  │
│                   │                            │
│          .orchestrator/                        │
│       (filesystem coordination)                │
└────────────────────────────────────────────────┘
        │                   │
 git worktree 1       git worktree 2
 (orc/001-feat)       (orc/002-feat)
```

## CLI commands

| Command | What it does |
|---------|-------------|
| `init` | Scaffold `.orchestrator/`, detect test command |
| `install` | Symlink skill, verify prerequisites |
| `spawn <task-id>` | Create tmux pane + git worktree, launch Claude, seed prompt |
| `respawn <task-id>` | Re-launch a dead worker, preserving branch state |
| `status [--json]` | Task status table (TTY or JSON) |
| `dashboard` | Interactive ratatui TUI |
| `watch` | Stream status changes and heartbeat alerts |
| `integrate [--dry-run]` | Merge branches in dependency order with test gates |
| `audit <task-id>` | TDD commit pattern audit |
| `teardown [task-id] [--all]` | Close pane, remove worktree |
| `checkpoint save / restore` | Save and restore run state |
| `resume` | Context dump for session recovery |
| `amend <task-id>` | Update a task brief mid-run and notify the worker |
| `plan validate` | Validate task DAG for cycles and missing deps |
| `run create / list / archive` | Manage named runs |
| `layout [tile\|collate]` | Retile worker panes across windows |

## Configuration

`agentrc init` creates `.orchestrator/config.json`:

| Field | Default | Description |
|-------|---------|-------------|
| `base_branch` | `"main"` | Branch workers fork from |
| `max_workers` | `12` | Maximum concurrent panes |
| `workers_per_window` | `4` | Panes per tmux window |
| `heartbeat_timeout_sec` | `120` | Seconds before flagged stale |
| `max_redispatch_attempts` | `2` | Auto-retry limit per task |
| `test_command` | *(auto-detected)* | `cargo test`, `npm test`, etc. |
| `auto_respawn` | `true` | Respawn dead workers automatically |

## Requirements

- Rust (edition 2021)
- tmux
- Claude CLI
- git
