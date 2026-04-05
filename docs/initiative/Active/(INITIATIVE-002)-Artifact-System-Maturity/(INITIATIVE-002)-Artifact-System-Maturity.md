---
title: "Artifact System Maturity"
artifact: INITIATIVE-002
track: container
status: Active
author: cristos
created: 2026-03-15
last-updated: 2026-04-04
parent-vision: VISION-001
success-criteria:
  - Unified artifact type system with consistent lifecycle tracks
  - Specgraph tooling supports cross-reference validation and querying
  - Artifact authoring ceremony is proportional to artifact complexity
  - Evidence pools are collected, normalized, and cached for reuse
linked-artifacts:
  - EPIC-001
  - EPIC-002
  - EPIC-008
  - EPIC-013
  - EPIC-014
  - ADR-022
  - DESIGN-013
  - DESIGN-014
  - EPIC-055
  - SPEC-236
  - EPIC-059
  - DESIGN-018
---

# Artifact System Maturity

## Strategic Focus

Build the document model and tooling that encode decisions, research, and plans. This initiative keeps artifacts as the single source of truth. They should be consistent, easy to write, and easy to query.

## Scope Boundaries

**In scope:** Artifact type system, lifecycle normalization, graph tooling, evidence pools, and workflow efficiency.

**Out of scope:** Frontend rendering of artifacts, external integrations beyond GitHub Issues, and agent-specific artifact consumption patterns.

## Child Epics

- EPIC-001: Evidence Pool Collection and Normalization (Complete)
- EPIC-002: Artifact Type System & Issue Integration (Complete)
- EPIC-008: Normalize Artifact Lifecycle States (Complete)
- EPIC-013: Specgraph Python Rewrite (Complete)
- EPIC-014: Artifact Workflow Efficiency (Complete)
- EPIC-055: Materialized Artifact Parenting View (Proposed)

## Small Work (Epic-less Specs)

| Spec | Title | Status |
|------|-------|--------|
| SPEC-236 | next-artifact-id Misses Untracked Artifacts In Other Worktrees | Proposed |

## Key Dependencies

None — this was foundational work.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Complete | 2026-03-15 | — | Retroactive creation during initiative migration; all child epics already complete |
| Active | 2026-04-02 | — | Reactivated for hierarchy materialization, graph-interface clarification, and allocator bug repair |
