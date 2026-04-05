---
title: "Lockfile Management"
artifact: SPEC-276
track: implementable
status: Complete
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-epic: EPIC-056
priority-weight: critical
depends-on-artifacts:
  - ADR-025
linked-artifacts:
  - DESIGN-004
  - SPIKE-057
---

# SPEC-276: Lockfile Management

## Goal

Implement the lockfile claiming, releasing, and stale detection library used by bin/swain to manage worktree ownership. This is the foundation that all other EPIC-056 specs depend on.

## Deliverables

A shell library (`.agents/bin/swain-lockfile.sh`) that provides functions for:
1. Claiming a worktree (atomic lockfile creation)
2. Releasing a claim (lockfile removal)
3. Stale detection (PID dead AND pane dead)
4. Listing all lockfiles with status
5. Marking `ready_for_cleanup` with commit hash

## Lockfile Format (from DESIGN-004)

Location: `.agents/worktrees/<branch-name>.lock`

```bash
version=1
pid=$$
user=$(whoami)
exe=$RUNTIME
pane_id=$PANE_ID
claimed_at=$(date -Iseconds)
worktree_path=$WORKTREE_PATH
purpose="$PURPOSE"
status=active
```

Shell-sourceable key=value format. `source "$lockfile"` loads all fields.

## Acceptance Criteria

- [ ] **AC1: Claim creates lockfile atomically**
  - `swain-lockfile.sh claim <branch> <worktree-path> <purpose>` creates lockfile
  - Uses mkdir for atomic creation (same pattern as tk claiming)
  - Fails if lockfile already exists for an active claim

- [ ] **AC2: Release removes lockfile**
  - `swain-lockfile.sh release <branch>` removes the lockfile
  - No-op if lockfile doesn't exist

- [ ] **AC3: Stale detection uses dual-check**
  - PID dead (kill -0 fails) AND pane dead (tmux list-panes)
  - Falls back to PID-only when not in tmux
  - Checks user and exe fields to catch PID recycling

- [ ] **AC4: List returns structured output**
  - `swain-lockfile.sh list` returns JSON array of all lockfiles with status (active/stale/ready)
  - Includes worktree path, purpose, age, PID, pane

- [ ] **AC5: Mark ready_for_cleanup**
  - `swain-lockfile.sh mark-ready <branch>` appends ready_for_cleanup=true and ready_commit=<HEAD>
  - Only succeeds if lockfile exists and is active

- [ ] **AC6: Verify ready**
  - `swain-lockfile.sh verify-ready <branch>` checks ready_commit matches current HEAD
  - Returns 0 if match, 1 if mismatch, 2 if not marked ready

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-04 | -- | Materialized for EPIC-056 |
