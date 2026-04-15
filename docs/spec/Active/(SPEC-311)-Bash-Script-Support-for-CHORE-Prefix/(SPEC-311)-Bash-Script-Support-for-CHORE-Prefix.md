---
title: "Bash Script Support for CHORE Prefix"
artifact: SPEC-311
track: implementable
status: Active
author: cristos
created: 2026-04-14
last-updated: 2026-04-14
type: enhancement
parent-epic: EPIC-077
linked-artifacts:
  - [ADR-045](../../../adr/Active/(ADR-045)-Chores-As-A-Lightweight-Artifact-Type/(ADR-045)-Chores-As-A-Lightweight-Artifact-Type.md)
depends-on-artifacts: []
addresses:
  - PERSONA-002
swain-do: required
---

# Bash Script Support for CHORE Prefix

## Problem Statement

Four bash scripts enumerate known artifact prefixes. None include `CHORE`, so `next-artifact-id.sh CHORE` fails, and relink/resolution scripts skip CHORE artifacts silently.

## Changes

All changes follow the same pattern: add `CHORE` to a prefix/directory mapping or regex.

| Script | Change |
|--------|--------|
| `next-artifact-id.sh` | Add `CHORE) subdir="chores" ;;` case |
| `detect-duplicate-numbers.sh` | Add case + `ALL_TYPES` entry |
| `resolve-artifact-link.sh` | Add to `VALID_PREFIXES` regex |
| `relink.sh` | Add to `id_re` pattern |

Verify that `next-artifact-id.sh CHORE` returns `1` and increments on repeated calls.

## Acceptance Criteria

- [ ] `next-artifact-id.sh CHORE` increments correctly
- [ ] `detect-duplicate-numbers.sh` scans `docs/chores/`
- [ ] `resolve-artifact-link.sh` resolves CHORE IDs to paths
- [ ] `relink.sh` relinks CHORE-NNN markdown links

## Verification

| Script | Expected behavior |
|--------|-------------------|
| `next-artifact-id.sh` | Returns next CHORE ID, increments |
| `detect-duplicate-numbers.sh` | Scans `docs/chores/` |
| `resolve-artifact-link.sh` | Resolves CHORE IDs to paths |
| `relink.sh` | Detects and relinks CHORE links |

## Scope & Constraints

- **In scope:** Four bash scripts
- **Out of scope:** Python (SPEC-312), docs (SPEC-313), CHORE-001 execution

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-14 | — | Initial creation; readability grade 11.2 after 3 revision attempts (script filenames in tables inflate score) |