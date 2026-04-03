---
title: "Retro ID renumbering migration"
artifact: SPEC-252
track: implementable
status: Active
author: operator
created: 2026-04-03
last-updated: 2026-04-03
priority-weight: medium
type: enhancement
parent-epic: ""
parent-initiative: INITIATIVE-002
linked-artifacts:
  - ADR-028
  - ADR-027
  - SPEC-225
depends-on-artifacts: []
addresses:
  - ADR-028
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Retro ID renumbering migration

## Problem Statement

Retro artifacts use date-slug IDs (`RETRO-2026-03-22-overnight-sweep`) instead of the numeric format every other type uses (`RETRO-001`). This creates special cases in type extraction, folder naming, ID allocation, and every tool that parses artifact IDs. ADR-028 decides that retros must use numeric IDs.

29 existing retros need renumbering and foldering (per ADR-027).

## Desired Outcomes

1. All existing retros have numeric IDs (`RETRO-001` through `RETRO-029`), assigned in chronological order by `created:` date.
2. All retros live in folders per ADR-027: `docs/swain-retro/(RETRO-NNN)-Title/(RETRO-NNN)-Title.md`.
3. Cross-references in other artifacts (`linked-artifacts`, `depends-on-artifacts`) are updated to the new IDs.
4. `next-artifact-id.sh RETRO` returns 30 after migration.
5. `swain-retro` skill creates new retros with numeric IDs.

## External Behavior

**Migration script** (`migrate-retro-ids.sh` or inline in doctor):

For each retro in `docs/swain-retro/`, sorted by `created:` date:
1. Assign the next sequential number starting from 001.
2. Update `artifact:` in frontmatter to `RETRO-NNN`.
3. Create the canonical folder: `docs/swain-retro/(RETRO-NNN)-Title/`.
4. `git mv` the file into the folder with the canonical name.
5. Scan all artifacts for references to the old ID in `linked-artifacts`, `depends-on-artifacts`, and body text. Replace with the new ID.

**swain-retro skill update:**

The retro creation workflow must use `next-artifact-id.sh RETRO` for ID allocation instead of deriving from the date and slug.

## Acceptance Criteria

**Given** the migration script runs,
**When** it completes,
**Then** every retro has a numeric `artifact:` field matching `RETRO-\d+` and lives in a `(RETRO-NNN)-Title/` folder.

**Given** another artifact references `RETRO-2026-03-22-overnight-autonomous-artifact-sweep` in `linked-artifacts`,
**When** migration runs,
**Then** that reference is updated to the new numeric ID (e.g., `RETRO-001`).

**Given** a new retro is created after migration,
**When** `swain-retro` runs,
**Then** the retro gets the next available numeric ID from `next-artifact-id.sh`.

**Given** `next-artifact-id.sh RETRO` runs after migration,
**When** output is checked,
**Then** it returns `30` (one past the 29 migrated retros).

## Scope & Constraints

- Migration must use `git mv` to preserve history.
- The old date-slug IDs must not appear in any frontmatter after migration.
- The `_extract_type` regex fix from SPEC-249 stays — it handles both formats and is correct either way.
- This can run alongside or after the flat-file migration in SPEC-225. Both are foldering operations but this one also renumbers.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-03 | -- | Initial creation |
