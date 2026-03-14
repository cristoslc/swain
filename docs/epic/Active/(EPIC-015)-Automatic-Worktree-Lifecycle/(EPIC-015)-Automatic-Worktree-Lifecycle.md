---
title: "Automatic Worktree Lifecycle"
artifact: EPIC-015
status: Active
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
parent-vision: ""
success-criteria:
  - swain-do creates a worktree automatically when invoked outside one; agents never implement in the main worktree
  - swain-sync lands worktree work on main (direct push or PR), then prunes the worktree
  - swain-doctor detects and reports stale/orphaned worktrees left by crashed agents
  - An operator can run swain-do, work in the resulting worktree, and invoke swain-sync with no manual git worktree commands
depends-on-artifacts: []
addresses: []
evidence-pool: ""
---

# Automatic Worktree Lifecycle

## Goal / Objective

Make isolated worktree execution the default and automatic behavior for agent task dispatch — no operator intervention required. Today, agents may run implementation tasks in the main worktree, risking state pollution and making concurrent dispatch unsafe. This epic closes that gap end-to-end: from task pickup (swain-do creates isolation) through task completion (swain-sync lands and cleans up) through recovery (swain-doctor detects orphans).

The governing architectural decisions are recorded in ADR-005.

## Scope Boundaries

**In scope:**
- swain-do: worktree detection and automatic creation via `using-git-worktrees` on every invocation; stop-and-report on creation failure
- swain-sync: worktree-aware completion — rebase onto `origin/main`, push `HEAD:main` (or open PR if branch-protected), prune worktree after landing
- swain-doctor: stale/orphaned worktree detection and operator-facing cleanup guidance

**Out of scope:**
- Changing how worktrees are created beyond delegating to `using-git-worktrees`
- Agent dispatch orchestration (swain-dispatch) — it may benefit downstream but is not part of this epic
- Automatic PR merging — branch protection is an operator gate, not something swain bypasses

## Child Specs

| Spec | Title | Status |
|------|-------|--------|
| SPEC-039 | swain-sync: worktree-aware execution | Proposed |
| SPEC-043 | swain-do: automatic worktree creation at dispatch | Proposed |
| SPEC-044 | swain-doctor: stale worktree detection | Proposed |

## Key Dependencies

- `using-git-worktrees` superpowers skill must be installed for swain-do to create worktrees (SPEC-040 hard dependency)
- `gh` CLI must be available for PR fallback in swain-sync (SPEC-039 soft dependency — only needed on branch-protected repos)
- ADR-005 governs architectural decisions for this epic; do not implement contrary to it

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Initial creation; three child specs identified |
