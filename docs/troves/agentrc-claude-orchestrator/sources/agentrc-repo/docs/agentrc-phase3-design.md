# Phase 3 — Dashboard & Resilience

## Overview

Phase 3 adds four features to agentrc in two parallel tracks, plus a project README.

**Track A (Visual):** Agent state detection + ratatui interactive dashboard.
**Track B (Resilience):** Checkpoint save/restore + auto-respawn.
**Standalone:** Project README.

### Motivation

Phase 2 was the first real dogfood run. It surfaced three gaps:
1. The orchestrator has limited visibility into what workers are actually doing.
2. If the session dies, there's no way to resume — you start over.
3. Dead workers require manual detection and re-dispatch.

The dashboard replaces the simple refresh-loop status pane with a rich interactive TUI. Checkpoints and respawn make the framework resilient to crashes and session loss.

### Dependencies on Prior Work

All Phase 2 features are merged. Key foundations:
- `agentrc status` / `agentrc status --json` — data source for dashboard
- `agentrc teardown --force` — used by respawn to kill old panes
- `agentrc amend` — exposed as dashboard action
- `agentrc integrate --dry-run` — exposed as dashboard action
- `agentrc watch` — superseded by the dashboard (may be removed or kept as non-TUI fallback)

---

## Feature 1: Agent State Detection

### Module: `src/detect/`

Passive inference of worker state by parsing tmux pane scrollback output.

### Interface

```rust
pub enum DetectedState {
    Thinking,       // LLM is generating
    ToolUse,        // reading/writing/editing files
    Running,        // executing a shell command
    Idle,           // waiting at prompt, no activity
    NeedsInput,     // permission prompt or question
    RateLimited,    // hit API limits
    Errored,        // crash/error in output
    Dead,           // pane no longer exists
    Unknown,        // couldn't determine
}

/// Capture last N lines of a tmux pane and infer state.
pub fn scan_pane(pane_id: &str, lines: u32) -> Result<DetectedState>;
```

### Detection Rules

Pattern matching on captured scrollback, applied in priority order:

| Priority | Pattern | State |
|---|---|---|
| 1 | Pane dead / tmux error on capture | `Dead` |
| 2 | `Do you want to proceed?` / `Yes, allow` / `permission` | `NeedsInput` |
| 3 | `rate limit` / `429` / `overloaded` | `RateLimited` |
| 4 | `Error` / `panic` / `SIGTERM` / `SIGSEGV` | `Errored` |
| 5 | `Precipitating` / `thinking` / `Thinking` | `Thinking` |
| 6 | `Reading` / `Writing` / `Editing` / `Edit` | `ToolUse` |
| 7 | `running` / `Bash(` / `cargo` / `npm` | `Running` |
| 8 | Claude prompt `>` at end of output, no spinner | `Idle` |
| 9 | Fallback | `Unknown` |

Rules are case-insensitive substring matches on the last 30 lines. First match wins.

### Active Self-Reporting Extension

Extend `agentrc worker status` with optional fields:

```
agentrc worker status --task 001 --state in_progress \
  --phase "writing tests" \
  --tokens 12400 \
  --message "implementing topo_sort"
```

New field on `TaskStatus` (backward-compatible with `#[serde(default)]`):
- `token_usage: Option<u64>` — cumulative tokens, self-reported

The `DetectedState` from passive scanning lives only in the TUI's in-memory `App` state — it is NOT added to `TaskStatus` or persisted to disk. The dashboard maps `task_id -> DetectedState` on each refresh tick.

### Tmux Wrapper Addition

```rust
impl Tmux {
    /// Capture last N lines of pane scrollback as a string.
    pub fn capture_pane(&self, pane_id: &str, lines: u32) -> Result<String>;
}
```

Calls: `tmux capture-pane -t <pane_id> -p -S -<lines>`

---

## Feature 2: Ratatui Dashboard

### Command: `agentrc dashboard`

Launches an interactive terminal UI in the current terminal. Replaces the old `dashboard setup`/`live`/`menu` subcommands.

The orchestrator session splits a pane and runs `agentrc dashboard` in it. The TUI consumes the full pane.

### New Dependencies

```toml
ratatui = "0.29"
crossterm = "0.28"
tui-scrollview = "0.4"
tui-input = "0.11"
```

### Screen Layout

```
+--------------------------------------------------+
| agentrc * run: 20260412-phase3 * 4/6 active      | <- Header
+--------------------------------------------------+
| ID  STATE       ACTIVITY  TOKENS ELAPSED  BRANCH | <- Worker Table
|>001 in_progress * think   12.4k  3m 21s   ok     |    (scrollable,
| 002 in_progress @ tool     8.1k  3m 18s   ok     |     selectable)
| 003 completed   - idle        -  5m 02s   ok     |
| 004 in_progress ! input       -  2m 44s   WARN   |
| 005 in_progress * think   15.2k  3m 20s   ok     |
| 006 failed      x dead        -  1m 12s   FAIL   |
+--------------------------------------------------+
| 001 plan-validate | orc/001-plan-validate         | <- Detail Bar
| Phase: writing tests | Pane: %28 | HB: 3s ago    |    (selected row)
| Last: "implementing topo_sort extraction"         |
+--------------------------------------------------+
| up/dn select  z zoom  t teardown  r respawn       | <- Key Hints
| a amend  i integrate  c checkpoint  q quit        |
+--------------------------------------------------+
```

