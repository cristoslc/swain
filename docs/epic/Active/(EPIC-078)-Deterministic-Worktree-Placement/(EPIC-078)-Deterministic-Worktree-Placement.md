---
title: "Deterministic Worktree Placement"
artifact: EPIC-078
track: container
status: Active
author: cristos
created: 2026-04-14
last-updated: 2026-04-14
parent-vision:
  - VISION-001
parent-initiative: ""
priority-weight: medium
success-criteria:
  - All worktree-creating code paths use a single deterministic function to compute worktree paths
  - Worktrees are always placed under <project-root>/.worktrees/ with type-based subdirectories (epic/, spec/, session/)
  - No worktrees are created as sibling directories of the project root
  - swain-do SKILL.md worktree isolation preamble references the deterministic placement convention
  - swain-worktree-overlap.sh reports worktree paths under .worktrees/
  - Existing misplaced worktrees (outside .worktrees/) are migrated and git worktree list is clean
depends-on-artifacts: []
addresses: []
evidence-pool: ""
linked-artifacts:
  - EPIC-063
  - ADR-025
---

# Deterministic Worktree Placement

## Goal / Objective

Establish a single, deterministic convention for where git worktrees are created within the swain project. Today, worktrees land in inconsistent locations — sibling directories of the project root, flat under `.worktrees/`, or under type subdirectories like `.worktrees/epic/`. This makes cleanup, overlap detection, and session resumption fragile.

## Desired Outcomes

- Agents and scripts always know where a worktree will be without querying git.
- Cleanup (swain-teardown, swain-doctor) can find and remove worktrees by convention.
- The `.worktrees/` directory has a predictable structure: `<type>/<slug>` (e.g., `.worktrees/epic/epic-078-deterministic-worktree-placement`).
- The swain-do skill preamble no longer guesses — it delegates to a shared function.

## Progress

<!-- Auto-populated from session digests. See progress.md for full log. -->

## Scope Boundaries

### In scope

- A shared bash function (or script) that computes the deterministic worktree path given a type and slug.
- Updating swain-do SKILL.md to reference the deterministic placement convention instead of ad-hoc `git worktree add` calls.
- Updating `swain-worktree-overlap.sh` and `bin/swain` to use the shared function.
- Migration guide or script for existing misplaced worktrees.

### Out of scope

- Changing the worktree lifecycle (creation, teardown, lockfile claiming) — that's EPIC-063.
- Changing session-based worktree naming conventions beyond path layout.

## Child Specs

| Spec | Title | Dependency |
|------|-------|------------|
| SPEC-314 | Deterministic Worktree Path Function and Convention | None |
| SPEC-315 | Update swain-do SKILL.md Worktree Isolation Preamble | SPEC-314 |

## Key Dependencies

- EPIC-063 (Worktree Isolation Redesign) — established the worktree router pattern; this EPIC refines the placement convention it introduced.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-14 | 88924d4d | Initial creation |