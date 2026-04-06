---
title: "Title-Based Artifact Migration"
artifact: EPIC-064
track: container
status: Active
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
parent-vision: VISION-001
parent-initiative: INITIATIVE-002
priority-weight: high
success-criteria:
  - All new artifacts use the TYPE-title-slug-DDDDhMM identifier format from ADR-035
  - All existing ~1,300 artifacts are migrated to title-based identifiers with canonical paths
  - Lifecycle phase transitions use symlinks instead of git mv
  - All tooling (chart, specwatch, skills) recognizes both old and new formats during transition
  - swain-doctor detects unmigrated artifacts and offers migration
  - Compat symlinks from old serial-ID paths resolve to new canonical paths
  - Operator has made and recorded a project-wide decision on compat symlink retention
depends-on-artifacts:
  - ADR-035
addresses: []
evidence-pool: ""
---

# Title-Based Artifact Migration

## Goal / Objective

Move swain from serial IDs to title-based IDs per [ADR-035](../../adr/Active/(ADR-035)-Title-Based-Artifact-Identifiers/(ADR-035)-Title-Based-Artifact-Identifiers.md). Artifacts get stable paths that do not change. Lifecycle dirs hold symlinks instead of files.

## Desired Outcomes

Operators see meaningful names in paths, references, and tooling output. Agents stop wasting context on ID lookups. Collision scripts are retired. Phase transitions become a symlink swap instead of a rename-and-relink cascade.

## Progress

<!-- Auto-populated from session digests. See progress.md for full log. -->

## Scope Boundaries

**In scope:**
- Epoch storage in project settings.
- ID generation script: title and timestamp to new format.
- Canonical paths that never move. Lifecycle dirs hold symlinks.
- Batch migration: rename, rewrite references, and create compat symlinks.
- Dual-format tooling during the transition window.
- Doctor detection of unmigrated artifacts with a migration offer.
- Doctor compat symlink report with a keep-or-prune prompt.
- Skill and tooling updates for chart, specwatch, and all swain skills.
- Hierarchy view updates for DESIGN-013 and DESIGN-014.
- Collision infrastructure retirement after migration.

**Out of scope:**
- Changes to artifact types or lifecycle phases.
- Frontmatter changes beyond the ID field.
- CI or GitHub Actions work.

## Child Specs

To be decomposed. Likely areas:
1. Epoch storage and ID generation script.
2. Canonical paths and lifecycle symlink mechanism.
3. Batch migration script with rename, rewrite, and compat symlinks.
4. Dual-format support in chart, specwatch, and graph tooling.
5. Skill updates for the new format.
6. Doctor hooks for migration detection and compat symlink lifecycle.
7. Hierarchy view updates for DESIGN-013 and DESIGN-014.
8. Collision infrastructure retirement.

## Key Dependencies

- ADR-035 defines the identifier format, canonical path layout, and migration needs.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-06 | — | Initial creation |
