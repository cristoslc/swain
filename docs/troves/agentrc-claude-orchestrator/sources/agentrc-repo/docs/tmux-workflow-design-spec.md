# tmux-teams — Design Spec

**Date:** 2026-04-11
**Status:** Draft, pending user review
**Working name:** `tmux-teams` (rename-friendly)

## Purpose

A unified meta-framework for building software with an LLM orchestrator (Claude Code) that kicks off specialized subagent workers in visible, interactive tmux panes. The human operator can observe every worker live, attach to any pane to redirect a worker in natural language, and trust that orchestration, merging, and integration are handled deterministically by a small Rust binary that complements the orchestrator's reasoning.

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
- **Orchestrator is the user's current Claude Code session.** The orchestrator is a reasoning layer invoked via the `tmux-teams` skill, not a separate process.
- **Workers are full `claude` instances.** They inherit every tool, skill, and MCP server the user has installed. They can dispatch their own Task-tool subagents.
- **Writer isolation via git worktrees.** Each writer task gets its own worktree on its own branch. Readers share the project root, read-only.

## Architecture

Two layers, cleanly separated:

1. **Skill layer (`skill/SKILL.md`)** — a superpowers-style skill installed into `~/.claude/`. Encodes the *workflow*: how to plan, decompose, dispatch, monitor, integrate, and report. Prose directives the orchestrator (LLM) follows. No executable code.

2. **Ops binary (`tmux-teams` Rust crate)** — a single compiled binary that handles all deterministic mechanics: creating panes, spawning workers, managing git worktrees, aggregating status, merging branches, detecting TDD violations, etc. Called by the orchestrator via the Bash tool. Single source of truth for "what happens when X."

There is **no bash layer**. Every piece of plumbing lives in the Rust binary.

### Division of responsibility

| Concern | Layer |
|---|---|
| Deciding what to do | Skill (LLM reasoning) |
| Writing task briefs and plans | Skill (LLM reasoning) |
| Classifying reader vs writer | Skill (LLM reasoning, user can override) |
| Spawning panes and worktrees | Rust binary (`tmux-teams spawn`) |
| Aggregating status | Rust binary (`tmux-teams status`) |
| Heartbeat daemon | Rust binary (`tmux-teams heartbeat`) |
| Integration merges and conflict handling | Rust binary (`tmux-teams integrate`) |
| TDD enforcement during integration | Rust binary (`tmux-teams integrate --verify-tdd`) |
| Teardown | Rust binary (`tmux-teams teardown`) |
| Layout / collation across windows | Rust binary (`tmux-teams layout`) |
| Reacting to failures | Skill (LLM reasoning) based on binary's reports |

### Key invariants

1. **The orchestrator never writes directly to a worker's worktree.** Workers own their worktrees. Orchestrator only reads them at integration time.
2. **Workers never write outside `.orchestrator/` or their own worktree.** Enforced by prompt discipline, not filesystem permissions.
3. **Authoritative status is file-based.** Worker → `.orchestrator/runs/<id>/status/<task>.json`. No `tmux capture-pane` parsing for status.
4. **Heartbeats are advisory.** A stuck worker surfaces in the user's status view. There is no automatic kill or respawn.
5. **Task briefs include pane ID.** Workers self-identify for logging and heartbeat filenames.
6. **One narrow exception to "no mid-task send-keys."** Conflict redispatch pings the worker with `send-keys` after updating the task brief file. Both are used; the file is the source of truth, the ping is a prompt to re-read.
7. **Teardown is never automatic.** A completed worker sits idle until explicitly torn down by the orchestrator or the user.
8. **TDD is enforced at integration time.** A writer worker whose git history shows implementation commits without preceding failing-test commits is flagged. Phase 2 binary enforces this mechanically; Phase 1 surfaces a warning.

## Phasing

Phasing is **feature progression within a single Rust codebase**, not a language migration.

### Phase 1 — MVP

Subcommands in scope:

- `tmux-teams init` — create `.orchestrator/` scaffold in the current project
- `tmux-teams spawn <task-id>` — create pane, worktree (if writer), launch claude, seed bootstrap prompt
- `tmux-teams teardown <task-id>` — close pane, remove worktree, archive artifacts
- `tmux-teams heartbeat --pane-id <id> [--interval 30s]` — background daemon that touches the heartbeat file and exits cleanly on parent death
- `tmux-teams status` — aggregate all runs' status files into a structured table (JSON or TTY-friendly)
- `tmux-teams layout [tile|collate]` — tile current workers window, collate overflow to new windows
- `tmux-teams integrate` — serial merge in dependency order, auto-redispatch on first conflict, pause on second
- Basic conflict handling (redispatch with addendum, max 2 attempts)
- Basic test-failure handling (auto-revert + redispatch, same loop guard)
- Basic `state: failed` surfacing

