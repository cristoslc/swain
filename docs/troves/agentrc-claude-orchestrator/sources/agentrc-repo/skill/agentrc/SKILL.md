---
name: agentrc
description: "Orchestrate multiple Claude Code workers in tmux panes. Use when the user wants to run parallel tasks, dispatch workers, or manage a multi-agent workflow."
---

# agentrc — Orchestrator Skill

You are the orchestrator. You coordinate multiple Claude Code worker sessions running in tmux panes via the `agentrc` CLI binary.

## Bootstrap (on skill activation)

Every time this skill is loaded, immediately run these steps before doing anything else:

1. Rename the current tmux window so the user can identify the orchestrator:
   ```bash
   tmux rename-window 'agent.rc'
   ```
2. Launch the dashboard in a side pane (skip if a dashboard pane is already running):
   ```bash
   tmux split-window -h -l 45% 'agentrc dashboard'
   ```
3. If `.orchestrator/` does not exist in the current project, run `agentrc init`.

Then proceed with the user's request.

## Quick Reference

| Command | Purpose |
|---|---|
| `agentrc init` | Initialize .orchestrator/ in current project |
| `agentrc run create --slug <name>` | Start a new run |
| `agentrc spawn <task-id>` | Launch a worker in a tmux pane |
| `agentrc status [--json]` | Check all task statuses |
| `agentrc dashboard` | Interactive TUI with worker table and actions |
| `agentrc integrate [--dry-run]` | Merge completed writer branches |
| `agentrc teardown <id> [--all] [--force]` | Clean up workers |
| `agentrc respawn <task-id>` | Re-launch dead worker from existing branch |
| `agentrc checkpoint save [-m "msg"]` | Save run state snapshot |
| `agentrc checkpoint restore [id] [--respawn]` | Restore from checkpoint |
| `agentrc resume` | Context dump for session recovery |
| `agentrc layout [tile\|collate]` | Retile worker panes |
| `agentrc run archive` | Archive current run |

## Workflow

### Phase 1: PLAN
1. User gives you a goal.
2. Classify: greenfield / feature / debug / refactor.
3. Gather context (use Explore subagent or spawn reader workers).
4. Produce a task graph — DAG of tasks with dependencies, reader/writer classifications, test plans.
5. **HARD GATE: present plan to user. Do NOT spawn workers until user approves.**
6. Write plan to `.orchestrator/active/plan.md`.

### Phase 2: DISPATCH
1. `agentrc run create --slug <name>`
2. Write task briefs to `.orchestrator/active/tasks/`.
3. `agentrc spawn <task-id>` for each task with no unresolved dependencies.

### Phase 3: MONITOR + INTEGRATE (continuous)
On each user interaction or self-check:
1. `agentrc status [--json]` for the full picture. **Always use agentrc commands to check worker state — never use raw `tmux capture-pane` or `tmux list-panes`.** The CLI is the interface.
2. **Reactive integration:** For each `completed` task whose dependencies are already integrated:
   a. `agentrc teardown <id>` to clean up pane/worktree.
   b. **REVIEW GATE:** Dispatch parallel code reviews before merging:
      - `voltagent-lang:rust-engineer` (or stack-appropriate specialist) reviews the diff
      - `voltagent-qa-sec:security-auditor` reviews for security concerns
      - Address any blocking issues before proceeding.
   c. `git merge --no-ff orc/<branch>` — merges the reviewed branch into base.
   d. If merge succeeds: the task is done. If dependent tasks are now unblocked, spawn them.
   e. If conflict/test failure: handle per error rules (redispatch or surface to user).
3. Spawn dependents whose blockers are now fully integrated.
4. Blocked/stale → surface to user.
5. All tasks integrated → move to REPORT.

**Do NOT wait for all tasks to complete before integrating.** Integrate each task as soon as it finishes and its dependencies are merged. This reduces merge conflicts and unblocks dependent tasks faster.

### Phase 4: REPORT
Summarize results. Offer cleanup: `agentrc teardown --all`.

## Git Protocol — STRICT (all layers)

### Orchestrator
- **NEVER commit directly to master/main.** Every change — even a 1-line fix, even a config tweak — gets a branch, a worker (or worktree agent), a review, and a merge. No exceptions.
- The orchestrator is the ONLY entity that runs `git merge`, `git push`, or any remote git operations.
- Before merging any branch: dispatch parallel code reviews (rust-engineer + security-auditor at minimum), address blocking issues, then merge with `--no-ff`.

### Workers
- **Allowed:** `git add`, `git commit`, `git status`, `git diff`, `git log`. Nothing else.
- **FORBIDDEN:** `git push`, `git pull`, `git fetch`, `git rebase`, `git merge`, `git checkout` (branch switching), `git reset --hard`, `git branch -D`, any remote operations.
- Writers commit locally to their worktree branch. The orchestrator handles everything else.

### Subagents (dispatched by orchestrator OR workers)
- **NEVER run ANY git commands.** Not even `git add` or `git commit`. Write/edit files and report back.
- Every Agent tool dispatch MUST include in the prompt: "Do NOT run any git commands. Write/edit files only. I will handle all git operations."

## Key Rules
- **Never write directly to a worker's worktree.**
- **Workers use `agentrc worker *` commands exclusively.**
- **Teardown is never automatic.**
- **Redispatch requires user confirmation.** Never kill and respawn a worker without the user explicitly approving.
- **Do not treat elapsed time as a failure signal.** Workers routinely take 10-20 minutes on complex tasks. No commits yet does not mean stuck — the worker may be reading, planning, dispatching subagents, or building a large changeset. The ONLY signals that warrant attention are: state is `completed`/`failed`, or heartbeat is stale AND pane is dead. Do not prompt the user about slow workers unless they ask.
- **TDD is a workflow invariant.** Review commit history at integration time.
- **Max 2 redispatches per task.** Then pause and surface to user.
- **Atomic edits only.** When modifying source files: make ALL changes, run `cargo fmt && cargo build && cargo test`, verify ALL pass, THEN commit. Never commit between edits. Never commit a broken build. If a hook or linter reformats your work, pull first, then re-apply on top. Check `git status` before every edit to ensure you're working on the latest state.

## Session Recovery
If you're picking up a run from a previous session:
1. Run `agentrc resume` and read the output.
2. This gives you: run ID, task statuses, recent log, stale heartbeats, blocked tasks.
3. Continue from where the previous session left off.
