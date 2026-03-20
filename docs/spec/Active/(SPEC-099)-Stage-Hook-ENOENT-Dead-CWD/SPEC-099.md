---
title: "stage-status-hook fails with ENOENT when CWD is removed"
artifact: SPEC-099
track: implementable
status: Active
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
source-issue: "https://github.com/anthropics/claude-code/issues/36720"
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
| Hook does not produce ENOENT after worktree removal | `.claude/settings.json` all four hook commands prefix with `cd /Users/cristos/Documents/code/swain 2>/dev/null || cd $HOME;` | Fail — `cd` prefix is inside the shell command, but `posix_spawn('/bin/sh')` fails *before* the shell starts when CWD is deleted |
| Belt-and-suspenders defensive `cd` inside script | `stage-status-hook.sh` lines 13–14: `cd "$HOME" 2>/dev/null || cd /` | Fail — same reason: shell never starts |
| Hook behavior unchanged in valid CWD | The `cd` prefix works correctly when CWD is valid | Pass |

## Scope & Constraints

- The ENOENT occurs at the OS/Node level when `child_process.spawn` calls `posix_spawn('/bin/sh')` with an invalid CWD. Neither shell-level `cd` prefixes nor script guards can help — the shell process never starts.
- The settings.json `cd` prefix **does not fix the pre-spawn CWD issue** — it only helps if `/bin/sh` can be spawned in the first place. Confirmed by reproduction: after `EnterWorktree` → sync agent removes worktree → stop hook fires → same ENOENT.
- **Root cause is in Claude Code itself**: hook commands are spawned with the session's current CWD, and there is no fallback when that CWD is deleted. This requires an upstream fix (filed as `anthropics/claude-code` issue).
- **Mitigation path**: prevent the CWD from becoming invalid in the first place:
  - SPEC-100 fixes swain-sync (cd before worktree removal) — but only helps when sync runs in the *same* process
  - swain-sync should **not remove worktrees entered via `EnterWorktree`** — let `ExitWorktree` handle cleanup, since it properly restores the session's CWD
  - SPEC-098 (tmux guard) would prevent the hook from running outside tmux, but can't execute due to the same pre-spawn failure

## Implementation Approach

1. ~~Update `.claude/settings.json` hook commands to prefix with an explicit `cd`~~ — insufficient (pre-spawn failure)
2. ~~Defensive `cd` inside the script~~ — insufficient (shell never starts)
3. **Upstream fix needed**: file Claude Code issue requesting `cwd` fallback in hook spawning — when the configured CWD doesn't exist, spawn with `$HOME` or `/` instead
4. **Swain-side mitigation**: update swain-sync to skip worktree removal when the worktree was entered via `EnterWorktree` (detect via the tool's branch naming convention `worktree-*`), deferring cleanup to `ExitWorktree`

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | — | Initial creation — user-reported bug |
| Implementation | 2026-03-20 | 33119f6 | Two-layer fix applied: settings.json cd prefix + script defensive cd — insufficient, pre-spawn failure |
| Active | 2026-03-20 | — | Reopened: `cd` prefix runs inside shell but `posix_spawn` fails before shell starts. Root cause is Claude Code spawning hooks with invalid CWD. Upstream issue filed. |
