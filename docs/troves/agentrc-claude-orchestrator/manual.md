# agent.rc Manual

> Reference documentation compiled from the source repo at commit `3886c99`.
> Covers installation, configuration, the four-phase workflow, CLI reference,
> task briefs, worker protocol, integration mechanics, and data model.

---

## Installation

**Requirements:** Rust (edition 2021), tmux, git, Claude CLI.

```bash
git clone https://github.com/ericsmithhh/agent.rc.git
cd agent.rc && cargo install --path .
agentrc install          # symlinks the skill, verifies prerequisites
```

In your project:

```bash
cd /path/to/your/project
agentrc init             # scaffolds .orchestrator/, auto-detects test command
```

Then start a Claude Code session and load the `agentrc` skill. The orchestrator
takes over from there.

---

## Project layout after `agentrc init`

```
.orchestrator/
  config.json            # project configuration
  active/
    plan.md              # current task DAG (written by orchestrator)
    tasks/               # task brief files: <id>-<slug>.md
    status/              # worker status JSON files: <id>.json
    worktrees/           # git worktrees: <id>/
    integration.log      # merge diagnostics
    events.jsonl         # event stream
  runs/                  # archived runs
  checkpoints/           # checkpoint snapshots
```

---

## Configuration

`agentrc init` creates `.orchestrator/config.json`. All fields are optional
except `project_root`.

| Field | Default | Description |
|-------|---------|-------------|
| `base_branch` | `"main"` | Branch workers fork from. |
| `max_workers` | `12` | Maximum concurrent active panes. |
| `workers_per_window` | `4` | Panes per tmux window before opening a new one. |
| `heartbeat_interval_sec` | `30` | How often workers send a heartbeat. |
| `heartbeat_timeout_sec` | `120` | Seconds of silence before a worker is flagged stale. |
| `max_redispatch_attempts` | `2` | Auto-retry cap per task. Surface to user after this. |
| `test_command` | *(auto-detected)* | Shell command run after each merge. `cargo test`, `npm test`, etc. |
| `worker_claude_args` | `[]` | Extra flags appended to every `claude` invocation. |

Example:

```json
{
  "project_root": "/path/to/project",
  "base_branch": "main",
  "max_workers": 8,
  "workers_per_window": 3,
  "heartbeat_timeout_sec": 180,
  "test_command": "cargo test --workspace"
}
```

---

## The four-phase workflow

### Phase 1 — PLAN

The orchestrator decomposes the user's goal before touching any code.

1. Classify the goal: greenfield / feature / debug / refactor.
2. Gather context — use an Explore subagent or spawn reader workers.
3. Produce a task DAG:
   - Each task has an ID, slug, classification (Reader or Writer), dependencies,
     and a test plan.
   - Writer tasks get their own git branch and worktree.
   - Reader tasks run in the project root and produce notes/results only.
4. **Hard gate:** present the full DAG to the user. Do not spawn any workers until
   the user approves. No exceptions.
5. Write the approved plan to `.orchestrator/active/plan.md`.

### Phase 2 — DISPATCH

```bash
agentrc run create --slug <name>   # create a named run
# for each task with no unresolved dependencies:
agentrc spawn <task-id>
```

`spawn` does all of this in one call:
- Parses the task brief frontmatter.
- Creates a git worktree at `active/worktrees/<id>/` on branch `orc/<id>-<slug>`
  (writer tasks only).
- Writes an initial status file (state: `spawning`).
- Creates a tmux pane in the `workers` window.
- Exports `AGENTRC_PROJECT_ROOT` so worker commands can find `.orchestrator/`.
- `cd`s the pane into the worktree (writer) or project root (reader).
- Starts a background heartbeat daemon.
- Launches `claude --dangerously-skip-permissions '<seed-prompt>'`.

The seed prompt reads:

> You are worker `<id>`. Read your task brief at `<path>` and begin work.
> Use `agentrc worker status --task <id> --state in_progress` to report progress.
> Use `agentrc worker heartbeat --task <id>` to send heartbeats.
> Use `agentrc worker done --task <id>` when finished.

### Phase 3 — MONITOR + INTEGRATE (continuous)

On each user interaction or self-check:

```bash
agentrc status [--json]   # full task state table
```

**Never use raw `tmux capture-pane` or `tmux list-panes` to inspect workers.
The CLI is the only interface.**

For each task in state `completed` whose dependencies are already integrated:

1. Dispatch parallel code reviews before merging:
   - Stack specialist (`voltagent-lang:rust-engineer` or equivalent)
   - Security auditor (`voltagent-qa-sec:security-auditor`)
   - Address any blocking issues.
2. `agentrc teardown <id>` — closes pane and removes worktree.
3. `git merge --no-ff orc/<branch>` — merges the reviewed branch.
4. If test gate passes: task is done. Spawn any newly unblocked dependents.
5. If merge conflict or test failure: handle per error rules below.

**Do not wait for all tasks to complete before integrating.** Integrate each task
as soon as it finishes. This reduces conflicts and unblocks dependents faster.

