# agentrc — Implementation Spec

**Date:** 2026-04-11
**Status:** Draft, pending user review
**Supersedes:** `docs/tmux-workflow-design-spec.md` (original design, retained as history)

## Purpose

A unified meta-framework for building software with an LLM orchestrator (Claude Code) that kicks off specialized subagent workers in visible, interactive tmux panes. The human operator can observe every worker live, attach to any pane to redirect a worker in natural language, and trust that orchestration, merging, and integration are handled deterministically by a single Rust binary (`agentrc`) that complements the orchestrator's reasoning.

The repo (`agent.rc`) is the portable bootstrapping mechanism — clone it on any new machine, install the Rust toolchain, `cargo install --path .`, `agentrc install`, and you're ready to orchestrate.

The workflow targets four task shapes with one mental model:

- **Greenfield** — build a new project from a brief
- **Feature work** — add capabilities to an existing codebase
- **Debugging / investigation** — hunt down bugs across a codebase
- **Refactoring** — large-scale coordinated changes

## Operating constraints

- **Single user, single laptop, single tmux session.** No multi-host, no shared CI, no daemon required to stay running across reboots.
- **Active steering (human-in-the-loop).** The user wants to attach to any worker pane and interact with it in natural language. Panes must be real interactive `claude` sessions, not log outputs.
- **Test-Driven Development is a workflow invariant, not a preference.** Writer workers must follow `superpowers:test-driven-development` rigorously. Red → green → refactor. No implementation commits without preceding failing-test commits.
- **Coordination via shared filesystem.** No daemon, no Redis, no message broker. The `.orchestrator/` directory is the source of truth for all cross-process state.
- **Orchestrator is the user's current Claude Code session.** The orchestrator is a reasoning layer invoked via the `agentrc` skill, not a separate process.
- **Workers are full `claude` instances.** They inherit every tool, skill, and MCP server the user has installed. They can dispatch their own Task-tool subagents.
- **Writer isolation via git worktrees.** Each writer task gets its own worktree on its own branch. Readers share the project root, read-only.
- **Workers interact exclusively through the `agentrc worker` CLI.** Workers never write raw files to `.orchestrator/`. All status, notes, results, and lifecycle transitions go through the binary, which owns the file layout and schema.

## Architecture

Two layers, cleanly separated:

1. **Skill layer (`skill/agentrc/SKILL.md`)** — a Claude Code skill installed into `~/.claude/skills/agentrc/` via symlink. Encodes the *workflow*: how to plan, decompose, dispatch, monitor, integrate, and report. Prose directives the orchestrator (LLM) follows. No executable code.

2. **Ops binary (`agentrc` Rust crate)** — a single compiled binary that handles all deterministic mechanics: creating panes, spawning workers, managing git worktrees, aggregating status, merging branches, etc. Called by the orchestrator via the Bash tool. Single source of truth for "what happens when X."

There is **no standalone bash layer**. All shell invocations are constructed and executed by the Rust binary. Shell-outs to `tmux` and `git` are expected — standalone `.sh` files are not (except the mock-worker test fixture).

### Division of responsibility

| Concern | Layer |
|---|---|
| Deciding what to do | Skill (LLM reasoning) |
| Writing task briefs and plans | Skill (LLM reasoning) |
| Classifying reader vs writer | Skill (LLM reasoning, user can override) |
| Spawning panes and worktrees | Rust binary (`agentrc spawn`) |
| Aggregating status | Rust binary (`agentrc status`) |
| Worker status/notes/results | Rust binary (`agentrc worker *`) |
| Heartbeat daemon | Rust binary (`agentrc worker heartbeat`) |
| Integration merges and conflict handling | Rust binary (`agentrc integrate`) |
| TDD review at integration | Rust binary surfaces commit history, skill (LLM) judges |
| Teardown | Rust binary (`agentrc teardown`) |
| Layout / collation across windows | Rust binary (`agentrc layout`) |
| Session recovery | Rust binary (`agentrc resume`) |
| Reacting to failures | Skill (LLM reasoning) based on binary's reports |

### Key invariants

