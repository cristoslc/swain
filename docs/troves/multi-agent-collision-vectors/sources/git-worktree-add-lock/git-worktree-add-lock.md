---
source-id: git-worktree-add-lock
type: repository
title: "git/git: worktree add --lock option (commit 507e6e9)"
url: "https://github.com/git/git/commit/507e6e9eecce5e7a2cc204c844bbb2f9b17b31e3"
fetched: 2026-03-20
content-hash: "--"
---

# git/git: worktree add --lock option

## The Race Condition

A race condition exists between `git worktree add` and `git worktree lock` — in the gap between creating the worktree and locking it, another process could prune it.

The commit message for the merge (e31159746e) explains: "To avoid race conditions between creation and locking, git worktree add --lock performs both actions atomically."

## Implementation

The `--lock` option was added in Git 2.13. It keeps a lock while preparing the worktree, and if `--lock` is specified, this lock remains after the worktree is created. Additional checks prevent double-locking a worktree or unlocking one that is not locked.

## Historical Context

- Prior to Git 2.9: `git branch -d` could incorrectly delete a branch checked out in another linked worktree
- Prior to Git 2.13: no atomic add+lock; race condition between add and prune
- Prior to Git 2.22: worktree name generation used a stat loop prone to race conditions

## Relevance

This commit demonstrates that the git project has actively addressed race conditions in the worktree subsystem. However, the fixes are focused on administrative operations (add, lock, prune) rather than on concurrent data operations (commits, merges) from multiple worktrees. The latter are handled by git's existing ref-locking and object-store atomicity mechanisms.
