---
title: "Worktree-Safe Skill Execution"
artifact: INITIATIVE-001
track: container
status: Superseded
superseded-by: INITIATIVE-013
author: cristos
created: 2026-03-15
last-updated: 2026-03-19
parent-vision: VISION-001
priority-weight: high
success-criteria:
  - Every swain skill that uses relative paths resolves them correctly in both the main checkout and any git worktree
  - Claude Code hooks (settings.json) execute without file-not-found errors in worktrees
  - Session bookmarks captured in a worktree restore correctly in that worktree or gracefully handle pruned worktrees
  - Concurrent agents in separate worktrees cannot corrupt shared state (.tickets/, artifact indexes, session.json)
  - swain-doctor validates worktree health — detects broken hooks, stale bookmarks, orphaned worktrees, and path resolution failures
linked-artifacts:
  - ADR-005
  - ADR-009
  - EPIC-015
  - EPIC-016
  - EPIC-020
  - SPEC-050
depends-on-artifacts: []
addresses: []
trove: ""
---

# Worktree-Safe Skill Execution

## Strategic Focus

Worktrees became the default execution environment with EPIC-015, but the skill ecosystem was built assuming a single main checkout. Hooks use relative paths that don't resolve. Session bookmarks are worktree-blind. Scripts hardcode assumptions about working directory. The MOTD panel goes stale because its status bridge can't find itself.

These aren't isolated bugs — they're symptoms of a missing invariant: **every swain component must work correctly regardless of which worktree it runs in.** This initiative establishes that invariant across hooks, skills, session state, and shared data, so that worktree-based execution (the default since EPIC-015) is genuinely safe rather than nominally supported.

## Scope Boundaries

**In scope:**
- Auditing all skill scripts, hooks, and settings for worktree-unsafe path assumptions
- Fixing hook path resolution in `.claude/settings.json` (SPEC-050)
- Making session bookmarks worktree-aware (EPIC-016)
- Protecting shared state under concurrent worktree access (EPIC-020)
- swain-doctor checks for worktree-specific health issues
- Establishing conventions for worktree-safe script writing (e.g., always resolve via `git rev-parse --show-toplevel`)

**Out of scope:**
- Worktree creation/cleanup lifecycle (already complete in EPIC-015)
- Distributed multi-machine agent coordination
- Changes to git worktree behavior itself

## Child Epics

| Epic | Title | Status |
|------|-------|--------|
| EPIC-015 | Automatic Worktree Lifecycle | Complete |
| EPIC-016 | Worktree-Aware Session Bookmarks | Proposed |
| EPIC-020 | Multi-Agent Workdir Safety | Proposed |

## Small Work (Epic-less Specs)

| Spec | Title | Status |
|------|-------|--------|
| SPEC-050 | Stage Status Hook Fails in Worktrees | Proposed |

## Key Dependencies

- EPIC-015 (Complete) — established the worktree model; this initiative hardens it
- ADR-005 — governs worktree architectural decisions

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-15 | — | Created after discovering hook path resolution failures in worktrees; EPIC-015 already complete, EPIC-016/020 Proposed |
| Superseded | 2026-03-19 | -- | Absorbed into INITIATIVE-013 (Concurrent Session Safety) per ADR-009; child epics re-parented |
