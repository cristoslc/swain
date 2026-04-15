---
title: "Artifact Cleanup And Restructuring"
artifact: SPEC-310
track: implementable
status: Active
author: cristos
created: 2026-04-14
last-updated: 2026-04-14
type: chore
parent-epic:
parent-initiative:
linked-artifacts:
  - [ADR-027](../../../adr/Active/(ADR-027)-All-Artifacts-Must-Be-Foldered/(ADR-027)-All-Artifacts-Must-Be-Foldered.md)
  - [SPEC-242](../(SPEC-242)-Worktree-Ticket-Isolation/(SPEC-242)-Worktree-Ticket-Isolation.md)
  - [ADR-043](../../../adr/Active/(ADR-043)-Shared-Ticket-State-Across-Worktrees/(ADR-043)-Shared-Ticket-State-Across-Worktrees.md)
depends-on-artifacts: []
addresses:
  - PERSONA-002
swain-do: required
---

# Artifact Cleanup And Restructuring

## Problem Statement

The artifact tree has drifted from ADR-027's foldering convention. Some ADRs and SPECs are flat files instead of directories. Cross-references still point to old paths. The relink script fixed many broken links after the ADR-043 move, but the root cause — flat files — remains.

ADR-043 also moves tickets from `.tickets/` to `.swain/tickets/`. Code and docs still reference the old path.

## Scope

### Chore 1: Folder flat ADR files

Six ADRs are flat `.md` files instead of directories per ADR-027.

- ADR-032 (Gherkin Notation)
- ADR-033 (Worktree Session Isolation)
- ADR-034 (Worktree Location) — filename uses short title; folder should use full title
- ADR-041 (Runtime State Location)
- ADR-042 (Track Dirs Not Symlinks)
- ADR-040 in Superseded/ (Bootstrap Hook)

Each gets its own `(ID)-Title/` directory with the `.md` inside, plus a `_Related/` stub.

### Chore 2: Folder flat SPEC files

SPEC-287 is a flat file. Move it into its own directory.

### Chore 3: Folder flat DESIGN files

DESIGN-026 is a flat file. Move it into its own directory if appropriate.

### Chore 4: Update `.tickets/` references to `.swain/tickets/`

After ADR-043 is implemented, rename `.tickets/` to `.swain/tickets/` everywhere. This covers the `tk` script (`find_tickets_dir()`, auto-create, gitignore paths), skill files, and ADR-024 text.

This chore is gated on ADR-043 implementation. Do it as part of that work, not separately.

## Acceptance Criteria

- [ ] All flat ADR files listed in Chore 1 are in their own folders with `_Related/` stubs
- [ ] SPEC-287 is foldered
- [ ] DESIGN-026 is foldered (if appropriate)
- [ ] `relink.sh` produces zero broken links after moves
- [ ] `specwatch.sh scan` passes cleanly
- [ ] `.tickets/` references updated to `.swain/tickets/` (or tracked as blocked on ADR-043)

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| ADRs foldered | No flat `.md` files in `docs/adr/` (except `list-adr.md`) | |
| SPECs foldered | No flat `.md` files in `docs/spec/Active/` (except `list-spec.md`) | |
| Relink clean | `relink.sh` reports zero BROKEN links | |
| Specwatch clean | `specwatch.sh scan` exits 0 | |

## Scope & Constraints

- **In scope:** Structural cleanup of artifacts listed above
- **Out of scope:** Content changes, new artifacts, implementing ADR-043's ticket migration

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-14 | — | Operator-requested cleanup spec |