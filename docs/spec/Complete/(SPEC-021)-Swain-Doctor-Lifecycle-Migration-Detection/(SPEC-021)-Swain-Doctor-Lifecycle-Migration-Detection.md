---
title: "swain-doctor Lifecycle Migration Detection"
artifact: SPEC-021
status: Complete
type: enhancement
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
parent-epic: EPIC-008
linked-artifacts:
  - ADR-003
depends-on-artifacts:
  - SPEC-020
implementation-commits: [a59fdd3]
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# swain-doctor Lifecycle Migration Detection

## Problem Statement

After the lifecycle normalization migration (SPEC-020), future sessions need to detect if a project still has artifacts in old phase directories. swain-doctor should check for stale directories and offer migration guidance.

## External Behavior

### Preflight check addition

Add to `swain-preflight.sh`:
- Scan `docs/*/` for old phase directory names: `Draft/`, `Planned/`, `Review/`, `Approved/`, `Testing/`, `Implemented/`, `Adopted/`, `Deprecated/`, `Archived/`, `Sunset/`
- If any non-empty old directories found, exit 1 (triggering full doctor run)

### Doctor remediation

When stale directories are detected:
1. List the old directories and their artifact count
2. Explain the ADR-003 normalization
3. Offer to run the migration script from SPEC-020
4. If migration script unavailable, provide manual `git mv` instructions

## Acceptance Criteria

- **Given** artifacts exist in `docs/spec/Draft/`, **when** preflight runs, **then** it exits 1
- **Given** no old phase directories exist, **when** preflight runs, **then** this check passes silently
- **Given** old directories detected, **when** swain-doctor runs, **then** it explains ADR-003 and offers migration
- **Given** empty old directories remain after migration, **when** preflight runs, **then** they are NOT flagged (only non-empty directories matter)

## Scope & Constraints

- Only adds detection and guidance — actual migration is SPEC-020's script
- Must not false-positive on the `Abandoned/` directory (it's unchanged)
- Must not false-positive on `Active/` or `Complete/` (they're unchanged)

## Implementation Approach

1. Add old-directory scan to `swain-preflight.sh`
2. Add remediation handler to `swain-doctor` skill
3. Test with both clean and stale project states

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-13 | 232369c | Initial creation |
| Complete | 2026-03-13 | a59fdd3 | Implementation verified |
