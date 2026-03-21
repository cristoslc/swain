---
title: "Roadmap data model"
artifact: SPEC-108
track: implementable
status: Complete
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
type: feature
parent-epic: EPIC-038
parent-initiative: ""
linked-artifacts:
  - SPEC-102
  - SPEC-104
  - SPEC-105
  - SPEC-109
  - SPEC-111
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Roadmap data model

## Problem Statement

The roadmap pipeline has no single data layer. Chart positioning, legend grouping, Eisenhower classification, and operator decisions are each computed independently by different renderers, causing ordering mismatches, item count discrepancies, and x-axis clustering.

## External Behavior

A single `collect_roadmap_items()` function is the authoritative source of roadmap data. All renderers (quadrant chart, legend, Eisenhower tables, Gantt, dependency graph) receive the same resolved item list and do not re-derive scores or positions. The function accepts the current graph state and returns a list of fully-resolved items.

## Acceptance Criteria

- `collect_roadmap_items()` returns fully-resolved items with: Eisenhower quadrant, x/y chart position (with deterministic jitter), display_score, initiative grouping, operator_decision, short_id
- All renderers (quadrant chart, legend, Eisenhower tables, Gantt, dependency graph) consume the same item list without re-deriving scores or positions
- x-axis jitter spreads items within each urgency tier so items with identical status/unblocks don't stack
- Given the same graph state, item positions are byte-identical across runs
- Legend item count equals quadrant chart point count (same data, different projections)

## Verification

<!-- Populated when entering Testing phase. Maps each acceptance criterion
     to its evidence: test name, manual check, or demo scenario.
     Leave empty until Testing. -->

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

Scope is limited to the data model layer only. Rendering changes are out of scope here and addressed by SPEC-109. The function must be deterministic: given identical graph state, output is identical.

## Implementation Approach

1. Identify all locations in roadmap.py where scores, positions, or Eisenhower classifications are computed.
2. Write tests asserting deterministic output for a fixed graph state.
3. Implement `collect_roadmap_items()` consolidating all derivations.
4. Refactor renderers to consume the returned list rather than re-deriving.
5. Verify legend count matches quadrant chart point count in tests.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 |  | Initial creation |
| Complete | 2026-03-20 | dbd0e66 | Unified data model with pre-computed derived fields — reimplemented after worktree merge loss |
