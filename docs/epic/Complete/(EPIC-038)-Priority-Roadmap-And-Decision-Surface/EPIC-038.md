---
title: "Priority Roadmap and Decision Surface"
artifact: EPIC-038
track: container
status: Complete
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
linked-artifacts:
  - SPEC-102
  - SPEC-103
  - SPEC-104
  - SPEC-105
  - SPEC-106
  - SPEC-107
  - SPEC-108
  - SPEC-109
  - SPEC-110
  - SPEC-111
  - SPEC-112---

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

## Child Specs

- SPEC-108 — Roadmap data model (foundation — single computed model for all renderers)
- SPEC-109 — Roadmap Jinja templates (presentation layer, depends on 108)
- SPEC-110 — Quadrant PNG pipeline (mmdc rendering, depends on 109)
- SPEC-111 — Status roadmap integration (swain-status reads from data model, depends on 108)
- SPEC-112 — Dependency graph initiative subgraphs (orientability, depends on 109)
- SPEC-107 — Sibling order ranking (scoring model tiebreaker, independent)

### Superseded specs (exploratory implementation)

- ~~SPEC-102~~ → SPEC-108
- ~~SPEC-103~~ → SPEC-111
- ~~SPEC-104~~ → SPEC-108
- ~~SPEC-105~~ → SPEC-108
- ~~SPEC-106~~ → SPEC-112

## Key Dependencies

```
SPEC-108 (data model)
├── SPEC-109 (templates)
│   ├── SPEC-110 (PNG pipeline)
│   └── SPEC-112 (dep graph subgraphs)
└── SPEC-111 (status integration)

SPEC-107 (sibling ranking) — independent, feeds into 108's scoring
```

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | | Created with initial implementation in progress |
| Progress | 2026-03-20 | dbd0e66 | SPEC-107 and SPEC-108 complete — 7/10 specs resolved |
| Complete | 2026-03-20 | e87c6b8 | All 10 child specs delivered: data model (108), sort-order (107), templates (109), PNG pipeline (110), status integration (111), dep graph subgraphs (112) |
