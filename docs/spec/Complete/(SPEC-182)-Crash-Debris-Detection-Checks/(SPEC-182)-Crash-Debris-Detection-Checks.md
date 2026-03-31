---
title: "Crash Debris Detection Checks"
artifact: SPEC-182
track: implementable
status: Complete
author: cristos
created: 2026-03-28
last-updated: 2026-03-30
priority-weight: high
type: feature
parent-epic: EPIC-046
parent-initiative: ""
linked-artifacts:
  - SPEC-180
  - ADR-015
  - ADR-011
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Crash Debris Detection Checks

## Problem Statement

A system crash leaves stale state that blocks the next session: git lock files prevent all git operations, interrupted merge/rebase state confuses git status, stale tk claim locks prevent re-claiming tasks, and dangling worktrees accumulate. Today, none of these are detected by swain-doctor or swain-preflight (except stale tk locks >1 hour). The operator must manually diagnose and clean up before work can resume.

## Desired Outcomes

Crash debris is detected automatically and cleanable with a single operator confirmation per item. The checks are standalone bash functions callable by both the pre-runtime script (SPEC-180) and swain-doctor (for in-session health checks).

## External Behavior

**Inputs:** Project root path, optional git worktree path

**Checks:**

| Check | Detection | Action |
|-------|-----------|--------|
| Git index lock | `.git/index.lock` exists AND creating PID not running | Offer to remove |
| Interrupted merge | `.git/MERGE_HEAD` exists | Offer `git merge --abort` |
| Interrupted rebase | `.git/rebase-merge/` directory exists | Offer `git rebase --abort` |
| Interrupted cherry-pick | `.git/CHERRY_PICK_HEAD` exists | Offer `git cherry-pick --abort` |
| Stale tk claim locks | `.tickets/.locks/{id}/` with dead owner PID or age >1 hour | Offer to remove |
| Dangling worktrees (crash-correlated) | Cross-reference `git worktree list` with orphaned runtime PIDs | Surface uncommitted changes, offer cleanup |
| Orphaned MCP servers | Process list matching MCP patterns for this project | Offer to kill |

**Outputs:** Structured report (JSON or formatted text) listing detected debris, proposed action, and result of operator's choice.

**Postconditions:** All confirmed debris is cleaned. Declined items are left in place. No destructive action without confirmation.

## Acceptance Criteria

1. **Given** a `.git/index.lock` left by a dead process, **when** the check runs, **then** it detects the lock and offers removal.
2. **Given** a `.git/MERGE_HEAD` from an interrupted merge, **when** the check runs, **then** it detects the state and offers `git merge --abort`.
3. **Given** a stale tk claim lock from a dead PID, **when** the check runs, **then** it detects the lock and offers removal.
4. **Given** a dangling worktree whose branch correlates with a dead runtime session, **when** the check runs, **then** it surfaces uncommitted changes and offers cleanup.
5. **Given** no crash debris, **when** the checks run, **then** they complete silently (no output, fast path).
6. **Given** the operator declines a cleanup action, **when** the check reports, **then** the debris is left in place and noted.
7. **Given** any check function, **when** invoked from swain-doctor, **then** it works identically to invocation from the pre-runtime script.

## Scope & Constraints

- Pure bash — each check is a standalone function, sourceable by both the pre-runtime script and swain-doctor
- Per ADR-015: never auto-discard worktree state
- Per ADR-011: crash during merge-with-retry may leave partial merge state — recovery is `git merge --abort` then retry sync
- Git lock file removal is safe only when the creating PID is dead — must verify
- MCP server detection is best-effort (process matching by name/port)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-28 | — | Initial creation from SPIKE-051 |
| Complete | 2026-03-30 | 584cd7f | 18/18 tests pass, all 7 ACs verified, doctor integration live |
