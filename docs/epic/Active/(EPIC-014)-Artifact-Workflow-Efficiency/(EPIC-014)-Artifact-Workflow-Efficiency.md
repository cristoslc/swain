---
title: "Artifact Workflow Efficiency"
artifact: EPIC-014
status: Active
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
parent-vision: VISION-001
success-criteria:
  - Filing a simple bug SPEC takes ≤30 seconds and ≤500 tokens of agent work
  - The full-ceremony path remains available for complex artifacts (specs, ADRs, epics)
  - Ceremony reduction does not compromise artifact quality or missing critical checks
depends-on-artifacts:
  - SPIKE-018
addresses: []
evidence-pool: ""
---

# Artifact Workflow Efficiency

## Goal / Objective

The swain-design workflow was designed for correctness and completeness — and delivers both. But for routine operations (filing a bug, quick enhancement note, trivial spike), the fixed ceremony cost (template population, adr-check, alignment check, index refresh, two-commit stamp) is disproportionate to the value of the artifact.

This epic introduces a tiered authoring model: a lightweight "fast path" for low-complexity artifacts and a full-ceremony path for artifacts that warrant it. The goal is to reduce latency and token cost for routine work without undermining the quality guarantees for complex artifacts.

## Scope Boundaries

In scope:
- Defining complexity tiers for artifact types (e.g., bug SPEC vs. feature SPEC vs. new epic)
- Implementing a fast-path `swain-design` invocation that skips optional steps for low-complexity artifacts
- Identifying which checks are mandatory vs. advisory per artifact type and complexity tier
- Rethinking the two-commit lifecycle stamp for trivial artifacts (is it necessary?)

Out of scope:
- Removing checks that catch real errors (e.g., adr-check for new feature specs is load-bearing)
- Changing the artifact schema or template format
- Performance optimization of the underlying scripts (specwatch, specgraph)

## Child Specs

To be defined after SPIKE-018 findings.

## Key Dependencies

SPIKE-018 must complete before implementation specs are written — the spike determines where latency actually lives and which ceremony steps are skippable.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Initial creation |
