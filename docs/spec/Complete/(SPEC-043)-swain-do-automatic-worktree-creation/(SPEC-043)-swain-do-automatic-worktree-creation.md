---
title: "swain-do: automatic worktree creation at dispatch"
artifact: SPEC-043
track: implementable
status: Complete
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
type: enhancement
parent-epic: EPIC-015
linked-artifacts:
  - ADR-005
  - SPEC-039
  - SPEC-044
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# swain-do: automatic worktree creation at dispatch

## Problem Statement

swain-do invocations for implementation tasks may run in the main worktree, risking state pollution and making concurrent agent dispatch unsafe. Per ADR-005, swain-do is the designated owner of worktree creation: it must ensure agents always operate in an isolated worktree before any implementation work begins.

## External Behavior

On every swain-do invocation that involves implementation or execution (plan creation, task claim, execution handoff):

1. Detect whether the current context is a linked worktree using `git rev-parse --git-common-dir` vs `git rev-parse --git-dir`.
2. If already in a linked worktree, proceed normally.
3. If in the main worktree, invoke the `using-git-worktrees` superpowers skill to create a new linked worktree before proceeding.
4. If `using-git-worktrees` is not installed or returns an error, stop and report to the operator — do not fall back to running in the main worktree.

**Precondition:** `using-git-worktrees` superpowers skill installed at `.agents/skills/using-git-worktrees/` or `.claude/skills/using-git-worktrees/`.

**Postconditions:**
- Implementation tasks always run inside a linked worktree.
- The operator receives a clear error if worktree creation fails, with the reason.

## Acceptance Criteria

**AC-1: Already in worktree → no-op**
- Given: swain-do is invoked from within a linked worktree.
- When: Worktree detection runs.
- Then: swain-do proceeds without attempting to create another worktree.

**AC-2: Main worktree → create worktree via superpowers**
- Given: swain-do is invoked from the main worktree and `using-git-worktrees` is installed.
- When: An implementation or execution operation is requested.
- Then: swain-do invokes `using-git-worktrees` to create a linked worktree, then hands off execution into that worktree.

**AC-3: Superpowers absent → stop and report**
- Given: swain-do is invoked from the main worktree and `using-git-worktrees` is not installed.
- When: Worktree creation is attempted.
- Then: swain-do stops, reports that superpowers is required for isolated dispatch, and provides install guidance. No implementation work begins.

**AC-4: Worktree creation failure → stop and report**
- Given: `using-git-worktrees` is installed but returns an error (disk full, git error, etc.).
- When: Worktree creation is attempted.
- Then: swain-do stops and surfaces the error to the operator. No implementation work begins.

**AC-5: Non-implementation operations unaffected**
- Given: swain-do is invoked for a read-only or coordination operation (e.g., `tk ready`, status check).
- When: Worktree detection runs.
- Then: No worktree creation is attempted; the operation proceeds in the current context.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC-1: Already in worktree → no-op | | |
| AC-2: Main worktree → create via superpowers | | |
| AC-3: Superpowers absent → stop | | |
| AC-4: Creation failure → stop | | |
| AC-5: Read-only ops unaffected | | |

## Scope & Constraints

**In scope:** Detection logic and superpowers invocation added to swain-do SKILL.md.

**Out of scope:** Worktree cleanup — that is swain-sync's responsibility (SPEC-039). Changing the `using-git-worktrees` skill itself.

## Implementation Approach

Add a worktree detection and creation preamble to swain-do's execution-dispatch section:

```bash
GIT_COMMON=$(git rev-parse --git-common-dir 2>/dev/null)
GIT_DIR=$(git rev-parse --git-dir 2>/dev/null)
[ "$GIT_COMMON" != "$GIT_DIR" ] && IN_WORKTREE=yes || IN_WORKTREE=no
```

If `IN_WORKTREE=no` and the operation is implementation/execution: detect superpowers, invoke `using-git-worktrees`, verify result, then hand off. Stop on any failure.

TDD cycles:
1. RED: test that read-only ops skip worktree creation → GREEN: gate on operation type
2. RED: test that main-worktree invocation triggers `using-git-worktrees` → GREEN: add creation preamble
3. RED: test that absent superpowers stops execution with guidance → GREEN: add detection + error path
4. RED: test that creation failure stops execution with error → GREEN: check return code and surface error

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Initial creation under EPIC-015 |
| Ready | 2026-03-14 | — | Approved |
| Complete | 2026-03-14 | 984dd27 | Worktree isolation preamble added to swain-do SKILL.md (v3.1.0) |
