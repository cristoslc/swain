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
  - SPEC-008
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Tmux Pane-Aware Session Naming

## Problem Statement

When the operator switches between tmux panes that are in different git worktrees or branches, the tmux session name and window name remain stale — showing whatever branch was active when `swain-session` last ran. The operator loses at-a-glance context about which branch they're operating in, which is especially disorienting when using worktrees for parallel feature work.

## External Behavior

**Preconditions:**
- Operator is in a tmux session
- `swain-session` has been invoked (either auto or manual) at least once in the session

**Trigger:** Operator switches focus to a different tmux pane (via pane select, window select, or any focus change).

**Behavior:**
1. The `pane-focus-in` tmux hook fires automatically.
2. The hook resolves the **active pane's working directory** via `tmux display-message -p '#{pane_current_path}'`.
3. From that directory, it resolves git context: project name (from repo root basename) and branch name (from `HEAD`).
4. Both the **tmux window name** and the **tmux session name** update to reflect the active pane's git context, using the configured `terminal.tabNameFormat` (default: `{project} @ {branch}`).

**Postconditions:**
- Tmux status bar shows the active pane's project and branch
- Outer terminal title (iTerm tab) reflects the active window name
- If the active pane is not in a git repo, names fall back to `unknown @ no-branch`

**Constraints:**
- The hook must be installed idempotently — re-running `--auto` replaces, not duplicates
- `--reset` must remove the hook cleanly
- No user interaction required after initial `swain-session` invocation
- The hook must resolve the script path absolutely so it survives across shell sessions

## Acceptance Criteria

1. **Given** a tmux session with two panes in different git branches, **when** the operator switches focus between them, **then** both the tmux session name and window name update to reflect the newly focused pane's branch.

2. **Given** `swain-tab-name.sh --auto` has been run, **when** `tmux show-hooks -g pane-focus-in` is queried, **then** the hook is registered with the absolute path to the script.

3. **Given** the pane-focus-in hook is installed, **when** `swain-tab-name.sh --reset` is run, **then** the hook is removed (`tmux show-hooks -g pane-focus-in` returns nothing).

4. **Given** a pane whose working directory is not inside a git repository, **when** that pane gains focus, **then** the title updates to `unknown @ no-branch` (graceful degradation, no error).

5. **Given** `--auto` is run twice, **when** the hooks are inspected, **then** only one `pane-focus-in` hook exists (idempotent install).

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- **In scope:** tmux hook installation, session + window rename on pane focus, git context from active pane path, cleanup on reset
- **Out of scope:** non-tmux terminals, shell prompt integration (precmd/PROMPT_COMMAND), branch change detection within the same pane (would require shell hooks, not tmux hooks)
- The `BASH_SOURCE[0]` idiom must be used for path resolution — `$0` is unreliable when the script is invoked from agent subprocesses

## Implementation Approach

The implementation modifies `skills/swain-session/scripts/swain-tab-name.sh`:

1. **`set_title`** — accept optional second arg for session name; call `tmux rename-session` alongside `tmux rename-window`
2. **`auto_title`** — resolve git context from active pane path via `tmux display-message -p '#{pane_current_path}'` with fallback to `$(pwd)`; pass title to both session and window
3. **`install_hook`** — new function; register `pane-focus-in` hook pointing to the script's absolute path (via `BASH_SOURCE[0]`); called by `--auto`
4. **`reset_title`** — also unset the `pane-focus-in` hook via `tmux set-hook -gu`

TDD cycle: AC1 (hook fires and renames) → AC2 (hook registered with absolute path) → AC3 (reset removes hook) → AC4 (non-git graceful fallback) → AC5 (idempotent install).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-16 | | Initial creation — implementation in progress |