### Three Regions

**Header:** Run ID, summary counters (N active, N done, N failed), heartbeat health ratio. Single line, always visible.

**Worker Table:** One row per task. Columns:

| Column | Source | Format |
|---|---|---|
| ID | status JSON `id` | "001" |
| STATE | status JSON `state` | colored text |
| ACTIVITY | passive detection `DetectedState` | icon + short label |
| TOKENS | status JSON `token_usage` | "12.4k" or "-" |
| ELAPSED | `started_at` to now | "3m 21s" |
| BRANCH | git branch check | "ok" / "WARN" / "FAIL" |

Activity icons:
- `*` Thinking
- `@` ToolUse
- `$` Running
- `-` Idle
- `!` NeedsInput (highlighted/blinking)
- `~` RateLimited
- `x` Dead/Errored
- `?` Unknown

Scrollable via arrow keys. Selected row highlighted. Cursor wraps.

**Detail Bar:** Expanded info for the cursor row. Shows: full slug, branch name, current phase, pane ID, heartbeat age, last message. 2-3 lines.

**Key Hints:** Contextual — shows available actions for the selected worker's state.

### Keyboard Actions

| Key | Action | Guard |
|---|---|---|
| `up`/`k`, `down`/`j` | Navigate table | Always |
| `z` | Zoom — attach to worker's tmux pane | Pane alive |
| `t` | Teardown selected worker | Confirmation prompt |
| `r` | Respawn selected worker | Task in_progress/failed, branch exists |
| `a` | Amend — prompt for message text | Task has pane |
| `i` | Integrate all completed branches | Any completed tasks |
| `c` | Checkpoint save | Active run |
| `s` | Cycle sort order (ID / state / elapsed) | Always |
| `?` | Toggle help overlay | Always |
| `q` | Quit TUI | Always |

Actions that shell out (teardown, respawn, integrate) temporarily exit the TUI, run the command, then re-enter. This avoids fighting over terminal control.

### Refresh Strategy

- Status JSON + passive detection scan: every 3 seconds
- Heartbeat file mtime check: every 5 seconds
- Branch existence check: every 30 seconds (expensive git operation)
- Keyboard input: immediate (crossterm event polling)

### Module Structure

```
src/tui/
  mod.rs        — pub exports
  app.rs        — App state struct, main event loop
  event.rs      — crossterm event reader + tick timer
  ui.rs         — render() draws all regions
  widgets/
    header.rs   — header bar
    table.rs    — worker table
    detail.rs   — detail bar for selected worker
    help.rs     — help overlay
  action.rs     — dispatch keyboard actions to agentrc commands
```

### Migration from Old Dashboard

The old `dashboard setup`/`live`/`menu` subcommands are removed. `agentrc dashboard` launches the TUI directly. The `agentrc dashboard setup` workflow (split pane + launch) moves into the orchestrator skill — the skill tells the orchestrator LLM to split a pane and run `agentrc dashboard` in it.

---

## Feature 3: Checkpoint Save/Restore

### Command: `agentrc checkpoint save [-m "description"]`

Captures run state to `.orchestrator/active/checkpoints/<timestamp>.json`.

### Checkpoint Schema

```json
{
  "id": "20260412T104500",
  "description": "before integration",
  "created_at": "2026-04-12T10:45:00Z",
  "run_id": "20260412T094228-phase3",
  "base_branch": "master",
  "base_commit": "fe68ffb",
  "tasks": [
    {
      "id": "001",
      "slug": "plan-validate",
      "state": "in_progress",
      "branch": "orc/001-plan-validate",
      "branch_exists": true,
      "branch_commit": "b95532b",
      "commits_ahead": 1,
      "pane_alive": true,
      "classification": "writer"
    }
  ],
  "config_snapshot": {}
}
```

Per-task state captured:
- Status state from JSON
- Branch existence and HEAD commit
- Commits ahead of base branch
- Whether the tmux pane is still alive
- Classification (reader/writer)

### Restore: `agentrc checkpoint restore [id] [--respawn]`

1. Read checkpoint JSON (latest if no ID specified)
2. Validate run directory exists and is active
3. For each task, check current branch state:
   - Branch exists + commits ahead → **Recoverable**
   - Branch exists + no commits → **Empty**
   - Branch missing → **Lost**
