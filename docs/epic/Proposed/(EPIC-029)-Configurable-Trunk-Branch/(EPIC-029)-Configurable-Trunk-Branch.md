---
title: "Configurable Trunk Branch"
artifact: EPIC-029
track: container
status: Proposed
author: cristos
created: 2026-03-17
last-updated: 2026-03-17
parent-initiative: INITIATIVE-009
priority-weight: high
success-criteria:
  - swain.settings.json with git.trunk is respected by all swain scripts
  - An operator can set git.trunk to "develop" and all swain operations target that branch
  - Default behavior (no setting) is identical to current behavior (main)
  - No literal "main" remains in runtime skill scripts (swain-sync, swain-doctor, preflight)
  - A shell helper function swain_trunk() reads the setting with fallback to main
depends-on-artifacts: []
linked-artifacts:
  - INITIATIVE-009
  - EPIC-025
  - ADR-005
  - SPEC-039
  - SPEC-044
---

# Configurable Trunk Branch

## Goal / Objective

Replace all hardcoded "main" branch references across swain with a configurable trunk branch. Operators using `develop`, `master`, `trunk`, or any custom branch name should be fully supported. This is a prerequisite for correctness in EPIC-025 (Event Bus), which must compile events to the trunk branch without assuming its name.

## Scope Boundaries

**In scope:**
- Add `git.trunk` key to `swain.settings.json` (default: `main`)
- Shell helper function: `swain_trunk()` that reads the setting with fallback to `main`
- Parameterize swain-sync: rebase target, push target, PR base
- Parameterize swain-doctor: stale worktree detection, merge-base checks
- Parameterize preflight script
- Parameterize event bus compilation target (EPIC-025)
- Update ADR-005 to note the parameterization

**Out of scope:**
- Multi-trunk workflows (e.g., simultaneous release branches)
- Changing existing completed SPECs (SPEC-039, SPEC-044) retroactively — they documented the decision at the time

## Design Decisions

1. **Single source of truth** — `swain.settings.json` `git.trunk` is the canonical trunk branch name. All scripts read from this file; no script infers the trunk from git state.
2. **Shell helper with fallback** — `swain_trunk()` reads `git.trunk` from `swain.settings.json` using `jq`, falling back to `main` if the file or key is absent. This ensures backward compatibility without requiring configuration for projects that use `main`.
3. **No retroactive SPEC changes** — completed SPECs (SPEC-039, SPEC-044) documented decisions at the time they were made. They are not updated retroactively; this EPIC parameterizes runtime behavior going forward.

## Child Specs

None yet — specs to be decomposed when this EPIC transitions to Active.

## Test Plan

### T1 — Default behavior without configuration
- Remove or omit `git.trunk` from `swain.settings.json`
- Run `swain_trunk()` and verify it returns `main`
- Run swain-sync, swain-doctor, and preflight and verify they target `main`

### T2 — Custom trunk branch
- Set `git.trunk` to `develop` in `swain.settings.json`
- Run `swain_trunk()` and verify it returns `develop`
- Run swain-sync and verify rebase target, push target, and PR base all use `develop`
- Run swain-doctor and verify worktree detection and merge-base checks use `develop`
- Run preflight and verify trunk references use `develop`

### T3 — No hardcoded main in runtime scripts
- Grep all runtime skill scripts (swain-sync, swain-doctor, preflight, event bus orchestrator) for literal `main` branch references
- Verify none remain outside of comments, documentation, or fallback default values

### T4 — Event bus compilation target
- Set `git.trunk` to `trunk` in `swain.settings.json`
- Verify event bus compile mode targets `trunk` branch for `events.jsonl` compilation
- Verify worktree enforcement guards use the configured trunk name

## Key Dependencies

None — this can be done independently and should ideally land before EPIC-025.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-17 | — | Initial creation as prerequisite for EPIC-025 |
