---
title: "swain-sync must restore CWD after worktree cleanup"
artifact: SPEC-100
track: implementable
status: Implementation
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
type: bug
parent-epic: ""
parent-initiative: ""
linked-artifacts:
  - SPEC-127
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# swain-sync must restore CWD after worktree cleanup

## Problem Statement

In swain-sync Step 6 (Push), when operating in a linked worktree (`IN_WORKTREE=yes`), the skill removes the worktree directory after pushing but never `cd`s back to the main repo. The agent's CWD becomes a deleted directory, breaking all subsequent commands — git operations, hook invocations, verification steps, and the session bookmark all fail. The session is effectively dead.

This also causes SPEC-127 (ENOENT on `/bin/sh`) as a downstream symptom: Claude Code hooks can't spawn a shell when the CWD doesn't exist.

## External Behavior

**Inputs:** swain-sync invoked from a linked worktree
**Preconditions:** Agent is operating in `.claude/worktrees/<name>/`
**Expected output:** After push and worktree removal, agent CWD is the main repo root and all subsequent operations work
**Constraints:** Must work when the worktree is already removed (defensive)

## Acceptance Criteria

- **Given** swain-sync runs in a linked worktree, **When** the push succeeds and the worktree is removed, **Then** the agent's CWD is restored to `$MAIN_REPO` before any further commands
- **Given** swain-sync runs in the main worktree, **When** the push succeeds, **Then** behavior is unchanged (no spurious cd)
- **Given** the worktree was already removed by another process, **When** swain-sync tries to cd back, **Then** it falls back to the main repo root gracefully

## Reproduction Steps

1. Start a Claude Code session in the swain project
2. Invoke `/swain-sync` from a linked worktree (e.g., via swain-do agent isolation)
3. After the push lands and worktree is removed, observe that git status, hooks, and all further commands fail
4. The session transcript shows: tools can't find binaries, hooks error with ENOENT

## Severity

high

## Expected vs. Actual Behavior

**Expected:** After worktree removal, CWD is restored to the main repo. Steps 7 (Verify) and Session bookmark execute normally.

**Actual:** CWD points to a deleted directory. Every subsequent command fails. The session is unrecoverable without manual intervention ("start a new session from ~/Documents/code/swain").

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| `cd` happens before `worktree remove` | `skills/swain-sync/SKILL.md` lines 268–274: `cd "$MAIN_REPO" \|\| cd "$HOME"` precedes `git -C "$MAIN_REPO" worktree remove --force "$WORKTREE_PATH"` | Pass |
| Fallback to `$HOME` when main repo unreachable | Same block: `cd "$MAIN_REPO" \|\| cd "$HOME"` | Pass |
| Main-worktree path unaffected | `IN_WORKTREE=no` branch in Step 6 has no worktree removal logic — unchanged | Pass |

## Scope & Constraints

- Fix is in `skills/swain-sync/SKILL.md` Step 6 — add `cd "$MAIN_REPO"` after worktree removal
- No script changes needed — swain-sync is a skill-file-driven workflow, not a standalone script

## Implementation Approach

1. In swain-sync SKILL.md Step 6, add `cd "$MAIN_REPO"` immediately after the worktree remove/prune commands
2. Add a defensive check: `[ -d "$MAIN_REPO" ] && cd "$MAIN_REPO" || cd "$HOME"`
3. Verify Steps 7 and Session bookmark reference `$MAIN_REPO` correctly

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | — | Initial creation — user-reported bug |
| Implementation | 2026-03-20 | — | Fix applied in skills/swain-sync/SKILL.md Step 6: cd to MAIN_REPO before worktree remove; all acceptance criteria verified via code inspection |
