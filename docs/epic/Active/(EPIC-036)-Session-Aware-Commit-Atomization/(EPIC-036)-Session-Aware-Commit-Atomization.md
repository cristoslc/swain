---
title: "Session-Aware Commit Atomization"
artifact: EPIC-036
track: container
status: Active
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
parent-vision: VISION-001
parent-initiative: INITIATIVE-013
priority-weight: ""
success-criteria:
  - swain-sync produces multiple logically-grouped commits per invocation when session history is available
  - Each commit maps to a discrete unit of work (artifact transition, task completion, script change) with an appropriate conventional-commit prefix
  - Multiple concurrent sessions on the same branch cannot clobber each other's action logs or commit attribution
  - Session action log captures structured events as skills operate, scoped by session ID
  - swain-sync only consumes and clears actions from its own session, leaving other sessions' actions intact
  - Fallback to single-commit behavior when no action log exists (backward compatible)
  - Commit ordering reflects chronological session activity
depends-on-artifacts:
  - EPIC-016
linked-artifacts:
  - SPEC-098
  - SPEC-099
addresses: []
evidence-pool: ""
---

# Session-Aware Commit Atomization

## Goal / Objective

swain-sync currently produces a single monolithic commit per invocation regardless of how many distinct units of work were performed during the session. A session that transitions two artifacts, fixes a script, and rebuilds an index collapses into one `feat: update specs and fix script` commit. This erases the logical structure of the work from git history.

Worse, multiple swain sessions can operate concurrently on the same worktree/branch (e.g., an operator session and a dispatched background agent, or two terminal tabs on the same branch). Today, whichever session runs swain-sync last produces a commit that silently absorbs the other session's uncommitted work with no attribution. There is no mechanism to distinguish which session produced which changes.

This epic introduces a **session-scoped action log** — a structured event stream keyed by session ID that skills emit into as they operate — and teaches swain-sync to consume only its own session's actions, producing one commit per logical unit of work with the correct conventional-commit prefix, without clobbering concurrent sessions.

## Scope Boundaries

**In scope:**
- Session-scoped action log schema and append API (extension to session.json, keyed by session ID)
- Session identity: each swain session gets a stable ID for its lifetime, used to namespace actions
- Concurrent-safe append: multiple sessions can write actions to the same session.json without data loss
- Action emission from core skills: swain-design (transitions, creation), swain-do (task completion), swain-sync (index rebuilds)
- swain-sync commit grouping: map action → files → commit, consuming only the current session's actions
- Orphan file handling: staged files not claimed by the current session's actions get a catch-all commit
- Log lifecycle: swain-sync clears only its own session's actions after successful push; other sessions' actions are untouched
- Backward compatibility: no action log → current single-commit behavior

**Out of scope:**
- Worktree-aware bookmark location resolution (EPIC-016 — dependency, not overlap)
- Interactive commit splitting (rebase -i style)
- Cross-session merge conflict resolution (if two sessions edit the same file, git handles it at push time)
- Action log visualization or querying beyond what swain-sync consumes

## Child Specs

- SPEC-098: Session Action Log — structured event history in session.json
- SPEC-099: Commit Atomization in swain-sync — multi-commit grouping from action log

## Key Dependencies

- EPIC-016 (Worktree-Aware Session Bookmarks) — session.json schema must be compatible; bookmark worktree field and action log coexist in the same file. EPIC-016 doesn't need to be complete first, but schema changes should be coordinated.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-19 | -- | Created from analysis of swain-sync single-commit behavior |
