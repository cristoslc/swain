---
title: "User Documentation System"
artifact: EPIC-034
track: container
status: Active
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
parent-vision: VISION-001
parent-initiative: INITIATIVE-015
priority-weight: high
success-criteria:
  - Operators can browse TRAIN documentation through a Docsify-based viewer
  - TRAINs are organized by Vision hierarchy and train-type in the navigation
  - Stale TRAINs display inline warnings with drift details
  - Existing tmux-based swain-stage is fully removed
  - The /swain-stage skill invocation launches the docs viewer
depends-on-artifacts:
  - SPEC-091
addresses: []
linked-artifacts:
  - INITIATIVE-015
  - DESIGN-004
  - SPEC-091
  - SPEC-093
trove: ""
---

# User Documentation System

## Goal / Objective

Deliver the first panel of the swain-stage redesign: a browsable documentation viewer that renders TRAIN artifacts as a structured documentation site. This epic groups the documentation viewer spec and any future documentation-related specs (e.g., search, versioned docs, export to static HTML).

The viewer replaces the tmux-based swain-stage entirely. The existing tmux code is deleted — this is a rip-and-replace, not an incremental enhancement.

## Scope Boundaries

**In scope:**
- Docsify-based documentation viewer with custom swain theme
- Vision-first navigation hierarchy with train-type grouping
- Inline staleness warnings via train-check.sh integration
- Complete removal of existing tmux-based swain-stage
- Rewriting the `/swain-stage` skill to launch the docs viewer
- Greyed-out tabs for future panels (per DESIGN-004)
- Placeholder pages for Status, Graph, and Diff panels

**Out of scope:**
- The TRAIN artifact type itself (SPEC-091, standalone under VISION-001)
- Full-text search within documentation (future spec)
- Static HTML export (future spec)
- Status dashboard, artifact graph, or branch diff panels (future epics under INITIATIVE-015)
- Worktree awareness or multi-branch content (single branch, current working directory only)

## Child Specs

| Spec | Title | Type | Priority |
|------|-------|------|----------|
| SPEC-093 | Documentation Viewer | feature | high |

## Key Dependencies

- **SPEC-091** (TRAIN Artifact Type) — the viewer renders TRAINs, so the artifact type definition, template, and tooling must exist. SPEC-093 depends on SPEC-091.
- **DESIGN-004** (swain-stage Interaction Design) — defines the navigation architecture, placeholder pages, and responsive layout that SPEC-093 implements.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-19 | — | Initial creation from approved design doc |
