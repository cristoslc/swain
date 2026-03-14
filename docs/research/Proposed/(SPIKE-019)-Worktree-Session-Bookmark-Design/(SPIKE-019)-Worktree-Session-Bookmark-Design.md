---
title: "Worktree Session Bookmark Design"
artifact: SPIKE-019
track: container
status: Proposed
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
parent-epic: EPIC-016
question: "What is the minimal bookmark schema change and restore-path logic needed to make swain-session worktree-aware without breaking existing bookmarks or adding operator friction?"
gate: Pre-implementation
risks-addressed:
  - Bookmark restore silently resolving against wrong worktree after EPIC-015 rollout
  - Schema changes breaking existing bookmark files for operators upgrading mid-project
evidence-pool: ""
---

# Worktree Session Bookmark Design

## Summary

<!-- Final-pass section: populated when transitioning to Complete.
     Lead with the verdict (Go / No-Go / Hybrid / Conditional), then
     1-3 sentences distilling the key finding and recommended next step.
     During Active phase, leave this section empty — keep the document
     evidence-first while research is in progress. -->

## Question

What is the minimal bookmark schema change and restore-path logic needed to make swain-session worktree-aware without breaking existing bookmarks or adding operator friction?

## Go / No-Go Criteria

**Go** if the spike produces:
1. A concrete proposed bookmark schema (YAML/JSON shape with the new `worktree` field and all required sub-fields)
2. A decision on restore-path behavior when the bookmarked worktree is missing (warn-and-fallback vs. hard-stop vs. auto-re-anchor)
3. Confirmation that the detection mechanism (`git worktree list --porcelain` or equivalent) is available in the environments swain targets
4. A backward-compatibility ruling: do existing bookmark files need migration, or is the new field purely additive?

**No-Go** if:
- No reliable way to detect the current worktree path at bookmark-write time (blocks the whole approach)
- Schema change requires breaking existing bookmarks with no clean migration path

**Pivot:** If worktree detection is unreliable, investigate embedding only the branch name (not the path) and resolving at restore time via `git worktree list`.

## Pivot Recommendation

If path-based anchoring is unreliable (e.g., operators move worktrees), design the schema around branch name as the primary key and use `git worktree list --porcelain` at restore time to resolve the current path for that branch. This is weaker on repo-less environments but avoids stale-path errors for the common case.

## Findings

### Current bookmark format

Investigate what swain-bookmark.sh currently writes. Key questions:
- What fields are in the current bookmark schema?
- Where are bookmarks persisted (file path, format)?
- Is the write path in a single script or spread across skill invocations?

### Worktree detection at write time

Determine how to detect whether the current working directory is inside a worktree and which worktree it is:
- `git worktree list --porcelain` — lists all worktrees with path, HEAD, and branch
- `git rev-parse --show-toplevel` — gives the root of the current checkout (differs per worktree)
- `git rev-parse --absolute-git-dir` — gives `.git` path; for worktrees this is `.git/worktrees/<name>`

Verify which of these is available and deterministic across macOS/Linux shells.

### Restore-path behaviors to evaluate

1. **Warn-and-fallback:** If bookmarked worktree is missing, warn and restore in main tree
2. **Hard-stop:** If bookmarked worktree is missing, abort and prompt operator
3. **Auto-re-anchor:** Find the branch in another worktree (or create one) automatically

Assess operator friction and risk for each.

### Backward compatibility

Determine whether the `worktree` field can be purely additive (absent = assume main tree) or whether a migration script is needed for existing bookmark files.

### swain-doctor integration

Confirm that `git worktree list` output is parseable to cross-reference bookmark paths against live worktrees. Assess cost of running this check at session start vs. only on restore.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Initial creation under EPIC-016 |
