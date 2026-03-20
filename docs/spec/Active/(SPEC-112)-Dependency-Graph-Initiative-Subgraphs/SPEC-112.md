---
title: "Dependency graph initiative subgraphs"
artifact: SPEC-112
track: implementable
status: Active
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
type: enhancement
parent-epic: EPIC-038
parent-initiative: ""
linked-artifacts:
  - SPEC-106
depends-on-artifacts:
  - SPEC-109
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Dependency graph initiative subgraphs

## Problem Statement

The blocking dependencies flowchart shows connected Epics as flat nodes with no visual grouping by Initiative. Cross-initiative dependencies are not visually distinguishable from within-initiative ones.

## External Behavior

The dependency graph (rendered via `deps.mmd.j2`) groups connected Epics into Mermaid subgraphs by Initiative. Dependency edges cross subgraph boundaries where cross-initiative dependencies exist. Epics with no Initiative parent appear outside any subgraph. When all subgraphs would contain only a single node, the renderer falls back to the flat layout.

## Acceptance Criteria

- Connected Epics grouped into Mermaid subgraphs by Initiative
- Cross-initiative dependency edges visually cross subgraph boundaries
- Standalone Epics (no Initiative parent) appear outside any subgraph
- Subgraph styling uses quadrant color scheme where feasible
- Falls back to flat layout if subgraphs make the diagram less readable (e.g., all single-node subgraphs)

## Verification

<!-- Populated when entering Testing phase. Maps each acceptance criterion
     to its evidence: test name, manual check, or demo scenario.
     Leave empty until Testing. -->

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

Only the dependency graph (deps.mmd.j2) is changed. Quadrant chart, legend, Gantt, and roadmap.md templates are out of scope. The fallback heuristic (all single-node subgraphs) must be deterministic and documented in the template as a comment.

## Implementation Approach

1. Update the data model (SPEC-108) or a view derived from it to group Epics by Initiative.
2. Update `deps.mmd.j2` to emit `subgraph <initiative_id>` blocks around each group.
3. Implement the single-node fallback: if every subgraph has exactly one Epic, render flat.
4. Apply quadrant color scheme to subgraph background or node styling.
5. Write snapshot tests for: grouped output, standalone Epics, and the flat fallback.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 |  | Initial creation |
