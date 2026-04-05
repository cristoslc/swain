---
title: "Materialized Artifact Parenting View"
artifact: EPIC-061
track: container
status: Proposed
author: cristos
created: 2026-04-02
last-updated: 2026-04-02
parent-vision: VISION-001
parent-initiative: INITIATIVE-002
priority-weight: high
success-criteria:
  - Parent-child hierarchy can be browsed directly inside lifecycle-scoped artifact folders without changing frontmatter authority
  - `chart` is the only hierarchy interface the materializer consumes
  - Each artifact materializes exactly once as a direct child under its narrowest valid parent
  - Unparented artifacts appear in per-type `_unparented/` repair surfaces with explanatory README files
  - Reconciliation removes stale symlinks and repairs drift automatically after hierarchy changes
depends-on-artifacts:
  - ADR-022
addresses: []
evidence-pool: ""
---

# Materialized Artifact Parenting View

## Goal / Objective

Project Swain's artifact hierarchy into the docs tree as a parent-first view. A reader enters one artifact folder, sees its own files and child folders, and keeps walking down the tree.

## Desired Outcomes

Operators and agents can inspect one parent in one place. The view stays trustworthy because `chart` rebuilds it.

## Progress

<!-- Auto-populated from session digests. See progress.md for full log. -->

## Scope Boundaries

**In scope:**
- machine-readable hierarchy output from `chart`
- lifecycle-scoped child-folder symlink projection
- narrowest-parent placement and duplicate suppression
- `_unparented/` repair surfaces and README generation
- automatic drift cleanup after hierarchy changes

**Out of scope:**
- rendering linked-artifacts or dependency edges in the child tree
- replacing existing canonical artifact files or folder conventions
- operator approval workflows before reconciliation

## Child Specs

- SPEC-266: Specgraph Hierarchy Projection Output
- SPEC-267: Lifecycle-Scoped Materialized Child Views
- SPEC-268: Automatic Hierarchy Reconciliation

## Key Dependencies

- ADR-022 establishes `chart` as the canonical hierarchy interface
- DESIGN-013 defines the materialization contract
- DESIGN-014 defines placement and `_unparented/` rules

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-02 | — | Initial creation |
