---
title: "Shared Ticket State Across Worktrees"
artifact: ADR-043
track: standing
status: Active
author: cristos
created: 2026-04-13
last-updated: 2026-04-13
linked-artifacts:
  - [ADR-024](../(ADR-024)-Merge-Tickets-To-Trunk-For-Cross-Session-Coordination/(ADR-024)-Merge-Tickets-To-Trunk-For-Cross-Session-Coordination.md)
  - [ADR-042](../(ADR-042)-Track-Runtime-And-Peer-Agent-Dirs-Instead-Of-Symlinking.md)
  - [SPEC-242](../../../spec/Active/(SPEC-242)-Worktree-Ticket-Isolation/(SPEC-242)-Worktree-Ticket-Isolation.md)
depends-on-artifacts: []
evidence-pool: ""
---

# Shared Ticket State Across Worktrees

## Context

`tk` stores tickets as individual markdown files in `.tickets/`. ADR-024 established tickets as committed coordination state — they merge to trunk and provide cross-agent collision detection via merge conflicts.

When a git worktree is created, it gets its own working tree. `tk` walks up from `$PWD` to find `.tickets/`, so it finds the worktree-local copy — not the main checkout's. Tickets created on trunk (prefix `swa-`) are invisible from the worktree, and vice versa (SPEC-242).

Three approaches were considered:

1. **Patch `find_tickets_dir()`** to detect worktrees and resolve the main checkout's `.tickets/` path, letting `tk` write directly to the main checkout from the worktree.
2. **Symlink `.swain/tickets/`** from the worktree to the main checkout, with no gitignore changes.
3. **Symlink `.swain/tickets/`** from the worktree to the main checkout, plus `git rm --cached` and worktree-local exclude to keep git's index clean.

## Decision

**Adopt approach 3: post-checkout hook that symlinks `.swain/tickets/` to the main checkout's copy, removes it from the worktree's git index, and adds it to the worktree's `info/exclude`.**

Specifics:

1. **Relocate tickets from `.tickets/` to `.swain/tickets/`.** Ticket files move under `.swain/`, which already houses swain infrastructure. This rename signals that tickets are swain-managed state and keeps the project root cleaner.
2. **`post-checkout` hook** runs in worktrees (detected by comparing `git rev-parse --git-common-dir` and `git rev-parse --git-dir`). It:
   - `git rm --cached -r .swain/tickets/` — removes ticket files from this worktree's index only
   - `rm -rf .swain/tickets/` — removes the checked-out copy
   - `mkdir -p .swain` — ensures the parent directory exists
   - `ln -s <main-checkout>/.swain/tickets .swain/tickets` — symlinks to the main checkout's ticket store
   - Appends `.swain/tickets/` to `<worktree-git-dir>/info/exclude` — tells this worktree's git to ignore the symlink
3. **On trunk, `.swain/tickets/` remains fully tracked.** No symlinks, no exclude. Tickets commit and merge normally.
4. **The hook must be idempotent.** `post-checkout` fires on every branch switch, not just `git worktree add`. The hook checks `[[ -L .swain/tickets ]]` before acting.
5. **`find_tickets_dir()` gets a fallback.** Even with the hook, `tk` should detect worktrees and fall back to the main checkout's `.swain/tickets/` if `TICKETS_DIR` is not set and `.swain/tickets/` is not found locally. This is a safety net, not the primary mechanism.
6. **The hook lives in `<git-common-dir>/hooks/`**, shared across all worktrees. One install covers the entire project.

## Alternatives Considered

**A. Patch `find_tickets_dir()` only (no symlinks, no hooks).**

`tk` resolves the main checkout's ticket directory and writes there directly from the worktree. Problem: `git status` in the worktree sees nothing — ticket changes land outside its working tree. The worktree cannot commit its own ticket status changes. The main checkout shows mystery modifications. Swain's commit-then-merge workflow breaks because `git add .` from the worktree misses ticket files entirely.

This is the same problem SPEC-242 identified, just moved to a new directory name.

**B. Symlink `.swain/tickets/` without gitignore or exclude (pure symlink).**

The symlink works at the shell level — `tk` and `cat` read tickets through it. But git's index expects `.swain/tickets/foo.md` to be a regular file, and the symlink makes it a directory entry. `git status` in the worktree shows every ticket as deleted or typechanged. `git diff` becomes useless noise. Someone editing a ticket on trunk changes what the worktree sees through the symlink, but the worktree's index doesn't match — constant dirty state.

**C. Gitignore `.swain/tickets/` globally (not just in worktrees).**

This would be ADR-015 again — tickets become untracked ephemera. ADR-024 already rejected this because it forecloses cross-agent collision detection and caused data loss.

**D. Sparse checkout to exclude `.swain/tickets/` from worktrees.**

Clean git-wise, but `git sparse-checkout` adds operational complexity (cone mode, re-apply on branch switches, interaction with other sparse patterns). The `post-checkout` hook would need to run `git sparse-checkout` commands instead of `git rm --cached`, and any mistake in the sparse config affects the entire worktree checkout.

## Consequences

**Positive:**
- Tickets are fully visible and editable from worktrees — `tk claim`, `tk close`, `tk add-note` all work as expected.
- `git status` in worktrees is clean — tickets excluded from index and from untracked scan.
- Trunk retains full git tracking of tickets — merge conflicts on claims surface collisions between agents.
- No `find_tickets_dir()` hackery for the primary path — the symlink makes the right directory appear at the expected location.
- Consistent with ADR-042's principle that tracked files appear in worktrees automatically, with one deliberate exception (tickets) handled by a targeted exclude.

**Negative:**
- A `post-checkout` hook must be installed in `<git-common-dir>/hooks/`. This is one more setup step during `swain-init`. If the hook is missing, worktrees fall back to the `find_tickets_dir()` safety net — degraded but not broken.
- Symlinks create a hard dependency on the main checkout's directory path. If the main checkout is moved or deleted, all worktrees lose ticket access. Mitigation: the `find_tickets_dir()` fallback resolves this gracefully.
- `git rm --cached` removes ticket files from the worktree's index. If the hook fails to run (e.g., missing from hooks directory), the worktree will have tracked ticket files checked out normally — not harmful, just inconsistent with the expected symlink behavior.
- `.swain/tickets/` appears in `<worktree-git-dir>/info/exclude`. This file is per-worktree and not shared. Each new worktree gets its own exclude entry via the hook — no accumulation.

**Downstream changes required:**
- **`tk`**: Update `find_tickets_dir()` to look for `.swain/tickets/` (not `.tickets/`) and add worktree detection fallback. Update `generate_id()` to use the main checkout's directory name for prefix when in a worktree.
- **Migrate `.tickets/` to `.swain/tickets/`**: Move existing ticket files, update `.gitignore`, update all references in skills and scripts.
- **`swain-init` or onboarding**: Install the `post-checkout` hook in `<git-common-dir>/hooks/`.
- **SPEC-242**: Close — the worktree ticket isolation bug is resolved.
- **ADR-024 reference update**: Note that tickets are now in `.swain/tickets/` instead of `.tickets/`.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-13 | — | Initial creation |
| Active | 2026-04-13 | — | Operator activated in session |