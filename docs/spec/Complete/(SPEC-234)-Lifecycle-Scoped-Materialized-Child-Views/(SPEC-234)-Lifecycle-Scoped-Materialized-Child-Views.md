---
title: "Lifecycle-Scoped Materialized Child Views"
artifact: SPEC-234
track: implementable
status: Complete
author: cristos
created: 2026-04-02
last-updated: 2026-04-03
priority-weight: ""
type: enhancement
parent-epic: EPIC-056
parent-initiative: ""
linked-artifacts:
  - DESIGN-013
  - DESIGN-014
  - SPEC-239
depends-on-artifacts:
  - SPEC-239
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Lifecycle-Scoped Materialized Child Views

## Problem Statement

The graph can be correct and still be hard to browse. A parent folder should show its direct children. Each link should point to the real artifact folder in its current lifecycle folder.

## Desired Outcomes

A reader should open an artifact folder and see that artifact's files plus its direct children. When they open a child folder, they should see that child's own children with no extra render step.

## External Behavior

- Create one child-folder symlink for each direct child inside the parent folder.
- Point each symlink at the child's real lifecycle folder.
- Create `_unparented/README.md` and unparented entries for each type that needs them.
- Keep the real artifact files, such as the main markdown file and `roadmap.md`, unchanged.
- Treat the symlink tree as output only. `chart` must skip those paths when it scans docs.

## Acceptance Criteria

1. A parent with direct children gets one child-folder symlink for each direct child in its lifecycle folder.
2. Opening a child symlink shows that child's own nested view.
3. If a type has unparented artifacts, `docs/<type>/_unparented/README.md` exists and says this is a repair surface, not a lifecycle state.
4. If an artifact lives in a non-Active lifecycle folder, the symlink points to that lifecycle folder.
5. When `chart` scans docs, it skips materialized child symlink paths and reads only the canonical file.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC1 | `test_materialize_creates_direct_child_symlinks` in `skills/swain-design/scripts/tests/test_materialize_hierarchy.py` | Pass |
| AC2 | `test_materialize_creates_direct_child_symlinks` in `skills/swain-design/scripts/tests/test_materialize_hierarchy.py` | Pass |
| AC3 | `test_materialize_writes_unparented_surface_and_readme` in `skills/swain-design/scripts/tests/test_materialize_hierarchy.py` | Pass |
| AC4 | `test_materialize_creates_direct_child_symlinks` in `skills/swain-design/scripts/tests/test_materialize_hierarchy.py` | Pass |
| AC5 | `test_build_graph_ignores_materialized_symlink_paths` in `skills/swain-design/scripts/tests/test_graph.py` | Pass |

## Scope & Constraints

In scope: child symlink layout, lifecycle-aware placement, `_unparented/README.md`, and safe directory handling.

Out of scope: changing hierarchy rules, parsing frontmatter in this layer, and rendering dependency links.

## Implementation Approach

Build a materializer that reads the projection from SPEC-239, updates direct child symlinks, and writes standard `_unparented/README.md` files when needed.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-02 | — | Initial creation |
| Complete | 2026-04-02 | — | Direct-child symlinks and `_unparented` surfaces implemented |
