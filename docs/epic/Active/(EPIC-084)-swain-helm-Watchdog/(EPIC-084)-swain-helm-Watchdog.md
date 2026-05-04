---
title: "swain-helm Watchdog"
artifact: EPIC-084
track: container
status: Active
author: cristos
created: 2026-04-18
last-updated: 2026-04-18
parent-vision: VISION-006
parent-initiative: INITIATIVE-018
priority-weight: high
success-criteria:
  - Watchdog reconciles desired state from projects/ config against running bridges every 30s.
  - Crashed project bridges are detected and restarted within one reconciliation cycle.
  - Credential resolution via 1Password succeeds at startup with biometric unlock present.
  - Resolved credentials are cached in process-locked memory and never written to disk or stdout.
  - opencode serve discovery finds existing instances on configured ports, starts new ones if none found.
  - Per-port credentials prevent spraying auth at unknown servers.
  - swain-helm CLI supports host up/down/status/provision and project add/remove/list with explicit scopes.
depends-on-artifacts:
  - ADR-046
  - ADR-047
addresses: []
evidence-pool: ""
---

# swain-helm Watchdog

## Goal / Objective

Build the persistent process manager for the swain-helm system. The watchdog ensures project bridges are running, resolves credentials once at startup, discovers or starts opencode serve, and reconciles desired state against running processes on a continuous loop.

## Desired Outcomes

The operator runs `swain-helm host up` once. The watchdog starts, resolves 1Password references, discovers opencode serve, and starts all configured project bridges. From then on, the operator only interacts through Zulip or the CLI for management. Crashes are self-healing. New projects appear when `swain-helm project add` writes a config file.

## Scope Boundaries

**In scope:**
- Desired-state reconciliation loop (30s cycle).
- Project bridge lifecycle management (spawn, health-check, restart, stop).
- Credential resolution via `op read` at startup, process-locked cache.
- Per-port opencode serve discovery, auth, and startup.
- Instance tracking in `opencode-instances.json`.
- `swain-helm` CLI with host/project scopes.
- PID file management in `~/.config/swain-helm/run/`.

**Out of scope:**
- Project bridge internals (EPIC-071).
- Chat adapter plugin (EPIC-072).
- Runtime adapter plugins (EPIC-073, EPIC-085).
- Provisioning UX (EPIC-074).

## Child Specs

- SPEC-318: swain-helm Watchdog Core
- SPEC-319: swain-helm CLI
- SPEC-320: Config and Credential Resolution

## Key Dependencies

- ADR-046 (Project-Level Microkernel Topology) — defines the topology the watchdog manages.
- ADR-047 (swain-helm Watchdog Architecture) — defines the watchdog's design decisions.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-18 | -- | Replaces EPIC-070 (Host Bridge Kernel). |