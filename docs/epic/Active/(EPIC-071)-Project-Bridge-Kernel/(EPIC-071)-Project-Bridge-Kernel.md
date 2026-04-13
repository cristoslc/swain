---
title: "Project Bridge Kernel"
artifact: EPIC-071
track: container
status: Active
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
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
  - ADR-038
  - EPIC-070
addresses: []
evidence-pool: ""
---

# Project Bridge Kernel

## Goal / Objective

Build the session orchestrator that manages agent sessions for a single project. It spawns runtime adapter plugins, tracks session state, and communicates with the host bridge.

## Desired Outcomes

Each project has a dedicated, lightweight orchestrator. Sessions are tracked with lifecycle state. Artifact binding prevents duplicate sessions. The operator can spawn, cancel, and steer sessions through commands routed from the host bridge.

## Scope Boundaries

**In scope:**
- Session aggregate (lifecycle states, runtime binding, artifact binding, thread ID).
- Runtime adapter plugin spawn and NDJSON communication.
- Session-to-artifact binding and collision detection.
- Tmux session management (create, destroy, reconnect).
- Session-scoped web output event emission (v2 prep — emit event, don't handle routing).

**Out of scope:**
- Chat adapter communication (routed through host bridge).
- Tmux polling for unmanaged sessions (host bridge responsibility).
- The runtime adapter plugins themselves (EPIC-073).

## Child Specs

_To be created during implementation planning._

## Key Dependencies

- EPIC-070 (Host Bridge Kernel) — project bridge is spawned and supervised by host bridge.
- ADR-038 (Microkernel Plugin Architecture) — defines the runtime plugin contract.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-06 | -- | Created from VISION-006 decomposition. |
