---
title: "Specgraph Hierarchy Projection Output"
artifact: SPEC-233
track: implementable
status: Complete
author: cristos
created: 2026-04-02
last-updated: 2026-04-02
priority-weight: ""
type: enhancement
parent-epic: EPIC-056
parent-initiative: ""
linked-artifacts:
  - ADR-022
  - DESIGN-013
  - DESIGN-014
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Specgraph Hierarchy Projection Output

## Problem Statement

The planned materializer needs normalized hierarchy data. Today the graph tooling is aimed at human CLI use. Without a stable machine-readable output shape, downstream scripts will scrape human text or re-derive hierarchy.

## Desired Outcomes

`chart` exposes a stable projection output for downstream tools. The output includes lifecycle-scoped canonical paths, narrowest valid direct-parent placement, and explicit unparented state.

## External Behavior

- Add a `chart` subcommand or flag that emits normalized hierarchy projection data as JSON.
- Each record identifies the artifact, canonical lifecycle-scoped folder path, direct parent if any, and whether the artifact should materialize under `_unparented/`.
- Output is stable enough for filesystem reconciliation scripts.

## Acceptance Criteria

1. **Given** an artifact graph with valid hierarchy, **when** the projection output is requested, **then** each artifact record includes exactly one direct placement target or an explicit unparented state.
2. **Given** an artifact whose broader ancestors also contain narrower parents, **when** projection output is generated, **then** the artifact is assigned only to the narrowest valid direct parent.
3. **Given** an artifact with no valid direct parent, **when** projection output is generated, **then** the artifact is marked for `_unparented/` placement instead of omitted.
4. **Given** artifacts in different lifecycle folders, **when** projection output is generated, **then** each record points at the current lifecycle-scoped authoritative folder.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC1 | `test_projection_uses_narrowest_parent_and_folder_paths` in `skills/swain-design/scripts/tests/test_graph.py` | Pass |
| AC2 | `test_projection_uses_narrowest_parent_and_folder_paths` in `skills/swain-design/scripts/tests/test_graph.py` | Pass |
| AC3 | `test_projection_marks_unparented_when_no_direct_parent` in `skills/swain-design/scripts/tests/test_graph.py` | Pass |
| AC4 | `test_projection_uses_narrowest_parent_and_folder_paths` and `test_projection_converts_flat_artifact_file_to_folder_target` in `skills/swain-design/scripts/tests/test_graph.py` | Pass |

## Scope & Constraints

In scope: `chart` output shape, placement-state derivation, and tests for narrowest-parent logic.

Out of scope: filesystem mutation, symlink creation, and README generation.

## Implementation Approach

Add projection rendering inside the `chart` graph layer, then cover it with graph fixtures that exercise nested parents, direct-to-initiative specs, re-parented children, and unparented artifacts.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-02 | — | Initial creation |
| Complete | 2026-04-02 | — | `chart projection --json` implemented with graph and wrapper coverage |