**Do not treat elapsed time as failure.** Workers routinely spend 10–20 minutes
reading, planning, or dispatching subagents. The only failure signals are:
- State is `completed` or `failed`.
- Heartbeat is stale AND the pane is dead.

### Phase 4 — REPORT

Summarize results. Offer cleanup:

```bash
agentrc teardown --all
```

---

## Task brief format

Task briefs live at `.orchestrator/active/tasks/<id>-<slug>.md`. The orchestrator
writes them; workers read them.

```markdown
---
id: "001"
slug: add-auth-middleware
classification: writer           # writer | reader
worktree: .orchestrator/active/worktrees/001
base_branch: main
branch: orc/001-add-auth-middleware
pane_id: null                    # filled in by spawn
depends_on: []
created_at: 2026-04-13T00:00:00Z
---

# Task 001: Add auth middleware

## Scope
Add JWT validation middleware to all protected API routes.

## Test plan
Unit tests for token parsing. Integration test for a protected route with valid
and invalid tokens.

## Acceptance criteria
- All protected routes return 401 on missing/invalid token.
- Valid tokens pass through unchanged.

## Out of scope
Token refresh, OAuth flows.

## Notes for worker
Use the existing `auth` crate. Do not add new dependencies.
```

---

## Worker protocol

Workers communicate exclusively through `agentrc worker *` commands. They never
interact with `.orchestrator/` files directly.

| Command | When to use |
|---------|-------------|
| `agentrc worker status --task <id> --state in_progress` | Signal work has started. |
| `agentrc worker status --task <id> --state blocked --message "reason"` | Signal a blocker. |
| `agentrc worker note --task <id> --message "..."` | Progress update (visible in dashboard). |
| `agentrc worker heartbeat --task <id>` | Keep-alive ping (usually run in background). |
| `agentrc worker done --task <id> --result-file ./result.md` | Signal completion with result. |

Workers run with a background heartbeat:

```bash
agentrc worker heartbeat --task <id> --interval 30 &
```

This runs automatically on spawn. Workers should not touch it.

---

## Git protocol — strict

This applies at all three layers: orchestrator, workers, and subagents.

### Orchestrator

- **Never commit directly to master/main.** Every change — including a one-line
  fix — gets a branch, a worker, review, and a merge. No exceptions.
- The orchestrator is the **only** entity that runs `git merge`, `git push`, or
  any remote operations.
- Before merging any branch: dispatch parallel reviews, address blocking issues,
  then merge with `--no-ff`.

### Workers

**Allowed:** `git add`, `git commit`, `git status`, `git diff`, `git log`.

**Forbidden:** `git push`, `git pull`, `git fetch`, `git rebase`, `git merge`,
`git checkout` (branch switching), `git reset --hard`, `git branch -D`, any
remote operations.

Workers commit locally to their worktree branch. The orchestrator handles
everything else.

### Subagents (dispatched by orchestrator or workers)

**Never run any git commands.** Not even `git add`. Write and edit files only.
Every Agent tool dispatch must include:

> "Do NOT run any git commands. Write/edit files only. I will handle all git
> operations."

---

## Integration mechanics

`agentrc integrate [--dry-run]` merges all completed writer task branches.

### Merge order

Tasks are sorted topologically: tasks with no dependencies first, then those
whose dependencies have been merged, using task ID as a tiebreaker within each
group. This is the same order used by `agentrc plan validate`.

### Merge process (per task)

1. Checkout base branch.
2. `git merge --no-ff orc/<branch>` — preserves branch topology.
3. On success: run `test_command` if configured.
   - Tests pass → task done, unblock dependents.
   - Tests fail → `git reset --hard HEAD~1`, mark `test_failure`, show touched
     files and first 50 lines of stderr.
4. On conflict → `git merge --abort`, collect conflicting files, cross-reference
   which other tasks touched those files, log diagnostics.

### Dry run

```bash
agentrc integrate --dry-run
```

Shows which branches would be merged, which files each touches, and any
potential file overlaps between tasks. No side effects.

### Integration log

All merge events (success, conflict, test failure) are appended to
`.orchestrator/active/integration.log`. Useful for post-mortem.

---

## Task state machine

```
spawning → ready → in_progress → completed
                               → failed
                               → blocked → in_progress
                                         → failed
                                         → aborted
spawning → failed
spawning → aborted
ready    → aborted
in_progress → aborted
```

States are stored as JSON in `.orchestrator/active/status/<id>.json`.

| State | Meaning |
|-------|---------|
| `spawning` | `agentrc spawn` called; Claude not yet started. |
| `ready` | Worker has started but not yet reported `in_progress`. |
| `in_progress` | Worker is actively working. |
| `blocked` | Worker reported a blocker via `agentrc worker status`. |
| `completed` | Worker called `agentrc worker done`. Ready to integrate. |
| `failed` | Worker reported failure or spawn failed. |
| `aborted` | Manually stopped or max redispatches exceeded. |

---

## CLI reference

### Setup

