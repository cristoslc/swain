---
title: "Worktree Session Branch Name Collision"
artifact: SPEC-174
track: implementable
status: Active
author: cristos
created: 2026-03-27
last-updated: 2026-03-27
priority-weight: ""
type: bug
parent-epic: ""
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Worktree Session Branch Name Collision

## Problem Statement

When multiple sessions start concurrently and each auto-creates a worktree, they all attempt to use the same branch name (`worktree-session` or similar static name). The second session fails because git refuses to create a branch that already exists. At minimum, branch names need a timestamp or other disambiguator to prevent collisions.

## Desired Outcomes

Concurrent swain sessions can each create their own worktree without colliding on branch names. The branch name is unique per session and identifiable (not just a random hash).

## External Behavior

**Precondition:** Multiple sessions start simultaneously (e.g., operator opens two terminal tabs running `swain`).

**Current behavior:** Both sessions attempt to create a branch named `worktree-session`. The second one fails with `fatal: a branch named 'worktree-session' already exists`.

**Expected behavior:** Each session creates a uniquely-named branch. The name should include enough context to identify the session (timestamp, short hash, or session ID) while remaining human-readable.

**Proposed naming scheme:** `worktree-<context>-<timestamp>` where timestamp is `YYYYMMDD-HHmmss` or a short random suffix. Examples:
- `worktree-session-20260327-143022`
- `worktree-epic-045-20260327-143022`

## Acceptance Criteria

1. **Given** two sessions start within the same second, **when** both attempt to create worktrees, **then** both succeed with distinct branch names.

2. **Given** a worktree branch name, **when** I read it, **then** I can identify when it was created (timestamp) or what it's for (context slug).

3. **Given** the `EnterWorktree` tool is called without a name, **when** it generates a branch name, **then** the name includes a disambiguator (not just `worktree-session`).

## Reproduction Steps

1. Open two terminal tabs
2. Run `swain` in both simultaneously
3. Both sessions attempt worktree auto-isolation
4. Second session fails on branch creation

## Severity

medium — workaround exists (manually name worktrees), but the default auto-isolation path is broken for concurrent sessions.

## Expected vs. Actual Behavior

**Expected:** Each session gets its own worktree with a unique branch name.

**Actual:** Second session fails with branch name collision.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Fix should be in whichever component generates the worktree branch name (EnterWorktree tool, swain-session auto-isolation, or swain-do worktree preamble)
- Must not break existing worktree naming when an explicit name is provided (e.g., `EnterWorktree` with `name: "epic-045"`)
- Timestamp resolution should be at least seconds; sub-second collisions can fall back to random suffix

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-27 | — | Initial creation |
