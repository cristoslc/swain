---
source-id: git-worktree-docs
type: documentation
title: "Git - git-worktree Documentation"
url: "https://git-scm.com/docs/git-worktree"
fetched: 2026-03-20
content-hash: "--"
---

# Git - git-worktree Documentation

## Shared vs Per-Worktree Architecture

Each linked worktree has a private subdirectory in `$GIT_DIR/worktrees`. The environment variables are:
- `$GIT_DIR` — points to the private directory (e.g., `/path/main/.git/worktrees/test-next`)
- `$GIT_COMMON_DIR` — points back to the main worktree's `$GIT_DIR` (e.g., `/path/main/.git`)

### Ref Sharing Rules

**Shared across all worktrees:**
- All refs starting with `refs/` (branches, tags, remote-tracking branches)
- Exception: `refs/bisect/`, `refs/worktree/`, and `refs/rewritten/` are NOT shared

**Per-worktree (pseudo refs):**
- `HEAD` (different for each worktree)
- `refs/bisect/`, `refs/worktree/`, `refs/rewritten/`
- Index files and working tree files

### Configuration Sharing

The repository `config` file is shared across all worktrees by default. Worktree-specific configuration can be enabled with `extensions.worktreeConfig`.

## Safety and Locking Mechanisms

### The --lock Option

Prevents administrative files from being pruned, moved, or deleted. Using `git worktree add --lock` is atomic — it avoids a race condition between `git worktree add` and `git worktree lock` where someone could accidentally prune the new worktree in the gap.

### Branch Checkout Protection

By default, `add` refuses to create a new worktree when a branch name is already checked out by another worktree. This prevents the most dangerous class of concurrent mutation on the same branch.

## Known Bugs and Limitations

1. "Multiple checkout in general is still experimental, and the support for submodules is incomplete. It is NOT recommended to make multiple checkouts of a superproject."
2. Main worktree cannot be removed.
3. Worktrees with submodules cannot be moved via `git worktree move`.
4. Prior to Git 2.9, `git branch -d` could incorrectly delete a branch still checked out in another linked worktree.
5. Prior to Git 2.13, the `--lock` option did not exist, creating a race between add and lock.
6. Prior to Git 2.22, worktree name generation used a stat loop prone to race conditions.

## Concurrent Operations Safety

- Each worktree has its own index, so `git add` and `git commit` in worktree A do not interfere with worktree B (provided they are on different branches, which git enforces).
- Object creation uses atomic temp-file-then-rename, so concurrent object writes are safe.
- Ref updates use `.lock` files — concurrent updates to the same ref will fail cleanly rather than corrupt.
- Git's internal locking handles concurrent access to shared reflogs.