1. **The orchestrator never writes directly to a worker's worktree.** Workers own their worktrees. Orchestrator only reads them at integration time.
2. **Workers never write outside `.orchestrator/` or their own worktree.** Enforced by prompt discipline, not filesystem permissions.
3. **Workers interact with `.orchestrator/` exclusively via `agentrc worker *` subcommands.** No raw file writes. The binary owns the schema and file layout.
4. **Heartbeats are advisory.** A stuck worker surfaces in the user's status view. There is no automatic kill or respawn.
5. **Task briefs include pane ID.** Written by `agentrc spawn` after pane creation.
6. **One narrow exception to "no mid-task send-keys."** Conflict redispatch pings the worker with `send-keys` after updating the task brief file. Both are used; the file is the source of truth, the ping is a prompt to re-read.
7. **Teardown is never automatic.** A completed worker sits idle until explicitly torn down by the orchestrator or the user.
8. **TDD is reviewed at integration time.** The binary surfaces the worker's commit history; the orchestrator (LLM) judges whether TDD was followed and decides accept/redispatch.

## Phasing

Phasing is **feature progression within a single Rust codebase**, not a language migration.

### Phase 1 — MVP

Subcommands in scope:

- `agentrc install` — symlink skill into `~/.claude/skills/agentrc/`, verify claude CLI and tmux are available.
- `agentrc init` — create `.orchestrator/` scaffold, auto-detect test command with user confirm, add `.orchestrator/` to `.gitignore`.
- `agentrc spawn <task-id>` — create pane, worktree (if writer), launch claude, seed bootstrap prompt.
- `agentrc teardown <task-id>` — close pane, remove worktree, archive artifacts. `--all` for full run teardown.
- `agentrc status` — aggregate all task status into structured table (JSON or TTY-friendly).
- `agentrc layout [tile|collate]` — tile current workers window, collate overflow to new windows.
- `agentrc integrate` — serial merge in dependency order, auto-redispatch on first conflict, pause on second.
- `agentrc resume` — print structured context dump for session recovery.
- `agentrc run create --slug <name>` — create run directory and `active` symlink.
- `agentrc run list` — list all runs with status summary.
- `agentrc run archive` — drop `active` symlink, mark run archived.
- `agentrc worker status --task <id> --state <state> [--phase <phase>] [--message <msg>]`
- `agentrc worker heartbeat --task <id> [--interval 30]` — background daemon.
- `agentrc worker note --task <id> --message <msg>` — append timestamped note.
- `agentrc worker result --task <id> --file <path>` or `--stdin` — write final result.
- `agentrc worker done --task <id> [--result-file <path>]` — atomic: write result + set completed + ring bell.
- Basic conflict handling (redispatch with addendum, max 2 attempts).
- Basic test-failure handling (auto-revert + redispatch, same loop guard).
- Basic `state: failed` surfacing.

### Phase 2 — Hardened

Additions to the same binary:

- `agentrc plan validate` — task graph validation with cycle detection.
- Smarter integration: 3-way merge heuristics, test-aware rollback.
- Task amend flow: `agentrc amend <task-id> --from-brief`.
- `notify`-based filesystem watching instead of polling (optional).
- Richer status reporting with estimated completion times.

## CLI surface area

### Top-level commands

| Command | Purpose |
|---|---|
| `agentrc install` | Symlink skill into `~/.claude/skills/agentrc/`, verify prerequisites. Idempotent. |
| `agentrc init` | Scaffold `.orchestrator/`, auto-detect test command, update `.gitignore`. Idempotent. |
| `agentrc spawn <task-id>` | Create pane, worktree (writer), launch claude, seed prompt. |
| `agentrc teardown <task-id> [--all]` | Close pane, remove worktree, archive. |
| `agentrc status` | Aggregate task status table. JSON (`--json`) or TTY. |
| `agentrc layout [tile\|collate]` | Retile worker panes, collate to new windows. |
| `agentrc integrate` | Serial merge in dependency order. |
| `agentrc resume` | Structured context dump for session recovery. |

### `agentrc run` subcommands

| Command | Purpose |
|---|---|
| `agentrc run create --slug <name>` | Create run directory, set `active` symlink. |
| `agentrc run list` | List all runs with status. |
| `agentrc run archive` | Drop `active` symlink. |

### `agentrc worker` subcommands

Called by workers, not the orchestrator. Workers use these exclusively — no raw file writes.

