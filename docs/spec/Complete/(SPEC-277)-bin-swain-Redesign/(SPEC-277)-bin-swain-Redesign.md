---
title: "bin/swain Redesign"
artifact: SPEC-277
track: implementable
status: Complete
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-epic: EPIC-056
priority-weight: critical
depends-on-artifacts:
  - SPEC-276
  - SPEC-251
linked-artifacts:
  - DESIGN-004
  - SPIKE-053
---

# SPEC-277: bin/swain Redesign

## Goal

Redesign bin/swain as the worktree router described in DESIGN-004. Key changes: lockfile-based claiming, interactive menu, post-runtime cleanup, and `SWAIN_WORKTREE_PATH` env var export.

## Critical Architecture Change

**Remove `exec`** — currently bin/swain uses `eval exec "$cmd"` which replaces the process. Post-runtime cleanup (verify ready_for_cleanup, prune worktree) requires bin/swain to regain control after the runtime exits. Change to running the runtime as a child process with signal forwarding.

## Deliverables

Update `skills/swain/scripts/swain` to:
1. Scan `.agents/worktrees/*.lock` for existing worktrees
2. Run stale detection on each (via swain-lockfile.sh)
3. Present interactive menu (DESIGN-004 screen states)
4. Claim worktree via lockfile before launch
5. Export `SWAIN_WORKTREE_PATH` and `SWAIN_LOCKFILE_PATH` env vars
6. Launch runtime as child process (not exec) with signal forwarding
7. On runtime exit: check ready_for_cleanup, verify commit hash, prune if safe
8. Support flags: `--resume <name>`, `--trunk`, `--runtime <name>`

## Acceptance Criteria

- [ ] **AC1: Interactive menu shows worktree state**
  - Active worktrees with age, PID, purpose
  - Orphaned worktrees (stale lockfiles)
  - Options: create new, resume, trunk, cleanup

- [ ] **AC2: Lockfile claiming before launch**
  - Calls swain-lockfile.sh claim
  - Collision detection: hard block for implementable/standing, soft for container

- [ ] **AC3: Env var export**
  - `SWAIN_WORKTREE_PATH` set to worktree absolute path
  - `SWAIN_LOCKFILE_PATH` set to lockfile path
  - Visible to the launched runtime

- [ ] **AC4: Runtime as child process**
  - No `exec` — bin/swain continues after runtime exits
  - SIGINT/SIGTERM forwarded to child
  - Exit code preserved

- [ ] **AC5: Post-runtime cleanup**
  - Checks lockfile for ready_for_cleanup
  - Verifies commit hash match
  - Prunes worktree + removes lockfile if safe
  - Offers re-entry if mismatch

- [ ] **AC6: --resume flag**
  - `swain --resume <name>` finds matching worktree, claims, launches

- [ ] **AC7: --trunk flag**
  - Warning about worktree discipline violation
  - Confirmation prompt
  - No lockfile created for trunk

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-04 | -- | Materialized for EPIC-056 |