### Phase 2 — hardened

Additions to the same binary:

- `tmux-teams plan validate` — task graph validation with cycle detection
- Smarter integration: 3-way merge heuristics, test-aware rollback
- Enforced TDD violation detection (not just warning)
- Task amend flow: `tmux-teams amend <task-id> --from-brief`
- `notify`-based filesystem watching instead of polling (optional)
- Richer status reporting with estimated completion times
- Resumable runs across orchestrator session boundaries

## Directory layout

### Repository layout

```
tmux-teams/                        # top-level repo
  skill/
    SKILL.md                       # prose workflow directives installed into ~/.claude/
    templates/
      worker-seed.txt              # bootstrap prompt template
      task-brief.md                # task brief template with frontmatter
  Cargo.toml                       # Rust crate at repo root
  src/
    main.rs                        # clap CLI entry
    commands/
      init.rs
      spawn.rs
      status.rs
      heartbeat.rs
      teardown.rs
      integrate.rs
      layout.rs
      plan.rs                      # Phase 2
    model/
      task.rs                      # Task, TaskGraph, TaskStatus types
      worker.rs                    # Worker, PaneId, WorkerState
      config.rs                    # OrchestratorConfig
      error.rs                     # AppError, Result alias
    fs/
      bus.rs                       # read/write .orchestrator/ layout
      run.rs                       # run-scoped dir helpers, active symlink
    git/
      wrapper.rs                   # typed git command wrappers
    tmux/
      wrapper.rs                   # typed tmux command wrappers
  tests/
    happy_path.rs                  # end-to-end with mock worker
    spawn_test.rs
    integrate_test.rs
    fault_injection.rs
    fixtures/
      mock-worker.sh               # simulates a claude session in tests
      toy-project/                 # tiny test repo
  Makefile                         # make test | make smoke | make install
  README.md
```

### Runtime layout (inside each project that uses tmux-teams)

```
<project>/.orchestrator/
  config.json                        # per-project orchestrator config
  active -> runs/<current-run-id>/   # symlink to active run; absent between runs
  runs/
    2026-04-11T14-30-auth-refactor/  # run-id = ISO timestamp + slug
      plan.md                        # approved task graph and rationale
      orchestrator.log               # timestamped orchestrator decisions
      integration.log                # merges, test results, conflicts
      config.json                    # snapshot of config at run start
      tasks/
        001-<slug>.md                # task brief (frontmatter + markdown)
      status/
        001.json                     # live status (worker writes)
      heartbeats/
        pane14.alive                 # zero-byte; mtime is the signal
      notes/
        001.md                       # worker scratchpad
      results/
        001.md                       # worker final report
      worktrees/
        001/                         # git worktree (writer tasks only)
    2026-04-09T10-15-bug-fix-xyz/    # completed runs sit here
      ...
```

### Data schemas

**`.orchestrator/config.json`** — per-project orchestrator config:

```json
{
  "project_root": "/home/eric/Code/foo",
  "base_branch": "main",
  "workers_per_window": 4,
  "heartbeat_timeout_sec": 120,
  "max_redispatch_attempts": 2,
  "worker_claude_args": [],
  "test_command": null
}
```

`test_command` is optional; if null, the binary auto-detects from `package.json`, `Cargo.toml`, `pyproject.toml`, etc.

**Task brief** — `runs/<id>/tasks/<task-id>-<slug>.md`:

```markdown
---
id: 001
slug: add-login-endpoint
classification: writer
worktree: .orchestrator/active/worktrees/001
base_branch: main
branch: orc/001-add-login-endpoint
pane_id: "%12"
depends_on: []
created_at: 2026-04-11T14:30:00Z
---

# Task 001: Add login endpoint

## Scope
Add POST /auth/login to the existing Express API...

## Test plan
- POST /auth/login with valid creds → 200, JWT in body
- POST /auth/login with wrong password → 401
- POST /auth/login with missing email → 400
- JWT secret read from env, not hardcoded

## Acceptance criteria
- [ ] Endpoint accepts {email, password}
- [ ] Returns JWT on success
- [ ] Tests pass

## Out of scope
- Password reset flow
- Email verification

## Notes for worker
You are pane %12. Heartbeat every 30s. Progress → notes/001.md.
Result → results/001.md. Set status.json state to "completed" when done.
```

