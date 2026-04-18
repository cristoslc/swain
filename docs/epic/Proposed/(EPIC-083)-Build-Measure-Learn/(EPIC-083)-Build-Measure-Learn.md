---
title: "Build-Measure-Learn Support"
artifact: EPIC-083
track: container
status: Proposed
author: cristos
created: 2026-04-18
last-updated: 2026-04-18
parent-vision: 004
parent-initiative: INITIATIVE-005
priority-weight: medium
success-criteria:
  - Shippers can track production experiments with hypotheses and success metrics
  - Decisions made after building (retroactive specs) are captured with the same rigor as prospective ones
  - Swain's artifact model supports a lifecycle that starts deployed, not planned
  - Product outcomes are tracked alongside implementation evidence
depends-on-artifacts:
  - PERSONA-004
  - PERSONA-003
addresses: []
evidence-pool: ""
---

# Build-Measure-Learn Support

## Goal / Objective

Add first-class support for the build-measure-learn loop to Swain's artifact model. Currently, every artifact starts with intent (Proposed) and tracks toward completion (Complete). This works for planned work but fails for experimental work — Shippers who deploy first and learn second have no way to capture hypotheses, success metrics, and outcomes. This epic also covers retroactive spec creation, which serves the same population: people who build first and document after.

## Desired Outcomes

- **Shippers** can create an EXPERIMENT artifact that starts deployed, captures a hypothesis and success metric, and resolves to Confirmed/Refuted/Inconclusive.
- **Shippers** can create retroactive SPECs for work already built, backfilling the artifact graph.
- **Builders** running experiments can track whether their quality improvements had measurable impact.
- **The system** links experiments to outcomes, not just to implementation evidence.

## Progress

<!-- Auto-populated from session digests. -->

## Scope Boundaries

**In scope:**
- EXPERIMENT artifact type (lifecycle: Proposed → Running → Resolved with resolution: Confirmed/Refuted/Inconclusive)
- Retroactive SPEC creation (`swain-design create SPEC --retroactive`)
- Hypothesis and success metric fields on EXPERIMENT
- Product outcome tracking on SPECs (optional field linking implementation evidence to measured outcomes)
- CI/deployment hooks in swain-sync and swain-release

**Out of scope:**
- Changes to verification gate model (tracked in EPIC-078)
- Changes to lifecycle pathways or fast paths (tracked in EPIC-077)
- A/B testing infrastructure (Swain tracks the experiment, does not run it)
- Analytics dashboards (outcome data comes from external tools)

## Child Specs

_To be decomposed when the epic transitions to Active._

## Key Dependencies

- EXPERIMENT requires a new artifact definition, template, folder structure, and lifecycle
- Retroactive SPEC creation requires git history scanning and commit analysis
- CI hooks require swain-sync/swain-release to support configurable post-push triggers
- PERSONA-004 (Shipper) evaluation is the primary driver; PERSONA-003 (Builder) benefits from outcome tracking

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-18 | — | Created from Builder/Shipper persona evaluation |