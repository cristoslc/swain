---
title: "tk close Must Release Claim Lock"
artifact: SPEC-057
track: implementable
status: Complete
author: cristos
created: 2026-03-17
last-updated: 2026-03-17
type: bug
parent-epic: ""
parent-initiative: INITIATIVE-003
linked-artifacts: []
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: "GH#70"
swain-do: required
---

# tk close Must Release Claim Lock

## Problem Statement

`tk close` sets the ticket's YAML status to `closed` but does not remove the claim lock directory created by `tk claim`. This leaves orphaned lock directories in `.tickets/.locks/` indefinitely. The lock leak undermines multi-agent atomicity (stale locks could block re-claim on reopened tickets) and triggers persistent `swain-preflight` warnings about stale lock files.

## Reproduction Steps

1. Create a ticket: `tk create "Test ticket" -d "test" -t task -p 2`
2. Claim it: `tk claim <id>`
3. Confirm lock exists: `ls .tickets/.locks/<id>/`
4. Close it: `tk close <id>`
5. Check lock still exists: `ls .tickets/.locks/<id>/` — lock directory persists

## Severity

medium — No data loss, but stale locks accumulate across sessions, trigger preflight warnings, and could block re-claim on reopened tickets.

## Expected vs. Actual Behavior

**Expected:** `tk close <id>` sets status to `closed` AND removes `.tickets/.locks/<id>/` if it exists.

**Actual:** `tk close <id>` only sets status to `closed`. The lock directory persists until manual `tk release <id>` or manual deletion.

## Acceptance Criteria

- **AC1:** `tk close <id>` removes `.tickets/.locks/<id>/` when it exists
- **AC2:** `tk close <id>` succeeds without error when no lock exists (no-op on lock removal)
- **AC3:** `tk reopen <id>` does NOT restore a lock (reopened tickets start unlocked, ready for `tk claim`)
- **AC4:** Existing stale locks from prior sessions are cleaned up (one-time)

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC1 — close removes lock | Live test: claim → close → lock directory removed | Pass |
| AC2 — close without lock succeeds | Live test: create → close (no claim) → no error | Pass |
| AC3 — reopen does not restore lock | Live test: close → reopen → no lock directory created | Pass |
| AC4 — stale locks cleaned | `.tickets/.locks/` contains no stale lock directories | Pass |

## Scope & Constraints

- Change is scoped to `cmd_close()` in `skills/swain-do/bin/tk` (line ~280)
- Must also clean up the 15 existing stale locks in `.tickets/.locks/`
- Do NOT change `cmd_release()` — it remains available for manual mid-work lock release
- Do NOT change `cmd_reopen()` — reopened tickets should start unclaimed

## Implementation Approach

1. In `cmd_close()`, add a lock release call after `cmd_status "$1" "closed"`:
   ```bash
   local lockdir="$TICKETS_DIR/.locks/$1"
   [[ -d "$lockdir" ]] && rm -rf "$lockdir"
   ```
2. Clean up existing stale locks: `rm -rf .tickets/.locks/swa-*/`
3. Test: claim, close, verify lock removed. Close without prior claim, verify no error.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-17 | | Direct to Active — clear root cause, operator-requested |
| Complete | 2026-03-22 | | Retroactive close — implementation found at commit a549105, all 4 ACs verified live |
