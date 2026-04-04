---
title: "Exclude Docker MCP Gateway from Crash Debris Detection"
artifact: SPEC-251
track: implementable
status: Active
author: cristos
created: 2026-04-03
last-updated: 2026-04-03
priority-weight: high
type: bug
parent-epic: EPIC-046
parent-initiative: ""
linked-artifacts:
  - SPEC-182
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Exclude Docker MCP Gateway from Crash Debris Detection

## Problem Statement

The `check_orphaned_mcp()` function in `crash-debris-lib.sh` uses a broad process-matching pattern (`mcp.*server|mcp.*gateway`) that catches Docker MCP gateway containers running as part of the normal MCP toolchain. These containers are managed by Docker's lifecycle, not by the agent session, so flagging them as crash debris is a false positive. The operator gets a cleanup prompt for processes that should not be touched.

## Desired Outcomes

Crash debris detection runs without false-positiving on Docker-managed MCP processes. Legitimate orphaned MCP servers (spawned directly by a crashed agent session) are still detected.

## External Behavior

**Inputs:** Same as [SPEC-182](../../Complete/(SPEC-182)-Crash-Debris-Detection-Checks/(SPEC-182)-Crash-Debris-Detection-Checks.md) — project root path, optional git worktree path.

**Changed behavior:** `check_orphaned_mcp()` excludes processes whose command line indicates they are managed by Docker (e.g., `docker`, `containerd-shim`, or similar container runtime signatures). The exclusion is pattern-based and covers common Docker MCP gateway invocations.

**Postconditions:** Docker MCP gateway processes are never reported as orphaned MCP servers. Non-Docker MCP processes with a dead parent session are still detected.

## Acceptance Criteria

1. **Given** a running Docker MCP gateway container, **when** `check_orphaned_mcp()` runs, **then** it does not flag the container as orphaned.
2. **Given** a non-Docker MCP server process whose parent session is dead, **when** `check_orphaned_mcp()` runs, **then** it still detects and reports the orphan.
3. **Given** no MCP processes running, **when** `check_orphaned_mcp()` runs, **then** it completes silently (existing fast-path behavior preserved).

## Reproduction Steps

1. Start a session with Docker MCP gateway running (e.g., via `mcp-docker` in Claude Code settings).
2. Run `swain-doctor` or trigger the pre-runtime crash debris check.
3. Observe that Docker MCP gateway processes are flagged as orphaned MCP servers.

## Severity

medium

## Expected vs. Actual Behavior

**Expected:** Docker MCP gateway containers are ignored by orphan detection since they are managed by Docker, not the agent session.

**Actual:** `check_orphaned_mcp()` matches any process with `mcp.*server` or `mcp.*gateway` in the command line, including Docker-managed containers, and reports them as crash debris.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Fix is scoped to `check_orphaned_mcp()` in `crash-debris-lib.sh` — no changes to other debris checks.
- Exclusion must be pattern-based (no Docker API dependency). Match on command-line signatures like `docker`, `containerd-shim`, or container runtime indicators.
- Existing tests for non-Docker orphan detection must continue to pass.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-03 | — | Bug: Docker MCP gateway false positive in orphan detection |
