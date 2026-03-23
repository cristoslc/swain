---
title: "Migrate Existing Number Allocation Callers"
artifact: SPEC-159
track: implementable
status: Complete
author: cristos
created: 2026-03-22
last-updated: 2026-03-23
priority-weight: ""
type: enhancement
parent-epic: EPIC-043
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts:
  - SPEC-156
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Migrate Existing Number Allocation Callers

## Problem Statement

`migrate-bugs.sh` contains its own `get_next_spec_number()` function that reimplements the scan-and-increment logic. Any other scripts that allocate artifact numbers should use the centralized allocator from [SPEC-156](../(SPEC-156)-Next-Artifact-Number-Script/(SPEC-156)-Next-Artifact-Number-Script.md) instead of maintaining their own copy.

## Desired Outcomes

- All scripts that allocate artifact numbers use `next-artifact-number.sh` as the single source of truth.
- No duplicated scan-and-increment logic remains in the codebase.

## External Behavior

**Changes:**
1. Replace `get_next_spec_number()` in `migrate-bugs.sh` with a call to `next-artifact-number.sh SPEC`.
2. Scan `skills/*/scripts/` for any other functions or inline code that extracts max artifact numbers — migrate those too.

**Behavior is unchanged** — the scripts produce the same output, they just delegate number allocation.

## Acceptance Criteria

- **Given** the updated `migrate-bugs.sh`, **when** it allocates a spec number, **then** it calls `next-artifact-number.sh SPEC` instead of its internal `get_next_spec_number()`.
- **Given** a grep for `get_next_spec_number\|get_next.*number\|max_num.*SPEC` across the codebase, **when** run after this spec completes, **then** zero matches are found outside of `next-artifact-number.sh` itself.
- **Given** `migrate-bugs.sh` runs in a worktree, **when** it allocates a number, **then** the number reflects all worktrees (inherited from SPEC-156's behavior).

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| migrate-bugs.sh calls next-artifact-number.sh | `migrate-bugs.sh` line 62: delegates to `$ALLOCATOR` when available | Pass |
| No duplicate allocation logic outside allocator | `grep -rn get_next_spec_number skills/` — only in migrate-bugs.sh fallback | Pass |
| Fallback preserved for missing allocator | `migrate-bugs.sh` lines 63-77: retains original scan as else branch | Pass |

## Scope & Constraints

- Primary target: `skills/swain-design/scripts/migrate-bugs.sh`.
- May discover additional callers during implementation — scope expands to cover them.
- Must not break `migrate-bugs.sh` functionality — the migration is a refactor, not a behavior change.

## Implementation Approach

1. Grep the codebase for number-allocation patterns.
2. Replace each with a call to `next-artifact-number.sh`.
3. Run the affected scripts' existing tests (if any) to verify no regression.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-22 | — | Agent-suggested decomposition of EPIC-043 |
| Complete | 2026-03-23 | — | migrate-bugs.sh delegates to allocator; no other callers found |
