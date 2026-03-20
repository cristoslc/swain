---
title: "Stage Status Hook Fails in Worktrees"
artifact: SPEC-050
track: implementable
status: Proposed
author: cristos
created: 2026-03-15
last-updated: 2026-03-15
type: bug
parent-epic: ""
parent-initiative: INITIATIVE-013
linked-artifacts:
  - INITIATIVE-013
  - EPIC-015
  - SPEC-041
  - SPEC-039
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# Stage Status Hook Fails in Worktrees

## Problem Statement

The `.claude/settings.json` hook command `bash skills/swain-stage/scripts/stage-status-hook.sh` uses a relative path that fails when Claude Code's hook runner executes from a working directory other than the repo root. This produces a non-blocking error on every PostToolUse, Stop, SubagentStart, and SubagentStop event:

```
Stop hook error: Failed with non-blocking status code: bash:
skills/swain-stage/scripts/stage-status-hook.sh: No such file or directory
```

The script exists at the expected relative location in both the main repo and worktrees. The error occurs because the hook runner's cwd is not the repo root — it may be `$HOME`, an internal Claude Code directory, or a subdirectory of the project.

## External Behavior

After the fix:

1. The hook resolves the script path correctly regardless of the hook runner's cwd.
2. The hook works identically in the main worktree and any git worktree.
3. The MOTD status panel receives `stage-status.json` updates in all worktrees.
4. No `No such file or directory` errors appear in hook output.

## Acceptance Criteria

- **Given** Claude Code fires a PostToolUse hook in a git worktree, **When** the hook command runs, **Then** `stage-status.json` is written with `{"state": "working", ...}`.
- **Given** Claude Code fires a Stop hook in the main repo checkout, **When** the hook command runs, **Then** `stage-status.json` is written with `{"state": "idle", ...}`.
- **Given** the hook runs from a cwd that is not the repo root (e.g., `$HOME`), **When** the script path is resolved, **Then** the hook still finds and executes `stage-status-hook.sh`.
- **Given** a worktree at `.claude/worktrees/foo/`, **When** any hook fires, **Then** no `No such file or directory` error appears.

## Reproduction Steps

1. Start a Claude Code session in a worktree (e.g., `claude --worktree`).
2. Perform any action that triggers a tool use.
3. Observe the hook error in the output: `bash: skills/swain-stage/scripts/stage-status-hook.sh: No such file or directory`.

## Severity

low — the hook is non-blocking, so it's noisy but not harmful. The MOTD panel falls back to stale data.

## Expected vs. Actual Behavior

**Expected:** Hook script runs silently, writes `stage-status.json`, MOTD panel shows live agent state.

**Actual:** Hook fails with file-not-found, `stage-status.json` is never updated, MOTD shows stale data.

## Implementation Approach

The hook command in `.claude/settings.json` needs to resolve the script path relative to the project root, not the hook runner's cwd. Options:

### Option A: Use `$CLAUDE_PROJECT_DIR` (preferred if available)

If Claude Code sets `CLAUDE_PROJECT_DIR` in the hook environment:

```json
"command": "bash \"$CLAUDE_PROJECT_DIR/skills/swain-stage/scripts/stage-status-hook.sh\""
```

### Option B: Inline git-based resolution

```json
"command": "bash \"$(git -C \"${CLAUDE_PROJECT_DIR:-.}\" rev-parse --show-toplevel)/skills/swain-stage/scripts/stage-status-hook.sh\""
```

### Option C: Wrapper script at a known absolute path

Create a thin wrapper that resolves the repo root and delegates:

```bash
#!/usr/bin/env bash
ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
exec bash "$ROOT/skills/swain-stage/scripts/stage-status-hook.sh"
```

The fix should be applied to `.claude/settings.json` in the main repo. swain-doctor should validate that hook script paths resolve correctly (stretch goal).

## Scope & Constraints

- Fix is confined to the hook command string in `.claude/settings.json` and/or a thin wrapper script.
- Do not change the hook script itself (`stage-status-hook.sh`) — it works correctly once found.
- Must work for both main checkout and worktrees.
- Must not break if `git` is unavailable (graceful no-op).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-15 | — | Discovered during worktree session; linked to EPIC-015 as a gap in worktree awareness |
