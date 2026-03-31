---
title: "fix-collisions.sh Over-Rewrites Keeper References"
artifact: SPEC-204
track: implementable
status: Active
author: Cristos L-C
created: 2026-03-31
last-updated: 2026-03-31
priority-weight: ""
type: bug
parent-epic: ""
parent-initiative: INITIATIVE-013
linked-artifacts:
  - SPEC-193
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# fix-collisions.sh Over-Rewrites Keeper References

## Problem Statement

`fix-collisions.sh` does a naive global find-and-replace of the colliding ID across all files. It does not distinguish between references that belong to the keeper artifact and references introduced by the collision. This causes keeper references to be incorrectly rewritten to the new number.

## Reproduction Steps

1. Two artifacts share SPEC-194: "Flesch-Kincaid Readability Enforcement" (older, the keeper) and "Fast-Path Session Greeting" (newer, the collision).
2. A design doc references SPEC-194 meaning Flesch-Kincaid (the keeper).
3. Run `fix-collisions.sh`. It renumbers the newer artifact to SPEC-203.
4. The design doc's SPEC-194 references are rewritten to SPEC-203 — but they referred to the keeper, not the collision.

## Severity

medium — requires manual correction after every collision fix, but the script's dry-run mode makes it catchable.

## Expected vs. Actual Behavior

**Expected:** Only references introduced by the collision artifact (or its related commits) are rewritten. References to the keeper artifact stay untouched.

**Actual:** All occurrences of the old ID in all files are rewritten, regardless of which artifact they refer to.

## Desired Outcomes

The operator can run `fix-collisions.sh` without manually reviewing every rewritten reference for false positives. The script correctly distinguishes keeper references from collision references.

## External Behavior

When `fix-collisions.sh` renumbers a collision artifact, it should only rewrite references that were introduced by or relate to the collision artifact. The approach:

1. Use `git log --all --diff-filter=A --format=%H -- <collision-artifact-path>` to find the commit that created the collision artifact.
2. Use `git diff <parent-of-creation-commit>..HEAD --name-only` to identify files that changed in commits referencing the collision artifact.
3. Within those files, only rewrite references that appear in lines added after the collision was created (use `git log -p --all -S "SPEC-NNN"` to trace when each reference was introduced).
4. References in files that predate the collision artifact's creation commit are left untouched — they belong to the keeper.

As a simpler fallback: rewrite references only in files that are inside the collision artifact's directory or in files whose `git log` shows the colliding ID was introduced after the collision artifact was created.

## Acceptance Criteria

1. **Given** two artifacts sharing an ID where the keeper predates the collision, **when** `fix-collisions.sh` runs, **then** references in files that predate the collision are not rewritten.

2. **Given** a file that references the colliding ID and was created after the collision artifact, **when** the script runs, **then** those references are rewritten to the new number.

3. **Given** `--dry-run`, **when** the script runs, **then** it shows which references would be rewritten and which would be skipped, with the reason.

4. **Given** the collision artifact's own files (frontmatter, body text), **when** the script runs, **then** all references within those files are always rewritten.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- In scope: `fix-collisions.sh` reference rewriting logic
- Out of scope: collision detection (`detect-duplicate-numbers.sh`) — that works correctly
- The fix should handle the common case (worktree creates a duplicate, references are recent) without needing full git archaeology for every reference

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | _pending_ | Initial creation |
