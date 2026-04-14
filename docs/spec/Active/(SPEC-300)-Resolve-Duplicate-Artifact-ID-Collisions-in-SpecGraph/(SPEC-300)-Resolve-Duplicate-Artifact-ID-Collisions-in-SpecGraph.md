---
title: "Resolve Duplicate Artifact ID Collisions in SpecGraph"
artifact: SPEC-300
track: implementable
status: Active
author: opencode
created: 2026-04-08
last-updated: 2026-04-08
priority-weight: high
type: bug
parent-initiative: VISION-006
linked-artifacts:
  - SPEC-297
  - SPEC-298
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Resolve Duplicate Artifact ID Collisions in SpecGraph

## Problem Statement

The `chart.sh` (and underlying `specgraph` Python logic) fails with a `ValueError: Duplicate artifact IDs detected` when multiple files share the same artifact ID in their frontmatter. This prevents all tree views, roadmap generation, and alignment checks from functioning.

## Desired Outcomes

The project status dashboard and `chart.sh` should be operational again. All artifacts must have unique IDs, and the tool should ideally report these collisions as warnings or errors that can be easily remediated without crashing the entire graph build.

## External Behavior

Running `bash .agents/bin/chart.sh scope <ID>` or `bash .agents/bin/swain-status.sh` should succeed and return the expected visualization/report.

## Acceptance Criteria

- [ ] Running `chart.sh` no longer throws `ValueError` due to duplicate IDs.
- [ ] All reported duplicate IDs in the current codebase are resolved (renamed or removed).
- [ ] The graph cache is successfully rebuilt.

## Reproduction Steps

Run `bash .agents/bin/chart.sh scope VISION-006`.

## Severity

critical

## Expected vs. Actual Behavior

**Expected:** The tool identifies the scope and renders a hierarchy tree.
**Actual:** The tool crashes with a `ValueError` listing multiple colliding IDs (e.g., EPIC-077, SPEC-308, SPEC-309, SPEC-310, SPIKE-052, SPIKE-058, SPIKE-059, SPIKE-060, SPIKE-061, SPIKE-062).

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| No crash on chart.sh | bash .agents/bin/chart.sh scope VISION-006 | Pending |

## Scope & Constraints

Focus is strictly on resolving the ID collisions and ensuring the graph builder can handle or report these issues gracefully.

## Implementation Approach

1. Identify all colliding files listed in the error message.
2. Audit the colliding files to determine which one is the "correct" version.
3. Rename the artifact IDs in the redundant/incorrect files (or move them to a different ID using `next-artifact-id.sh`).
4. Run `bash .agents/bin/chart.sh build` to verify the fix.
