# agentrc

Orchestrate parallel Claude Code workers with discipline.

---

- **Human-in-the-loop** -- you approve every plan before workers launch. The full task DAG, dependencies, and test plans are visible. The workflow blocks on your judgment.
- **TDD enforced** -- red-green-refactor is a workflow invariant, not a suggestion. Commit history is audited at integration. Branches that skip tests get redispatched.
- **Maximal models** -- every worker and every subagent runs the strongest available model. No downgrading for subtasks.
- **Sub-team orchestration** -- each worker can dispatch its own specialist team: implementation, testing, security review, architecture, code quality.
- **Full Claude Code instances** -- workers are not sandboxed API calls. Full skills, full MCP servers, full tool access. Each one is a real Claude Code session.
- **Multi-agent review panels** -- every chunk of work is reviewed by a stack specialist, code quality reviewer, and security auditor before merge.
- **Git worktree isolation** -- every task gets its own branch and worktree. Merges happen in dependency order with test gates.
- **Active steering** -- attach to any worker's tmux pane mid-task and redirect it in natural language.
- **Tmux-native** -- no Electron, no web UI, no containers. Just terminal multiplexing you already know.

---

<video src="https://github.com/user-attachments/assets/03aa4af3-87f3-411c-a885-cc7b670f1291" controls muted></video>

*Orchestrator dispatching workers across tmux panes -- dashboard, isolated worktrees, live steering.*

## System Architecture

```
┌────────────────────────────────────────────────┐
│ Terminal (tmux)                                │
│                                                │
│ ┌──────────────┐ ┌───────────┐ ┌───────────┐   │
│ │ Orchestrator │ │ Worker 1  │ │ Worker 2  │   │
│ │ Claude Code  │ │ Claude    │ │ Claude    │   │
│ │              │ │           │ │           │   │
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

Tmux contains everything. The orchestrator and workers are peer Claude Code sessions in separate panes. The `agentrc` CLI is the coordination layer -- spawning panes, managing worktrees, aggregating status, merging branches. `.orchestrator/` is the shared filesystem bus. Git worktrees live outside the main repo so workers never collide.

## How It Works

You describe a goal. The orchestrator decomposes it into a task DAG with dependencies, reader/writer classifications, and test plans, then presents the full plan for your approval. Once you approve, workers launch in parallel -- each in its own tmux pane and git worktree, running full Claude Code with your MCP servers and tools. Workers follow strict TDD, dispatch their own review panels, and signal completion. Branches merge in dependency order with test gates. If anything fails, it gets redispatched or surfaced to you.

## Quick Start

Requires **Rust**, **tmux**, **git**, and the [**Claude CLI**](https://docs.anthropic.com/en/docs/claude-code).

```bash
git clone https://github.com/ericsmithhh/agent-rc.git
cd agent-rc && cargo install --path .
agentrc install
```

```bash
cd /path/to/your/project
agentrc init
```

Start a Claude Code session and describe your goal. The orchestrator takes it from there.

## Commands

| Command | What it does |
|---|---|
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

Workers use `agentrc worker *` subcommands internally for status reporting, heartbeats, notes, and completion signaling.

## Architecture

Two layers, cleanly separated. The **skill layer** (`skill/agentrc/SKILL.md`) encodes the workflow as prose directives the orchestrator follows -- plan, decompose, dispatch, monitor, integrate, report. The **ops binary** (`agentrc`) is a single Rust binary handling deterministic mechanics: tmux panes, git worktrees, status aggregation, branch merging, TDD auditing, checkpoint/restore. The LLM decides *what* to build. The binary handles *how*. Full spec in [`skill/agentrc/SKILL.md`](skill/agentrc/SKILL.md).

## Configuration

`agentrc init` creates `.orchestrator/config.json`:

| Field | Default | Description |
|---|---|---|
| `base_branch` | `"main"` | Branch workers fork from |
| `max_workers` | `12` | Maximum concurrent panes |
| `workers_per_window` | `4` | Panes per tmux window |
| `heartbeat_timeout_sec` | `120` | Seconds before flagged stale |
| `max_redispatch_attempts` | `2` | Auto-retry limit per task |
| `test_command` | *(auto-detected)* | `cargo test`, `npm test`, etc. |
| `auto_respawn` | `true` | Respawn dead workers automatically |

## Requirements

- [Rust](https://rustup.rs/) (edition 2021)
- [tmux](https://github.com/tmux/tmux)
- [Claude CLI](https://docs.anthropic.com/en/docs/claude-code)
- git

## License

MIT
