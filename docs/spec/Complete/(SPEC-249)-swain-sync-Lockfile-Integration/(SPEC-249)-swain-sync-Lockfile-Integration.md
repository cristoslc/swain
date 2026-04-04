---
title: "swain-sync Lockfile Integration"
artifact: SPEC-249
track: implementable
status: Complete
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-epic: EPIC-056
priority-weight: high
depends-on-artifacts:
  - SPEC-244
  - SPEC-252
linked-artifacts:
  - SPIKE-057
---

# SPEC-249: swain-sync Lockfile Integration

## Goal

Integrate swain-sync with the lockfile system. After successful merge+push, swain-sync marks the lockfile `ready_for_cleanup` instead of removing the worktree itself.

## Deliverables

Update `skills/swain-sync/SKILL.md` push completion logic to:
1. Source swain-lockfile.sh
2. After successful push: call `swain-lockfile.sh mark-ready <branch>`
3. Remove the `worktree-*` branch name heuristic
4. Remove all `git worktree remove` calls from swain-sync
5. Replace with lockfile-based status reporting

## Acceptance Criteria

- [ ] **AC1: Mark ready after push**
  - After successful `git push origin HEAD:trunk`, calls `swain-lockfile.sh mark-ready`
  - Lockfile updated with `ready_for_cleanup=true` and `ready_commit=<hash>`

- [ ] **AC2: No worktree removal**
  - swain-sync never calls `git worktree remove`
  - All cleanup deferred to bin/swain

- [ ] **AC3: Branch heuristic removed**
  - No `case "$BRANCH" in worktree-*)` pattern
  - Worktree detection via lockfile existence or git plumbing only

- [ ] **AC4: Error handling preserves lockfile state**
  - Merge conflict: lockfile stays `status=active`, no ready mark
  - Push rejection after retries: lockfile stays active
  - Only mark ready on confirmed successful push

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-04 | -- | Materialized for EPIC-056 |
