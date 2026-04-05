---
title: "Defer Worktree Creation to Task Dispatch"
artifact: SPEC-195
track: implementable
status: Active
author: cristos
created: 2026-03-30
last-updated: 2026-03-30
priority-weight: high
type: enhancement
parent-epic: EPIC-048
parent-initiative: ""
linked-artifacts:
  - SPEC-175
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Defer Worktree Creation to Task Dispatch

## Problem Statement

swain-session currently creates a worktree at bootstrap time — before the operator has said what they want to work on. This has two costs:

1. **Startup latency:** EnterWorktree is a synchronous tool call that adds 3-5 seconds to session startup.
2. **Poor naming:** The worktree gets a generated name because the session doesn't yet know the work context. When a SPEC or task is later assigned, the worktree name doesn't match the work being done.
3. **Overlap risk:** Without knowing the target work, the bootstrap can't check for existing worktrees that already cover the same scope.

## Desired Outcomes

Worktrees are created at the right time — when the operator starts executing a specific piece of work (via swain-do task dispatch). The worktree name reflects the work context (e.g., `spec-194-fast-path-greeting`), and creation checks for existing worktrees covering the same spec/epic to avoid duplicates.

## External Behavior

**Before (current):**
```
swain → bootstrap → EnterWorktree (generic name) → greeting
```

**After:**
```
swain → bootstrap (no worktree) → greeting → ... → /swain-do start SPEC-203 → EnterWorktree (named for spec)
```

**Preconditions:** swain-session bootstrap detects whether already in a worktree (existing behavior) and skips creation if so.

**Postconditions:** When swain-do dispatches work, it creates a worktree named for the work item, checks for overlap with existing worktrees, and enters it.

## Acceptance Criteria

1. **Given** a session starting on trunk, **when** the operator runs `swain`, **then** no worktree is created during bootstrap.
2. **Given** a session already in a worktree, **when** the operator runs `swain`, **then** bootstrap detects this and proceeds normally (no change from current behavior).
3. **Given** the operator starts work on SPEC-203, **when** swain-do dispatches the task, **then** a worktree is created with a name derived from the spec (e.g., `spec-194-fast-path-greeting`).
4. **Given** a worktree for SPEC-203 already exists, **when** swain-do dispatches work on SPEC-203, **then** it detects the existing worktree and offers to reuse it instead of creating a duplicate.
5. **Given** the operator asks to work on something without a formal spec (ad-hoc work), **when** swain-do dispatches, **then** a worktree is still created with a reasonable name derived from the task description.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- swain-session bootstrap must still detect existing worktrees (for resumed sessions).
- The `using-git-worktrees` superpowers skill may need coordination — it has its own worktree creation logic.
- swain-do's worktree creation should use the existing `swain-worktree-name.sh` script but with a spec/task context parameter.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-30 | -- | Initial creation; operator-requested |
| Complete | 2026-04-05 | cd6f0ccb | Retroactive verification; all 5 ACs pass |
