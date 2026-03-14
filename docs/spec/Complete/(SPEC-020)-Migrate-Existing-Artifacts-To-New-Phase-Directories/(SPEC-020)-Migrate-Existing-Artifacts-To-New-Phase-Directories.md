---
title: "Migrate Existing Artifacts to New Phase Directories"
artifact: SPEC-020
track: implementable
status: Complete
type: enhancement
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
parent-epic: EPIC-008
linked-artifacts:
  - ADR-003
depends-on-artifacts:
  - SPEC-018
  - SPEC-019
implementation-commits: [2da897b]
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Migrate Existing Artifacts to New Phase Directories

## Problem Statement

~54 existing artifacts live in phase subdirectories using old names (Draft, Planned, Approved, Implemented, Adopted, etc.). ADR-003 renames these phases. All artifacts must be moved to new directories and have their frontmatter status field updated.

## External Behavior

### Migration script

A Python migration script that:
1. Scans all `docs/<type>/` directories for artifact folders
2. Maps old phase directory to new phase name per ADR-003's mapping table
3. Updates the artifact's `status` field in frontmatter
4. Uses `git mv` to move the folder to the new phase subdirectory
5. Creates new phase subdirectories as needed
6. Removes empty old phase directories
7. Supports `--dry-run` for preview

### Phase mapping (from ADR-003 / EPIC-008)

| Old directory | New directory | Notes |
|---------------|---------------|-------|
| Draft/ | Proposed/ | All types |
| Planned/ | Proposed/ | SPIKE |
| Review/ | (dropped) | Merge into Proposed/ |
| Approved/ | Ready/ | SPEC only |
| Active/ | Active/ | No change |
| Testing/ | NeedsManualTest/ | SPEC only |
| Implemented/ | Complete/ | SPEC only |
| Adopted/ | Active/ | ADR only |
| Complete/ | Complete/ | No change |
| Deprecated/ | Retired/ | All types |
| Archived/ | Retired/ | Merge |
| Sunset/ | Retired/ | Merge |
| Abandoned/ | Abandoned/ | No change |

### Index files

After migration, regenerate all `list-<type>.md` index files with correct phase tables.

## Acceptance Criteria

- **Given** the migration script runs, **when** all artifacts are processed, **then** every artifact's directory matches its phase name per ADR-003
- **Given** an artifact in `Draft/`, **when** migrated, **then** it moves to `Proposed/` and its status field reads "Proposed"
- **Given** an ADR in `Adopted/`, **when** migrated, **then** it moves to `Active/` and its status reads "Active"
- **Given** a SPEC in `Implemented/`, **when** migrated, **then** it moves to `Complete/` and its status reads "Complete"
- **Given** `--dry-run` flag, **when** the script runs, **then** it prints changes without modifying files
- **Given** migration completes, **when** specwatch runs, **then** it reports no stale references from old phase names
- **Given** migration completes, **when** specgraph runs, **then** it correctly resolves all artifacts

## Scope & Constraints

- Must use `git mv` to preserve history
- Must be idempotent (running twice is safe)
- Old empty directories should be cleaned up
- Index files must be regenerated after migration

## Implementation Approach

1. Write Python migration script with ADR-003 phase mapping
2. Dry-run to verify correctness
3. Execute migration
4. Regenerate all list-*.md index files
5. Run specwatch and specgraph to validate
6. Commit as a single atomic change

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-13 | 232369c | Initial creation |
| Complete | 2026-03-13 | a59fdd3 | Implementation verified |
