---
title: "swain-sync Lockfile Integration"
artifact: SPIKE-057
track: implementable
status: Proposed
author: cristos
created: 2026-04-04
priority-weight: high
parent-epic: EPIC-056
type: research
swain-do: required
---

# SPIKE-057: swain-sync Lockfile Integration

## Goal

Design and test swain-sync integration with lockfile claiming:
1. Merge trunk → worktree (from inside worktree)
2. Push to remote trunk (from worktree)
3. Mark lockfile `ready_for_cleanup` with commit hash
4. bin/swain verifies + prunes

## Context

**Current swain-sync:**
- Assumes it can `git worktree remove` after merge
- Fails when runtime can't leave worktree directory

**New design:**
- swain-sync does merge + push (all from worktree — git supports this)
- Marks lockfile `ready_for_cleanup=true` with `ready_commit=<hash>`
- bin/swain prunes after runtime exits (verifies no new commits)

## Research Questions

1. **Git operations from worktree:**
   - Does `git merge trunk` work from worktree? (yes, confirmed)
   - Does `git push origin HEAD:trunk` work? (yes, confirmed)
   - Any operations that DON'T work from worktree?

2. **Lockfile update protocol:**
   - Append vs overwrite?
   - Atomic writes (temp file + mv)?
   - What if lockfile doesn't exist?

3. **Commit hash verification:**
   - What if worktree has new commits after ready_for_cleanup?
   - bin/swain should detect + offer re-entry

4. **Error handling:**
   - Merge conflicts → abort, don't mark ready
   - Push rejected → abort, don't mark ready
   - Lockfile write fails → warn, continue

## Acceptance Criteria

- [ ] **SPIKE-057-AC1: Git operations verified**
  - merge trunk works from worktree
  - push to trunk works from worktree
  - List any unsupported operations

- [ ] **SPIKE-057-AC2: Lockfile protocol defined**
  - ready_for_cleanup format
  - Commit hash stamp
  - Atomic write mechanism

- [ ] **SPIKE-057-AC3: bin/swain verification logic**
  - Check commit hash match
  - Handle mismatch (offer re-entry)

- [ ] **SPIKE-057-AC4: Error handling tested**
  - Merge conflicts
  - Push rejection
  - Lockfile write failure

## Implementation Plan

1. **Test git operations** — merge/push from worktree
2. **Design lockfile format** — ready_for_cleanup + commit hash
3. **Implement swain-sync changes** — mark ready after successful merge/push
4. **Implement bin/swain verification** — check hash before prune
5. **Test error scenarios** — conflicts, rejection, write failures

## Evidence

- Git worktree documentation (confirms merge/push work from worktree)
- Current swain-sync implementation
- Lockfile schema from EPIC-056

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-04 | — | Drafted for EPIC-056 |