The `test_plan` section is new and mandatory for writer tasks under the TDD invariant.

**Worker status** — `runs/<id>/status/<task-id>.json`:

```json
{
  "id": "001",
  "pane_id": "%12",
  "state": "in_progress",
  "phase": "implementing",
  "started_at": "2026-04-11T14:31:02Z",
  "updated_at": "2026-04-11T14:45:18Z",
  "last_message": "Wrote handler, tests passing, starting refactor pass",
  "result_path": null,
  "branch": "orc/001-add-login-endpoint",
  "redispatch_count": 0
}
```

State values: `spawning` → `ready` → `in_progress` → `blocked` → `completed` | `failed` | `aborted`.

**Heartbeat** — `runs/<id>/heartbeats/pane<N>.alive`: zero-byte file. Mtime is the signal. Worker touches every 30s via the `tmux-teams heartbeat` daemon.

**Worker result** — `runs/<id>/results/<task-id>.md`: free-form markdown with a standard skeleton (Summary / Changes / Tests / Notes for integration / Followups).

**Notes** — `runs/<id>/notes/<task-id>.md`: free-form scratchpad, worker appends as it works, orchestrator reads for context.

## Worker lifecycle

Five stages: spawn → seed → run → report → teardown.

### 1. Spawn

Driven by `tmux-teams spawn <task-id>`. Deterministic sequence:

1. Read the task brief from `runs/<active>/tasks/<id>-<slug>.md`, parse frontmatter.
2. If classification is writer, create the git worktree:
   - `git worktree add <path> -b <branch> <base_branch>`
   - Fail loudly on errors (dirty base, name collision, existing worktree).
3. If classification is reader, skip worktree creation; worker operates in project root with read-only discipline enforced by prompt.
4. Find the target tmux window: query `workers_per_window` from config, count panes in current workers window. If full, create a new one (`tmux new-window -n workers-2`). If no workers window exists, create `workers-1`.
5. Create the pane: `tmux split-window -h -P -F '#{pane_id}' -t <target-window>`. Capture the pane ID.
6. Retile: `tmux select-layout tiled` (configurable).
7. Write pane ID back into the task brief frontmatter.
8. Write initial status (`state: spawning`).
9. Cd the pane to the worktree (or project root for readers) via `send-keys`.
10. Launch the heartbeat daemon and claude as a single pane startup command via `send-keys`. The command is crafted by the spawn subcommand to handle lifetime correctly: background the heartbeat, run claude in the foreground, kill the heartbeat when claude exits, exit the shell. Pane death at any point propagates SIGHUP and cleans both up. Implementation sketch: `tmux-teams heartbeat --pane-id %14 & HB=$!; claude; kill $HB 2>/dev/null; exit`.
11. Wait briefly for claude to present its prompt.
12. Seed the bootstrap prompt (see next stage).

### 2. Seed

The orchestrator injects the worker's initial prompt via `tmux send-keys`. This is one of two legitimate send-keys uses (the other is conflict redispatch pings). It's safe here because the pane was just created and the user isn't in it yet.

The seed is a compact bootstrap (not the full task brief) that tells the worker where to find its brief and what its operating contract is. Stored as a template at `skill/templates/worker-seed.txt` with substitutions for pane ID, task ID, and task-brief path.

Example seed (simplified):

```
You are a tmux-teams worker. Your pane ID is %14. Your task brief is at
.orchestrator/active/tasks/001-add-login-endpoint.md — read it fully before
doing anything.

Contract:
1. On start, read your task brief and acknowledge in one line to
   .orchestrator/active/notes/001.md.
2. Update .orchestrator/active/status/001.json with state transitions.
3. A heartbeat daemon is running under `tmux-teams heartbeat --pane-id %14`
   in a background process; do not touch it.
4. Append progress notes to .orchestrator/active/notes/001.md liberally.
5. For writer tasks: MANDATORY. Invoke the superpowers:test-driven-development
   skill at the start and follow it rigorously. Red → green → refactor. No
   implementation code without a preceding failing test. Your git history must
   reflect this sequence.
6. When done, write your final report to .orchestrator/active/results/001.md
   and set status.json state to "completed". Optionally signal via
   `tmux wait-for -S worker-001-done`.
7. Writers: all code changes stay in your worktree. Do not touch files outside
   it. Do not merge your branch — orchestrator handles integration.
8. Readers: do not modify any files. Your output is in notes/results only.
9. If stuck or blocked, set state to "blocked" with last_message explaining
   what you need, and wait.
10. You have full Claude Code tooling. Use what helps. You are a junior
    orchestrator of your own work.

Begin by reading your task brief.
```

