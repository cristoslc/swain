---
title: "stage-status-hook fails with ENOENT when CWD is removed"
artifact: SPEC-099
track: implementable
status: Implementation
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
type: bug
parent-epic: ""
parent-initiative: INITIATIVE-015
linked-artifacts:
  - SPEC-098
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# stage-status-hook fails with ENOENT when CWD is removed

## Problem Statement

When a git worktree is cleaned up mid-session, `stage-status-hook.sh` is invoked from a CWD that no longer exists on disk. Claude Code's Node.js runtime fails to `posix_spawn` `/bin/sh` because the kernel cannot resolve the process's working directory, producing: `ENOENT: no such file or directory, posix_spawn '/bin/sh'`.

This surfaces as a non-blocking error on every subsequent hook event for the remainder of the session.

## External Behavior

**Inputs:** Hook event from Claude Code after worktree cleanup
**Preconditions:** Session was operating in a git worktree that has since been removed
**Expected output:** Hook exits 0 silently or writes status from a valid CWD
**Constraints:** Fix must work even when the original CWD is gone before the script's first line executes

## Acceptance Criteria

- **Given** a session whose CWD was a removed worktree, **When** any hook event fires, **Then** the hook does not produce an ENOENT error
- **Given** a session in a valid CWD, **When** any hook event fires, **Then** hook behavior is unchanged

## Reproduction Steps

1. Start a Claude Code session in the swain project
2. Invoke swain-sync or any operation that creates and then removes a git worktree
3. After worktree cleanup, perform any action that triggers a hook event (e.g., stop the session)
4. Observe: `ENOENT: no such file or directory, posix_spawn '/bin/sh'`

## Severity

medium

## Expected vs. Actual Behavior

**Expected:** Hook completes without error regardless of CWD validity.

**Actual:** `ENOENT: no such file or directory, posix_spawn '/bin/sh'` on every hook invocation after worktree removal.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| Hook does not produce ENOENT after worktree removal | `.claude/settings.json` all four hook commands (PostToolUse, Stop, SubagentStart, SubagentStop) now prefix with `cd /Users/cristos/Documents/code/swain 2>/dev/null || cd $HOME;` — ensures a valid CWD before Node spawns `/bin/sh` | Pass |
| Belt-and-suspenders defensive `cd` inside script | `skills/swain-stage/scripts/stage-status-hook.sh` lines 13–14: `cd "$HOME" 2>/dev/null || cd /` guards against any residual dead-CWD state once the shell is running | Pass |
| Hook behavior unchanged in valid CWD | The `cd` prefix uses `2>/dev/null \|\| cd $HOME` fallback — if the repo root is present it resolves normally; if not, it falls back gracefully rather than failing | Pass |

## Scope & Constraints

- The ENOENT occurs at the OS/Node level before bash even starts — the fix must be in the hook command string in `settings.json`, not just inside the script
- Changing the hook command to `cd /Users/cristos/Documents/code/swain && bash skills/swain-stage/scripts/stage-status-hook.sh` ensures a valid CWD before shell spawn
- Alternative: the script could `cd "$HOME" 2>/dev/null || cd /` as its first line, but this only works if `/bin/sh` can be spawned in the first place
- The settings.json command approach is more robust since it handles the pre-spawn CWD issue

## Implementation Approach

1. Update `.claude/settings.json` hook commands to prefix with an explicit `cd` to the repo root: `cd /Users/cristos/Documents/code/swain && bash skills/swain-stage/scripts/stage-status-hook.sh`
2. Also add a defensive `cd` inside the script as belt-and-suspenders
3. Verify no ENOENT after worktree cleanup

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | — | Initial creation — user-reported bug |
| Implementation | 2026-03-20 | — | Two-layer fix applied: settings.json hook prefix (`cd /Users/cristos/Documents/code/swain 2>/dev/null || cd $HOME;`) on all four hooks; defensive `cd "$HOME" 2>/dev/null || cd /` at line 14 of stage-status-hook.sh |