| Command | Purpose |
|---|---|
| `agentrc worker status --task <id> --state <s> [--phase <p>] [--message <m>]` | Update task status JSON. |
| `agentrc worker heartbeat --task <id> [--interval 30]` | Background daemon, touches heartbeat file. |
| `agentrc worker note --task <id> --message <msg>` | Append timestamped note. |
| `agentrc worker result --task <id> --file <path> \| --stdin` | Write final result markdown. |
| `agentrc worker done --task <id> [--result-file <path>]` | Atomic: result + completed + bell. |

## Repository layout

```
agent.rc/
  Cargo.toml
  Cargo.lock
  .gitignore
  README.md
  Makefile                         # make test | make smoke | make install

  skill/
    agentrc/
      SKILL.md                     # prose workflow skill
      worker-seed.txt              # bootstrap prompt template
      task-brief.md                # task brief template with frontmatter

  src/
    main.rs                        # clap CLI entry
    commands/
      install.rs
      init.rs
      spawn.rs
      status.rs
      teardown.rs
      integrate.rs
      layout.rs
      resume.rs
      run.rs                       # run create/list/archive
      worker/
        mod.rs
        status.rs
        heartbeat.rs
        note.rs
        result.rs
        done.rs
    model/
      task.rs                      # Task, TaskGraph, TaskStatus types
      worker.rs                    # Worker, PaneId, WorkerState
      config.rs                    # OrchestratorConfig
      run.rs                       # RunId, RunMetadata
      error.rs                     # AppError, Result alias
    fs/
      bus.rs                       # read/write .orchestrator/ layout
      run.rs                       # run-scoped dir helpers, active symlink
    git/
      wrapper.rs                   # typed git command wrappers
    tmux/
      wrapper.rs                   # typed tmux command wrappers

  tests/
    happy_path.rs
    spawn_test.rs
    integrate_test.rs
    fault_injection.rs
    fixtures/
      mock-worker.sh               # simulates a claude session
      toy-project/                 # tiny test repo

  docs/
    tmux-workflow-design-spec.md   # original design spec (history)
    agentrc-implementation-spec.md # this document
```

## Runtime layout

Created inside each project that uses agentrc, via `agentrc init`.

```
<project>/.orchestrator/
  config.json                        # per-project config
  active -> runs/<current-run-id>/   # symlink; absent between runs
  runs/
    2026-04-11T14-30-auth-refactor/  # run-id = ISO timestamp + slug
      plan.md                        # approved task graph
      orchestrator.log               # timestamped orchestrator decisions
      integration.log                # merges, test results, conflicts
      config.json                    # snapshot of config at run start
      tasks/
        001-<slug>.md                # task brief (frontmatter + markdown)
      status/
        001.json                     # written by `agentrc worker status`
      heartbeats/
        001.alive                    # written by `agentrc worker heartbeat`
      notes/
        001.md                       # written by `agentrc worker note`
      results/
        001.md                       # written by `agentrc worker result/done`
      worktrees/
        001/                         # git worktree (writer tasks only)
```

Heartbeat files are keyed by task ID (stable) not pane ID (can change on respawn).

## Data schemas

### `config.json`

Written by `agentrc init`:

```json
{
  "project_root": "/home/eric/Code/foo",
  "base_branch": "main",
  "max_workers": 12,
  "workers_per_window": 4,
  "heartbeat_interval_sec": 30,
  "heartbeat_timeout_sec": 120,
  "max_redispatch_attempts": 2,
  "test_command": "cargo test",
  "worker_claude_args": []
}
```

### Task brief

`tasks/001-<slug>.md` — the skill (LLM) writes these files directly as prose. `agentrc run create` creates the directory structure; `agentrc spawn` parses the frontmatter:

```markdown
---
id: "001"
slug: add-login-endpoint
classification: writer
worktree: .orchestrator/active/worktrees/001
base_branch: main
branch: orc/001-add-login-endpoint
pane_id: null
depends_on: []
created_at: 2026-04-11T14:30:00Z
---

# Task 001: Add login endpoint

## Scope
...

## Test plan
...

## Acceptance criteria
...

## Out of scope
...

## Notes for worker
...
```

`pane_id` starts null, filled by `agentrc spawn`.

### Status JSON

