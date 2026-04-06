---
title: "Trunk + Release Branch Model With Merge-and-Retry Landing"
artifact: SPEC-114
track: implementable
status: Complete
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
type: feature
parent-epic: ""
parent-initiative: INITIATIVE-005
linked-artifacts:
  - ADR-011
  - ADR-012
  - ADR-013
  - SPIKE-022
depends-on-artifacts:
  - ADR-011
  - ADR-013
addresses: []
trove: "multi-agent-collision-vectors"
source-issue: ""
swain-do: required
---

# Trunk + Release Branch Model With Merge-and-Retry Landing

## Problem Statement

Swain's current branch model uses `main` as both the development target and the distribution channel. [ADR-011](../../../adr/Active/(ADR-011)-Worktree-Landing-Via-Merge-With-Retry/(ADR-011)-Worktree-Landing-Via-Merge-With-Retry.md) replaces rebase with merge for worktree landing, which introduces merge commits on the development branch. [ADR-013](../../../adr/Active/(ADR-013)-Release-Branch-With-Squash-Merge-From-Trunk/(ADR-013)-Release-Branch-With-Squash-Merge-From-Trunk.md) separates development from distribution by introducing a `trunk` + `release` branch model. This SPEC implements both decisions and the one-time migration.

## External Behavior

**Before:**
- Single branch: `main` (default, development, and distribution)
- Worktree landing: rebase onto `origin/main`, push `HEAD:main`, stop on rejection
- `npx skills add cristoslc/swain` installs from `main`

**After:**
- Two branches: `trunk` (development) and `release` (default, distribution)
- Worktree landing: merge `origin/trunk`, run tests, push `HEAD:trunk`, retry on rejection (max 3 attempts)
- `npx skills add cristoslc/swain` installs from `release` (squash-merged from trunk at release time)
- `swain-release` cuts a release by: tagging trunk, squash-merging trunk into release, tagging release, pushing both

**Inputs:**
- `swain-sync` in a worktree: detects worktree context, merges (not rebases) `origin/trunk`, tests, pushes, retries on rejection
- `swain-release`: operator invokes to cut a release from trunk to release
- `swain-init`: configures new repos with `trunk` + `release` branch model
- `swain-dispatch`: targets `trunk` for agent work

**Outputs:**
- Worktree agents land on `trunk` via merge-and-retry without operator intervention
- `release` branch receives squash-merged snapshots at release time
- Tags exist on trunk (for lifecycle traceability per [ADR-012](../../../adr/Active/(ADR-012)-Lifecycle-Hashes-Must-Be-Reachable-From-Main/(ADR-012)-Lifecycle-Hashes-Must-Be-Reachable-From-Main.md))

## Acceptance Criteria

### AC1: Worktree landing uses merge with retry

**Given** a worktree agent completing on its branch while trunk has advanced (another agent already landed)
**When** swain-sync runs in the worktree
**Then** it merges `origin/trunk` (not rebase), runs tests on the merged result, pushes `HEAD:trunk`, and retries up to 3 times on non-fast-forward rejection

### AC2: Merge conflicts surface explicitly

**Given** two agents modified overlapping regions of the same file
**When** the second agent's swain-sync attempts to merge
**Then** git raises a merge conflict (not a silent auto-resolution), and the agent reports the conflict to the operator

### AC3: swain-release squash-merges trunk into release

**Given** work has been merged to trunk since the last release
**When** the operator invokes swain-release
**Then** it tags trunk, squash-merges trunk into release, tags release, and pushes both branches and tags

### AC4: release is the GitHub default branch

**Given** the migration has been applied
**When** a user runs `npx skills add cristoslc/swain`
**Then** they receive the content from the `release` branch (the latest squash-merged release)

### AC5: All references updated from main to trunk

**Given** the migration has been applied
**When** any swain skill, ADR, or script references the development branch
**Then** it references `trunk`, not `main`

### AC6: swain-init configures new repos with trunk + release

**Given** a user runs swain-init on a new project
**When** branch setup is performed
**Then** the project is configured with `trunk` as the development branch and `release` as the default branch (or the user is informed of the recommended model)

### AC7: Lifecycle hashes remain reachable

**Given** lifecycle tables reference commit hashes from agent worktree branches
**When** those branches are merged (not squash-merged) to trunk and the worktree is pruned
**Then** all stamped hashes are reachable via `git log trunk`

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC1: Worktree landing uses merge with retry | Worktree agent test: merge commit with 2 parents confirmed (commit 5ef5fbe), push to trunk succeeded | Pass |
| AC2: Merge conflicts surface explicitly | Conflict in SPEC-114.md surfaced during AC1 test — agent stopped and reported, did not auto-resolve | Pass |
| AC3: swain-release squash-merges trunk into release | Squash-merge test: 6 commits collapsed to 1 commit with 1 parent (not merge commit) on temp branch | Pass |
| AC4: release is GitHub default branch | gh api PATCH confirmed default_branch=release during migration | Pass |
| AC5: All references updated from main to trunk | swain-sync, swain-doctor, swain-status, swain-session updated; grep confirms no active origin/main refs in skills/ | Pass |
| AC6: swain-init configures trunk+release | Phase 2.5 added to swain-init SKILL.md with branch model guidance and migration script reference | Pass |
| AC7: Lifecycle hashes remain reachable | Merge-based landing preserves commits on trunk; ADR-012 codified the invariant | Pass |

## Scope & Constraints

**In scope:**
- swain-sync: replace rebase with merge, add retry loop (per ADR-011)
- swain-release: add squash-merge from trunk to release workflow
- swain-init: configure trunk + release model for new repos
- swain-dispatch: update branch targets from main to trunk
- One-time migration script: rename main → trunk, create release, set default on GitHub
- Update all references to `main` in skill files, ADRs, scripts, CI workflows, AGENTS.md

**Out of scope:**
- Changing the `npx skills add` command itself (that's external tooling)
- Implementing merge queue or CI integration (that's a separate concern)
- Changing how non-worktree swain-sync works (only the worktree landing path changes)

**Constraints:**
- Must not break existing installs — `npx skills add cristoslc/swain` must continue to work throughout migration
- Lifecycle hash reachability invariant ([ADR-012](../../../adr/Active/(ADR-012)-Lifecycle-Hashes-Must-Be-Reachable-From-Main/(ADR-012)-Lifecycle-Hashes-Must-Be-Reachable-From-Main.md)) must be preserved
- Migration must be reversible if issues are discovered

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | 88591ca | Created from ADR-011, ADR-012, ADR-013 |
| InProgress | 2026-03-20 | -- | All 6 tasks implemented via parallel worktree agents |
| NeedsManualTest | 2026-03-20 | af0c847 | Migration script executed; awaiting manual verification |
| Complete | 2026-03-20 | 5c92f0b | All 7 ACs pass — verified via subagent testing |
