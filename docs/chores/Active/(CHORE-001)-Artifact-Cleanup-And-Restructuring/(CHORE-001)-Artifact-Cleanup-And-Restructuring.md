---
title: "Artifact Cleanup And Restructuring"
artifact: CHORE-001
track: implementable
status: Active
author: cristos
created: 2026-04-14
last-updated: 2026-04-14
linked-artifacts:
  - [ADR-027](../../../adr/Active/(ADR-027)-All-Artifacts-Must-Be-Foldered/(ADR-027)-All-Artifacts-Must-Be-Foldered.md)
  - [ADR-043](../../../adr/Active/(ADR-043)-Shared-Ticket-State-Across-Worktrees/(ADR-043)-Shared-Ticket-State-Across-Worktrees.md)
  - [ADR-045](../(ADR-045)-Chores-As-A-Lightweight-Artifact-Type/(ADR-045)-Chores-As-A-Lightweight-Artifact-Type.md)
---

# Artifact Cleanup And Restructuring

## Problem

The artifact tree has drifted from ADR-027's foldering rule. Some ADRs and SPECs are flat files instead of directories. Links point to old paths. ADR-043 also moves tickets from `.tickets/` to `.swain/tickets/`, so code and docs need updating.

## Checklist

### Folder flat ADR files

Six ADRs are flat `.md` files instead of directories per ADR-027:

- [ ] ADR-032 (Gherkin)
- [ ] ADR-033 (Worktree Sessions)
- [ ] ADR-034 (Worktree Location) — use full title for folder name
- [ ] ADR-041 (Runtime State)
- [ ] ADR-042 (Track Dirs Not Symlinks)
- [ ] ADR-040 in Superseded/

Each gets its own `(ID)-Title/` directory, the `.md` inside, and a `_Related/` stub with `.gitkeep`.

### Folder flat SPEC files

- [ ] SPEC-287 — move into its own directory

### Folder flat DESIGN files

- [ ] DESIGN-026 — move into its own directory if appropriate

### Update `.tickets/` references

- [ ] After ADR-043 implementation: rename `.tickets/` to `.swain/tickets/` in `tk`, skills, and docs. Blocked on ADR-043's migration.

### Verification

- [ ] Run `relink.sh` after all moves — zero broken links
- [ ] Run `specwatch.sh scan` — exits 0

## Notes