---
title: "Project Bridge Kernel"
artifact: EPIC-071
track: container
status: Active
author: cristos
created: 2026-04-06
last-updated: 2026-04-18
parent-vision: VISION-006
parent-initiative: INITIATIVE-018
priority-weight: high
success-criteria:
  - Manages session lifecycle (spawn, active, waiting_approval, idle, dead) for one project.
  - Spawns runtime adapter plugins as subprocesses speaking NDJSON over stdio.
  - Binds sessions to artifacts with collision detection (warns if two sessions target the same artifact).
  - Emits domain events to the host bridge and receives commands from it.
  - Manages tmux sessions (create, destroy, reconnect) for its project.
depends-on-artifacts:
  - ADR-046
  - ADR-038
addresses: []
evidence-pool: ""
---

# Project Bridge Kernel

## Goal / Objective

Build the session orchestrator that manages agent sessions for a single project as a self-contained microkernel. The ProjectBridge spawns its own chat adapter and runtime adapter subprocesses, discovers git worktrees continuously, and enforces one session per worktree.

## Desired Outcomes

The operator adds a project via `swain-helm project add`. The watchdog starts a ProjectBridge subprocess. The bridge discovers worktrees, creates sessions in each, and connects them to Zulip topics. No manual per-project setup. No host bridge routing.

## Scope Boundaries

**In scope:**
- Chat adapter subprocess spawning and routing (replaces host bridge routing).
- Runtime adapter subprocess spawning (one per session, per ADR-038).
- Git worktree discovery via polling (15s).
- One session per worktree enforcement.
- Session registry persistence (.swain/swain-helm/session-registry.json).
- Topic naming: branch name for worktrees, "trunk" for trunk.

**Out of scope:**
- Chat adapter plugin itself (EPIC-072).
- OpenCode serve discovery and auth (EPIC-085).
- Watchdog process management (EPIC-084).
- Provisioning UX (EPIC-074).

## Child Specs

- SPEC-322: Project Bridge Microkernel Refactor
- SPEC-323: Continuous Worktree Discovery
- SPEC-324: Session Registry Persistence
- SPEC-293: Output Shaping for Chat
- SPEC-294: Mermaid Rendering for Chat
- SPEC-298: Control Thread Worktree and Session Spawning (update scope)

## Key Dependencies

ADR-046 (Project-Level Microkernel Topology), ADR-038 (Microkernel Plugin Architecture).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-06 | -- | Created from VISION-006 decomposition. |
| Active | 2026-04-18 | -- | Updated for swain-helm architecture. Removed EPIC-070 dependency. |