### 3. Run

Worker reads its brief, acknowledges, sets `state: in_progress`, and executes autonomously. The heartbeat daemon (spawned as a background process at worker start) touches the heartbeat file on its interval. Worker writes progress to notes, updates status at phase transitions, writes code into its worktree (writer) or produces a research report (reader).

The user may attach to any pane at any time and interact with the worker in natural language. The worker's contract permits this — it accepts both task brief updates and direct input as legitimate redirection.

### 4. Report

When the worker believes it's done:

1. Write `results/<id>.md` with summary, changes, test output, followups.
2. For writers: ensure all work is committed on the branch inside the worktree. Workers commit their own code with their own messages (worker-owned commit granularity and attribution).
3. Update status to `completed`, set `result_path`.
4. Optionally ring the completion bell: `tmux wait-for -S worker-<id>-done`.
5. Kill the heartbeat daemon (or let it die naturally on pane exit).
6. Print the completion banner:

```
─────────────────────────────────────────
 TASK 001 COMPLETE — awaiting orchestrator teardown
 Status: .orchestrator/active/status/001.json
 Result: .orchestrator/active/results/001.md
─────────────────────────────────────────
```

7. Sit idle. Do **not** self-terminate the pane.

### 5. Teardown

Driven by `tmux-teams teardown <task-id>`. Only runs after successful integration or explicit user request.

1. Archive the worker's artifacts (they already live under `runs/<id>/` — nothing to move; the run directory is the archive).
2. For writers: `git worktree remove <path>`. Branch is preserved.
3. `tmux kill-pane -t <pane_id>`.
4. Retile remaining workers.
5. If the window is now empty of workers, close it.

Workers with `state` other than `completed` are not torn down except by explicit user abort.

## Orchestrator workflow

Five phases: **plan → dispatch → monitor → integrate → report**.

### Mental model

The orchestrator (Claude Code session) is not a daemon. It does not have a background event loop. It runs synchronously with the user — the "monitor" phase is really "I check status whenever the user sends me a message, or when I explicitly decide to self-check before the next action I want to take." Workers run asynchronously in their panes; the orchestrator runs turn-by-turn.

Consequence: if the user walks away for 10 minutes while 4 workers are running, the workers keep going, but the orchestrator does nothing until the user returns. The user comes back, says "status?", and the orchestrator reads state files and reports. This is the correct model for active-steering — the user is always in the loop.

### Phase 1: PLAN

Triggered when the user gives the orchestrator a goal.

1. Classify the task type (greenfield / feature / debug / refactor / hybrid).
2. Gather context:
   - **Quick look:** Task tool's Explore subagent (no pane, cheap, fast). Use for small-scope context.
   - **Deep investigation:** spawn 1-N reader workers in tmux panes with explicit investigation briefs. Use for multiple independent hypotheses or when investigation should be watched.
3. Brainstorm if design work is needed: invoke `superpowers:brainstorming` internally.
4. Plan: invoke `superpowers:writing-plans` to produce a task graph — a DAG of tasks with dependencies, reader/writer classifications, acceptance criteria, and test plans.
5. **Present the plan to the user for approval. HARD GATE.** No writer workers spawn until the user approves. The approved plan is written to `runs/<id>/plan.md`.

### Phase 2: DISPATCH

Triggered by plan approval.

1. Create the run directory: `runs/<run-id>/` and the `active` symlink.
2. Topological sort the task graph.
3. Write all task briefs to `runs/<id>/tasks/`.
4. Spawn every task with no unresolved dependencies (up to worker-per-window limit, collating across windows as needed).
5. For each spawn: write initial status, call `tmux-teams spawn <task-id>`, capture the pane ID, update the task brief's frontmatter with the pane ID.
6. Transition to MONITOR.

### Phase 3: MONITOR

Triggered by user interaction or orchestrator self-check.

On each monitor pass:

1. Read all status files (or use `tmux-teams status` for a structured table).
2. Check heartbeats: any `.alive` file older than `heartbeat_timeout_sec` is stale.
3. Non-blocking peek of any `tmux wait-for` completion bells.
4. Skim recent notes (files with updated mtimes) for progress context.
5. Decide and act:
   - **Task completed.** If its dependents are now unblocked, dispatch them. If all tasks complete, transition to INTEGRATE.
   - **Task blocked.** Surface to user with last_message and notes pointer; wait for direction.
   - **Worker stale.** Surface to user; no auto-kill.
   - **Everything healthy.** Brief report; wait for next user interaction.