`status/001.json` — written exclusively by `agentrc worker status`:

```json
{
  "id": "001",
  "pane_id": "%12",
  "state": "in_progress",
  "phase": "implementing",
  "started_at": "2026-04-11T14:31:02Z",
  "updated_at": "2026-04-11T14:45:18Z",
  "last_message": "Tests passing, starting refactor pass",
  "result_path": null,
  "branch": "orc/001-add-login-endpoint",
  "redispatch_count": 0
}
```

State values: `spawning` → `ready` → `in_progress` → `blocked` → `completed` | `failed` | `aborted`.

### Resume context

Output of `agentrc resume`, structured for LLM ingestion:

```
=== AGENTRC ACTIVE RUN ===
Run: 2026-04-11T14-30-auth-refactor
Plan: .orchestrator/active/plan.md
Config: base_branch=main, test_command="cargo test"

=== TASK STATUS ===
001 add-login-endpoint  writer  completed  pane=%12
002 add-signup-flow     writer  in_progress  pane=%14  phase=implementing
003 review-auth-deps    reader  completed  pane=%16

=== RECENT LOG (last 20 lines) ===
[2026-04-11T14:45:00Z] Integrated 001 — tests green
[2026-04-11T14:45:30Z] Waiting on 002, 003
...

=== STALE HEARTBEATS ===
(none)

=== BLOCKED TASKS ===
(none)
```

## Worker lifecycle

Five stages: spawn → seed → run → report → teardown.

### 1. Spawn

Driven by `agentrc spawn <task-id>`. Deterministic sequence:

1. Read task brief from `active/tasks/<id>-<slug>.md`, parse frontmatter.
2. Writer → `git worktree add <path> -b <branch> <base_branch>`. Fail loudly on errors.
3. Reader → skip worktree creation; worker operates in project root with read-only discipline enforced by prompt.
4. Find target tmux window: count panes in current workers window. If full (`workers_per_window`), create new window (`workers-2`, etc.). If none exist, create `workers-1`.
5. Create pane: `tmux split-window -h -P -F '#{pane_id}' -t <target>`. Capture pane ID.
6. Retile: `tmux select-layout tiled`.
7. Write pane ID into task brief frontmatter and initial status (`state: spawning`).
8. `cd` the pane to worktree (writer) or project root (reader) via `send-keys`.
9. Launch via `send-keys`: `agentrc worker heartbeat --task 001 & HB=$!; claude; kill $HB 2>/dev/null; exit`.
10. Seed the bootstrap prompt via `send-keys` after a brief wait.

### 2. Seed

Single `send-keys` injection. Generated from `worker-seed.txt` template with substitutions. Tells the worker:

- Its task ID and where to find its brief.
- To use `agentrc worker *` commands exclusively for all interaction with `.orchestrator/`.
- TDD contract for writers (invoke `superpowers:test-driven-development`, follow rigorously).
- Stay in your worktree (writer) / don't modify files (reader).
- How to signal completion (`agentrc worker done`).
- How to signal being blocked (`agentrc worker status --state blocked --message "..."`).

### 3. Run

Worker reads its brief, calls `agentrc worker status --task 001 --state in_progress`, and executes autonomously. Heartbeat daemon runs in background. Worker uses `agentrc worker note` for progress updates. User can attach and steer at any time.

### 4. Report

Worker calls `agentrc worker done --task 001 --result-file ./result.md`. This atomically:
- Writes the result markdown to `results/001.md`.
- Sets status to `completed` with `result_path`.
- Rings the tmux bell via `tmux wait-for -S worker-001-done`.

Worker sits idle. Does not self-terminate the pane.

### 5. Teardown

Driven by `agentrc teardown <task-id>`. Only runs after successful integration or explicit user request.

1. Writer → `git worktree remove <path>`. Branch is preserved.
2. `tmux kill-pane -t <pane_id>`.
3. Retile remaining workers.
4. If window is now empty of workers, close it.

Only tears down `completed` tasks unless explicitly forced.

## Orchestrator workflow

Five phases: **plan → dispatch → monitor → integrate → report**.

### Mental model

The orchestrator (Claude Code session) is not a daemon. It runs synchronously with the user — the "monitor" phase is "check status when the user sends a message or when I decide to self-check before my next action." Workers run asynchronously in their panes; the orchestrator runs turn-by-turn.

