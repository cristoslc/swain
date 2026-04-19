---
title: "Verification Model Reform"
artifact: EPIC-082
track: container
status: Abandoned
author: cristos
created: 2026-04-18
last-updated: 2026-04-18
parent-vision: 004
parent-initiative: INITIATIVE-022
priority-weight: medium
success-criteria:
  - Verification happens continuously during implementation, not only at completion
  - Review gate strength scales with diff size — large AI-generated diffs get mandatory review, small changes skip it
  - Builders catch AI-generated bugs mid-flight while the context window still contains the relevant code
  - Shippers close trivial SPECs without filling out evidence forms for one-line changes
depends-on-artifacts:
  - PERSONA-003
  - PERSONA-004
addresses: []
evidence-pool: ""
---

# Verification Model Reform

## Goal / Objective

Move Swain's verification model from a single gate at completion to continuous, proportional verification. Currently, the only verification checkpoint is `Needs Manual Test → Complete` — after all implementation is done. This means AI-generated bugs compound through the entire implementation before detection, and trivial changes carry the same evidence burden as complex ones. The model needs to become continuous (checking during In Progress) and proportional (scaling gate strength with risk).

## Desired Outcomes

- **Builders** catch AI-generated bugs when the context window still has the relevant code, not weeks later at the verification gate.
- **Shippers** close trivial SPECs without disproportionate evidence requirements.
- **Both** benefit from a verification model that applies force proportional to risk, not uniformly regardless of complexity.
- **The system** accumulates quantitative data on where verification catches problems and where it doesn't.

## Progress

<!-- Auto-populated from session digests. -->

## Scope Boundaries

**In scope:**
- Incremental verification during In Progress (acceptance criteria checked per task, not per SPEC)
- Verification confidence scoring (3/7 criteria verified, 2 pending, 2 not started)
- Mandatory code review for diffs exceeding a configurable line threshold (default: 500 lines added)
- Proportional gate strength: low-complexity SPECs get lighter verification

**Out of scope:**
- New artifact types
- Changes to artifact lifecycle phases
- ADR compliance checking (already exists and works)
- CI integration for automated test running (tracked in EPIC-079)

## Child Specs

_To be decomposed when the epic transitions to Active._

## Key Dependencies

- swain-do task completion logic must be extended to run acceptance criteria checks per task
- `spec-verify.sh` must support partial verification (not just all-or-nothing)
- The line threshold for mandatory review must be configurable per repo
- PERSONA-003 and PERSONA-004 evaluations inform the design

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-18 | — | Created from Builder/Shipper persona evaluation |
| Abandoned | 2026-04-18 | — | Redundant with INITIATIVE-022: incremental verification and confidence scoring contradict I22's operator-out-until-teardown model; mandatory code review is a teardown step, not a separate gate |