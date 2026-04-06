---
title: "Appraisal Value Model"
artifact: EPIC-064
track: container
status: Proposed
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
parent-vision: VISION-004
parent-initiative: INITIATIVE-021
priority-weight: ""
success-criteria:
  - PURPOSE.md declares the appraisal philosophy and names swain's own value axes
  - Vision frontmatter supports appraisal-goals as structured axis weights
  - Initiative/Epic/Spec frontmatter supports serves-goals with per-axis impact estimates
  - serves-goals cascades down the parent chain (inherit when absent, override when present)
  - Artifacts with no serves-goals and no ancestor with serves-goals are flagged as unappraised
depends-on-artifacts: []
linked-artifacts:
  - SPIKE-059
  - ADR-010
addresses: []
---

# Appraisal Value Model

## Goal / Objective

Define how value is declared and measured across the artifact hierarchy. PURPOSE.md articulates the appraisal philosophy and swain's own value axes. Visions declare `appraisal-goals` with structured axis weights. Children declare `serves-goals` with per-axis impact estimates. Value cascades: set it high, inherit it low.

## Desired Outcomes

When an operator creates a Vision, the template prompts for appraisal-goals — "what axes does this bet serve, and how heavily?" When an agent creates a Spec, the template prompts for serves-goals — "which of the parent Vision's axes does this advance, and by how much?" The connection between PURPOSE-level goals and leaf-level work is explicit and auditable.

## Scope Boundaries

**In scope:** PURPOSE.md appraisal section, frontmatter schema for `appraisal-goals` and `serves-goals`, frontmatter contract updates, vision/initiative/epic/spec definition updates, template updates, "unappraised" flagging in specgraph.

**Out of scope:** Cost model (EPIC-065), scoring formula (EPIC-066), migration of existing artifacts (EPIC-067).

## Child Specs

To be decomposed after the Initiative is activated.

## Key Dependencies

None — this Epic can proceed independently of EPIC-065.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-06 | | Initial creation |
