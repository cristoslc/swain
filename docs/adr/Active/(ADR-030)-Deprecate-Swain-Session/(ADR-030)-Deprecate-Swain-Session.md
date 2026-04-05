---
title: "Deprecate swain-session — Split Lifecycle into Init and Teardown"
artifact: ADR-030
track: standing
status: Active
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
linked-artifacts:
  - ADR-018
depends-on-artifacts: []
evidence-pool: ""
---

# Deprecate swain-session — Split Lifecycle into Init and Teardown

## Context

swain-session owns too much. It handles startup (greeting, bootstrap, focus lane, README reconciliation, status dashboard) AND shutdown (digest, retro, close state, teardown delegation, commit handoff). This creates two problems:

1. **Teardown never works.** The close sequence lives inside swain-session's close handler, but swain-teardown is just a passive hygiene checker. When the operator invokes `/swain-teardown` directly, retro does not fire, branches do not merge, and worktrees do not get cleaned up. The real shutdown logic is buried in session's close handler where the operator cannot reach it independently.

2. **Startup is split across two skills.** swain-init handles one-time onboarding (phases 1-6) and then delegates to swain-session for per-session startup. This two-hop path adds complexity without value. The per-session fast path (greeting, focus lane, session state init) belongs in init's already-initialized codepath.

The session skill also owns mid-session features (status dashboard, bookmarks, decision recording, focus lane, README reconciliation) that have better homes in purpose-built skills.

## Decision

Deprecate swain-session. Split its responsibilities:

### Startup (swain-init)

swain-init absorbs all per-session startup from swain-session:

- Fast greeting (tab naming, worktree detection, bookmark display)
- Session state init (`swain-session-state.sh init`)
- Focus lane setting (post-phase-1, after operator picks work)
- Session resume detection

The already-initialized fast path (phase 0) no longer delegates to swain-session. It runs the greeting and focus lane directly.

### Shutdown (swain-teardown)

swain-teardown becomes the single entry point for the full close sequence:

1. Session digest generation
2. Retro (while session is still active)
3. Merge worktree branches to trunk (or offer PR)
4. Worktree cleanup (post-merge, so branches are now merged)
5. Close session state
6. Commit handoff artifacts

### Mid-session features

| Feature | New home | Rationale |
|---------|----------|-----------|
| Status dashboard | **swain-roadmap** | Already owns roadmap rendering; dashboard is a scoped view of the same data |
| Bookmarks | **swain-do** | Bookmarks track work context; swain-do owns work execution |
| Decision recording | **swain-do** | Decisions happen during task work |
| Progress log | **swain-do** | Progress is a function of task completion |
| README reconciliation | **swain-retro**, **swain-sync**, **swain-release** | Drift detection is a reconciliation concern at review, commit, and release boundaries |
| Focus lane | **swain-init** | Focus is set at session start when the operator chooses what to work on |

### Meta-router changes

The swain meta-router removes the swain-session row. Its triggers reroute:

| Trigger | New target |
|---------|-----------|
| "status", "dashboard", "what's next", "overview", "where are we", "what should I work on" | **swain-roadmap** |
| "session end", "close session", "wrap up", "teardown" | **swain-teardown** |
| "session", "session info", "tab name" | **swain-init** |
| "bookmark", "remember where I am" | **swain-do** |
| "focus on" | **swain-init** |

## Consequences

- Operators get a working teardown that fires retro, merges, and cleans up.
- Single entry point for shutdown: `/swain-teardown` does everything.
- Single entry point for startup: `/swain-init` does everything.
- No more two-hop startup path (init -> session).
- Skills that reference `swain-session` in session-check preambles need updating to reference `swain-init` instead.
- The `swain-session-check.sh` script remains unchanged. It reads session state files, which are still written by `swain-session-state.sh`. Only the skill that orchestrates the calls changes.

## Migration

1. Update swain-teardown with full shutdown sequence.
2. Update swain-init to absorb startup features.
3. Update swain meta-router to reroute triggers.
4. Update swain-roadmap to absorb status dashboard.
5. Update swain-do to absorb bookmarks, decisions, progress log.
6. Update swain-retro, swain-sync, swain-release for README reconciliation.
7. Update session-check preambles across all skills (replace "start one with `/swain-session`" with "start one with `/swain-init`").
8. Remove swain-session skill directory.

## Lifecycle

| Hash | Transition | Date |
|------|-----------|------|
