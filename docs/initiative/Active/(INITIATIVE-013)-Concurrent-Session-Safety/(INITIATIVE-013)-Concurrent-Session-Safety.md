---
title: "Concurrent Session Safety"
artifact: INITIATIVE-013
track: container
status: Active
author: cristos
created: 2026-03-18
last-updated: 2026-03-19
parent-vision:
  - VISION-001
  - VISION-002
priority-weight: high
success-criteria:
  - Multiple concurrent sessions (operator tabs, dispatched agents) cannot clobber each other's files, commits, or shared state
  - Each session is scoped to its own branch where feasible; sessions sharing a branch commit only their own work
  - Every swain skill resolves paths correctly in any worktree
  - A confused or chaotic agent can be terminated without affecting other sessions' work
  - swain-doctor validates session isolation health — detects stale bookmarks, orphaned worktrees, unsafe concurrent patterns
linked-artifacts:
  - ADR-005
  - ADR-009
  - EPIC-015
  - EPIC-016
  - EPIC-020
  - EPIC-036
  - INITIATIVE-001
  - INITIATIVE-010
  - INITIATIVE-012
  - SPEC-050
  - SPEC-081
  - VISION-001
  - VISION-002
depends-on-artifacts:
  - INITIATIVE-012
addresses: []
trove: ""
---

# Concurrent Session Safety

## Strategic Focus

Multiple swain sessions routinely operate concurrently — an operator in one terminal tab, a dispatched agent in a worktree, a second agent on the same branch. Today, nothing prevents these sessions from clobbering each other's files, absorbing each other's uncommitted work into monolithic commits, or racing on shared state like `.tickets/` and `session.json`.

This isn't hypothetical. Worktrees became the default execution environment with EPIC-015, but the skill ecosystem was built assuming a single session. Hooks use relative paths that don't resolve in worktrees. Session bookmarks are worktree-blind. swain-sync commits everything it finds with no concept of "my changes vs. someone else's."

The invariant: **every swain session must operate safely regardless of how many other sessions are active, whether they share a worktree or not.** This initiative pursues that invariant through two parallel tracks — worktree isolation (filesystem-level separation) and same-branch isolation (session-scoped state and commits).

## Scope Boundaries

**In scope:**
- Worktree-safe path resolution across all skills, hooks, and scripts
- Worktree-aware session bookmarks and restore flow
- Session identity and session-scoped action logs
- Session-aware commit atomization in swain-sync
- Concurrent-safe shared state access (.tickets/, artifact indexes, session.json)
- Worktree-scoped filesystem isolation for dispatched agents
- Branch-scoped push access
- swain-doctor checks for session isolation health

**Out of scope:**
- Agent orchestration (assignment, scheduling) — that's work intake
- Agent correctness (did it do the right thing)
- Single-agent sandboxing (covered by INITIATIVE-010/011)
- Distributed multi-machine agent coordination
- Cross-session merge conflict resolution (git handles this)

## Tracks

### Worktree isolation

Filesystem-level separation: each session gets its own worktree, skills resolve paths correctly in any worktree, bookmarks are worktree-aware.

| Epic/Spec | Title | Status |
|-----------|-------|--------|
| EPIC-015 | Automatic Worktree Lifecycle | Complete |
| EPIC-016 | Worktree-Aware Session Bookmarks | Proposed |
| EPIC-020 | Multi-Agent Workdir Safety | Proposed |
| SPEC-050 | Stage Status Hook Fails in Worktrees | Complete |

### Same-branch isolation

Session-scoped state and commits: when sessions share a branch (because worktree entry isn't reliable yet), each session tracks its own actions and commits only its own work.

| Epic | Title | Status |
|------|-------|--------|
| EPIC-036 | Session-Aware Commit Atomization | Active |

### Sandbox enforcement

Mechanically enforcing isolation at the sandbox boundary for dispatched agents.

| Spec | Title | Status |
|------|-------|--------|
| SPEC-081 | Worktree-Enforced Sandbox Isolation | Active |

## Child Epics

| Epic | Title | Track | Status |
|------|-------|-------|--------|
| EPIC-015 | Automatic Worktree Lifecycle | Worktree | Complete |
| EPIC-016 | Worktree-Aware Session Bookmarks | Worktree | Proposed |
| EPIC-020 | Multi-Agent Workdir Safety | Worktree | Proposed |
| EPIC-036 | Session-Aware Commit Atomization | Same-branch | Active |

## Small Work (Epic-less Specs)

| Spec | Title | Track | Status |
|------|-------|-------|--------|
| SPEC-050 | Stage Status Hook Fails in Worktrees | Worktree | Complete |
| SPEC-081 | Worktree-Enforced Sandbox Isolation | Sandbox | Active |

## Key Dependencies

- INITIATIVE-012 (Unified Runtime Architecture) — sandbox enforcement builds on the multi-runtime architecture
- ADR-005 — governs worktree architectural decisions
- ADR-009 — authorizes multi-vision parenting for this initiative

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-18 | — | Created during VISION-002 decomposition as "Swarm Safety" |
| Active | 2026-03-19 | — | INITIATIVE-012 complete; SPEC-081 covers sandbox enforcement |
| Active | 2026-03-19 | -- | Renamed from "Swarm Safety"; absorbed INITIATIVE-001 (Worktree-Safe Skill Execution) per ADR-009; added VISION-001 as second parent; added Tracks structure |
