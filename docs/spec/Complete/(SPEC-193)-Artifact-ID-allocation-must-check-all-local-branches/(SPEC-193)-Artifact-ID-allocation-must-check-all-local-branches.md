---
title: "Artifact ID allocation must check all local branches"
artifact: SPEC-193
track: implementable
status: Complete
author: cristos
created: 2026-03-29
last-updated: 2026-03-31
priority-weight: high
type: bug
parent-epic: ""
parent-initiative: INITIATIVE-013
linked-artifacts:
  - SPEC-192
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Artifact ID allocation must check all local branches

## Problem Statement

When swain-design creates a new artifact, it scans `docs/<type>/` in the current working tree to determine the next available ID number. In a worktree-based workflow, the working tree may have branched before recent commits landed on trunk or other branches. This causes ID collisions — two different artifacts get the same number because the allocation scan didn't see the other branch's artifacts.

## Desired Outcomes

Artifact ID allocation is collision-free across all local branches, even when working in an isolated worktree that branched before the latest artifacts were created.

## External Behavior

**Input:** A request to create a new artifact (e.g., `spec:bug ...`).

**Precondition:** Other local branches (trunk, release, worktree branches) may contain artifacts with higher IDs than the current working tree.

**Output:** The new artifact receives an ID that is strictly greater than the highest ID found across ALL local branches, not just the current HEAD.

## Acceptance Criteria

- AC1: Given a worktree branched from trunk at SPEC-190, and trunk now has SPEC-191, when a new spec is created in the worktree, then it receives SPEC-192 or higher.
- AC2: Given artifacts on multiple worktree branches (e.g., worktree-a has SPEC-195, worktree-b has SPEC-198), when a new spec is created on either branch, then it receives SPEC-196 or higher.
- AC3: The scan checks all local branches (`git branch --list`), not just `HEAD` and `trunk`.
- AC4: The scan completes in under 2 seconds for a repository with 200+ artifacts and 10+ local branches.

## Reproduction Steps

1. Create a worktree from trunk when the highest spec is SPEC-190.
2. On trunk (or another worktree), create SPEC-191 and commit it.
3. In the original worktree, create a new spec.
4. Observe that it is assigned SPEC-191 — a collision.

## Severity

high — ID collisions cause merge conflicts and can silently overwrite artifact content if directory names match.

## Expected vs. Actual Behavior

**Expected:** The ID allocation scan considers all local branches and assigns an ID higher than any existing artifact across the entire local repository.

**Actual:** The scan only reads `docs/<type>/` from the current working tree (current HEAD), missing artifacts on other branches.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC1: worktree branched before trunk advances | next-artifact-id.sh returns 194 (> all existing IDs across branches) | PASS |
| AC2: multiple worktree branches | Script uses git for-each-ref to scan ALL refs/heads/ | PASS |
| AC3: scans all local branches | bash -x confirms git for-each-ref refs/heads/ call | PASS |
| AC4: completes in under 2 seconds | 0.35s with 190+ artifacts and multiple branches | PASS |

## Scope & Constraints

- The fix belongs in the swain-design skill's artifact creation workflow (step 1: "Scan `docs/<type>/` to determine the next available number").
- Consider extracting this into a reusable script (e.g., `.agents/bin/next-artifact-id.sh <type>`) so the logic is testable and consistent across all artifact types.
- Must handle all artifact type prefixes: SPEC, EPIC, INITIATIVE, VISION, SPIKE, ADR, PERSONA, RUNBOOK, DESIGN, JOURNEY, TRAIN.
- Should use `git ls-tree -r --name-only <branch> -- docs/<type>/` to scan each branch without checking it out.
- Detached HEAD worktrees and branches with no `docs/` directory should not cause errors.

## Implementation Approach

Create `.agents/bin/next-artifact-id.sh` that:

1. Accepts an artifact type prefix (e.g., `SPEC`, `EPIC`).
2. Iterates all local branches via `git for-each-ref --format='%(refname:short)' refs/heads/`.
3. For each branch, runs `git ls-tree -r --name-only <branch> -- docs/ | grep '<PREFIX>-[0-9]'` to extract IDs.
4. Also scans the current working tree (`docs/` on disk) to catch uncommitted artifacts.
5. Returns `max(all_ids) + 1`.

Update swain-design step 1 to call this script instead of scanning the local filesystem only.

## Known Gaps

**Known gap (discovered 2026-03-31):** `next-artifact-id.sh` does not detect untracked files in the working tree. An untracked `(SPEC-222)-Doctor-Warn-Only-Check-Auto-Repair-Audit/` folder was not detected, causing a collision when SPEC-226 (originally assigned SPEC-222) was created in the same session. The script only scans committed content across local branches. Consider adding a `git ls-files --others --exclude-standard` pass for untracked artifact folders.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-29 | — | Initial creation — ID collision observed in SPEC-191/192 |
| Complete | 2026-03-30 | — | Retroactive verification — script on trunk, all ACs pass |
