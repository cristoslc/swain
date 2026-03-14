---
title: "ticket-query TICKETS_DIR Unbound Variable"
artifact: SPEC-035
status: Proposed
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
type: bug
parent-epic: ""
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# ticket-query TICKETS_DIR Unbound Variable

## Problem Statement

`ticket-query` crashes with `TICKETS_DIR: unbound variable` when called directly by external scripts (e.g., specwatch). The script relies on `TICKETS_DIR` being pre-set by the caller, which only happens when `tk` invokes it as a plugin. Any direct invocation — specwatch's `scan_tk_sync`, swain-status, swain-retro — fails silently with the error suppressed by `2>/dev/null`, causing tk integration to be skipped project-wide.

## External Behavior

After the fix, `ticket-query` must:

1. Auto-detect `.tickets/` using the same directory-walk logic `tk` uses (`find_tickets_dir`): walk up from `$PWD` until a `.tickets/` directory is found or the repo root is reached.
2. Respect `TICKETS_DIR` if already set in the environment (preserve backward compatibility with `tk` plugin invocations).
3. Emit a clear error to stderr and exit non-zero if `.tickets/` cannot be found (rather than crashing with an unbound variable).

No callers need to change their invocation — the fix is entirely within `ticket-query`.

## Acceptance Criteria

- **Given** `ticket-query` is run directly from the repo root without `TICKETS_DIR` set, **When** `.tickets/` exists in the working directory, **Then** it outputs valid JSON.
- **Given** `ticket-query` is run directly from the repo root without `TICKETS_DIR` set, **When** `.tickets/` does not exist, **Then** it exits non-zero with a clear stderr message (not an unbound variable crash).
- **Given** `TICKETS_DIR` is already set in the environment, **When** `ticket-query` is invoked, **Then** it uses the provided value (backward compat with `tk` plugin flow).
- **Given** specwatch runs `scan_tk_sync`, **When** `.tickets/` exists, **Then** the "ticket-query failed, skipping" message no longer appears in specwatch output.

## Reproduction Steps

1. `cd` to the repo root.
2. Run `skills/swain-do/bin/ticket-query` directly (without setting `TICKETS_DIR`).
3. Observe: `TICKETS_DIR: unbound variable` error on stderr, exit 1.
4. Run `bash skills/swain-design/scripts/specwatch.sh scan`.
5. Observe: `specwatch tk-sync: ticket-query failed, skipping.` in output.

## Severity

low

## Expected vs. Actual Behavior

**Expected:** `ticket-query` auto-detects `.tickets/` and outputs JSON when called without `TICKETS_DIR`.

**Actual:** Crashes with `TICKETS_DIR: unbound variable`; specwatch silently skips all tk cross-reference checks.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| Direct invocation outputs JSON | `skills/swain-do/bin/ticket-query` exits 0, stdout is valid JSON | — |
| Missing .tickets/ gives clean error | Confirm stderr message + non-zero exit | — |
| TICKETS_DIR env respected | Set `TICKETS_DIR=/tmp/fake`; confirm it uses that path | — |
| specwatch no longer skips tk-sync | Run specwatch scan; confirm no "failed, skipping" line | — |

## Scope & Constraints

- Fix is confined to `skills/swain-do/bin/ticket-query`.
- Do not break `tk`'s plugin invocation flow (where `TICKETS_DIR` is already exported).
- No changes needed to callers (specwatch, swain-status, swain-retro).

## Implementation Approach

1. Copy `find_tickets_dir` logic from `tk` (walk up from `$PWD` looking for `.tickets/`) into `ticket-query`, or extract it into a shared shell function.
2. At the top of `ticket-query`, after the existing env check: if `TICKETS_DIR` is unset or empty, call `find_tickets_dir` and assign the result; exit with an error if not found.
3. Verify by running `ticket-query` directly and confirming specwatch no longer emits the skip message.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Initial creation |
