---
title: "swain-sync Merge Logic"
artifact: SPEC-252
track: implementable
status: Proposed
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-epic: EPIC-056
priority-weight: high
depends-on-artifacts: []
linked-artifacts:
  - SPIKE-057
---

# SPEC-252: swain-sync Merge Logic

## Goal

Ensure swain-sync's merge-from-worktree logic is correct and tested. swain-sync already has merge+push+retry logic (per ADR-011). This spec validates the existing logic works for the EPIC-056 flow and fixes the shared-stash risk.

## Findings (from SPIKE-057)

- `git merge origin/trunk` works from worktree (confirmed)
- `git push origin HEAD:trunk` works from worktree (confirmed)
- Retry loop (3 attempts) handles concurrent push races
- PR fallback handles branch protection
- **Risk: shared stash** — `git stash pop` pops top of stack, not by label. Concurrent worktree stash operations can interleave.

## Deliverables

1. Fix stash handling: use `git stash push -m "swain-sync: <branch>"` and pop by matching stash index, or avoid stash entirely (commit dirty state to a temp commit, then soft-reset after merge)
2. Remove worktree self-removal logic (deferred to bin/swain per EPIC-056)
3. Add tests for merge-from-worktree flow

## Acceptance Criteria

- [ ] **AC1: Stash safety**
  - No bare `git stash pop` — either targeted pop by index or temp-commit approach
  - Concurrent worktree stash operations cannot interfere

- [ ] **AC2: No self-removal**
  - swain-sync does NOT call `git worktree remove` after push
  - Cleanup deferred to bin/swain (via ready_for_cleanup in SPEC-249)

- [ ] **AC3: Merge from worktree tested**
  - Test: merge trunk into worktree branch succeeds
  - Test: push from worktree to trunk succeeds (in test repo)
  - Test: retry on non-fast-forward works

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-04 | -- | Materialized for EPIC-056 |
