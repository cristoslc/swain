---
title: "finishing-a-development-branch: Merge Locally fails in worktrees"
artifact: SPEC-183
track: implementable
status: Active
author: operator
created: 2026-03-28
last-updated: 2026-03-28
priority-weight: high
type: bug
parent-epic: ""
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# finishing-a-development-branch: Merge Locally fails in worktrees

## Problem Statement

The `finishing-a-development-branch` skill's Option 1 (Merge Locally) runs `git checkout <base-branch>`, which fatally errors when executed inside a git worktree because the base branch is already checked out in the main worktree. Git enforces a one-branch-per-worktree constraint.

## Desired Outcomes

Worktree-based development sessions can merge locally without manual intervention. The skill correctly detects a worktree context and uses a merge strategy that doesn't require checking out the target branch.

## External Behavior

**Precondition:** Agent is working inside a git worktree with a session branch checked out; trunk is checked out in the main worktree.

**Current behavior:** Skill emits `git checkout trunk && git merge <branch>`, git exits 128 with `fatal: 'trunk' is already used by worktree at '...'`.

**Expected behavior:** Skill detects worktree context and uses an alternative merge strategy (e.g., `git push origin HEAD:<base-branch>` as swain-sync already does, or `git -C <main-worktree> merge <branch>`).

## Acceptance Criteria

- **AC-1:** Given the agent is in a worktree, when Option 1 (Merge Locally) is selected, then the skill does not emit `git checkout <base-branch>`.
- **AC-2:** Given the agent is in a worktree, when Option 1 is selected, then the merge completes successfully using a worktree-safe strategy.
- **AC-3:** Given the agent is NOT in a worktree (normal repo), when Option 1 is selected, then existing `git checkout` behavior is preserved unchanged.
- **AC-4:** The worktree detection method is consistent with the detection used in swain-sync (`git rev-parse --show-toplevel` vs `git worktree list`).

## Reproduction Steps

1. Create a worktree: `git worktree add ../worktree-test -b session-branch`
2. Make a commit in the worktree
3. Invoke `/finishing-a-development-branch` and select Option 1 (Merge Locally)
4. Observe: `git checkout trunk` fails with exit code 128

## Severity

high — blocks the primary worktree merge-back workflow; operator must work around manually.

## Expected vs. Actual Behavior

**Expected:** Merge Locally completes and the session branch is merged into trunk.

**Actual:** `fatal: 'trunk' is already used by worktree at '/Users/cristos/Documents/code/swain'`

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Fix is scoped to `finishing-a-development-branch/SKILL.md` Option 1 logic only.
- Must not change Option 2 (PR) or Option 3 (cleanup) behavior.
- Should reuse the same worktree-safe push pattern already proven in swain-sync (`git push origin HEAD:$TRUNK`), or use `git -C` to run merge from the main worktree directory.
- Non-goal: adding worktree awareness to other skills (swain-sync already handles this correctly).

## Implementation Approach

1. Add worktree detection to Option 1's code block (check if `git worktree list --porcelain` shows multiple worktrees, or compare `git rev-parse --show-toplevel` with main worktree path).
2. When in a worktree, replace `git checkout <base-branch> && git merge <feature-branch>` with the worktree-safe alternative.
3. Preserve the existing flow for non-worktree repos.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-28 | — | Initial creation |
