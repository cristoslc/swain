---
title: "Tmux Pane-Aware Session Naming"
artifact: SPEC-056
track: implementable
status: Active
author: cristos
created: 2026-03-16
last-updated: 2026-03-16
type: enhancement
parent-epic: ""
parent-initiative: ""
linked-artifacts:
  - DESIGN-001
  - SPEC-008
  - SPEC-130
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Tmux Pane-Aware Session Naming

## Problem Statement

The operator runs multiple tmux sessions (one per project), each with panes running TUI agents (Claude Code, opencode, gemini cli, codex, copilot) or interactive shells. Two naming gaps exist:

1. **Cross-pane switching:** When switching between panes that are `cd`'d into different git branches or worktrees, the tmux session and window names stay stale.
2. **TUI agent worktree entry:** When a TUI agent (e.g., Claude Code) enters a worktree via its internal mechanism, the tmux pane's `#{pane_current_path}` doesn't update — it's frozen at the agent's launch directory. The operator loses at-a-glance context for which branch the agent is operating in.

## Design

### Two sources of truth, one naming pipeline

The script `swain-tab-name.sh` resolves git context (project + branch) and renames both the tmux **session** and **window**. Context comes from two sources depending on the trigger:

| Trigger | Source | Mechanism |
|---------|--------|-----------|
| Pane focus change (operator switches panes) | `#{pane_current_path}` — the focused pane's CWD | Per-window `pane-focus-in` hook |
| Agent enters a worktree | Explicit `--path` argument | Agent calls script directly |

### Per-pane state via tmux user option

TUI agents are long-running processes whose pane CWD never changes. To bridge this gap, the script stores the resolved path in a **per-pane tmux user option** `@swain_path`:

```
tmux set-option -p @swain_path "/path/to/worktree"
```

The `pane-focus-in` hook reads `@swain_path` first. If set, it uses that path for git resolution. If unset, it falls back to `#{pane_current_path}`. This means:

- **Shell panes:** No `@swain_path` set → hook uses pane CWD → correct
- **Agent panes after `--path`:** `@swain_path` set → hook uses stored path → correct
- **Agent panes before any `--path`:** No `@swain_path` → hook uses pane CWD (launch dir) → stale but safe (shows original project/branch)

### Hook scope: per-window, not global

The hook is installed per-window (`set-hook -w`) rather than globally (`set-hook -g`). This avoids interfering with other tmux sessions/windows that may have their own naming conventions.

### Project name resolution for worktrees

`git rev-parse --show-toplevel` returns the worktree root, not the main repo root. The script uses `git rev-parse --git-common-dir` instead, which returns the main repo's `.git` directory. The project name is `basename` of its parent.

## External Behavior

**Session start (`--auto`):**
1. Resolves git context from `@swain_path` (if set on current pane) → `$(pwd)` → `#{pane_current_path}` (fallback)
2. Renames both tmux session and window to `{project} @ {branch}`
3. Installs per-window `pane-focus-in` hook
4. Sets `@swain_path` on current pane to the resolved path

**Agent worktree entry (`--path <dir> --auto`):**
1. Sets `@swain_path` on current pane to `<dir>`
2. Resolves git context from `<dir>`
3. Renames both tmux session and window

**Pane switch (hook fires):**
1. Reads `@swain_path` from newly focused pane
2. Falls back to `#{pane_current_path}` if unset
3. Resolves git context and renames session + window

**Reset (`--reset`):**
1. Removes per-window `pane-focus-in` hook
2. Clears `@swain_path` on current pane
3. Restores default tmux automatic-rename behavior

**Non-git directory:** Falls back to `unknown @ no-branch`, exit 0.

## Acceptance Criteria

### Session start (DESIGN-001 Flow 1)

1. **Given** a tmux session with no prior swain naming, **when** an agent calls `swain-tab-name.sh --auto`, **then** the tmux session name and window name both update to `{project} @ {branch}` based on the pane's CWD.

2. **Given** AC1, **when** the per-window hooks are inspected (`tmux show-hooks -w`), **then** a `pane-focus-in` hook is registered with the script's absolute path.

3. **Given** AC1, **when** the pane's tmux options are inspected (`tmux show-options -p @swain_path`), **then** `@swain_path` is set to the resolved working directory.

