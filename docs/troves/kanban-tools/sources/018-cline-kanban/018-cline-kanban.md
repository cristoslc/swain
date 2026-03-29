---
source-id: 018-cline-kanban
type: repository
url: https://github.com/cline/kanban
fetched: 2026-03-28T22:35:00Z
title: "Cline Kanban — Browser-based agent orchestration board with worktree isolation"
---

# Cline Kanban

**Repository:** [cline/kanban](https://github.com/cline/kanban)
**License:** Apache 2.0
**Status:** Research preview (March 2026)
**Install:** `npm i -g kanban` or `npx kanban`
**Stack:** TypeScript, Node.js, browser-based web UI

## What it is

Cline Kanban is a terminal-launched, browser-based kanban board designed specifically for orchestrating multiple CLI coding agents in parallel. Each task card gets its own git worktree and terminal. It runs locally from any git repo, requires no account, and works out of the box.

## Architecture

- **Local web server** — `npx kanban` launches a local web server and opens it in the browser
- **Ephemeral worktrees** — each task card creates an isolated git worktree; cleaned up when the card is trashed
- **Symlinked dependencies** — gitignored files (e.g., `node_modules`) are symlinked from the main repo into worktrees rather than reinstalled
- **Agent adapters** — detects installed CLI agents (Cline CLI, Claude Code, Codex, OpenCode) and runs them in per-card terminals
- **Hooks system** — uses runtime hooks to display the latest message or tool call on each card for at-a-glance monitoring
- **Sidebar chat agent** — a conversational interface for board management (create, link, start tasks)
- **Built-in git interface** — commit history, branch switching, fetch/pull/push, git graph visualization

## Key features

### Parallel execution with worktree isolation
Every task runs in its own git worktree. Agents work simultaneously without merge conflicts. Worktrees are ephemeral — created on task start, destroyed on trash.

### Task linking and dependency chains
`Cmd+click` a card to link it to another. When a card completes and is trashed, linked tasks auto-start. Combined with auto-commit, this creates fully autonomous pipelines: one agent finishes, commits, and the next agent picks up automatically.

### Auto-commit and auto-PR
Agents can automatically commit changes as they work (incremental trail of commits). Auto-PR creates pull requests when agents finish. Both are toggleable in settings.

### Diff viewer with checkpoints
Click a card to see a full diff of worktree changes. Checkpoint system lets you scope diffs to specific message ranges. Inline commenting sends feedback directly to the agent ("handle this edge case", "use a different pattern here").

### Agent-agnostic
Works with any CLI-based coding agent. Currently supports Cline CLI, Claude Code, Codex, and OpenCode. Uses experimental features that bypass permissions and runtime hooks for agent autonomy.

### Resume tasks
Trashing a card saves a resume ID. Tasks can be picked up later without starting from scratch.

### Linear integration
Supports Linear ticket import — turn a sprint backlog into agent tasks in one step.

### Script shortcuts
Define commands (e.g., `npm run dev`, `npm test`) in settings that appear as play buttons on cards for quick testing within worktrees.

## CLI interface

```
kanban                          # Launch board
kanban task list                # List tasks (JSON)
kanban task create --prompt "..." # Create task
kanban task link --task-id X --linked-task-id Y
kanban task start --task-id X
kanban hooks ingest|notify|...  # Runtime hook helpers
kanban mcp                      # MCP server mode
```

## How it differs from other kanban tools in this trove

| Dimension | Cline Kanban | Other tools in survey |
|-----------|-------------|----------------------|
| **Data model** | Board-owns-the-data (task manager) | Mixed — some board-owns, some file-reader |
| **Purpose** | Agent orchestration — run parallel coding agents | Project management / artifact visualization |
| **Worktree isolation** | First-class — automatic ephemeral worktrees per task | None (except swain's manual worktree workflow) |
| **Agent integration** | Native — detects and launches CLI agents | Agent Kanban [007] only; others are manual |
| **Dependency chains** | Auto-start linked tasks on completion | None |
| **Diff review** | Built-in with checkpoints and inline comments | None |

## Relevance to swain

Cline Kanban operates in **Model 1** (board-owns-the-data) — it creates and manages its own task cards, not reading existing markdown artifacts. It competes with `tk` for task tracking, not with daymark for artifact visualization. However, it introduces several concepts relevant to swain:

1. **Worktree-per-task is validated** — Cline Kanban's core UX insight is that ephemeral worktrees per task card eliminate merge conflicts in parallel agent work. Swain already uses worktrees for isolation (swain-session), but Cline validates the pattern at scale (hundreds of agents).

2. **Dependency chain automation** — task linking with auto-start on completion is a pattern swain-do could adopt for spec implementation ordering.

3. **Hook-based monitoring** — using runtime hooks to surface agent status on cards is a lightweight observability pattern. Swain's hook infrastructure could display similar status.

4. **Agent-agnostic orchestration** — Cline Kanban works with multiple CLI agents. Swain is already agent-agnostic (AGENTS.md-based), but the orchestration layer (multiple agents in parallel on the same board) is a capability swain lacks.

5. **Symlinked gitignored files** — practical technique for fast worktree setup that swain could adopt.

## Limitations

- **Research preview** — uses experimental features (permission bypass, runtime hooks). Not production-stable.
- **Board-owns-the-data** — cannot read existing markdown artifacts by frontmatter. Different design space than daymark.
- **No lifecycle awareness** — tasks have simple columns (backlog, in_progress, review, trash), not configurable multi-track lifecycles.
- **Permission bypass** — "experimental features that bypass permissions and runtime hooks for more autonomy" is a significant trust/safety tradeoff.
