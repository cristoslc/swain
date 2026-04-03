---
title: "Lifecycle-Scoped Materialized Child Views"
artifact: SPEC-234
track: implementable
status: Complete
author: cristos
created: 2026-04-02
last-updated: 2026-04-02
priority-weight: ""
type: enhancement
parent-epic: EPIC-055
parent-initiative: ""
linked-artifacts:
  - DESIGN-013
  - DESIGN-014
  - SPEC-233
depends-on-artifacts:
  - SPEC-233
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Lifecycle-Scoped Materialized Child Views

## Problem Statement

Even with normalized hierarchy output, the docs tree stays hard to browse unless Swain projects direct-child links into artifact folders. The projection must respect lifecycle-scoped canonical folders and whole-folder child traversal.

## Desired Outcomes

Entering an artifact folder shows its own files and direct child subfolders. Descending into a child continues the hierarchy because the child folder contains its own projected child view.

## External Behavior

- Create one direct-child symlink per placed child inside the parent's lifecycle-scoped authoritative folder.
- Point each symlink at the child's lifecycle-scoped authoritative folder.
- Create `_unparented/README.md` and per-type unparented entries for artifacts marked unparented by `chart`.
- Preserve existing canonical files like the primary artifact markdown file and `roadmap.md`.

## Acceptance Criteria

1. **Given** a parent artifact with direct children, **when** the materializer runs, **then** the parent's lifecycle-scoped folder contains one child-folder symlink per direct child.
2. **Given** a child with its own descendants, **when** a reader enters the child symlink, **then** the child's nested child view is visible without extra rendering in the ancestor.
3. **Given** a type with unparented artifacts, **when** the materializer runs, **then** `docs/<type>/_unparented/README.md` exists and explains that `_unparented/` is a repair surface rather than a lifecycle state.
4. **Given** an artifact in a non-Active lifecycle folder, **when** it is materialized, **then** the symlink target resolves to that lifecycle-scoped folder rather than a type root or lifecycle-agnostic path.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC1 | `test_materialize_creates_direct_child_symlinks` in `skills/swain-design/scripts/tests/test_materialize_hierarchy.py` | Pass |
| AC2 | `test_materialize_creates_direct_child_symlinks` in `skills/swain-design/scripts/tests/test_materialize_hierarchy.py` | Pass |
| AC3 | `test_materialize_writes_unparented_surface_and_readme` in `skills/swain-design/scripts/tests/test_materialize_hierarchy.py` | Pass |
| AC4 | `test_materialize_creates_direct_child_symlinks` in `skills/swain-design/scripts/tests/test_materialize_hierarchy.py` | Pass |

## Scope & Constraints

In scope: symlink layout, lifecycle-scoped placement, `_unparented/README.md`, and collision-safe directory creation.

Out of scope: deciding hierarchy semantics, parsing frontmatter directly, and dependency-edge rendering.

## Implementation Approach

Build a materializer that consumes the projection JSON from SPEC-233, reconciles per-parent child symlinks, and writes standardized `_unparented/README.md` files where needed.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-02 | — | Initial creation |
| Complete | 2026-04-02 | — | Direct-child symlinks and `_unparented` surfaces implemented |
