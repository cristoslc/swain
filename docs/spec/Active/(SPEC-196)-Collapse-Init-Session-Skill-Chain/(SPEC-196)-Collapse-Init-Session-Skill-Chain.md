---
title: "Collapse Init-Session Skill Chain"
artifact: SPEC-196
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
  - ADR-018
  - SPEC-175
  - EPIC-045
depends-on-artifacts:
  - SPIKE-052
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Collapse Init-Session Skill Chain

## Problem Statement

The current startup path forces two full LLM round-trips before the operator sees anything:

1. **Shell launcher** sends `/swain-init` as the initial prompt.
2. **swain-init** reads the skill file, checks the `.swain-init` marker, finds it's current, and invokes `/swain-session`.
3. **swain-session** reads its skill file, runs bootstrap, renders output.

Step 2 is pure overhead on established projects — the `.swain-init` marker exists and is current, so swain-init does nothing except delegate. That's a full skill file read + LLM reasoning cycle (~10-15 seconds) for a conditional that could be a 50ms shell check.

## Desired Outcomes

The shell launcher checks the `.swain-init` marker itself. If the marker exists and its major version matches the installed swain version, the launcher skips `/swain-init` entirely and sends `/swain-session` directly. One fewer LLM round-trip on every session start.

## External Behavior

**Before:**
```
swain() → claude --initial-prompt "/swain-init"
  → LLM reads swain-init skill → checks marker → invokes /swain-session
    → LLM reads swain-session skill → bootstrap
```

**After:**
```
swain() → check .swain-init marker
  → if current: claude --initial-prompt "/swain-session"
  → if missing/outdated: claude --initial-prompt "/swain-init"
```

**Preconditions:** `.swain-init` file contains a version that can be compared in shell.

**Postconditions:** First-time setup still goes through `/swain-init`. Established projects skip directly to `/swain-session`.

## Acceptance Criteria

1. **Given** a project with a current `.swain-init` marker, **when** the operator runs `swain`, **then** the initial prompt is `/swain-session` (not `/swain-init`).
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
- The shell launcher template in swain-init must be updated to include the marker check for new installs.
- Must coordinate with EPIC-045 (Shell Launcher Onboarding) and EPIC-046 (Pre-Runtime Crash Recovery) which also modify the shell launcher.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-30 | -- | Initial creation; operator-requested |
