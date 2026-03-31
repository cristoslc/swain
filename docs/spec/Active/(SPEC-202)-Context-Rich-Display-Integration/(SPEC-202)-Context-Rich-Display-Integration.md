---
title: "Context-Rich Display Integration"
artifact: SPEC-202
track: implementable
status: Active
author: Cristos L-C
created: 2026-03-31
last-updated: 2026-03-31
priority-weight: ""
type: feature
parent-epic: EPIC-049
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts:
  - SPEC-201
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Context-Rich Display Integration

## Problem Statement

Even with the artifact-context utility available (SPEC-201), skills still print bare IDs in their operator-facing output. Each skill must be updated to call the utility instead. This is the integration work that makes context-rich display real across all surfaces.

## Desired Outcomes

Every operator-facing surface in swain shows context lines instead of bare artifact IDs. The operator never has to look up what an ID means.

## External Behavior

Update these skill surfaces to use the artifact-context utility:

| Surface | Skill | Current output | New output |
|---------|-------|---------------|------------|
| Status dashboard recommendations | swain-session | `Recommended: SPEC-203` | Context line with progress |
| "What's next?" list | swain-session | Ranked IDs with titles | Context lines ranked by readiness |
| Focus lane display | swain-session | `Focus: INITIATIVE-019` | Context line for the Initiative |
| Roadmap items | swain-roadmap | IDs in Gantt/quadrant | IDs + plain-language labels + progress |
| Retro artifact references | swain-retro | References by ID | Context lines for each artifact |
| Scope/ancestry checks | swain-design | `SPEC-203 → INITIATIVE-019` | Ancestry chain with plain-language names |

Each skill calls `artifact-context.sh <ID>` and uses the returned context line in its output formatting.

## Acceptance Criteria

1. **Given** the swain-session status dashboard, **when** it shows recommendations, **then** each recommendation is a context line with title, scope, and progress.

2. **Given** the swain-session focus lane display, **when** a focus is set, **then** it shows a context line for the focused artifact.

3. **Given** swain-roadmap output, **when** it lists items, **then** each item includes a plain-language title and progress clause alongside the ID.

4. **Given** swain-retro output referencing child artifacts, **when** it lists them, **then** each reference is a context line.

5. **Given** swain-design ancestry checks, **when** showing scope chains, **then** each node in the chain includes a plain-language name.

6. **Given** the artifact-context utility is unavailable, **when** a skill tries to call it, **then** it falls back to the current behavior (bare ID + title) without errors.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- In scope: skill file updates for swain-session, swain-roadmap, swain-retro, swain-design
- Out of scope: the utility script itself (that's SPEC-201), progress data generation (that's SPEC-199 and SPEC-200)
- Depends on SPEC-201 for the artifact-context utility
- Skill changes require worktree isolation per the skill change discipline governance rule

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | _pending_ | Initial creation |
