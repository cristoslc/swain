---
title: "swain-doctor: stale worktree detection"
artifact: SPEC-044
status: Ready
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
type: enhancement
parent-epic: EPIC-015
linked-artifacts:
  - ADR-005
depends-on-artifacts:
  - SPEC-039
  - SPEC-043
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# swain-doctor: stale worktree detection

## Problem Statement

When an agent crashes or is interrupted mid-task, the linked worktree it was using is never pruned (swain-sync never ran). Over time these stale worktrees accumulate: `git worktree list` grows noisy, disk usage creeps up, and future agents may be confused by leftover branch state. swain-doctor runs at session start and is the natural place to surface this condition to the operator.

## External Behavior

During swain-doctor's session-start health check:

1. Run `git worktree list --porcelain` to enumerate all linked worktrees.
2. For each linked worktree (excluding the main worktree), check whether its directory still exists and whether its branch has unmerged commits relative to `main`.
3. Classify each as:
   - **Stale (merged):** directory exists, branch fully merged into main — safe to remove.
   - **Stale (orphaned):** directory does not exist — git ref dangling, `git worktree prune` will clean it.
   - **Active (unmerged):** directory exists, branch has commits not in main — warn but do not remove.
4. Report findings in swain-doctor's output. For stale worktrees, provide the exact commands to clean up. Do not auto-remove — operator confirms.

**Postconditions:**
- Operator is informed of stale worktrees and given cleanup commands.
- No worktrees are removed without operator action.
- Clean repos (no linked worktrees, or all active) produce no output from this check.

## Acceptance Criteria

**AC-1: No linked worktrees → silent**
- Given: The repo has no linked worktrees.
- When: swain-doctor runs the worktree check.
- Then: No output is produced for this check.

**AC-2: Orphaned worktree (missing directory) → report + prune command**
- Given: `git worktree list` shows a linked worktree whose directory no longer exists on disk.
- When: swain-doctor runs.
- Then: swain-doctor reports the orphaned entry and provides `git worktree prune` as the cleanup command.

**AC-3: Stale worktree (merged branch) → report + remove command**
- Given: A linked worktree exists on disk and its branch is fully merged into `main`.
- When: swain-doctor runs.
- Then: swain-doctor reports the worktree as safe to remove and provides `git worktree remove <path> && git branch -d <branch>` as the cleanup command.

**AC-4: Active worktree (unmerged) → warn only**
- Given: A linked worktree exists on disk and its branch has commits not yet in `main`.
- When: swain-doctor runs.
- Then: swain-doctor warns that the worktree has unmerged work and lists the branch name and commit count. It does not suggest removal.

**AC-5: Check is non-destructive**
- Given: Any worktree state.
- When: swain-doctor runs.
- Then: No worktrees are removed, no branches are deleted. All output is advisory.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC-1: No worktrees → silent | | |
| AC-2: Orphaned directory → prune command | | |
| AC-3: Merged branch → remove command | | |
| AC-4: Unmerged → warn only | | |
| AC-5: Non-destructive | | |

## Scope & Constraints

**In scope:** New check added to swain-doctor's session-start scan. Output follows swain-doctor's existing `WARN`/`INFO` conventions.

**Out of scope:** Automatic removal of any worktree — operator always confirms. Integration with swain-sync's pruning step (that's runtime, not session-start).

**Depends on:** SPEC-039 and SPEC-043 should be complete first — this spec cleans up after failures in those flows, so the flows should exist before detecting their leftovers.

## Implementation Approach

Add a worktree health section to swain-doctor's SKILL.md (or its preflight script, whichever is appropriate for the check weight):

```bash
git worktree list --porcelain | awk '/^worktree /{path=$2} /^branch /{branch=$2} /^$/{print path, branch}'
```

For each linked worktree:
- Check directory exists: `[ -d "$path" ]`
- Check branch merged: `git merge-base --is-ancestor "$branch" origin/main`

Classify and emit structured output per swain-doctor conventions.

TDD cycles:
1. RED: test that a repo with no linked worktrees produces no worktree-check output → GREEN: guard on worktree count
2. RED: test that a missing-directory entry triggers orphan report with prune command → GREEN: add directory existence check
3. RED: test that a merged branch triggers safe-remove report → GREEN: add merge-base check
4. RED: test that an unmerged branch triggers warn-only output → GREEN: differentiate merged vs. unmerged path

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Initial creation under EPIC-015; depends on SPEC-039 and SPEC-043 |
| Ready | 2026-03-14 | — | Approved |