| Command | Description |
|---------|-------------|
| `agentrc install` | Symlink skill into project, verify prerequisites. |
| `agentrc init` | Scaffold `.orchestrator/`, detect test command. |

### Run management

| Command | Description |
|---------|-------------|
| `agentrc run create --slug <name>` | Create a new named run. |
| `agentrc run list` | List all runs. |
| `agentrc run archive` | Archive the current run. |

### Worker lifecycle

| Command | Description |
|---------|-------------|
| `agentrc spawn <task-id>` | Create pane + worktree, launch Claude, seed prompt. |
| `agentrc respawn <task-id>` | Re-launch a dead worker on its existing branch. |
| `agentrc teardown <task-id>` | Close pane, remove worktree. |
| `agentrc teardown --all` | Tear down all workers. |
| `agentrc teardown --force` | Teardown even if worker is still active. |
| `agentrc amend <task-id>` | Update task brief mid-run and notify worker. |

### Monitoring

| Command | Description |
|---------|-------------|
| `agentrc status` | Task status table (TTY format). |
| `agentrc status --json` | Task status as JSON (for scripting). |
| `agentrc dashboard` | Interactive ratatui TUI with worker table and actions. |
| `agentrc watch` | Stream status changes and heartbeat alerts. |
| `agentrc events` | Show the event stream. |
| `agentrc audit <task-id>` | TDD commit pattern audit for a task's branch. |

### Integration

| Command | Description |
|---------|-------------|
| `agentrc integrate` | Merge completed writer branches in dependency order. |
| `agentrc integrate --dry-run` | Preview merge plan, detect file overlaps. |
| `agentrc plan validate` | Validate task DAG for cycles and missing dependencies. |

### Session management

| Command | Description |
|---------|-------------|
| `agentrc checkpoint save [-m "msg"]` | Save current run state. |
| `agentrc checkpoint list` | List saved checkpoints. |
| `agentrc checkpoint restore [id]` | Restore from checkpoint. |
| `agentrc checkpoint restore [id] --respawn` | Restore and respawn all tasks. |
| `agentrc resume` | Context dump for session recovery (shows run ID, task statuses, stale heartbeats). |

### Layout

| Command | Description |
|---------|-------------|
| `agentrc layout tile` | Tile all worker panes evenly. |
| `agentrc layout collate` | Group panes by dependency tier. |

### Worker internals (called by workers, not operators)

| Command | Description |
|---------|-------------|
| `agentrc worker status --task <id> --state <state>` | Update task state. |
| `agentrc worker note --task <id> --message "..."` | Post a progress note. |
| `agentrc worker heartbeat --task <id> [--interval N]` | Send or loop heartbeat. |
| `agentrc worker done --task <id> [--result-file <path>]` | Signal completion. |
| `agentrc worker result --task <id> --file <path>` | Attach a result file. |

---

## Subagent dispatch patterns

Workers use the `voltagent-*` namespace for specialized subagents. All subagent
dispatches must include: `"Do NOT run any git commands. Write/edit files only."`

| Role | Subagent type |
|------|--------------|
| Rust implementation | `voltagent-lang:rust-engineer` |
| Test authoring | `voltagent-qa-sec:test-automator` |
| Code review | `voltagent-qa-sec:code-reviewer` |
| Debugging | `voltagent-qa-sec:debugger` |
| Performance | `voltagent-qa-sec:performance-engineer` |
| Architecture review | `voltagent-qa-sec:architect-reviewer` |
| Security audit | `voltagent-qa-sec:security-auditor` |

All subagent work uses the `opus` model setting.

The orchestrator dispatches **parallel review panels** before merging any branch:
stack specialist + security auditor at minimum.

---

## Session recovery

If picking up a run from a previous session:

```bash
agentrc resume
```

Output includes: run ID, task statuses, recent event log, stale heartbeats,
blocked tasks. Continue from where the previous session left off — no need to
re-plan or re-approve the DAG.

For hard failures, use checkpoints:

```bash
agentrc checkpoint list
agentrc checkpoint restore <id> --respawn   # restore state and re-launch workers
```

---

## Error handling

| Situation | Default behavior |
|-----------|-----------------|
| Merge conflict | Abort merge, log conflicting files and which tasks caused them. Surface to user. |
| Test failure after merge | Roll back the merge commit (`reset --hard HEAD~1`), log touched files + stderr. Surface to user. |
| Worker stale (heartbeat timeout + dead pane) | Flag in `agentrc status`. Do not auto-respawn. |
| Worker blocked | Worker calls `agentrc worker status --state blocked`. Surface to operator. |
| Max redispatches reached | Stop and surface to user. Never kill/respawn beyond `max_redispatch_attempts` without explicit operator approval. |

---

## Dashboard TUI

`agentrc dashboard` opens an interactive ratatui terminal UI. It shows:

- Task table: ID, slug, state, last message, heartbeat age.
- Event stream pane.
- Key bindings for common actions (teardown, respawn, integrate).

The dashboard is launched automatically by the skill bootstrap as a side pane:

```bash
tmux split-window -h -l 45% 'agentrc dashboard'
```
