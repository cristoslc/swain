---
title: "Watchdog Bridge Restart"
artifact: SPEC-330
track: implementable
status: Active
author: cristos
created: 2026-04-25
last-updated: 2026-04-25
priority-weight: medium
type: feature
parent-epic: EPIC-084
parent-initiative: INITIATIVE-018
linked-artifacts:
  - SPEC-318
  - ADR-047
depends-on-artifacts:
  - SPEC-318
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: deferred
---

# Watchdog Bridge Restart

## Problem Statement

If a bridge subprocess dies (crash, OOM, segfault), the watchdog does not currently restart it. The reconciliation loop checks PID existence and process liveness per SPEC-318, but bridges that exit between cycles are only detected at the next 30-second reconciliation. The watchdog should detect bridge process death promptly and restart within one cycle.

## Desired Outcomes

When a bridge subprocess exits unexpectedly, the watchdog detects it within the next reconciliation cycle and restarts it. Bridge restarts are logged with timestamps.

## Acceptance Criteria

1. **Given** a bridge is running with a valid PID file, **when** the bridge process crashes between reconciliation cycles, **then** the next cycle detects the dead PID and restarts the bridge.

2. **Given** a bridge restarts after a crash, **when** the watchdog writes the new PID, **then** the PID file is updated and a log entry records the restart.

3. **Given** a bridge crashes repeatedly, **when** it has crashed more than 3 times in the last 10 minutes, **then** the watchdog stops restarting it and logs a "crash loop detected" warning.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope and Constraints

- Out of scope: exponential backoff, backoff reset, notification. Just a simple crash loop limit.
- This SPEC was referenced in RUNBOOK-004 as a known gap. Currently deferred until the core reconciliation is stable.