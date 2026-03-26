---
title: "Artifact Number Collision Detection"
artifact: SPEC-158
track: implementable
status: Complete
author: cristos
created: 2026-03-22
last-updated: 2026-03-23
priority-weight: ""
type: feature
parent-epic: EPIC-043
parent-initiative: ""
linked-artifacts:
  - EPIC-010
  - SPEC-042
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
- When collisions are detected during sync, the operator can auto-fix them without manual renumbering.

## External Behavior

**Option A — specwatch integration:** Add a duplicate-number check to `specwatch scan`. For each artifact type, collect all `<TYPE>-NNN` numbers across all phase directories. If any number appears more than once, report it as an error (not a warning).

**Option B — pre-commit hook:** A lightweight pre-commit check that scans staged files for artifact frontmatter and verifies no two staged artifacts share a number. This catches collisions at commit time in the worktree that creates the duplicate.

**Option C — swain-sync gate:** Before swain-sync commits, run collision detection across all artifact directories. When collisions are found, report them with both paths and offer to auto-fix by renumbering the newer artifact (by `created` date) using `next-artifact-number.sh`. Update frontmatter, directory name, and any cross-references in one operation. If the allocator script is not yet available (SPEC-156 incomplete), fall back to detection-only with a manual fix prompt.

**Recommendation:** Implement all three. Specwatch catches existing duplicates. Pre-commit prevents new ones at commit time. Swain-sync catches collisions introduced by merges or concurrent worktrees and offers automated remediation.

## Acceptance Criteria

- **Given** two artifacts with the same number exist in `docs/spec/` (e.g., two `SPEC-042` directories), **when** `specwatch scan` runs, **then** it reports a duplicate-number error with both paths.
- **Given** a staged commit that would introduce a second `EPIC-010` artifact, **when** the pre-commit hook runs, **then** it exits non-zero with a message identifying the collision.
- **Given** no duplicates exist, **when** either check runs, **then** it passes silently (exit 0 or no additional output).
- **Given** a superseded artifact and its replacement share no number, **when** specwatch runs, **then** no false positive is raised.
- **Given** two artifacts with the same number exist after a merge, **when** swain-sync runs, **then** it reports the collision with both paths and offers to auto-fix by renumbering the newer artifact.
- **Given** swain-sync detects a collision and the operator accepts auto-fix, **when** `next-artifact-number.sh` is available, **then** the newer artifact is renumbered (directory, frontmatter `artifact` field, and cross-references in other artifacts' `linked-artifacts`/`depends-on-artifacts`/`addresses` fields).
- **Given** swain-sync detects a collision but `next-artifact-number.sh` is not yet available, **when** the operator is prompted, **then** the collision is reported with manual fix instructions and sync does not proceed until resolved.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Specwatch integration modifies `skills/swain-design/scripts/specwatch.sh`.
- Pre-commit hook added to `.agents/hooks/` or documented for installation.
- Swain-sync integration modifies `skills/swain-sync/SKILL.md` to add a pre-commit collision gate.
- Must handle the case where an artifact exists in multiple phase directories (moved but not committed) — this is normal, not a duplicate.
- Auto-fix renumbering (swain-sync) depends on SPEC-156's `next-artifact-number.sh`; detection works independently.
- Renumbering must update cross-references in other artifacts — not just the colliding artifact's own frontmatter and directory.

## Implementation Approach

1. **Specwatch:** After the existing scan loop, add a pass that collects `<TYPE>-NNN` from all artifact paths, groups by type+number, and reports any group with size > 1.
2. **Pre-commit:** A shell script that inspects `git diff --cached --name-only` for artifact paths, extracts type+number, and checks for duplicates within the staged set and against existing artifacts on disk.
3. **Swain-sync:** Before the commit step, invoke the same collision detection logic. On collision: display both paths, identify the newer artifact by `created` date, and prompt to auto-fix. Auto-fix calls `next-artifact-number.sh` for a fresh number, then renames directory (`git mv`), updates frontmatter, and rewrites cross-references in other artifacts.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-22 | — | Agent-suggested decomposition of EPIC-043 |
| Proposed | 2026-03-23 | — | Extended scope: swain-sync gate with auto-fix via next-artifact-number.sh |
