---
title: "Priority Roadmap and Decision Surface"
artifact: EPIC-038
track: container
status: Active
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
parent-vision: ""
parent-initiative: INITIATIVE-005
priority-weight: ""
success-criteria:
  - "`chart.sh roadmap` generates a ROADMAP.md with quadrant chart, staggered Gantt, Eisenhower tables with hyperlinked artifacts and decision callouts, and a blocking dependency graph"
  - "ROADMAP.md is deterministic (same graph state = byte-identical output)"
  - "swain-status refreshes ROADMAP.md before rendering and surfaces top decision items contextually"
  - "Diagrams are legible in both light and dark mode at typical terminal/editor widths"
depends-on-artifacts: []
addresses: []
evidence-pool: ""
linked-artifacts: []
---

# Priority Roadmap and Decision Surface

## Goal / Objective

Deliver a persistent, auto-refreshed ROADMAP.md at the project root that visualizes the project's Eisenhower-prioritized work as a quadrant chart, staggered Gantt, and dependency graph. Integrate this roadmap into swain-status so the operator sees contextual decision prompts (filtered by focus lane) alongside the existing status output. The roadmap is the visual decision surface; swain-status is the contextual decision advisor that reads from it.

## Design Principles

**The roadmap is descriptive, not prescriptive.** It projects what will be worked on given current priority weights — it is a computed output, not an editable plan. To change the order, the operator adjusts weights on Visions, Initiatives, or Epics (via `priority-weight` frontmatter), and the roadmap recomputes deterministically. The roadmap is never edited directly; it is always regenerated from the graph.

This principle enables a future interaction model where a visual surface (e.g., swain-stage drag-and-drop) lets the operator reorder roadmap items intuitively, with the surface translating positional changes back into weight adjustments on the source artifacts.

## Scope Boundaries

**In scope:**
- `chart.sh roadmap` command generating ROADMAP.md with quadrant chart, staggered Gantt, Eisenhower tables (hyperlinked artifacts, decision callouts), and blocking dependency graph
- Deterministic output guarantee (same graph state = byte-identical ROADMAP.md)
- swain-status integration: refresh ROADMAP.md before rendering, surface top decision items filtered by focus lane
- Diagram legibility fixes for both light and dark mode at typical terminal/editor widths

**Out of scope:**
- Calendar-based scheduling or effort estimation
- Real-time or streaming roadmap updates
- New frontmatter fields beyond what exists in SPEC-102

## Child Specs

- SPEC-102 — specgraph: deterministic roadmap output based on priorities
- SPEC-103 — swain-status roadmap integration
- SPEC-104 — Roadmap diagram legibility

## Key Dependencies

- SPEC-102 must be complete before SPEC-103 and SPEC-104 can be finalized, as both depend on the `chart.sh roadmap` command and ROADMAP.md format it produces.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | | Created with initial implementation in progress |
