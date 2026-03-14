---
title: "Gantt-Style Timeline Visualizations For Swain-Status"
artifact: EPIC-018
track: status
status: Proposed
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
parent-vision: VISION-001
success-criteria:
  - swain-status can render a timeline view showing epics and specs on a time axis
  - Timeline rendering works in at least one output mode (terminal, browser, or both)
  - Visualization approach is informed by SPIKE-021 findings (library selection, rendering target)
  - Timeline integrates with existing artifact frontmatter (created, last-updated, phase dates from lifecycle table)
  - No mandatory external installs for the default output mode
depends-on-artifacts:
  - SPIKE-021
addresses: []
evidence-pool: ""
---

# Gantt-Style Timeline Visualizations For Swain-Status

## Goal / Objective

Extend `swain-status` with a timeline view — a Gantt-style visualization that shows how epics, specs, and spikes relate in time. Today swain-status gives a dependency graph and progress ratios; it has no temporal axis. A timeline view surfaces scheduling, parallelism, and bottlenecks that are invisible in a flat list.

## Scope Boundaries

**In scope:**
- Timeline view as an additional output mode for `swain-status` (not replacing existing output)
- Read artifact dates from existing frontmatter fields (`created`, `last-updated`) and lifecycle tables (phase transition dates)
- At minimum, render active epics and their child specs with start/end anchors
- Output target TBD by SPIKE-021 (terminal rendering via Rich/Textual, browser-based chart, or static SVG)

**Out of scope:**
- Editing or scheduling artifacts through the timeline (read-only view)
- Predictive scheduling or effort estimation
- Integration with external calendar or project management tools

## Child Specs

Updated after SPIKE-021 resolves the rendering target and library selection.

## Key Dependencies

- **SPIKE-021** — must select the rendering approach and libraries before implementation specs are written
- **swain-status** (SPEC-036) — existing status dashboard; timeline view extends it

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Initial creation; gated on SPIKE-021 |