### Phase 4: INTEGRATE

Triggered when all writer tasks report `completed` or the user says "integrate now."

Serial merge in topological order of the task graph:

1. `git checkout <base_branch>` in the project root.
2. Record the pre-merge test state: run the detected test command once, note which tests were already failing. These don't count as regressions.
3. For each writer task in order:
   - `git merge --no-ff <worker_branch>` (configurable to rebase).
   - **On conflict:** `git merge --abort`, update the worker's task brief with a conflict addendum section explaining which files conflicted against which prior task's merge. Send the worker a `send-keys` ping: *"Your task brief has a conflict addendum. Please re-read and re-submit."* Set status back to `in_progress` with `phase: resolving-conflict`. Increment `redispatch_count`. Continue integrating other tasks if they don't depend on the conflicted one.
   - **On merge success:** run the test suite.
     - **Tests green** (or only already-failing tests are red): advance to next task.
     - **Tests newly red:** `git reset --hard HEAD~1` (undo the merge). Update the worker's task brief with a test-failure addendum containing the failing test output. Redispatch (same mechanism as conflict). Increment `redispatch_count`.
   - **TDD violation check:** inspect the worker's git history on its branch. If implementation commits appear without preceding failing-test commits, surface to the user: *"Worker 003 did not follow TDD. Accept anyway or redispatch with TDD addendum?"* Phase 1: surface-only. Phase 2: mechanically enforced by the binary.
4. **Retry loop guard:** max `max_redispatch_attempts` (default 2) redispatches per task. On the third failure, fall back to pause-and-surface: *"Worker 003 has failed to integrate twice. Manual resolution needed."*
5. Reader tasks are aggregated into the final report; they don't produce branches.
6. Transition to REPORT.

### Phase 5: REPORT

Final summary after INTEGRATE (or after user says "we're done"):

- Tasks planned → completed → integrated, as a table with IDs, slugs, states, and final commit hashes.
- Test status per merge step.
- Followups flagged by workers.
- Pointers to `runs/<run-id>/` artifacts.
- Cleanup offer: *"Tear down workers and remove worktrees? (y/n)"* — teardown is never automatic.

### Pause / resume / abort

- **Pause:** user says "pause" or gives other work. Orchestrator stops actively monitoring. Workers keep running.
- **Resume:** user says "status" / "continue" / "back to the tmux-teams run". Orchestrator re-reads state and picks up.
- **Abort one worker:** `tmux-teams teardown <id>`. Dependents are marked blocked; orchestrator asks user for direction.
- **Abort all:** teardown every worker. Archive the run (drop the `active` symlink, leave the run dir in place). Report what was lost.

## Error handling

Each failure class has a consistent shape: trigger, auto action, surface to user, loop guard.

### Worker-side failures

**`state: failed`.** Worker's own diagnosis. Keep pane alive for inspection. Surface to user: "Worker <id> reported failure: <reason>. Options: retry, redispatch, skip, abort run." No auto-retry (retrying without new information is usually pointless).

**Stuck worker (stale heartbeat).** Mtime of heartbeat file older than `heartbeat_timeout_sec`. Mark status view stale. Surface: "Worker <id> hasn't heartbeat'd in <duration>. Peek, kill, or wait?" No auto-kill in active-steering mode.

**Worker process dies (pane vanishes).** Detected on next monitor pass: pane gone, status not `completed`/`failed`. Mark task `aborted`. Surface: "Worker <id>'s pane is gone. Worktree has <N> uncommitted changes. Respawn, salvage, or abandon?" Salvage path: respawn with the same task brief pointed at the existing worktree.

### Integration-side failures

**Merge conflict.** Abort merge, update task brief with conflict addendum, redispatch worker via send-keys ping. Max 2 redispatches per task, then pause-and-surface.

**Test failure post-merge.** `git reset --hard HEAD~1` to undo the merge. Update task brief with test-failure addendum. Redispatch. Same loop guard: max 2 attempts, then pause-and-surface. Tests already failing on base before the run don't count as regressions.

**TDD violation.** Writer's git history shows implementation commits without preceding failing-test commits. Phase 1: surface-only warning, user decides accept/redispatch. Phase 2: mechanically enforced, auto-redispatch with TDD addendum.

