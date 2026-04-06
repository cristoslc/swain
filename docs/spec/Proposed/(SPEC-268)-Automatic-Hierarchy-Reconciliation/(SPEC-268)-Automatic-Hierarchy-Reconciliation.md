---
title: "Automatic Hierarchy Reconciliation"
artifact: SPEC-268
track: implementable
status: Proposed
author: cristos
created: 2026-04-02
last-updated: 2026-04-02
priority-weight: ""
type: enhancement
parent-epic: EPIC-055
parent-initiative: ""
linked-artifacts:
  - ADR-022
  - DESIGN-013
  - DESIGN-014
  - SPEC-266
  - SPEC-267
depends-on-artifacts:
  - SPEC-266
  - SPEC-267
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Automatic Hierarchy Reconciliation

## Problem Statement

The hierarchy view only helps if it stays current. A manual plan/apply flow adds operator work and breaks the purpose of projecting frontmatter-driven hierarchy into the filesystem.

## Desired Outcomes

Whenever hierarchical artifact state changes, Swain rebuilds the graph through `chart` and then reconciles the hierarchy view automatically. Drift is corrected without a separate approval workflow.

## External Behavior

- Hierarchy-relevant workflows invoke `chart build` and then the materializer automatically.
- Stale child symlinks and stale `_unparented/` entries are removed when no longer justified by current graph output.
- Real file or directory collisions cause a loud failure instead of destructive cleanup.

## Acceptance Criteria

1. **Given** a re-parented artifact, **when** hierarchy reconciliation runs, **then** the old direct-child slot is removed and the new direct-child slot appears automatically.
2. **Given** an artifact that moves from unparented to validly placed, **when** reconciliation runs, **then** it disappears from `_unparented/` and appears under its direct parent.
3. **Given** unchanged graph output, **when** reconciliation runs repeatedly, **then** the resulting symlink tree is unchanged.
4. **Given** a path collision where a symlink should be created, **when** reconciliation runs, **then** the command exits non-zero and reports the blocking path without deleting operator-managed content.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

In scope: automatic invocation hooks, idempotent drift cleanup, collision failure mode, and re-parent and lifecycle-move repair.

Out of scope: introducing operator approval steps, modifying body content in artifacts, and replacing other chart rebuild hooks.

## Implementation Approach

Attach materializer invocation to the same workflows that already rebuild graph state, then add fixture-backed tests for re-parent, lifecycle move, unparenting, and collision cases.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-02 | — | Initial creation |
