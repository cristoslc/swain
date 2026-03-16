---
title: "Product Design"
artifact: INITIATIVE-007
track: container
status: Proposed
author: cristos
created: 2026-03-15
last-updated: 2026-03-15
parent-vision: VISION-001
success-criteria:
  - swain-design name freed for frontend orchestration (swain-commission rename complete)
  - Frontend design orchestrator integrates Anthropic plugin, superpowers frontend-design, and impeccable.style
  - DESIGN and JOURNEY artifact types inform frontend decisions
linked-artifacts:
  - EPIC-019
  - EPIC-021
  - SPIKE-023
---

# Product Design

## Strategic Focus

Build the frontend design orchestration layer for swain. This initiative first clears the namespace (renaming swain-design to swain-commission), then builds a new swain-design skill as a product design orchestrator — integrating Anthropic's frontend design plugin, superpowers' frontend-design skill, and the impeccable.style design system.

## Scope Boundaries

**In scope:** Skill rename (swain-design → swain-commission), new swain-design frontend orchestrator, design system integration, DESIGN and JOURNEY artifact consumption.

**Out of scope:** Design system creation (impeccable.style is external), Anthropic plugin development, superpowers frontend-design skill development.

## Child Epics

- EPIC-019: Rename swain-design to swain-commission (Proposed)
- EPIC-021: Product Design Orchestrator (Proposed)

## Small Work (Epic-less Specs)

None.

## Key Dependencies

- EPIC-021 depends on EPIC-019 (name must be freed first)
- EPIC-021 depends on SPIKE-023 (integration research)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-15 | — | Created during initiative migration; both child epics still proposed |
