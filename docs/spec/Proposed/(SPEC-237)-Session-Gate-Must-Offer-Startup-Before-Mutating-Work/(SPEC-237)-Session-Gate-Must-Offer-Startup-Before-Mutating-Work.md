---
title: "Session Gate Must Offer Startup Before Mutating Work"
artifact: SPEC-237
track: implementable
status: Proposed
author: cristos
created: 2026-04-02
last-updated: 2026-04-02
priority-weight: ""
type: bug
parent-epic: ""
parent-initiative: INITIATIVE-019
linked-artifacts:
  - EPIC-056
  - SPEC-241
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Session Gate Must Offer Startup Before Mutating Work

## Problem Statement

The agent proceeded with mutating work after `swain-session-check.sh` returned `{"status":"none"}`. It treated the missing session as a warning to mention instead of a gate that should trigger session startup or an explicit operator choice.

## Desired Outcomes

When mutating work begins and no session is active, the flow must stop long enough to start a session or get an explicit operator dismissal. The agent should not silently continue after seeing the missing-session signal.

## External Behavior

**Before:** A skill can detect `status: none`, mention it in chat, and keep mutating files anyway.

**After:** A skill that is about to mutate files and detects `status: none` must either:
1. start the session flow, or
2. get a clear operator override to proceed without a session.

## Acceptance Criteria

1. **Given** a mutating workflow in a worktree, **when** session check returns `status: none`, **then** the workflow offers session startup before continuing.
2. **Given** the operator tells the agent to start the session, **when** the startup path runs, **then** the session is initialized before any further mutating work.
3. **Given** the operator explicitly dismisses the session gate, **when** work continues, **then** the bypass is treated as an override rather than the default path.
4. **Given** a read-only workflow, **when** session check returns `status: none`, **then** the workflow may remain informational and does not need to block.

## Reproduction Steps

1. Enter a worktree with no active session state.
2. Begin artifact or task work that mutates files.
3. Run session check and observe `status: none`.
4. Continue mutating work without starting a session.

## Severity

medium

## Expected vs. Actual Behavior

**Expected:** Missing-session detection should force startup or a clear operator override before mutating work continues.

**Actual:** The agent saw the missing-session signal, mentioned it, and kept going until the operator intervened.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

In scope: session gate behavior for mutating workflows, startup handoff, override path, regression coverage.

Out of scope: changing read-only behavior, redesigning the full session model, changing chart or tk.

## Implementation Approach

Identify the mutating entry points that currently treat missing-session as advisory. Make them trigger session startup or require an explicit override before continuing. Cover the regression with a fixture or command-level test that reproduces the exact missing-session path.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-02 | — | Created from live session-start failure during EPIC-056 handoff |
