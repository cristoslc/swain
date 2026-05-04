---
title: "Quality Signal Pipeline"
artifact: EPIC-080
track: container
status: Proposed
author: cristos
created: 2026-04-18
last-updated: 2026-04-18
parent-vision: 004
parent-initiative: INITIATIVE-022
priority-weight: high
success-criteria:
  - AI-generated code patterns that violate architectural norms are detected and surfaced before merge
  - Quality debts accepted for velocity are tracked, visible, and time-bound
  - Commits carry a signal indicating whether the diff was primarily human or AI-generated
  - Artifacts stuck in non-terminal phases beyond a threshold are flagged for triage
depends-on-artifacts:
  - PERSONA-003
  - PERSONA-004
addresses: []
evidence-pool: ""
---

# Quality Signal Pipeline

## Goal / Objective

Make invisible quality costs visible. When AI agents generate code, the downstream cost — debugging, architectural drift, slop accumulation — is borne by Builders but not tracked by the system. This epic creates a pipeline of signals that surface those costs so they can be acted on: detection before merge, tracking of accepted debt, and staleness detection for organizational health.

## Desired Outcomes

- **Builders** can identify AI-characteristic code patterns before they land in main, reducing the debugging tax.
- **Shippers** can explicitly accept quality debt with a reconciliation schedule, instead of accumulating it invisibly.
- **Operators** can see which artifacts are stalled and which codebases carry the most debt.
- **The system** produces quantitative evidence about where AI output quality falls short, not just qualitative guesses.

## Progress

<!-- Auto-populated from session digests. -->

## Scope Boundaries

**In scope:**
- AI slop pattern detection (configurable ruleset, advisory warnings)
- `quality-debt` frontmatter field on SPEC artifacts with due dates
- Commit generation signal annotations (`Code-By` trailer)
- Artifact staleness detection in specwatch
- `debt` lens in `chart.sh` for surfacing quality debt

**Out of scope:**
- Automated code fixing (detection only, no auto-repair)
- CI/CD pipeline integration (tracked in EPIC-079)
- Changing the verification gate model (tracked in EPIC-078)
- Linting or formatting rules (use existing tools)

## Child Specs

_To be decomposed when the epic transitions to Active._

## Key Dependencies

- `specwatch.sh` and `chart.sh` must be extended to support new finding types and lenses
- The quality debt field must not break existing SPEC frontmatter schemas
- PERSONA-003 (Builder) and PERSONA-004 (Shipper) evaluations inform the design

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-18 | — | Created from Builder/Shipper persona evaluation |