---
title: "Project-Level Microkernel Topology"
artifact: ADR-046
track: standing
status: Active
author: cristos
created: 2026-04-18
last-updated: 2026-04-18
linked-artifacts:
  - VISION-006
  - INITIATIVE-018
  - ADR-038
  - ADR-047
depends-on-artifacts:
  - ADR-038
evidence-pool: ""
---

# Project-Level Microkernel Topology

## Context

ADR-039 decided on a hub-and-spoke topology where a host bridge (hub) routes events between project bridges and a shared chat adapter. After implementation and retros, the host bridge adds an unnecessary routing hop. The chat adapter already filters messages by stream. Project bridges already receive all events for their project. The hub's only contribution — forwarding between chat and project — is local IPC that introduces process management complexity without clear benefit.

Meanwhile, ADR-038's promise of subprocess runtime adapters was never fulfilled. Runtime adapters (OpenCode, Claude Code, Tmux) are still in-process Python classes, not isolatable subprocess plugins.

The operator needs a simpler model: one watchdog process ensures things run, each project bridge is a self-contained microkernel, and runtime adapters become true subprocess plugins.

## Decision

Each ProjectBridge is a self-contained microkernel that loads both its chat adapter and its runtime adapters as subprocess plugins speaking NDJSON over stdio. The host bridge (kernel) is removed. A lightweight watchdog process manages bridge lifecycle but does not route events.

```
Watchdog (process manager)          — reconciles desired state, starts/stops bridges
├── ProjectBridge (swain)          — microkernel per project
│   ├── ChatAdapter subprocess     — NDJSON over stdio (Zulip, one stream)
│   └── RuntimeAdapter subprocess  — NDJSON over stdio (per session)
└── ProjectBridge (rk)
    └── ...
```

Key properties:

- **No hub routing.** Project bridges talk directly to their chat adapter subprocess.
- **One session per worktree.** A project bridge manages exactly one runtime session per git worktree. The Zulip topic is the worktree's branch name. Trunk is `trunk`.
- **Continuous worktree discovery.** Project bridges poll `git worktree list --porcelain` every 15s to detect new and removed worktrees.
- **Watchdog does not route.** The watchdog ensures processes are running, resolves credentials once at startup, and manages opencode serve discovery. It never sits in the event path.

## Alternatives Considered

- **Hub-and-spoke (ADR-039, current).** Adds one IPC hop per event. The host bridge must stay alive for anything to work. Runtime adapters remain in-process. Rejected: the hub solves a routing problem that Zulip streams already solve.
- **Watchdog as hub.** Combine the watchdog with event routing. Rejected: this recreates ADR-039 with a different name. Process management and event routing are independent concerns.
- **No supervisor at all.** Each project bridge is started manually by the operator. Rejected: the operator wants fire-and-forget; manual per-project startup is ceremony that scales poorly.
- **Chat adapter as hub.** The Zulip adapter routes between project bridges. Rejected: ADR-038 correctly identified that a plugin (replaceable, operator-chosen) should not be the trust anchor. The watchdog (kernel code) is a better supervisor.

## Consequences

- Project bridges are simpler — they manage sessions and subprocesses, not routing.
- Chat adapters are simpler — they receive events pre-scoped to one project's stream, no bridge-to-stream routing needed.
- Runtime adapters finally become true subprocess plugins as ADR-038 promised. Language-agnostic, isolated, independently testable.
- The watchdog is a new component (~200 lines). It is not in the event path — if it crashes, bridges and their sessions continue running. It just stops reconciling until restarted.
- One Zulip bot account is shared across all project bridges. Each bridge's chat adapter subprocess subscribes with a narrow filter for its own stream.
- Removing the hub means project bridges must handle host-scope commands (clone, init, adopt) directly, or these commands move to the CLI.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-18 | -- | Supersedes ADR-039. Decided during swain-helm architecture refactor. |