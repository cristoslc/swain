---
title: "Shell-Level Marker Check for Init Fast Path"
artifact: SPEC-196
track: implementable
status: Active
author: cristos
created: 2026-03-30
last-updated: 2026-04-05
priority-weight: high
type: enhancement
parent-epic: EPIC-048
parent-initiative: ""
linked-artifacts:
  - ADR-018
  - ADR-030
  - SPEC-175
  - EPIC-045
depends-on-artifacts:
  - SPIKE-052
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Shell-Level Marker Check for Init Fast Path

## Problem Statement

swain-init's Phase 0 checks the `.swain-init` marker to decide whether to run full onboarding (phases 1-6) or the fast path (phase 7). This check is pure shell logic, but it requires a full LLM round-trip (~10-15 seconds) to read the skill file and reason about the marker. That overhead happens on every session start for established projects.

## Desired Outcomes

The shell launcher checks the `.swain-init` marker before invoking the runtime. On established projects (current marker), the launcher passes a hint so swain-init can skip directly to its fast path without re-reading and re-reasoning about the marker. On new or outdated projects, the launcher sends `/swain-init` for full onboarding.

Per ADR-030, the launcher always routes to `/swain-init` — never to `/swain-session`. The marker check determines the *mode*, not the *destination*.

## External Behavior

**Before:**
```
swain() → claude --initial-prompt "/swain-init"
  → LLM reads swain-init skill → checks marker → fast path or onboarding
```

**After:**
```
swain() → check .swain-init marker in shell (<100ms)
  → if current: claude --initial-prompt "/swain-init --fast"
  → if missing/outdated: claude --initial-prompt "/swain-init"
```

**Preconditions:** `.swain-init` file contains a version that can be compared in shell.

**Postconditions:** First-time setup still goes through full `/swain-init`. Established projects get the fast-path hint, saving one LLM reasoning cycle over the marker.

## Acceptance Criteria

1. **Given** a project with a current `.swain-init` marker, **when** the operator runs `swain`, **then** the initial prompt is `/swain-init` with a fast-path hint (not `/swain-session`).
2. **Given** a project with no `.swain-init` marker, **when** the operator runs `swain`, **then** the initial prompt is `/swain-init` (existing behavior).
3. **Given** a project with an outdated `.swain-init` marker (older major version), **when** the operator runs `swain`, **then** the initial prompt is `/swain-init` (triggers re-onboarding).
4. **Given** the shell launcher's marker check, **when** it runs, **then** it completes in <100ms (no LLM involvement).
5. **Given** the `.swain-init` file format, **when** the launcher reads it, **then** it can extract the major version with standard shell tools (grep/sed/jq).

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- The `.swain-init` marker format must remain compatible — this spec adds a consumer, not a new format.
- ADR-018 (structural not prosaic invocation) still applies — the launcher remains the structural entry point.
- ADR-030 (deprecate swain-session) sets the direction — all routing goes to `/swain-init`, never `/swain-session`.
- The shell launcher template in swain-init must be updated to include the marker check for new installs.
- Template launchers already have `_swain_check_marker()` from prior work — need updating to route to `/swain-init --fast` instead of `/swain-session`.
- Must coordinate with EPIC-045 (Shell Launcher Onboarding) and EPIC-046 (Pre-Runtime Crash Recovery) which also modify the shell launcher.

## Rescope Note (2026-04-05)

Original spec routed established projects to `/swain-session`. ADR-030 (2026-04-04) decided to deprecate swain-session and fold all startup into swain-init. Rescoped to align: the marker check stays (it's the valuable work), but the routing destination changes from `/swain-session` to `/swain-init --fast`. Template launchers need a one-line change (`/swain-session` -> `/swain-init --fast`). The main structural launcher (`skills/swain/scripts/swain`) already routes to `/swain-init` and needs the marker check added.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-30 | -- | Initial creation; operator-requested |
| Active | 2026-04-05 | -- | Rescoped to align with ADR-030; routing destination changed from /swain-session to /swain-init --fast |
