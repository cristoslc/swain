---
title: "Retro README Drift Check"
artifact: SPEC-210
track: implementable
status: Complete
author: operator
created: 2026-03-31
last-updated: 2026-03-31
priority-weight: ""
type: enhancement
parent-epic: EPIC-050
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts:
  - SPEC-207
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Retro README Drift Check

## Problem Statement

Retrospectives reflect on what happened in an epic but don't check whether the README still describes the project accurately. Gradual drift goes undetected until release.

## Desired Outcomes

Every retro includes a README reconciliation pass. The operator sees where the README drifted during the epic's lifetime.

## External Behavior

After reflection (Step 4.5) and before closing the retro, check README.md against artifacts that changed during the retro scope. Surface drift: new features omitted, stale promises, changed behavior.

## Acceptance Criteria

- Given an epic that added a capability not in the README, when swain-retro runs, then drift is surfaced.
- Given an epic that dropped a feature the README still promises, then the stale promise is surfaced.
- Given no drift, then the check passes silently.
- Given deferred findings, then they appear in the retro output.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| Step 4.7 section in SKILL.md | Haiku agent verified section with drift categories | PASS |
| Correct placement | After Step 4.5, before Step 5 | PASS |
| Handles both auto and interactive modes | Both modes documented | PASS |

## Scope & Constraints

- Depends on semantic extraction from SPEC-207.
- Adds a section to existing retro flow, does not change structure.
- Drift findings are informational during retro, not blocking.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | — | Initial creation |
| Complete | 2026-03-31 | 61379ba | Step 4.7 in swain-retro SKILL.md |