If the user walks away for 10 minutes while 4 workers run, the workers keep going, but the orchestrator does nothing until the user returns. This is the correct model for active steering.

### Phase 1: PLAN

Triggered when the user gives the orchestrator a goal.

1. Classify task type (greenfield / feature / debug / refactor / hybrid).
2. Gather context: Task tool's Explore subagent for quick looks, reader workers for deep investigation.
3. Brainstorm if needed: invoke `superpowers:brainstorming` internally.
4. Plan: invoke `superpowers:writing-plans` to produce a task graph — a DAG of tasks with dependencies, classifications, test plans.
5. **Hard gate: user approves the plan.** No workers spawn until approval. Approved plan written to `runs/<id>/plan.md`.

### Phase 2: DISPATCH

Triggered by plan approval.

1. `agentrc run create --slug <name>` — creates run directory and `active` symlink.
2. Topological sort the task graph.
3. Skill writes all task briefs to `runs/<id>/tasks/`.
4. Spawn every task with no unresolved dependencies (up to `max_workers`).
5. For each spawn: `agentrc spawn <task-id>` handles pane creation, worktree setup, claude launch, and seed injection.
6. Transition to MONITOR.

### Phase 3: MONITOR

Triggered by user interaction or orchestrator self-check. On each pass:

1. `agentrc status` for the full picture.
2. Check heartbeats: any `.alive` file older than `heartbeat_timeout_sec` is stale.
3. Completed task → dispatch its dependents if now unblocked. All tasks done → INTEGRATE.
4. Blocked task → surface to user with `last_message` and notes pointer.
5. Stale worker → surface to user, no auto-kill.
6. Everything healthy → brief report, wait for next interaction.

### Phase 4: INTEGRATE

Triggered when all writer tasks report `completed` or user says "integrate now."

Serial merge in topological order:

1. `git checkout <base_branch>` in project root.
2. Run test suite once to capture pre-existing failures (baseline).
3. For each writer task in order:
   - `git merge --no-ff <worker_branch>`.
   - **Conflict:** `git merge --abort`. Update task brief with conflict addendum. `send-keys` ping to worker. Set status back to `in_progress` with `phase: resolving-conflict`. Increment `redispatch_count`.
   - **Success:** run test suite.
     - **Green** (or only pre-existing failures): advance to next task.
     - **New failures:** `git reset --hard HEAD~1`. Update brief with test-failure addendum. Redispatch. Same loop guard.
   - **TDD review:** surface the worker's commit history to the orchestrator. LLM judges whether TDD was followed. Options: accept, redispatch with TDD addendum.
4. **Loop guard:** max `max_redispatch_attempts` (default 2) per task. On exceeding: pause and surface to user.
5. Reader results aggregated into final report.
6. Transition to REPORT.

### Phase 5: REPORT

Final summary:

- Task table: IDs, slugs, states, final commit hashes.
- Test status per merge step.
- Worker-flagged followups.
- Pointers to `runs/<run-id>/` artifacts.
- Cleanup offer: "Tear down workers and remove worktrees? (y/n)" — teardown is never automatic.

### Pause / resume / abort

- **Pause:** user gives other work. Workers keep running. Orchestrator stops monitoring.
- **Resume:** user says "status" / "continue" / starts new session + `agentrc resume`.
- **Abort one:** `agentrc teardown <id>`. Dependents marked blocked.
- **Abort all:** `agentrc teardown --all`. Archive the run. Report what was lost.

## Error handling

Each failure class: trigger → auto action → surface to user → loop guard.

### Worker-side failures

| Failure | Action | Loop guard |
|---|---|---|
| `state: failed` | Keep pane alive, surface immediately | No auto-retry |
| Stale heartbeat | Mark stale in status view, surface to user | No auto-kill |
| Pane vanishes (status not completed/failed) | Mark `aborted`, surface with salvage options | No auto-respawn |

### Integration-side failures

| Failure | Action | Loop guard |
|---|---|---|
| Merge conflict | Abort merge, redispatch with conflict addendum | 2 attempts → pause |
| Test failure post-merge | Revert merge, redispatch with test output | 2 attempts → pause |
| TDD concern | Surface commit history, LLM judges | Orchestrator decides |
| No test command detected | Log warning, skip verification, flag in report | — |

