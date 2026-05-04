---
title: "swain-helm Watchdog Core"
artifact: SPEC-318
track: implementable
status: Active
author: cristos
created: 2026-04-18
last-updated: 2026-04-18
priority-weight: high
type: feature
parent-epic: EPIC-084
parent-initiative: ""
linked-artifacts:
  - ADR-046
  - ADR-047
depends-on-artifacts:
  - ADR-046
  - ADR-047
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# swain-helm Watchdog Core

## Problem Statement

The bridge needs a persistent process manager that reconciles desired state against running processes. Without a watchdog, there is no mechanism to detect stale bridges, restart crashed ones, or shut down bridges when their project configs are removed. The system currently lacks a reconciliation loop that can compare desired state (project configs) with actual state (running PIDs) and take corrective action.

## Desired Outcomes

A watchdog daemon that continuously maintains the bridge fleet at the desired state. Projects with `auto_start=true` always have a running bridge. Crashed bridges restart within one cycle (30s). Removed configs trigger clean shutdown. The watchdog runs as a long-lived process in either foreground or daemon mode.

## External Behavior

**Input:** Project configs from `~/.config/swain-helm/projects/`.

**Output:** Running bridge processes, PID files in `~/.config/swain-helm/run/bridges/<name>.pid`, and a watchdog PID file at `~/.config/swain-helm/run/watchdog.pid`.

**Reconciliation cycle (30s):**
1. Read all project configs.
2. For each config with `auto_start=true`, check if bridge is running (PID file exists and process is alive).
3. If not running, start bridge and write PID.
4. If PID is alive but health check fails, kill and restart.
5. If a config was removed, stop its bridge.

**Daemon mode (`--daemon`):** Backgrounds the process, writes `watchdog.pid`.

**Foreground mode (default):** Ctrl-C triggers graceful shutdown of all managed bridges.

## Acceptance Criteria

1. **Given** project configs exist in `~/.config/swain-helm/projects/`, **when** the watchdog runs a reconciliation cycle, **then** it reads all configs and evaluates each one.

2. **Given** a project config with `auto_start=true` and no running bridge (PID file stale or missing), **when** the watchdog cycle runs, **then** it starts a new bridge process and writes the PID to `~/.config/swain-helm/run/bridges/<name>.pid`.

3. **Given** a bridge PID is alive but its health check fails, **when** the watchdog cycle runs, **then** it kills the process and starts a new bridge.

4. **Given** a project config is removed from the projects directory, **when** the next watchdog cycle runs, **then** it stops the corresponding bridge process.

5. **Given** a bridge is running, **when** the watchdog writes its PID, **then** the PID file is at `~/.config/swain-helm/run/bridges/<name>.pid`.

6. **Given** the watchdog is started with `--daemon`, **when** it backgrounds, **then** it writes its own PID to `~/.config/swain-helm/run/watchdog.pid`.

7. **Given** the watchdog is running in foreground mode, **when** Ctrl-C is pressed, **then** it gracefully shuts down all managed bridges before exiting.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Reconciliation cycle is fixed at 30s (no dynamic adjustment in this spec).
- PID files are the sole mechanism for tracking running processes — no D-Bus, no sockets.
- Health check mechanism is defined here as "process is alive" plus a configurable health endpoint check; the actual endpoint is project-specific.
- ~200 lines of Python estimated.
- No signal handling beyond SIGINT (Ctrl-C) in this spec.

## Implementation Approach

TDD cycles in order:
1. **Reconciliation loop:** Config reader, cycle timer, desired-state vs actual-state comparison.
2. **PID management:** Write PID files on start, read and validate on check, clean up on stop.
3. **Health checks:** HTTP or socket-based liveness check per bridge, kill-and-restart on failure.
4. **Daemon mode:** Fork/background, write watchdog.pid, detach from terminal.
5. **Graceful shutdown:** SIGINT handler that sends stop signals to all managed bridges, waits for exit, then exits itself.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-18 | -- | Initial creation |