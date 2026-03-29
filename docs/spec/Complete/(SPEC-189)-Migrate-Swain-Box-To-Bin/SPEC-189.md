---
title: "Migrate swain-box to bin/"
artifact: SPEC-189
track: implementation
status: Complete
author: cristos
created: 2026-03-28
last-updated: 2026-03-29
parent-epic: EPIC-047
priority-weight: low
depends-on-artifacts:
  - SPEC-188
linked-artifacts:
  - ADR-019
  - SPEC-067
---

# Migrate swain-box to bin/

## Goal

Move the `swain-box` symlink from the project root (`./swain-box`) to `bin/swain-box`, completing the ADR-019 operator-facing convention for the first script that established the pattern.

## Behavior

### In the swain repo itself

1. Remove the root symlink `./swain-box`
2. Create `bin/swain-box -> ../skills/swain/scripts/swain-box`
3. Update `.gitignore` if needed (root entry → `bin/` entry)
4. Update any documentation referencing `./swain-box` to `bin/swain-box`

### In consumer projects

Handled automatically by SPEC-188 (doctor `bin/` auto-repair with backward-compatible migration from root symlinks).

### References to update

- `swain-doctor/SKILL.md` — existing swain-box symlink check
- `swain-doctor/scripts/swain-preflight.sh` — existing swain-box symlink check
- Any SKILL.md files referencing `./swain-box` invocation

## Deliverables

- `bin/swain-box` symlink (replacing `./swain-box`)
- Updated doctor checks to look in `bin/` instead of root
- Updated documentation references

## Test Plan

- T1: `bin/swain-box` resolves and is executable
- T2: Doctor on swain repo shows `bin/swain-box` as ok
- T3: No references to `./swain-box` remain in skill files (outside historical context)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-28 | — | Created as EPIC-047 child |
| Complete | 2026-03-29 | — | bin/swain-box symlink exists and tracked; doc references updated in RUNBOOK-002, DESIGN-005, SPEC-092; old root symlink removed; migration logic in preflight |
