---
title: "BUG-to-SPEC Migration"
artifact: SPEC-006
status: Complete
author: cristos
created: 2026-03-12
last-updated: 2026-03-12
parent-epic: EPIC-002
addresses: []
evidence-pool:
swain-do: required
linked-artifacts:
  - SPIKE-003
depends-on-artifacts:
  - SPEC-004
---

# BUG-to-SPEC Migration

## Problem Statement

When SPEC-004 eliminates the BUG artifact type, existing repos may have BUG artifacts on disk. These need automated migration to SPECs with `type: bug`, and cross-references throughout the repo need rewriting. This migration must be safe, idempotent, and integrated into swain-doctor so it runs automatically on session start for affected repos.

## External Behavior

**Inputs:**
- `docs/bug/` directory tree (if it exists) containing BUG-NNN artifacts
- Cross-references to BUG-NNN in other artifacts' frontmatter and body text

**Outputs:**
- Each `BUG-NNN` artifact moved to `docs/spec/<Phase>/(SPEC-NNN)-<Title>/` with:
  - `artifact:` changed from `BUG-NNN` to `SPEC-NNN` (next available number)
  - `type: bug` added to frontmatter
  - Bug-specific sections preserved (Reproduction Steps, Severity, Expected/Actual)
  - Lifecycle table preserved with a new row recording the migration
- All cross-references updated: `BUG-NNN` → `SPEC-NNN` in frontmatter fields and body text of all artifacts
- `docs/bug/` directory removed after migration
- `list-bug.md` removed (if it existed), entries merged into `list-spec.md`
- A migration report printed to stdout summarizing what was moved and rewritten

**Idempotency:**
- If no `docs/bug/` exists, the migration is a no-op (exit 0, no output)
- If run twice, the second run detects no BUG artifacts and skips

## Acceptance Criteria

1. **Given** a repo with `docs/bug/Active/(BUG-NNN)-Foo/`, **when** swain-doctor runs, **then** the artifact is moved to `docs/spec/<Phase>/(SPEC-NNN)-Foo/` with `type: bug` and the next available SPEC number
2. **Given** another artifact references `BUG-NNN` in its frontmatter, **when** migration runs, **then** the reference is rewritten to the new `SPEC-NNN`
3. **Given** a BUG artifact with a lifecycle table, **when** migrated, **then** the lifecycle table is preserved and a `Migrated` row is appended with the migration commit hash
4. **Given** a repo with no `docs/bug/` directory, **when** swain-doctor runs, **then** the migration check is a silent no-op
5. **Given** migration has already run, **when** swain-doctor runs again, **then** no changes are made (idempotent)
6. **Given** the migration completes, **when** specwatch scans, **then** no stale BUG references remain

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| 1. BUG artifact migrated to SPEC with type:bug | `migrate-bugs.sh` moved BUG-001 to SPEC-007 with `type: bug`, correct phase mapping (Resolved→Implemented) | Pass |
| 2. Cross-references rewritten | `migrate-bugs.sh` scans all .md files for BUG-NNN references and rewrites to SPEC-NNN | Pass |
| 3. Lifecycle table preserved with Migrated row | SPEC-007 retains original lifecycle rows plus `Migrated` entry with commit hash | Pass |
| 4. No docs/bug/ = silent no-op | Script checks `[ -d docs/bug ]` and exits 0 immediately if absent | Pass |
| 5. Idempotent on second run | After migration, docs/bug/ is removed, so re-run exits immediately at step 4 | Pass |
| 6. No stale BUG references after specwatch | `specwatch.sh scan` finds no BUG- references after migration completes | Pass |

## Scope & Constraints

- This spec depends on SPEC-004 landing first (the unified type system must exist before migration targets it)
- Migration is integrated into swain-doctor, not a standalone script — it runs as part of session-start health checks
- The migration must handle all BUG lifecycle phases (mapping to equivalent SPEC phases)
- BUG phase → SPEC phase mapping: Reported→Draft, Triaged→Draft, Active→Approved, Verified→Testing, Resolved→Implemented, Abandoned→Abandoned

## Implementation Approach

1. **TDD cycle 1 — detection:** Add BUG directory detection to swain-doctor. Test: create fake docs/bug/, verify detection.
2. **TDD cycle 2 — artifact conversion:** Implement BUG→SPEC conversion (renumber, add type:bug, rewrite frontmatter). Test: convert a BUG, verify output format.
3. **TDD cycle 3 — cross-reference rewriting:** Scan all artifacts for BUG-NNN references, rewrite to SPEC-NNN. Test: create cross-referencing artifacts, verify rewrite.
4. **TDD cycle 4 — cleanup:** Remove docs/bug/, list-bug.md, update list-spec.md. Test: verify clean state after migration.
5. **TDD cycle 5 — idempotency:** Run migration twice, verify second run is no-op. Test: assert no git changes on second run.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-12 | — | Initial creation |
| Testing | 2026-03-12 | 93798e9 | Verification table populated, all criteria pass |
| Implemented | 2026-03-12 | 3a1ed03 | All acceptance criteria verified |