**Merge succeeds, no test command detected.** Log "skipping post-merge verification." Continue. Flag in final report.

### Orchestrator-side failures

**Plumbing errors (tmux-teams subcommand non-zero exit).** Abort current action. Log raw error to `orchestrator.log`. Surface in this pane immediately — these are environmental issues (dirty branch, name collision) that need to be seen raw.

**Orchestrator context overflow.** `orchestrator.log` is the persistence mechanism. On recovery in a fresh session: invoke `tmux-teams` skill, point at the active run, read the log and status files, pick up. Worktrees, panes, workers are all still there as external state.

**User interruption (pause / abort / do something else).** Documented above under orchestrator workflow.

### Environmental failures (caught before dispatch)

**Dirty base branch.** `git status --porcelain` check before any worktree creation. Abort dispatch entirely. Surface: "Base branch has uncommitted changes. Commit, stash, or force (not recommended)."

**Worktree/branch name collision.** `git worktree list` + `git branch --list` check per task. Skip that task's spawn, continue others. Surface the collision and options.

### State corruption

**Malformed JSON or frontmatter.** Orchestrator doesn't act on the file. Log parse error. Surface to user. No auto-correction — workflow state is too important to guess at.

### Retry loop guard summary

| Failure | Auto-retry | Loop guard | Fallback |
|---|---|---|---|
| Worker `state: failed` | No | — | Surface immediately |
| Merge conflict | Yes (redispatch) | 2 attempts | Pause, surface |
| Test failure post-merge | Yes (revert + redispatch) | 2 attempts | Pause, surface |
| TDD violation (Phase 2) | Yes (redispatch) | 2 attempts | Pause, surface |
| Stuck / stale heartbeat | No | — | Surface, ask user |
| Plumbing error | No | — | Surface raw |
| Environmental failure | No | — | Abort dispatch, surface |
| State corruption | No | — | Surface parse error |

## Testing strategy

### Scope

We test **the tmux-teams framework itself**. Workers' own TDD discipline is enforced by the workflow contract, not tested by this test suite.

### Layer 1 — unit and integration tests (fast, deterministic, run on every change)

- Pure logic unit tests: task graph parsing, cycle detection, status aggregation, config deserialization, frontmatter parsing.
- Integration tests using `tempfile` for filesystem ops and temporary git repos for git ops.
- Heartbeat subcommand: interval accuracy and parent-process-death signal handling.
- Fault injection via a **mock worker shell script** (`tests/fixtures/mock-worker.sh`) that simulates a claude session — reads its brief, writes progress to notes, touches heartbeats, writes fake results, sets status. Kept as a shell script because "simulate file writes" is exactly what shell is best at; it is a test fixture, not production code.

Run via `cargo test`. Sub-second to few seconds.

### Layer 2 — smoke tests (slow, real, run manually or nightly)

Rust integration tests annotated `#[ignore]`, invoked with `cargo test -- --ignored`. These spawn **real `claude` sessions** in a sandbox tmux session against a toy project in `tests/fixtures/toy-project/`. Minimal set:

1. Happy path, single writer.
2. Happy path, two parallel writers, independent tasks.
3. Happy path, reader + writer mix.
4. Conflict resolution: two writers touch the same file, second merge fails, auto-redispatch fires, rebase succeeds.

Run before releasing a skill update, not on every change. Cost tokens.

### Layer 3 — fault injection

Integrated with layer 1 tests using sabotage flags on the mock worker. Exercises every error path in the retry-loop-guard table above.

### What is NOT tested

- Real Claude output quality (not the framework's concern)
- Worker code correctness (that's TDD at the worker level)
- Tmux and git themselves (trusted dependencies)
- The `superpowers:*` skills (trusted dependencies)

## Crates

- `clap` with `derive` for the CLI
- `serde` + `serde_json` + `serde_yaml` for data schemas and frontmatter parsing
- `anyhow` for application-level errors in `main.rs`
- `thiserror` for typed library errors inside modules
- `duct` for subprocess ergonomics
- `chrono` for timestamps
- `tempfile` for test fixtures
- `notify` (Phase 2, optional) for filesystem watching instead of polling

Estimated size when Phase 2 is complete: 2000-3000 lines.

## Open items

- Worker-seed prompt template needs iteration with real workers.
- Test command auto-detection heuristics need validation against multiple project types.
- Phase 2 TDD enforcement rules need more specification (what exactly counts as "implementation code without preceding failing test" when the worker does partial commits).
- Resumable-run mechanics (Phase 2) need a resume entry point in the skill.
