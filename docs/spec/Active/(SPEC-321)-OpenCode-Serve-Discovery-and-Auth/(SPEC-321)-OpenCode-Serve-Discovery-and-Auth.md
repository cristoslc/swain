---
title: "OpenCode Serve Discovery and Auth"
artifact: SPEC-321
track: implementable
status: Active
author: cristos
created: 2026-04-18
last-updated: 2026-04-18
priority-weight: high
type: feature
parent-epic: EPIC-085
parent-initiative: ""
linked-artifacts:
  - ADR-047
  - ADR-038
depends-on-artifacts:
  - ADR-047
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# OpenCode Serve Discovery and Auth

## Problem Statement

The bridge must discover running opencode serve instances, authenticate with per-port credentials, and start one if none are found. Currently there is no mechanism to scan for healthy instances, test authentication against each, or start a new instance when all available instances are unreachable or auth-mismatched. The bridge must also never connect to a port without matching credentials in config.

## Desired Outcomes

A discovery module that, at bridge startup, scans configured and previously seen ports for healthy opencode serve instances, tests authentication, registers usable instances, and — if none are found — starts a new one. All discovery state is persisted to a JSON file for cross-cycle memory.

## External Behavior

**Input:** `opencode` section of `helm.config.json` (ports map, config_path, default_port) plus `~/.config/swain-helm/run/opencode-instances.json`.

**Output:** A list of authenticated, usable opencode serve instances. If none found, a freshly started instance. State persisted to `opencode-instances.json`.

**Discovery flow:**
1. Read `opencode.config_path` to extract `server.port` (default 4096).
2. Build a candidate port set: all ports from `opencode.ports` config plus previously seen ports from `opencode-instances.json`.
3. For each candidate port, `GET /global/health`. If healthy, try auth with that port's cached credentials.
4. If auth succeeds, register as usable. If auth fails, mark as `auth_mismatch` — do not try other credentials against that port.
5. If no usable instance, start `opencode serve --port <default_port>` with auth env vars. Mark `started_by_bridge=true`.
6. Write updated `opencode-instances.json`.

**opencode-instances.json entry schema:**
- `port`, `pid`, `started_by_bridge`, `first_seen`, `last_health_check`, `last_health_result`, `auth_required`, `auth_tested`, `auth_valid`

## Acceptance Criteria

1. **Given** `opencode.config_path` in the config, **when** discovery runs, **then** it reads the config file to extract `server.port` (falling back to default 4096).

2. **Given** configured ports and previously seen ports, **when** discovery runs, **then** it scans all candidate ports for running instances.

3. **Given** a port with a healthy instance, **when** discovery tests auth, **then** it attempts authentication with that port's cached credentials from config.

4. **Given** auth succeeds for a port, **when** discovery registers the instance, **then** it is marked as usable.

5. **Given** auth fails for a port, **when** discovery records the result, **then** it marks the instance as `auth_mismatch` and never tries alternative credentials against that port.

6. **Given** no usable instance is found, **when** discovery completes scanning, **then** it starts `opencode serve --port <default_port>` with auth env vars and marks `started_by_bridge=true`.

7. **Given** discovery completes, **when** it writes state, **then** `opencode-instances.json` is updated with port, pid, started_by_bridge, first_seen, last_health_check, last_health_result, auth_required, auth_tested, and auth_valid for each instance.

8. **Given** a port with no matching credentials in config, **when** discovery scans, **then** it never attempts to connect to that port.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- ~150 lines of Python.
- Health check is `GET /global/health` — no other endpoints.
- Auth test is a single authenticated request; the specific endpoint depends on opencode serve's API (e.g., session list).
- `opencode-instances.json` is the single source of truth for cross-cycle port memory.
- Starting a new instance requires `opencode serve` on PATH.

## Implementation Approach

1. Write a `DiscoveryScanner` class with a `scan()` method that builds the candidate port set.
2. Write a `HealthChecker` that GETs `/global/health` per port and returns up/down.
3. Write an `AuthTester` that attempts an authenticated request per healthy port using config credentials.
4. Write an `InstanceTracker` that reads/writes `opencode-instances.json` and manages the instance registry.
5. Write the `start_if_needed` path that spawns `opencode serve` when no usable instance exists.
6. Wire into bridge startup — discovery runs once per bridge start, not per cycle.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-18 | -- | Initial creation |