---
title: "Release README Gate"
artifact: SPEC-211
track: implementable
status: Complete
author: operator
created: 2026-03-31
last-updated: 2026-03-31
priority-weight: ""
type: feature
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

# Release README Gate

## Problem Statement

A release can ship with a README that contradicts the artifact tree or promises behavior that no test covers. Broken promises erode trust.

## Desired Outcomes

Every release passes two README checks before shipping. Overrides require an explicit statement. Untested promises get a clear choice: add a test, remove the promise, or accept the gap.

## External Behavior

Two-part hard gate between security check (5.5) and commit/tag (6):

1. **Alignment check** — README claims vs. artifact tree. Unresolved drift blocks the release.
2. **Verification check** — README claims that imply testable behavior must be covered by the test suite. For each untested promise: add test, remove promise, or accept gap.

Override requires explicit statement, recorded in release notes.

## Acceptance Criteria

- Given README drift, when swain-release runs, then alignment check blocks with findings.
- Given untested README promises, then verification check surfaces each one.
- Given operator override, then it is recorded in release metadata.
- Given no drift and full coverage, then both checks pass silently.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| Section 5.7 in SKILL.md | Haiku agent verified two-part gate | PASS |
| Alignment check covers 3 categories | Stale promises, missing coverage, contradictions | PASS |
| Verification check covers 5 categories | Install, CLI, API, behavioral, integration | PASS |
| Override requires explicit statement | Haiku agent confirmed no silent bypass | PASS |

## Scope & Constraints

- Depends on semantic extraction from SPEC-207.
- Swain does not auto-generate tests.
- Override requires explicit operator statement, not a flag.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | — | Initial creation |
| Complete | 2026-03-31 | 61379ba | Step 5.7 in swain-release SKILL.md |
