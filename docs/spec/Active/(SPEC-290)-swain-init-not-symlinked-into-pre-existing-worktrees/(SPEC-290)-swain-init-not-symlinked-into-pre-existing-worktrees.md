---
id: SPEC-290
artifact: SPEC-290
title: ".swain-init not symlinked into pre-existing worktrees"
type: bug
status: Active
priority-weight: high
parent-initiative: INITIATIVE-002
created: 2026-04-06
last-updated: 2026-04-06
swain-do: not-required
---

## Lifecycle

| Phase | Date | Commit |
|-------|------|--------|
| Active | 2026-04-06 | — |

## Problem

When `bin/swain` creates a worktree, `create_session_worktree` symlinks
`.swain-init` from the main repo root into the new worktree. This code was
added in commit `c05c0acc` / `18076075`. Worktrees that existed before those
commits — or worktrees created by the `using-git-worktrees` skill, which
calls raw `git worktree add` — do not have the symlink.

When the `swain-init-preflight.sh` runs inside such a worktree it sees no
`.swain-init` file and sets `marker.action = "onboard"`. This triggers the
full onboarding flow instead of the fast-path `"delegate"` branch, making
every session in that worktree appear uninitialized.

## Acceptance criteria

1. `swain-doctor` detects linked worktrees that are missing a valid
   `.swain-init` entry (real file or symlink with a live target).
2. `swain-doctor` auto-repairs the gap by creating a symlink from
   `$REPO_ROOT/.swain-init` to `$worktree_path/.swain-init`, provided the
   source file exists.
3. After the repair, `swain-init-preflight.sh` running inside the worktree
   reports `"action": "delegate"` rather than `"action": "onboard"`.
4. If `$REPO_ROOT/.swain-init` does not exist, the check reports advisory
   (not blocking) — the project itself is uninitialized.

## Fix location

`skills/swain-doctor/scripts/swain-doctor.sh` — add a sub-check inside
`check_worktrees()` that iterates linked worktrees and repairs missing
`.swain-init` symlinks.
