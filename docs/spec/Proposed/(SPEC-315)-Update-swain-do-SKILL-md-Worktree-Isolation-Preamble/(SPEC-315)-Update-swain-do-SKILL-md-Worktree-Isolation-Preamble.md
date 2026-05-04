---
title: "Update swain-do SKILL.md Worktree Isolation Preamble"
artifact: SPEC-315
track: implementable
status: Proposed
author: cristos
created: 2026-04-14
last-updated: 2026-04-14
priority-weight: ""
type: enhancement
parent-epic: EPIC-078
parent-initiative: ""
linked-artifacts:
  - SPEC-314
depends-on-artifacts:
  - SPEC-314
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Update swain-do SKILL.md Worktree Isolation Preamble

## Problem Statement

The swain-do SKILL.md worktree isolation preamble instructs agents to create worktrees with `git worktree add` but does not specify where they should be placed. Agents default to sibling directories of the project root, producing inconsistent paths and requiring manual cleanup.

## Desired Outcomes

Agents following the swain-do preamble always create worktrees at deterministic paths under `.worktrees/<type>/`. No guesswork. No sibling-directory pollution.

## External Behavior

**Inputs:** The swain-do preamble reads `SPEC_ID` or `EPIC_ID` and determines the artifact type and slug.

**Output:** The preamble calls `deterministic-worktree-path.sh` to compute the worktree path before running `git worktree add`.

**Preconditions:** `.agents/bin/deterministic-worktree-path.sh` exists and is executable.

**Postconditions:** Worktree is created under `.worktrees/<type>/<slug>`.

## Acceptance Criteria

1. The swain-do SKILL.md preamble references `deterministic-worktree-path.sh` for path computation instead of inline path construction.
2. The preamble specifies the three type categories (`epic`, `spec`, `session`) and their corresponding `.worktrees/` subdirectories.
3. No passage in SKILL.md instructs agents to create worktrees as sibling directories of the project root.
4. The worktree isolation detection step (`IN_WORKTREE` check) is unchanged — only the creation path changes.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| | | |

## Scope & Constraints

- Only updates the SKILL.md prose — no script changes (those are SPEC-314).
- Does not change the overlap detection logic or lockfile claiming.

## Implementation Approach

1. Edit the "Worktree isolation preamble" section of swain-do SKILL.md to replace inline `git worktree add` calls with a call to `deterministic-worktree-path.sh`.
2. Add a type mapping table (artifact ID prefix → type → subdirectory).
3. Update the example command to show the correct path convention.
4. Remove any language that suggests sibling-directory placement.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-14 | 88924d4d | Initial creation |