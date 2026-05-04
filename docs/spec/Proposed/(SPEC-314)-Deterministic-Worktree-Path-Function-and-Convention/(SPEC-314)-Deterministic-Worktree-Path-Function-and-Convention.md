---
title: "Deterministic Worktree Path Function and Convention"
artifact: SPEC-314
track: implementable
status: Proposed
author: cristos
created: 2026-04-14
last-updated: 2026-04-14
priority-weight: ""
type: feature
parent-epic: EPIC-078
parent-initiative: ""
linked-artifacts:
  - EPIC-063
  - ADR-025
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Deterministic Worktree Path Function and Convention

## Problem Statement

Worktree paths are computed ad-hoc by different callers — `bin/swain`, `swain-do`'s preamble, and `swain-worktree-overlap.sh` each construct paths independently. This produces inconsistent placements: some worktrees land as sibling directories of the project root, others under `.worktrees/` flat, others under `.worktrees/epic/`. No single function owns the convention.

## Desired Outcomes

Agents and scripts call one function to get the worktree path. The path is always `<project-root>/.worktrees/<type>/<slug>`. Cleanup and overlap detection scripts use the same function and find worktrees where expected.

## External Behavior

**Inputs:** artifact type (`epic`, `spec`, `session`) and slug (e.g., `epic-078-deterministic-worktree-placement`).

**Output:** Absolute path: `<project-root>/.worktrees/<type>/<slug>`.

**Preconditions:** `<project-root>/.worktrees/<type>/` directory is created if absent.

**Postconditions:** The returned path is deterministic — calling with the same inputs always returns the same path.

## Acceptance Criteria

1. Given artifact type `epic` and slug `epic-078-deterministic-worktree-placement`, the function returns `<project-root>/.worktrees/epic/epic-078-deterministic-worktree-placement`.
2. Given artifact type `spec` and slug `spec-314-deterministic-worktree-path`, the function returns `<project-root>/.worktrees/spec/spec-314-deterministic-worktree-path`.
3. Given an unknown type, the function returns `<project-root>/.worktrees/other/<slug>`.
4. The function creates intermediate directories if they don't exist.
5. `bin/swain` and `swain-worktree-overlap.sh` use this function instead of constructing paths manually.
6. Existing worktrees outside `.worktrees/` are migrated to the new convention.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| | | |

## Scope & Constraints

- No changes to worktree lifecycle (lockfiles, claiming, teardown) — that stays in EPIC-063's scope.
- The function is a bash script in `.agents/bin/` — no Python dependency for path computation.

## Implementation Approach

1. Create `deterministic-worktree-path.sh` in `.agents/bin/` that computes and optionally creates the path.
2. Update `bin/swain` to source and call this function for worktree creation.
3. Update `swain-worktree-overlap.sh` to use it for path lookups.
4. Write a test script that validates all three type branches and error cases.
5. Migrate any existing worktrees outside `.worktrees/`.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-14 | 88924d4d | Initial creation |