4. Print recovery report:
   ```
   Checkpoint: 20260412T104500 — "before integration"
   Base: master @ fe68ffb

   ID   STATE        BRANCH                    RECOVERY
   001  in_progress  orc/001-plan-validate     ok (1 commit)
   002  completed    orc/002-amend-command      ok (2 commits)
   003  in_progress  orc/003-collate-layout     ok (1 commit)
   004  in_progress  orc/004-smart-integrate    LOST (branch missing)
   005  completed    orc/005-rich-status        ok (1 commit)
   006  failed       orc/006-notify-watch       empty (no commits)
   ```
5. If `--respawn`: auto-call `agentrc respawn` for each task that was `in_progress` and is recoverable.

### List: `agentrc checkpoint list`

Lists all checkpoints for the active run with ID, timestamp, description, and task count.

### Storage

New subdirectory in run scaffold: `.orchestrator/active/checkpoints/`. Added to `RunPaths`:
- `checkpoints_dir() -> PathBuf`
- `checkpoint_file(id) -> PathBuf`

---

## Feature 4: Auto-Respawn

### Command: `agentrc respawn <task-id>`

Re-launches a dead or failed worker, preserving its branch state.

### Sequence

1. **Validate state:** Task must be `in_progress`, `failed`, or `aborted`. Error on `completed` or `spawning`.
2. **Check branch:** `orc/<id>-<slug>` must exist. Count commits ahead of base. Error if branch missing.
3. **Kill old pane:** If `pane_id` in status and pane is alive, kill it.
4. **Check redispatch limit:** `redispatch_count >= max_redispatch_attempts` → error. Increment on success.
5. **Re-create worktree:** Remove old worktree if exists. `git worktree add` from the **existing branch** (not base — preserves commits).
6. **Generate resume seed:**
   ```
   You are worker {task_id} resuming work. Your task brief is at {brief_path}.
   Your branch orc/{id}-{slug} has {N} commits already. Read the brief
   AND review your existing commits (git log --oneline) to understand
   where the previous session stopped. Continue from there.
   Use `agentrc worker status --task {id} --state in_progress` to signal
   you've resumed. Use `agentrc worker done --task {id}` when finished.
   ```
7. **Launch pane:** New tmux pane, export `AGENTRC_PROJECT_ROOT`, cd to worktree, heartbeat daemon, `claude --dangerously-skip-permissions` with resume seed.
8. **Update status:** Set state to `spawning`, update `pane_id`, increment `redispatch_count`.

### Key Difference from Spawn

- Worktree created from existing branch (preserving commits), not from base
- Seed prompt tells worker to read its own git log
- Status `redispatch_count` incremented, not reset

### Dashboard Integration

The `r` key in the TUI calls `respawn::run()` for the selected worker. Available when selected task is `in_progress`, `failed`, or `aborted` and branch exists.

---

## Feature 5: README

### File: `README.md` (project root)

Creates a new file — no code changes to the binary.

### Sections

1. **Title + one-liner** — "agentrc — Orchestrate multiple Claude Code workers in tmux panes"
2. **What it does** — 4-5 bullets: parallel workers in tmux, git worktree isolation, TDD enforcement, interactive dashboard, checkpoint/resume
3. **Quick start** — Install, init, create run, write briefs, spawn workers, launch dashboard
4. **Command reference** — grouped table: orchestrator commands, worker commands, run management, dashboard
5. **Architecture** — two-layer model (skill + binary), filesystem coordination, worktree isolation. Brief, with pointer to `docs/agentrc-implementation-spec.md` for details.
6. **Configuration** — `.orchestrator/config.json` fields with defaults
7. **Requirements** — Rust toolchain, tmux, claude CLI, git
8. **Screenshots** — placeholder section ("Screenshots coming soon — imagine 6 Claude Code workers humming away in tiled tmux panes with a ratatui dashboard tracking progress")

---

## Task Decomposition

### Track A (Visual) — depends on each other, serial within track

| Task | Slug | Classification | Depends On |
|---|---|---|---|
| 001 | detect-state | writer | — |
| 002 | ratatui-dashboard | writer | 001 |

### Track B (Resilience) — depends on each other, serial within track

| Task | Slug | Classification | Depends On |
|---|---|---|---|
| 003 | checkpoint | writer | — |
| 004 | auto-respawn | writer | 003 |

### Standalone

| Task | Slug | Classification | Depends On |
|---|---|---|---|
| 005 | readme | writer | — |

### Parallelism

Track A and Track B run in parallel. README runs in parallel with both. Maximum 3 concurrent workers (001, 003, 005), then 2 (002, 004) after deps complete.

### Integration Order

1. 005-readme (no code conflicts)
2. 001-detect-state (new module, minimal main.rs touch)
3. 003-checkpoint (new command, touches main.rs)
4. 002-ratatui-dashboard (heaviest, replaces dashboard.rs, touches main.rs)
5. 004-auto-respawn (new command, touches main.rs + spawn.rs)

### Merge Risk

- 002 (dashboard) and 004 (respawn) both touch `main.rs` — integrate dashboard first
- 002 replaces `src/commands/dashboard.rs` entirely — no partial merge issues
- 001 adds a new module `src/detect/` — clean addition, no conflicts
