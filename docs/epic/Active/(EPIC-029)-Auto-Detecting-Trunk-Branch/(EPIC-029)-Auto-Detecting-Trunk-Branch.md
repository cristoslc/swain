---
title: "Auto-Detecting Trunk Branch"
artifact: EPIC-029
track: container
status: Active
author: cristos
created: 2026-03-17
last-updated: 2026-03-21
parent-initiative: INITIATIVE-009
priority-weight: high
success-criteria:
  - swain_trunk() auto-detects trunk from git state — returns the main worktree's branch
  - All swain scripts use swain_trunk() instead of hardcoded "main"
  - An operator on "develop" gets all swain operations targeting "develop" with zero configuration
  - From a worktree, swain_trunk() returns the parent worktree's branch (not the worktree's branch)
  - Optional swain.settings.json git.trunk override exists for edge cases but is not required
  - No literal "main" remains in runtime skill scripts (swain-sync, swain-doctor, preflight)
depends-on-artifacts: []
linked-artifacts:
  - INITIATIVE-009
  - EPIC-025
  - ADR-005
  - SPEC-039
  - SPEC-044
---

# Auto-Detecting Trunk Branch

## Goal / Objective

Replace all hardcoded "main" branch references across swain with auto-detection from git state. The trunk is wherever you are when you're not in a worktree — no configuration required. Operators on `develop`, `master`, `trunk`, or any branch are supported automatically. This is a prerequisite for correctness in EPIC-025 (Event Bus), which must compile events to the trunk branch without assuming its name.

## Scope Boundaries

**In scope:**
- Shell helper function: `swain_trunk()` that auto-detects trunk from git worktree state
- Optional `swain.settings.json` `git.trunk` override for edge cases
- Parameterize swain-sync: rebase target, push target, PR base
- Parameterize swain-doctor: stale worktree detection, merge-base checks
- Parameterize preflight script
- Parameterize event bus compilation target (EPIC-025)
- Update ADR-005 to note the parameterization

**Out of scope:**
- Multi-trunk workflows (e.g., simultaneous release branches)
- Changing existing completed SPECs (SPEC-039, SPEC-044) retroactively — they documented the decision at the time

## Design Decisions

1. **Auto-detect from git state, not config** — Trunk is not a setting, it's a fact about the repo. `swain_trunk()` detects it from git worktree state:
   - **Not in a worktree** (`GIT_COMMON_DIR == GIT_DIR`): you ARE on trunk. Return current branch.
   - **In a worktree** (`GIT_COMMON_DIR != GIT_DIR`): trunk is the main worktree's branch. Read it from the main worktree.
   - **Optional override**: if `swain.settings.json` has `git.trunk`, use that instead. This is for edge cases (detached HEAD, unusual repo structures), not normal operation.
2. **Zero configuration for the common case** — An operator on `develop` gets all swain operations targeting `develop` without touching any config file. An operator on `main` gets the same behavior as today. The override exists but is never required.
3. **No retroactive SPEC changes** — completed SPECs (SPEC-039, SPEC-044) documented decisions at the time they were made. They are not updated retroactively; this EPIC parameterizes runtime behavior going forward.

## Child Specs

- **SPEC-118** — swain_trunk() Auto-Detection Helper (scripts/swain-trunk.sh + tests)
- **SPEC-119** — Parameterize Runtime Skills (swain-sync, swain-doctor, swain-release)
- **SPEC-120** — Doctor Trunk/Release Migration Detection (preflight + doctor section)

## Test Plan

### T1 — Auto-detection on main
- On a repo where the main worktree is on `main`, run `swain_trunk()` — returns `main`
- Run swain-sync, swain-doctor, and preflight — all target `main`

### T2 — Auto-detection on non-main trunk
- Check out `develop` in the main worktree
- Run `swain_trunk()` — returns `develop`
- Run swain-sync — rebase target, push target, and PR base all use `develop`
- Run swain-doctor — worktree detection and merge-base checks use `develop`

### T3 — Detection from inside a worktree
- Create a worktree from a repo whose main worktree is on `develop`
- From inside the worktree, run `swain_trunk()` — returns `develop` (not the worktree's branch)

### T4 — Override via settings
- Set `git.trunk` to `release` in `swain.settings.json`
- Run `swain_trunk()` — returns `release` regardless of current branch
- Remove the override — returns to auto-detection

### T5 — No hardcoded main in runtime scripts
- Grep all runtime skill scripts (swain-sync, swain-doctor, preflight, event bus orchestrator) for literal `main` branch references
- Verify none remain outside of comments, documentation, or fallback default values

## Key Dependencies

None — this can be done independently and should ideally land before EPIC-025.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-17 | — | Initial creation as prerequisite for EPIC-025 |
| Active | 2026-03-21 | — | Decomposed into SPEC-118, SPEC-119, SPEC-120 |
