---
title: "Numeric Retro Artifact IDs"
artifact: ADR-028
track: standing
status: Active
author: Cristos L-C
created: 2026-04-03
last-updated: 2026-04-03
linked-artifacts:
  - ADR-027
  - SPEC-252
depends-on-artifacts: []
evidence-pool: ""
---

# Numeric Retro Artifact IDs

## Context

Every artifact type in swain uses numeric IDs: `SPEC-001`, `EPIC-042`, `ADR-026`. Retros are the exception. They use date-slug IDs like `RETRO-2026-03-22-overnight-autonomous-artifact-sweep`.

This happened because retros started as plain files in `docs/swain-retro/` with date-based names. When they got `artifact:` frontmatter, the ID was copied from the filename instead of getting a number.

The date-slug format creates special cases everywhere:

- **Type extraction** broke. The `_extract_type` regex expected `-\d+` at the end. Each retro got its own type string, spawning 19 zombie directories.
- **Folder naming** needs special logic. `(RETRO-2026-03-22-overnight-sweep)` is a valid but ugly folder name that doesn't match the `(TYPE-NNN)-Title` pattern.
- **ID allocation** uses `next-artifact-id.sh`, which scans for the highest number. Date-slugs don't have a number to scan.
- **Every tool** that parses artifact IDs needs to handle two formats instead of one.

The date and slug carry no information that `created:` and `title:` frontmatter fields don't already hold.

## Decision

Retro artifacts must use numeric IDs: `RETRO-001`, `RETRO-002`, etc. The date-slug format is retired.

- New retros get the next available number from `next-artifact-id.sh RETRO`.
- Existing retros are renumbered in chronological order (oldest = lowest number).
- The original date lives in `created:` frontmatter. The descriptive slug lives in `title:`.
- `docs/swain-retro/` remains the storage directory. Retros are foldered per ADR-027.

After migration, the `_extract_type` regex fix (`^([A-Z]+)-`) is still correct and handles both formats, but the date-slug path is no longer exercised by real data.

## Alternatives Considered

1. **Keep date-slug IDs, fix tooling.** Every tool that touches artifact IDs needs a second code path. The `_extract_type` fix was the first; folder naming in doctor was the second. More will follow. The complexity compounds with each new feature.

2. **Embed the date in the folder title instead of the ID.** E.g., `(RETRO-001)-2026-03-22-Overnight-Sweep`. The ID is numeric but the folder name still carries the date. Adds no value — `created:` frontmatter already has the date, and folder titles should describe content, not timestamps.

3. **Move retros out of the artifact system entirely.** Retros have relationship links (`linked-artifacts`) that connect them to the work they reflect on. Removing them from the graph loses valuable cross-references.

## Consequences

- One ID format for all artifact types. No special cases in parsers, materializers, doctor, or any future tooling.

- 29 existing retros need renumbering. This is a one-time migration with a script. Cross-references in other artifacts must be updated.

- The original date-slug filenames disappear from git history at the rename point. `git log --follow` tracks the rename.

- `next-artifact-id.sh RETRO` starts working correctly after migration (currently returns 1 because no numeric retro IDs exist).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-03 | -- | Decision recorded |
