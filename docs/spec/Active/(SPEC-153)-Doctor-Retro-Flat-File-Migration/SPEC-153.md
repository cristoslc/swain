---
title: "swain-doctor: retro flat-file migration"
artifact: SPEC-153
track: implementable
status: Active
author: cristos
created: 2026-03-22
last-updated: 2026-03-23
priority-weight: ""
type: enhancement
parent-epic: EPIC-042
parent-initiative: ""
linked-artifacts:
  - EPIC-042
  - SPEC-163
depends-on-artifacts:
  - SPEC-151
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# swain-doctor: retro flat-file migration

## Problem Statement

After SPEC-151, the retro convention changes from flat files (`docs/swain-retro/YYYY-MM-DD-topic.md`) to folders (`docs/swain-retro/RETRO-YYYY-MM-DD-topic/`). Existing retros need migration. swain-doctor already handles similar migrations (e.g., `.beads/` → `.tickets/`), so this fits its remediation pattern.

## Desired Outcomes

Operators don't need to manually restructure existing retros. swain-doctor detects flat-file retros during session startup and migrates them automatically — same pattern as other doctor remediations. After migration, all retros follow the folder convention and are discoverable via manifest scanning.

## External Behavior

**Detection:** Scan `docs/swain-retro/` for `.md` files that are not inside a subdirectory (flat files at the root level).

**Migration per flat file `YYYY-MM-DD-topic.md`:**
1. Derive retro ID: `RETRO-YYYY-MM-DD-topic`
2. Create folder: `docs/swain-retro/RETRO-YYYY-MM-DD-topic/`
3. Move file: `git mv docs/swain-retro/YYYY-MM-DD-topic.md docs/swain-retro/RETRO-YYYY-MM-DD-topic/RETRO-YYYY-MM-DD-topic.md`
4. Generate a minimal `manifest.yaml` from the file's frontmatter (title, date, scope, linked-artifacts). Set `sessions: []` (no JSONL available for historical retros) and `summary.generated: false`. Manifest schema follows SPEC-151/SPEC-163.

**Properties:**
- Idempotent — safe to run multiple times. Skips retros already in folders.
- Uses `git mv` for clean history.
- No JSONL or session summary is retroactively generated — those sessions are gone.
- Reports migration count: "Migrated N retro(s) to folder structure"

**Integration:** Add detection to swain-doctor's remediation list. Doctor runs during session startup (via swain-preflight); this check runs alongside existing checks.

## Acceptance Criteria

- Given flat-file retros exist in `docs/swain-retro/`, when swain-doctor runs, then each is moved to `docs/swain-retro/RETRO-<date>-<slug>/RETRO-<date>-<slug>.md`
- Given a flat file is migrated, then a minimal `manifest.yaml` is generated in the folder with `sessions: []`
- Given a retro is already in a folder, when swain-doctor runs, then it is not modified (idempotent)
- Given no flat-file retros exist, when swain-doctor runs, then no migration occurs and no errors are raised
- Given multiple flat-file retros exist, when migrated, then `git mv` is used for each and the migration is committed as a single commit
- Given the frontmatter of a flat-file retro contains `linked-artifacts`, then the generated manifest preserves them

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Migration script lives in `skills/swain-doctor/scripts/` or is added to the existing doctor check pipeline
- The minimal manifest generated during migration is intentionally sparse — only fields derivable from the existing frontmatter are populated. Uses `sessions: []` per SPEC-163's unified schema.
- Does not attempt to locate or archive historical session JSONL files

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-22 | — | Initial creation |
