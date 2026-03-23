---
title: "Artifact Number Collision Detection"
artifact: SPEC-158
track: implementable
status: Proposed
author: cristos
created: 2026-03-22
last-updated: 2026-03-22
priority-weight: ""
type: feature
parent-epic: EPIC-043
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts:
  - SPEC-156
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Artifact Number Collision Detection

## Problem Statement

Even with a centralized allocator ([SPEC-156](../(SPEC-156)-Next-Artifact-Number-Script/(SPEC-156)-Next-Artifact-Number-Script.md)), race conditions remain possible: two worktrees could call the script at the same instant and get the same number before either commits. A safety net is needed to catch collisions before they reach trunk.

## Desired Outcomes

- Duplicate artifact numbers are caught before they merge to trunk — operators never encounter them in the mainline.
- The detection is automatic, not reliant on the operator remembering to check.

## External Behavior

**Option A — specwatch integration:** Add a duplicate-number check to `specwatch scan`. For each artifact type, collect all `<TYPE>-NNN` numbers across all phase directories. If any number appears more than once, report it as an error (not a warning).

**Option B — pre-commit hook:** A lightweight pre-commit check that scans staged files for artifact frontmatter and verifies no two staged artifacts share a number. This catches collisions at commit time in the worktree that creates the duplicate.

**Recommendation:** Implement both. Specwatch catches existing duplicates (historical or from merges). Pre-commit prevents new ones from being committed.

## Acceptance Criteria

- **Given** two artifacts with the same number exist in `docs/spec/` (e.g., two `SPEC-042` directories), **when** `specwatch scan` runs, **then** it reports a duplicate-number error with both paths.
- **Given** a staged commit that would introduce a second `EPIC-010` artifact, **when** the pre-commit hook runs, **then** it exits non-zero with a message identifying the collision.
- **Given** no duplicates exist, **when** either check runs, **then** it passes silently (exit 0 or no additional output).
- **Given** a superseded artifact and its replacement share no number, **when** specwatch runs, **then** no false positive is raised.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Specwatch integration modifies `skills/swain-design/scripts/specwatch.sh`.
- Pre-commit hook added to `.agents/hooks/` or documented for installation.
- Must handle the case where an artifact exists in multiple phase directories (moved but not committed) — this is normal, not a duplicate.
- Does not auto-fix collisions — it reports them for the operator to resolve.

## Implementation Approach

1. **Specwatch:** After the existing scan loop, add a pass that collects `<TYPE>-NNN` from all artifact paths, groups by type+number, and reports any group with size > 1.
2. **Pre-commit:** A shell script that inspects `git diff --cached --name-only` for artifact paths, extracts type+number, and checks for duplicates within the staged set and against existing artifacts on disk.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-22 | — | Agent-suggested decomposition of EPIC-043 |
