---
title: "Framework Cost Model"
artifact: EPIC-065
track: container
status: Proposed
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
parent-vision: VISION-004
parent-initiative: INITIATIVE-021
priority-weight: ""
success-criteria:
  - cost-estimate field supports two dimensions (operator-attention, compute-budget) as t-shirt sizes
  - Cost axes are documented as framework-structural (apply to all swain projects)
  - Cost composition formula is decided and documented in an ADR
  - Cost cascades down parent chain like serves-goals
depends-on-artifacts:
  - SPIKE-060
linked-artifacts:
  - SPIKE-059
addresses: []
---

# Framework Cost Model

## Goal / Objective

Define how cost is estimated and composed across the artifact hierarchy. Cost has two axes baked into swain's operating model: operator-attention (cognitive load, decision time) and compute-budget (tokens, API calls, CI minutes). These apply to every swain project because swain prescribes the solo-operator-plus-agents model.

## Desired Outcomes

When an agent creates a Spec, the template prompts for `cost-estimate` with both dimensions. The operator can see that a task is "cheap in tokens but expensive in my time" vs "expensive in tokens but I barely have to think about it." The cost composition formula (how the two axes combine into a single cost number for ROI) is settled by SPIKE-060 and documented in an ADR.

## Scope Boundaries

**In scope:** Frontmatter schema for `cost-estimate` (two-axis t-shirt sizing), cost axis documentation in swain framework docs, cost composition formula (blocked on SPIKE-060), frontmatter contract, definition updates, template updates.

**Out of scope:** Value model (EPIC-077), scoring formula (EPIC-066), project-level cost axis weighting (follow-on — lets operator say "I'm attention-constrained right now").

## Child Specs

To be decomposed after SPIKE-060 completes.

## Key Dependencies

- SPIKE-060 (Cost Axis Composition Model) must complete first — its answer shapes the formula.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-06 | | Initial creation |