### Shell pane switching (DESIGN-001 Flow 2)

4. **Given** two shell panes in the same window — pane A `cd`'d to branch `main`, pane B `cd`'d to a worktree on branch `feature-x` — **when** the operator focuses pane B, **then** session and window names update to `swain @ feature-x`.

5. **Given** AC4, **when** the operator focuses pane A again, **then** names revert to `swain @ main`.

### Agent pane with @swain_path (DESIGN-001 Flows 3, 4)

6. **Given** a TUI agent pane, **when** the agent runs `swain-tab-name.sh --path <worktree> --auto`, **then** tmux names update to the worktree's branch AND `@swain_path` is set on that pane.

7. **Given** AC6, the operator switches to a shell pane (names update per AC4), **when** the operator switches back to the agent pane, **then** the hook reads `@swain_path` and names update to the worktree's branch (not the pane's stale launch CWD).

### Agent exits worktree (DESIGN-001 Flow 5)

8. **Given** AC6, **when** the agent runs `swain-tab-name.sh --path <main-repo> --auto`, **then** names revert to `swain @ main` and `@swain_path` is updated to the main repo path.

### Cross-session isolation (DESIGN-001 Flow 6)

9. **Given** two tmux sessions (swain and HouseOps) each with the hook installed, **when** the operator switches from swain to HouseOps, **then** HouseOps's naming reflects its own pane context (not swain's).

10. **Given** only the swain session has run `--auto`, **when** the operator switches to a session that hasn't, **then** no naming interference occurs (hook is per-window, not global).

### Reset (DESIGN-001 Flow 7)

11. **Given** the hook is installed and `@swain_path` is set, **when** `swain-tab-name.sh --reset` is run, **then** the per-window hook is removed, `@swain_path` is cleared, and automatic-rename is re-enabled.

### Edge cases

12. **Given** a pane whose CWD is not inside a git repository and has no `@swain_path`, **when** it gains focus, **then** names fall back to `unknown @ no-branch` with exit 0.

13. **Given** a worktree of repository `swain`, **when** `--path <worktree> --auto` runs, **then** the project name resolves to `swain` (not the worktree directory name), via `--git-common-dir`.

14. **Given** `--auto` is run twice on the same window, **when** hooks are inspected, **then** only one `pane-focus-in` hook exists (idempotent).

### Agent-agnostic contract

15. The `--path` flag, `@swain_path` mechanism, and per-window hook work identically regardless of which agent invokes them. No agent-specific hooks or configuration required — only the ability to run bash commands.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- **In scope:** `swain-tab-name.sh` modifications, per-window hook, per-pane `@swain_path`, `--path` flag, project name resolution for worktrees, SKILL.md agent instructions
- **Out of scope:** non-tmux terminals, shell prompt hooks (precmd/PROMPT_COMMAND), agent-specific hook configurations (Claude Code WorktreeCreate, etc.)
- **Constraint:** `BASH_SOURCE[0]` must be used for path resolution — `$0` is unreliable in agent subprocesses
- **Constraint:** `set -e` must NOT be used — script must never fail hard (per SKILL.md error handling policy)
- **Constraint:** All tmux commands must use `|| true` to degrade gracefully outside tmux

## Implementation Approach

Modify `skills/swain-session/scripts/swain-tab-name.sh`:

1. **`set_title`** — accept second arg for session name; call `tmux rename-session` alongside `rename-window`
2. **`auto_title`** — path resolution: `--path` arg → `@swain_path` (via `tmux show-options -pqv`) → `$(pwd)` → `#{pane_current_path}`; use `--git-common-dir` for project name; set `@swain_path` on current pane after resolution
3. **`install_hook`** — register `pane-focus-in` per-window (`set-hook -w`); resolve script path via `BASH_SOURCE[0]`
4. **`reset_title`** — remove per-window hook (`set-hook -uw`); clear `@swain_path` (`set-option -pu`)

Update `skills/swain-session/SKILL.md`:
- Document `--path` flag for agent worktree entry
- Document agent-agnostic contract: any agent entering a worktree must call `--path <dir> --auto`

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-16 | | Initial creation |
| Active | 2026-03-16 | | Rewritten after design exploration — added per-pane `@swain_path`, per-window hooks, worktree project name fix |
