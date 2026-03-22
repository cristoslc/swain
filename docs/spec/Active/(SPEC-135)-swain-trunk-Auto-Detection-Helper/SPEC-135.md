---
title: "swain_trunk() Auto-Detection Helper"
artifact: SPEC-135
track: implementation
status: Active
author: cristos
created: 2026-03-21
last-updated: 2026-03-21
parent-epic: EPIC-029
priority-weight: high
depends-on-artifacts: []
linked-artifacts:
  - EPIC-029
  - ADR-013
---

# swain_trunk() Auto-Detection Helper

## Goal

Create `scripts/swain-trunk.sh` — a standalone shell script that auto-detects the trunk (development) branch from git state. Zero configuration required for the common case.

## Detection Logic

1. **Settings override:** If `swain.settings.json` has `git.trunk`, return that value
2. **Not in a worktree** (`GIT_COMMON_DIR == GIT_DIR`): current branch IS trunk — return it
3. **In a worktree** (`GIT_COMMON_DIR != GIT_DIR`): read the main worktree's branch from `$GIT_COMMON_DIR/HEAD`
4. **Fallback:** return `"trunk"` on detached HEAD or detection failure

## Deliverables

- `scripts/swain-trunk.sh` — executable, prints trunk branch name to stdout
- `scripts/test-swain-trunk.sh` — test suite covering all detection paths

## Test Plan

- T1: Normal repo returns current branch name
- T2: Settings override returns configured value
- T3: Empty settings override falls through to auto-detect
- T4: No settings file falls through to auto-detect
- T5: From inside a worktree, returns main worktree's branch
- T6: Settings override works from inside a worktree

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-21 | — | Created as EPIC-029 child |
