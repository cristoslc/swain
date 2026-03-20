---
title: "Blocking flowchart initiative subgraphs"
artifact: SPEC-106
track: implementable
status: Superseded
superseded-by: SPEC-112
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
type: enhancement
parent-epic: EPIC-038
parent-initiative: ""
linked-artifacts:
  - SPEC-105
depends-on-artifacts:
  - SPEC-102
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Blocking flowchart initiative subgraphs

## Problem Statement

The blocking dependencies flowchart in ROADMAP.md shows connected Epics as flat nodes with color-coded quadrant membership, but provides no visual grouping by Initiative. When multiple Epics from the same Initiative participate in dependency chains, the operator can't see at a glance which strategic direction the blocking relationship affects. Initiative subgraphs would provide orientability — the viewer immediately sees "this Security & Trust epic blocks that other Security & Trust epic" vs "this cross-initiative dependency is the real constraint."

## External Behavior

**Inputs:** `chart.sh roadmap` with Epics that have dependency edges
**Expected output:** A Mermaid flowchart where connected Epics are grouped into Initiative subgraphs. Standalone Epics (no Initiative parent) appear outside any subgraph.

## Acceptance Criteria

- **Given** two Epics from the same Initiative that have a dependency edge, **When** the flowchart renders, **Then** both appear inside a subgraph labeled with their Initiative name
- **Given** a dependency edge crossing two different Initiative subgraphs, **When** rendered, **Then** the edge visually crosses the subgraph boundary (Mermaid handles this natively)
- **Given** an Epic with no parent Initiative, **When** it participates in a dependency, **Then** it appears as a standalone node outside any subgraph
- Subgraph colors should use the same quadrant color scheme as node fills (if feasible in Mermaid)

## Scope & Constraints

- Only affects `render_dependency_graph()` in `roadmap.py`
- Only nodes that participate in dependencies are rendered (existing behavior preserved)
- If adding subgraphs makes the diagram less readable (e.g., single-node subgraphs everywhere), fall back to current flat layout

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | | Initial creation |
| Superseded | 2026-03-20 | | Superseded by SPEC-112 — architectural decomposition |
