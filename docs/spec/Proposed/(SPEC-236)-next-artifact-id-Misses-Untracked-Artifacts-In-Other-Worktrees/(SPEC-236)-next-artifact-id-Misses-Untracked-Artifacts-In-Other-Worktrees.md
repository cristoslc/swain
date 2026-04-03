---
title: "next-artifact-id Misses Untracked Artifacts In Other Worktrees"
artifact: SPEC-236
track: implementable
status: Proposed
author: cristos
created: 2026-04-02
last-updated: 2026-04-02
priority-weight: ""
type: bug
parent-epic: ""
parent-initiative: INITIATIVE-002
linked-artifacts:
  - EPIC-043
  - SPEC-140
  - EPIC-055
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# next-artifact-id Misses Untracked Artifacts In Other Worktrees

## Problem Statement

`next-artifact-id.sh` allocated `DESIGN-012`, `EPIC-054`, and `SPEC-232` in this worktree even though those IDs already existed as untracked artifacts in another local checkout. That makes concurrent artifact authoring unsafe and breaks cross-worktree collision avoidance.

## Desired Outcomes

Artifact number allocation accounts for untracked artifact files in sibling worktrees. It refuses to hand out an ID that is already present anywhere in the local multi-worktree repo.

## External Behavior

**Before:** `next-artifact-id.sh` can return an ID that is already in use by untracked artifacts in another worktree.

**After:** `next-artifact-id.sh` scans all local worktrees, including untracked artifact folders and files, before allocating the next ID.

## Acceptance Criteria

1. **Given** an untracked artifact with ID `TYPE-NNN` in another local worktree, **when** `next-artifact-id.sh TYPE` runs, **then** it does not return `NNN`.
2. **Given** tracked and untracked artifacts across multiple worktrees, **when** allocation runs, **then** the returned number is greater than every observed in-use number of that type.
3. **Given** no collisions are present, **when** allocation runs, **then** behavior for normal single-worktree cases remains unchanged.

## Reproduction Steps

1. Create or leave untracked artifact folders in one local worktree.
2. Run `next-artifact-id.sh` for the same artifact type from another worktree.
3. Observe the allocator returning an already-used ID.

## Severity

high

## Expected vs. Actual Behavior

**Expected:** Artifact creation never reuses an ID that is already present in any local worktree, whether tracked or untracked.

**Actual:** The allocator ignored untracked artifacts in another checkout and proposed colliding IDs.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

In scope: allocator detection logic, multi-worktree fixtures or integration coverage, regression test for untracked collisions.

Out of scope: general graph collision detection after creation; that remains adjacent but separate safety coverage.

## Implementation Approach

Extend the allocator's search surface to include local worktree paths and untracked artifact folders or files, then add a regression test that reproduces the same cross-worktree collision.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-02 | — | Initial creation from cross-worktree allocation collision |
