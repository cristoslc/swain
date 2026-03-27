---
title: "Quadrant PNG pipeline"
artifact: SPEC-110
track: implementable
status: Complete
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
type: feature
parent-epic: EPIC-038
parent-initiative: ""
linked-artifacts:
  - SPEC-105
  - SPEC-109
depends-on-artifacts:
  - SPEC-109
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# Quadrant PNG pipeline

## Problem Statement

Mermaid quadrantChart labels overlap when rendered inline. Pre-rendering to PNG with short ID labels + a side-by-side legend table in markdown solves this, but requires mmdc (mermaid-cli) as a dependency.

## External Behavior

`chart.sh roadmap` renders the quadrant chart to `assets/quadrant.png` using mmdc. ROADMAP.md embeds the PNG in a markdown table cell with the legend in an adjacent cell. When mmdc is not available, the pipeline falls back to an inline Mermaid block without the side-by-side layout. swain-doctor warns when mmdc is missing.

## Acceptance Criteria

- `chart.sh roadmap` renders quadrant chart to `assets/quadrant.png` via mmdc
- ROADMAP.md embeds PNG in a markdown table cell with legend in adjacent cell
- If mmdc is not on PATH, falls back to inline Mermaid block (no side-by-side but functional)
- swain-doctor checks for mmdc availability and warns if missing
- PNG is regenerated deterministically (same data = same image)

## Verification

<!-- Populated when entering Testing phase. Maps each acceptance criterion
     to its evidence: test name, manual check, or demo scenario.
     Leave empty until Testing. -->

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

Only the quadrant chart is converted to PNG in this spec. Gantt and dependency graph remain as inline Mermaid. The fallback must keep ROADMAP.md valid and renderable without mmdc.

## Implementation Approach

1. Add mmdc availability check to swain-doctor.
2. In chart.sh (or roadmap.py), detect mmdc on PATH.
3. When present: render `quadrant.mmd` to `assets/quadrant.png` via mmdc, then write side-by-side markdown table.
4. When absent: write inline Mermaid block as today.
5. Update the `roadmap.md.j2` template (SPEC-109) to support both branches.
6. Test determinism: run twice on the same data, assert PNG bytes are identical.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 |  | Initial creation |
| Complete | 2026-03-20 | c768cd2 | PNG pipeline verified — mmdc check added to swain-doctor |
