---
title: "Work Scope Progress Visualizations For Swain-Status"
artifact: EPIC-018
track: status
status: Proposed
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
parent-vision: VISION-001
parent-initiative: INITIATIVE-005
success-criteria:
  - swain-status can render a scope progress view showing epics and specs as done/total counts
  - Progress visualization makes it immediately clear what fraction of work is complete (e.g., "10 of 15 specs done")
  - Visualization approach is informed by SPIKE-021 findings (rendering target and library selection)
  - View integrates with existing artifact frontmatter and specgraph output (phase, status, dependencies)
  - No mandatory external installs for the default output mode
depends-on-artifacts:
  - SPIKE-021
addresses: []
trove: ""
---

# Work Scope Progress Visualizations For Swain-Status

## Goal / Objective

Extend `swain-status` with a scope progress view — a visualization that shows how much work has been done vs. how much remains across epics and their child specs. Today swain-status reports progress ratios in text (e.g., "3/7 specs done"); this epic adds a richer visual representation of that scope. The focus is on **work completed**, not time elapsed or time estimated. Think "10 out of 15 specs done" rather than "5 hours remaining."

## Scope Boundaries

**In scope:**
- Scope progress view as an additional output mode for `swain-status` (not replacing existing output)
- Read artifact state from existing frontmatter fields (`status`, `phase`) and specgraph output
- Render active epics and their child specs with completion ratios — blocked, in-progress, done counts
- Visual breakdown by phase (Proposed → Active → Implemented → Done) if useful
- Output target TBD by SPIKE-021 (terminal rendering via Rich/Textual, browser-based chart, or static SVG)

**Out of scope:**
- Time-based Gantt charts, scheduling, or estimated hours remaining
- Editing or rescheduling artifacts through the view (read-only)
- Predictive completion dates or effort estimation
- Integration with external calendar or project management tools

## Child Specs

Updated after SPIKE-021 resolves the rendering target and library selection.

## Key Dependencies

- **SPIKE-021** — must select the rendering approach and libraries before implementation specs are written
- **swain-status** (SPEC-036) — existing status dashboard; scope view extends it

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Initial creation; pivoted from time-based Gantt to scope-based progress; gated on SPIKE-021 |
