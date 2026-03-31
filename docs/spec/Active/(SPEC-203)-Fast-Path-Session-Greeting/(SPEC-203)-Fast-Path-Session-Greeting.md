---
title: "Fast-Path Session Greeting"
artifact: SPEC-203
track: implementable
status: Active
author: cristos
created: 2026-03-30
last-updated: 2026-03-30
priority-weight: high
type: enhancement
parent-epic: EPIC-048
parent-initiative: ""
linked-artifacts:
  - SPEC-175
  - SPEC-122
depends-on-artifacts:
  - SPIKE-001
  - SPEC-196
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Fast-Path Session Greeting

## Problem Statement

swain-session currently treats startup and status as one operation. The bootstrap script runs, then the full status dashboard renders (specgraph build, GitHub API, task collection) before the operator sees anything. The key purpose of `swain` is to get the tmux window named and tell the user what's up — everything else should be backgrounded or deferred.

## Desired Outcomes

The operator sees useful context within seconds of typing `swain`: their tmux tab is named, they know what branch they're on, what they were last working on (bookmark), and their focus lane. The full status dashboard is available via `/swain-session status` but doesn't block the greeting.

## External Behavior

**Inputs:** `swain` shell command or `/swain-session` skill invocation.

**Outputs (fast greeting):**
- tmux tab renamed to project + branch context
- One-line branch status (branch name, clean/dirty)
- Last bookmark (if any)
- Focus lane (if set)
- Any preflight warnings (crash debris, stale locks)

**Outputs (deferred, on-demand):**
- Full artifact graph / specgraph status
- GitHub issue sync
- Task breakdown and progress
- Session lifecycle state

**Postconditions:** session.json loaded, tab named, operator can immediately start working.

## Acceptance Criteria

1. **Given** a clean project with session.json, **when** the operator runs `swain`, **then** the tmux tab is named and greeting is displayed within one LLM response (no chained skill invocations for the greeting itself).
2. **Given** a project with a bookmark and focus lane, **when** the greeting renders, **then** both are shown in the greeting output.
3. **Given** a project with preflight warnings (crash debris, stale locks), **when** the greeting renders, **then** warnings are surfaced inline without blocking.
4. **Given** the operator wants full status, **when** they run `/swain-session status`, **then** the full dashboard renders (specgraph, tasks, issues).
5. **Given** a greeting was already shown this session, **when** the operator asks "what's next", **then** the full status dashboard renders (not the greeting again).

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Must not break session.json state management or lifecycle tracking.
- The greeting script should be a single bash call (building on SPEC-175's consolidation pattern).
- Status dashboard internals are unchanged — this spec only gates when they run.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-30 | -- | Initial creation; operator-requested |
