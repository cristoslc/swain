---
title: "swain-doctor Orphan Scanning"
artifact: SPEC-246
track: implementable
status: Complete
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-epic: EPIC-056
priority-weight: medium
depends-on-artifacts:
  - SPEC-244
linked-artifacts: []
---

# SPEC-246: swain-doctor Orphan Scanning

## Goal

Add lockfile-aware orphan worktree detection to swain-doctor. Doctor should detect lockfiles without corresponding worktrees, worktrees without lockfiles, and stale lockfiles.

## Deliverables

Add a new check to `skills/swain-doctor/scripts/swain-doctor.sh`:
1. Cross-reference `git worktree list` with `.agents/worktrees/*.lock`
2. Detect mismatches: lockfile but no worktree, worktree but no lockfile
3. Detect stale lockfiles via swain-lockfile.sh stale detection
4. Report findings with remediation suggestions

## Acceptance Criteria

- [ ] **AC1: Lockfile without worktree detected**
  - Lockfile exists but worktree path doesn't -> "Stale lockfile: <path>"
  - Offers to remove lockfile

- [ ] **AC2: Worktree without lockfile detected**
  - Worktree exists (non-trunk) but no lockfile -> "Unclaimed worktree: <path>"
  - Offers to create lockfile or remove worktree

- [ ] **AC3: Stale lockfile detected**
  - PID dead AND pane dead -> "Stale lockfile: <path> (PID dead, pane dead)"
  - Offers to release stale claim

- [ ] **AC4: Clean state passes silently**
  - All worktrees have matching active lockfiles -> no output

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-04 | -- | Materialized for EPIC-056 |
