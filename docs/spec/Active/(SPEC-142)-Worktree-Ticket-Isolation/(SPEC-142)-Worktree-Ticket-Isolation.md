---
title: "Worktree Ticket Isolation"
artifact: SPEC-142
track: implementable
status: Active
author: operator
created: 2026-03-21
last-updated: 2026-03-21
type: bug
parent-epic:
parent-initiative:
linked-artifacts: []
depends-on-artifacts: []
addresses:
  - PERSONA-002
evidence-pool:
source-issue:
swain-do: required
---

# Worktree Ticket Isolation

## Problem Statement

When `tk` tasks are created in the main checkout (prefix `swa-`), they cannot be claimed, noted, or closed from within a git worktree because the worktree has its own `.tickets/` directory with a different prefix (e.g. `aa-`). Running `tk claim swa-fd5h` from the worktree returns "ticket not found" — the worktree's `.tickets/` doesn't contain the main checkout's tickets.

The current workaround is `cd`-ing to the main checkout for all tk operations, which breaks the worktree isolation model and causes confusion when the shell's cwd resets back to the worktree after each command.

## Desired Outcomes

The agent (PERSONA-002) can create a plan in the main checkout, enter a worktree for implementation, and close tasks as work completes — all without leaving the worktree or manually switching directories. Worktree isolation should be transparent to the task tracking workflow.

## Reproduction Steps

1. In the main checkout, create a tk epic and child tasks: `tk create "Test plan" -t epic` → e.g. `swa-abc1`
2. Enter a worktree: use `EnterWorktree` or `git worktree add`
3. From the worktree, attempt: `tk claim swa-abc1`
4. Observe: "ticket 'swa-abc1' not found"
5. Run `tk ready` in the worktree — it shows only worktree-local tickets (different prefix)

## Severity

medium

## Expected vs. Actual Behavior

**Expected:** `tk claim swa-abc1` from a worktree succeeds — tk resolves the ticket from the main checkout's `.tickets/` directory, or the worktree shares the same ticket store.

**Actual:** `tk claim swa-abc1` fails with "ticket not found" because tk looks in the worktree's local `.tickets/` directory, which has its own independent ticket store with a different prefix.

## External Behavior

The fix should ensure that tk operations within a worktree resolve tickets from the main checkout's `.tickets/` directory. Possible approaches:

1. **Symlink `.tickets/`** — when entering a worktree, symlink `.tickets/` to the main checkout's `.tickets/`. Simplest, but may cause write conflicts if multiple worktrees write concurrently.
2. **tk `--tickets-dir` flag** — tk already rejects this flag, but if it were supported, swain-do could pass the main checkout's `.tickets/` path when operating in a worktree. Requires tk changes.
3. **Environment variable** — set `TICKETS_DIR` to point at the main checkout's `.tickets/` when entering a worktree. Requires tk to respect this env var.
4. **Git common dir resolution** — tk could auto-detect worktrees via `git rev-parse --git-common-dir` and resolve `.tickets/` relative to the main checkout rather than the worktree root.

Approach 4 is the most robust — it requires no manual setup and handles all worktree scenarios transparently.

## Acceptance Criteria

- Given a tk task created in the main checkout, when `tk claim <id>` is run from a worktree, then the task is successfully claimed.
- Given a tk task created in the main checkout, when `tk close <id>` is run from a worktree, then the task is successfully closed.
- Given a tk task created in the main checkout, when `tk add-note <id> "text"` is run from a worktree, then the note is appended to the correct ticket file.
- Given multiple worktrees exist, when `tk ready` is run from any worktree, then it shows the same task list as the main checkout.

## Verification

<!-- Populated when entering Testing phase. -->

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- **In scope:** Making tk operations work transparently from worktrees when tickets were created in the main checkout.
- **Out of scope:** Supporting independent per-worktree ticket stores (the current behavior) as a feature. Concurrent write safety across multiple worktrees (acceptable to defer).
- tk is a vendored shell script (`skills/swain-do/bin/tk`) — changes are local to this project.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-21 | — | Initial creation |
