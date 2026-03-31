---
title: "Session Startup Fast Path"
artifact: EPIC-048
track: container
status: Active
author: cristos
created: 2026-03-30
last-updated: 2026-03-30
parent-vision: VISION-001
parent-initiative: INITIATIVE-003
priority-weight: high
success-criteria:
  - Session greeting (tmux tab name + brief status) visible within 5 seconds of `swain` invocation
  - Full status dashboard available on-demand, not blocking startup
  - Worktree creation deferred until task dispatch, not session start
  - No regression in session state integrity (bookmark, focus lane, session.json)
depends-on-artifacts: []
addresses: []
evidence-pool: ""
---

# Session Startup Fast Path

## Goal / Objective

Reduce swain session startup from 25-45 seconds to under 5 seconds for the initial greeting. The current startup chain (shell launcher -> swain-init -> preflight -> doctor -> swain-session bootstrap -> status dashboard) forces 4-6 LLM round-trips through the skill chain before the operator sees anything useful. The actual computation is ~5-8s; the rest is inference overhead.

The operator types `swain` with a task in mind. By the time the session loads, they've forgotten what it was.

## Desired Outcomes

The operator gets immediate feedback: tmux tab is named, brief context is shown (branch, last bookmark, focus lane), and they can start talking. Everything else — full status dashboard, specgraph, GitHub issue sync, worktree creation — happens on-demand or in the background.

## Scope Boundaries

**In scope:**
- Collapsing the init -> session skill chain
- Splitting fast greeting from full status dashboard
- Deferring worktree creation to swain-do
- Instrumenting startup to validate assumptions (SPIKE-001)

**Out of scope:**
- Rewriting swain-session's status dashboard internals (those are fine once invoked)
- Changes to swain-doctor's checks (they run infrequently)
- Prompt caching or model-level optimizations

## Child Specs

- [SPIKE-001](../../spike/Active/(SPIKE-001)-Session-Startup-Time-Instrumentation/(SPIKE-001)-Session-Startup-Time-Instrumentation.md) — Instrument startup time breakdown
- [SPEC-203](../../spec/Active/(SPEC-203)-Fast-Path-Session-Greeting/(SPEC-203)-Fast-Path-Session-Greeting.md) — Fast-path session greeting
- [SPEC-195](../../spec/Active/(SPEC-195)-Defer-Worktree-Creation-to-Task-Dispatch/(SPEC-195)-Defer-Worktree-Creation-to-Task-Dispatch.md) — Defer worktree creation to task dispatch
- [SPEC-196](../../spec/Active/(SPEC-196)-Collapse-Init-Session-Skill-Chain/(SPEC-196)-Collapse-Init-Session-Skill-Chain.md) — Collapse init -> session skill chain

## Key Dependencies

- SPEC-196 (chain collapse) should land before SPEC-203 (fast greeting) — the chain collapse removes a round-trip that the fast greeting then optimizes further.
- SPIKE-001 should complete first to validate assumptions and set baseline measurements.
- [EPIC-046](../Active/(EPIC-046)-Pre-Runtime-Crash-Recovery/(EPIC-046)-Pre-Runtime-Crash-Recovery.md) touches the same shell launcher layer; coordinate to avoid conflicts.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-30 | -- | Initial creation; operator-requested |
