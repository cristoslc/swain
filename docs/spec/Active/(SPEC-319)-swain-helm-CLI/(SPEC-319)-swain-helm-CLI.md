---
title: "swain-helm CLI"
artifact: SPEC-319
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
  - ADR-047
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# swain-helm CLI

## Problem Statement

The operator needs a CLI with explicit scopes to manage the watchdog and projects. Currently there is no structured command interface — bridging operations are ad-hoc scripts or manual process management. The operator needs clear, scoped subcommands: `host` for watchdog lifecycle and `project` for project registration and removal.

## Desired Outcomes

A CLI tool (`swain-helm`) with two scopes — `host` and `project` — that cover all day-to-day operations: starting and stopping the watchdog, checking status, provisioning credentials, and managing which projects are registered.

## External Behavior

```
swain-helm host up [--foreground]     # Start watchdog (daemon or foreground)
swain-helm host down [--project NAME] # Stop watchdog (and all bridges) or one bridge
swain-helm host status                 # Show watchdog PID, bridge PIDs, opencode health, port
swain-helm host provision              # Run Zulip provisioning, write helm.config.json

swain-helm project add ./              # Add current directory (reject if no .git/)
swain-helm project add ~/code/swain    # Add by absolute path
swain-helm project remove --project NAME  # Remove project config
swain-helm project list                # List all registered projects with status
```

## Acceptance Criteria

1. **Given** the watchdog is not running, **when** the operator runs `swain-helm host up`, **then** the watchdog daemon starts.

2. **Given** the `--foreground` flag, **when** the operator runs `swain-helm host up --foreground`, **then** the watchdog runs in the foreground (no daemon fork).

3. **Given** the watchdog and all bridges are running, **when** the operator runs `swain-helm host down`, **then** the watchdog and all bridges stop.

4. **Given** the operator wants to stop one bridge, **when** they run `swain-helm host down --project <name>`, **then** only that bridge is stopped (watchdog and other bridges remain).

5. **Given** the watchdog is running with managed bridges, **when** the operator runs `swain-helm host status`, **then** output shows watchdog PID, bridge PIDs, opencode serve health, and port.

6. **Given** Zulip credentials are not yet configured, **when** the operator runs `swain-helm host provision`, **then** Zulip provisioning runs and writes `helm.config.json`.

7. **Given** the current directory contains `.git/`, **when** the operator runs `swain-helm project add ./`, **then** the project is registered in `~/.config/swain-helm/projects/<name>.json`.

8. **Given** the current directory has no `.git/`, **when** the operator runs `swain-helm project add ./`, **then** the command rejects with a clear error.

9. **Given** a valid absolute path, **when** the operator runs `swain-helm project add ~/code/swain`, **then** the project at that path is registered.

10. **Given** a project is registered, **when** the operator runs `swain-helm project remove --project <name>`, **then** the project config is removed.

11. **Given** one or more projects are registered, **when** the operator runs `swain-helm project list`, **then** all registered projects are listed with their status (running/stopped).

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- ~250 lines of shell script or Python CLI with subcommands.
- No interactive prompts — all inputs via flags or positional args.
- `host provision` requires Zulip API access; failure exits with a clear error.
- Project names are derived from the directory basename (e.g., `swain` for `~/code/swain`).

## Implementation Approach

1. Define CLI structure with `host` and `project` subcommand groups.
2. Implement `host up` and `host down` as thin wrappers around watchdog start/stop (SPEC-318).
3. Implement `host status` by reading PID files and checking opencode serve health.
4. Implement `host provision` as a Zulip bot creation + config write.
5. Implement `project add` with `.git/` validation and config file write.
6. Implement `project remove` with config file delete and optional bridge stop.
7. Implement `project list` by reading all config files and checking PID files.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-18 | -- | Initial creation |