### Orchestrator-side failures

| Failure | Action | Loop guard |
|---|---|---|
| Binary non-zero exit | Abort current action, log raw error, surface | — |
| Context overflow / new session | `agentrc resume` for cold pickup | — |
| Malformed JSON/frontmatter | Don't act on file, surface parse error | No auto-correction |

### Environmental failures (pre-dispatch)

| Failure | Action | Loop guard |
|---|---|---|
| Dirty base branch | Abort dispatch entirely, surface options | — |
| Worktree/branch collision | Skip that task's spawn, continue others, surface | — |

### Retry loop guard summary

| Failure | Auto-retry | Loop guard | Fallback |
|---|---|---|---|
| Worker `state: failed` | No | — | Surface immediately |
| Merge conflict | Yes (redispatch) | 2 attempts | Pause, surface |
| Test failure post-merge | Yes (revert + redispatch) | 2 attempts | Pause, surface |
| TDD concern | LLM decides | — | Surface, user decides |
| Stuck / stale heartbeat | No | — | Surface, ask user |
| Plumbing error | No | — | Surface raw |
| Environmental failure | No | — | Abort dispatch, surface |
| State corruption | No | — | Surface parse error |

## Testing strategy

### Scope

We test the agentrc framework itself. Workers' own TDD discipline is enforced by the workflow contract, not tested by this test suite.

The `agentrc` binary itself is built with rigorous TDD: red → green → refactor for every feature. E2e tests validate integration paths.

### Layer 1 — Unit and integration tests

Fast, deterministic, run on every change (`cargo test`).

- Pure logic: task graph parsing, cycle detection, status aggregation, config deserialization, frontmatter parsing.
- Filesystem integration tests using `tempfile` for `.orchestrator/` layout operations.
- Git integration tests using temporary repos.
- Worker CLI subcommands: verify correct JSON output, timestamped note appends, state transition validation.
- Heartbeat: interval accuracy, parent-process-death cleanup.
- Fault injection via `mock-worker.sh` — simulates a claude session (reads brief, calls `agentrc worker *` commands). Only `.sh` file in the repo; test fixture, not production code.

### Layer 2 — Smoke tests

Slow, real, run manually or pre-release (`cargo test -- --ignored`).

- Real `claude` sessions in a sandbox tmux session against `tests/fixtures/toy-project/`.
- Happy path: single writer.
- Happy path: two parallel writers, independent tasks.
- Happy path: reader + writer mix.
- Conflict resolution: two writers touch same file, redispatch fires, resolution succeeds.

Costs tokens. Run before releasing, not on every change.

### Layer 3 — Fault injection

Integrated with Layer 1 using sabotage flags on mock-worker. Exercises every error path in the retry-loop-guard table.

### Not tested

- Real Claude output quality (not the framework's concern).
- Worker code correctness (TDD at worker level).
- tmux and git themselves (trusted dependencies).
- `superpowers:*` skills (trusted dependencies).

## Crate dependencies

- `clap` (derive) — CLI
- `serde` + `serde_json` + `serde_yaml` — data schemas, frontmatter
- `anyhow` — application errors in `main.rs`
- `thiserror` — typed library errors in modules
- `duct` — subprocess ergonomics (git, tmux shell-outs)
- `chrono` — timestamps
- `tempfile` — test fixtures
- `notify` — Phase 2 optional, filesystem watching

Estimated size at Phase 2 complete: 2000-3000 lines.

## Skill installation

`agentrc install` creates a symlink:

```
<repo>/skill/agentrc/ → ~/.claude/skills/agentrc/
```

Claude Code auto-discovers skills from `~/.claude/skills/<name>/SKILL.md`. The symlink means `git pull` on the repo automatically updates the installed skill.

The install command also verifies:
- `claude` CLI is available.
- `tmux` is available.
- Symlink target is healthy (idempotent — recreates if broken).

## Open items

- Worker-seed prompt template needs iteration with real workers.
- Test command auto-detection heuristics need validation against multiple project types.
- `agentrc resume` output format may need tuning based on real session-recovery experience.
- Phase 2 scope is intentionally loose — prioritize based on Phase 1 learnings.
