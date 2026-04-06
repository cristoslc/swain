---
title: "Host Bridge Kernel"
artifact: EPIC-070
track: container
status: Active
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
parent-vision: VISION-006
parent-initiative: INITIATIVE-018
priority-weight: high
success-criteria:
  - Host bridge runs as an OS-native daemon (launchd on macOS, systemd on Linux) with automatic restart.
  - Polls tmux sessions and publishes managed/unmanaged session inventory to the chat adapter.
  - Spawns, supervises, and stops project bridges by operator command or config.
  - Routes events between project bridges and the shared chat adapter with bridge ID metadata.
  - Scopes to a security domain via include/exclude project list.
  - Stops all project bridges cleanly when the host bridge terminates.
depends-on-artifacts:
  - ADR-038
  - ADR-039
addresses: []
evidence-pool: "process-supervision-patterns"
---

# Host Bridge Kernel

## Goal / Objective

Build the hub daemon that manages project bridges, spawns the shared chat adapter, routes events, and polls tmux sessions. This is the core kernel component of the Untethered Operator system.

## Desired Outcomes

The operator gets a persistent, reliable daemon on each project host. Sessions are discoverable from the chat interface. Project bridges start and stop under supervision. If the host reboots, the daemon restarts and reconciles state.

## Scope Boundaries

**In scope:**
- OS-native daemon installation (launchd plist, systemd unit).
- Tmux session polling and unmanaged session discovery.
- Project bridge lifecycle management (spawn, stop, crash recovery).
- Chat adapter plugin spawn and NDJSON event routing.
- Security domain scoping (include/exclude project lists).
- Graceful shutdown cascading to children.

**Out of scope:**
- The chat adapter plugin itself (EPIC-072).
- Runtime adapter plugins (EPIC-073).
- The provisioning UX (EPIC-074).

## Child Specs

_To be created during implementation planning._

## Key Dependencies

- ADR-038 (Microkernel Plugin Architecture) — defines the plugin contract.
- ADR-039 (Hub-and-Spoke Topology) — defines the routing model.
- `process-supervision-patterns` trove — informs daemon design.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-06 | -- | Created from VISION-006 decomposition. |
