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
- Instrumenting startup to validate assumptions (SPIKE-052)

**Out of scope:**
- Rewriting swain-session's status dashboard internals (those are fine once invoked)
- Changes to swain-doctor's checks (they run infrequently)
- Prompt caching or model-level optimizations

## Child Specs

- [SPIKE-052](../../../research/Complete/(SPIKE-052)-Replace-Beads-CLI-With-Backlog-Md/(SPIKE-052)-Replace-Beads-CLI-With-Backlog-Md.md) — Instrument startup time breakdown
- [SPEC-203](../../../spec/Active/(SPEC-203)-Fast-Path-Session-Greeting/(SPEC-203)-Fast-Path-Session-Greeting.md) — Fast-path session greeting
- [SPEC-195](../../../spec/Active/(SPEC-195)-Defer-Worktree-Creation-to-Task-Dispatch/(SPEC-195)-Defer-Worktree-Creation-to-Task-Dispatch.md) — Defer worktree creation to task dispatch
- [SPEC-196](../../../spec/Active/(SPEC-196)-Collapse-Init-Session-Skill-Chain/(SPEC-196)-Collapse-Init-Session-Skill-Chain.md) — Collapse init -> session skill chain

## Key Dependencies

- SPEC-196 (chain collapse) should land before SPEC-203 (fast greeting) — the chain collapse removes a round-trip that the fast greeting then optimizes further.
- SPIKE-052 should complete first to validate assumptions and set baseline measurements.
- [EPIC-046](../../Complete/(EPIC-046)-Pre-Runtime-Crash-Recovery/(EPIC-046)-Pre-Runtime-Crash-Recovery.md) touches the same shell launcher layer; coordinate to avoid conflicts.

## Retrospective

**Terminal state:** Complete
**Period:** 2026-03-30 — 2026-03-31
**Related artifacts:** [SPIKE-052](../../../research/Complete/(SPIKE-052)-Replace-Beads-CLI-With-Backlog-Md/(SPIKE-052)-Replace-Beads-CLI-With-Backlog-Md.md), [SPEC-196](../../../spec/Active/(SPEC-196)-Collapse-Init-Session-Skill-Chain/(SPEC-196)-Collapse-Init-Session-Skill-Chain.md), [SPEC-203](../../../spec/Active/(SPEC-203)-Fast-Path-Session-Greeting/(SPEC-203)-Fast-Path-Session-Greeting.md), [SPEC-195](../../../spec/Active/(SPEC-195)-Defer-Worktree-Creation-to-Task-Dispatch/(SPEC-195)-Defer-Worktree-Creation-to-Task-Dispatch.md), [SPEC-197](../../../spec/Active/(SPEC-197)-Specgraph-Module-Import-Shadowing/(SPEC-197)-Specgraph-Module-Import-Shadowing.md)

### Summary

All four success criteria met. Session greeting now runs in ~500ms (script time) down from 25-45s total. The work followed a clean spike-then-implement pattern: SPIKE-052 instrumented the startup chain, validated that LLM round-trips dominated (60-75% of wall time), and the three specs attacked different layers of the problem. SPEC-197 (specgraph bug) was discovered during spike instrumentation and fixed as a bonus.

### Reflection

**What went well:**
- Spike-first approach paid off. SPIKE-052's timing data directly shaped which specs mattered most and set measurable targets. Without it, we might have optimized the wrong layer (scripts vs. LLM chain).
- The operator's framing — "key purpose of `swain` is tmux naming and telling the user what's up, everything else deferred" — gave a clear design principle that made every scope decision easy.
- Autonomous overnight execution worked: operator said "keep going until you hit something that needs an operator" and 3 specs + 1 bug fix landed without blocking.
- TDD approach caught issues early — 24 new tests across 3 scripts, all passing on trunk.

**What was surprising:**
- Preflight takes 7.5s, mostly from subprocess spawning overhead (~3.5s for 60+ `python3 -c` calls in the symlink repair loop), not from any individual check. The biggest single check was `git ls-remote` at 1.5s (network I/O).
- The status dashboard spends 17s of its 18.4s total in bash text processing and jq pipelines — only 1.5s is actual data collection (git, tk, GitHub API). The script is 1,067 lines of bash doing work that Python would handle in milliseconds.
- `EnterWorktree` created worktrees from the wrong branch (release instead of trunk). Had to fall back to manual `git worktree add -b ... trunk` for SPEC-194 and SPEC-195.
- SPEC-194 had a number collision (later renumbered to SPEC-203) — `next-artifact-id.sh` didn't prevent it, suggesting the collision avoidance from EPIC-043 has edge cases.

**What would change:**
- The background agent that updated non-claude launcher templates incorrectly modified crush launchers (which don't support initial prompts per ADR-017). Had to revert twice before it stuck. Better to include explicit exclusion criteria in agent prompts when dispatching.
- Could have skipped the tk task tracking for this work — the worktree was manually created (not via swain-do), so tickets ended up in the wrong directory and were inaccessible. The overhead of setting up tk plans for small, fast-moving specs in a single session may not be worth it.

**Patterns observed:**
- "Agent overhead dominates script execution" is now a confirmed recurring pattern. [SPEC-113](../../../spec/Active/(SPEC-113)-Sync-Latency-Reduction/SPEC-113.md) found the same thing for swain-sync (12-15 LLM round-trips = 40-60s, git ops = 3.5s). The architectural response — collapse skill chains, defer expensive work, do more in shell before invoking the LLM — applies broadly across swain.
- Status dashboard bash overhead (17s for text processing) suggests a deeper rewrite is needed. Not in this epic's scope, but the data is now captured.

### Learnings captured

| Item | Type | Summary |
|------|------|---------|
| Preflight subprocess overhead | SPEC candidate | Preflight spawns 60+ subprocesses for symlink repair; batch into single Python call |
| Status dashboard bash rewrite | SPEC candidate | 17s of 18.4s is bash text processing; rewrite collectors in Python |
| EnterWorktree branch selection | SPEC candidate (bug) | EnterWorktree creates from default branch, not HEAD; needs investigation |
| Dispatched agents need exclusion criteria | feedback (memory) | When dispatching agents to modify templates, include explicit exclusion lists for edge cases (e.g., crush doesn't support initial prompts) |
| next-artifact-id.sh collision edge case | SPEC candidate (bug) | SPEC-194 collided despite EPIC-043's collision prevention; investigate |

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-30 | -- | Initial creation; operator-requested |
