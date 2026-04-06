---
title: "Backlog Appraisal Bootstrap"
artifact: EPIC-067
track: container
status: Proposed
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
parent-vision: VISION-004
parent-initiative: INITIATIVE-021
priority-weight: ""
success-criteria:
  - All active Visions have appraisal-goals with structured axis weights
  - All active Initiatives have serves-goals and cost-estimate
  - Agent-proposed estimates are reviewed and confirmed by the operator
  - chart.sh recommend produces differentiated scores across the active backlog
depends-on-artifacts:
  - EPIC-066
linked-artifacts:
  - SPIKE-059
addresses: []
---

# Backlog Appraisal Bootstrap

## Goal / Objective

Apply value and cost estimates to swain's existing artifacts so the ROI scoring engine has data to work with. Without this, the engine exists but produces uniform scores (all unappraised).

## Desired Outcomes

The operator runs a bootstrap pass across the active backlog. Agents propose estimates based on artifact content and parent Vision context. The operator reviews, adjusts, and confirms. After bootstrap, `chart.sh recommend` produces meaningfully differentiated rankings. The operator can see which Visions are getting the most investment relative to their expected return.

## Scope Boundaries

**In scope:** Appraisal of active Visions (axis weights), active Initiatives (serves-goals, cost-estimate), active Epics (serves-goals, cost-estimate where scope is concrete enough). Agent-assisted estimation tooling or workflow.

**Out of scope:** Appraisal of completed or abandoned artifacts, Spec-level estimates (these are set at creation time going forward), portfolio-level views beyond what chart.sh recommend provides.

## Child Specs

To be decomposed after EPIC-066 is complete.

## Key Dependencies

- EPIC-066 (ROI Scoring Engine) — schema and tooling must exist before estimates can be entered and validated

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-06 | | Initial creation |
