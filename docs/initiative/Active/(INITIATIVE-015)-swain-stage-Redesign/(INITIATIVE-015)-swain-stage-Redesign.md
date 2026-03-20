---
title: "swain-stage Redesign"
artifact: INITIATIVE-015
track: container
status: Active
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
parent-vision: VISION-001
priority-weight: high
success-criteria:
  - Browser-based project control surface replaces tmux-based swain-stage entirely
  - Docs viewer panel renders TRAINs as a navigable documentation site
  - Architecture supports future panels (status dashboard, artifact graph, branch diffing) without structural rewrites
  - Greyed-out navigation tabs communicate the product roadmap to operators
  - Placeholder pages for future features return meaningful content, not 404s
depends-on-artifacts:
  - SPEC-091
addresses: []
linked-artifacts:
  - SPEC-091
  - DESIGN-004
  - EPIC-034
  - SPEC-093
evidence-pool: ""
---

# swain-stage Redesign

## Strategic Focus

Replace the existing tmux-based swain-stage with a browser-based project control surface. The documentation viewer is the first active panel, but the architecture is designed from the start to host multiple panels: status dashboard, artifact graph visualization, and worktree-aware branch diffing.

The core bet: operators benefit more from a browsable, always-open documentation site than from tmux pane layouts. The tmux approach conflated "development environment layout" with "project information surface." Splitting them lets the information surface evolve independently of the terminal workflow.

## Scope Boundaries

**In scope:**
- Complete removal of existing tmux-based swain-stage code
- Browser-based documentation viewer as the first panel (Docsify with custom swain theme)
- Navigation architecture that supports a multi-panel future
- DESIGN artifact capturing the full interaction vision
- Staleness detection for documentation (via train-check.sh integration)

**Out of scope:**
- Status dashboard panel (future EPIC under this initiative)
- Artifact graph visualization panel (future EPIC under this initiative)
- Worktree-aware branch diffing panel (future EPIC under this initiative)
- Multi-branch or multi-worktree awareness (single branch, current working directory only)
- Changes to the TRAIN artifact type itself (that's SPEC-091, a standalone spec under VISION-001)

## Child Epics

- **EPIC-034** — User Documentation System (Active): groups the docs viewer spec and future documentation-related specs
- _(future)_ Status Dashboard Panel
- _(future)_ Artifact Graph Visualization
- _(future)_ Worktree-Aware Branch Diffing

## Small Work (Epic-less Specs)

_None yet._

## Design Artifacts

- **DESIGN-004** — swain-stage Interaction Design (Active): full UI vision including navigation, placeholder pages, and responsive layout

## Key Dependencies

- SPEC-091 (TRAIN Artifact Type) — the docs viewer renders TRAINs, so the artifact type must exist first
- TRAIN artifacts must be authored before the docs viewer has meaningful content to display

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-19 | — | Initial creation from approved design doc |
