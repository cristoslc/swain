---
title: "swain-teardown Integration"
artifact: SPEC-279
track: implementable
status: Complete
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-epic: EPIC-056
priority-weight: medium
depends-on-artifacts:
  - SPEC-276
linked-artifacts: []
---

# SPEC-279: swain-teardown Integration

## Goal

Update swain-teardown to release lockfile claims during session teardown and use lockfile state for cleanup decisions.

## Deliverables

Update `skills/swain-teardown/SKILL.md` to:
1. Release lockfile claim for current worktree on teardown
2. Check lockfile state when deciding whether to remove orphan worktrees
3. Respect `ready_for_cleanup` flag (safe to remove without confirmation)
4. Warn if lockfile shows active claim by another session

## Acceptance Criteria

- [ ] **AC1: Release current claim on teardown**
  - If in a worktree with an active lockfile, call `swain-lockfile.sh release`
  - No-op if no lockfile exists

- [ ] **AC2: Lockfile-aware orphan decisions**
  - Stale lockfile + worktree: safe to remove (with confirmation)
  - Active lockfile + worktree: warn "claimed by PID <pid>, skip"
  - ready_for_cleanup + worktree: safe to remove without confirmation

- [ ] **AC3: Lockfile cleanup on worktree removal**
  - When removing a worktree, also remove its lockfile
  - When removing a lockfile, also prune the worktree entry from git

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-04 | -- | Materialized for EPIC-056 |
