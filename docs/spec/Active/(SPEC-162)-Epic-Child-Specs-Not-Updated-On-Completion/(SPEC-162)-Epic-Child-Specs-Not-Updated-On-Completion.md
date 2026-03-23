---
title: "EPIC Child Specs Section Not Updated on Completion"
artifact: SPEC-162
track: implementable
status: Active
author: cristos
created: 2026-03-23
last-updated: 2026-03-23
priority-weight: ""
type: bug
parent-epic: ""
parent-initiative: INITIATIVE-003
linked-artifacts:
  - EPIC-043
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# EPIC Child Specs Section Not Updated on Completion

## Problem Statement

When child SPECs are created under an EPIC, the EPIC's `## Child Specs` section should be updated with linked references to the actual specs. In practice, the section retains placeholder entries (e.g., `SPEC-TBD`) through EPIC completion because no step in the swain-design workflow enforces updating it.

Observed in EPIC-043: four child specs (SPEC-156..159) were created, implemented, and completed, but the EPIC's child specs section still read `SPEC-TBD` at completion time.

## Reproduction Steps

1. Create an EPIC with placeholder child spec entries (`SPEC-TBD`)
2. Decompose into child SPECs (agent creates SPEC-156..159)
3. Implement and complete all child SPECs
4. Transition EPIC to Complete
5. Read the EPIC's `## Child Specs` section — still says `SPEC-TBD`

## Severity

Medium — the EPIC is the coordination artifact; stale child specs make it unreliable as a reference. Readers must check specgraph instead.

## Expected vs. Actual Behavior

**Expected:** The EPIC's `## Child Specs` section lists linked references to all child SPECs with their current status, updated automatically when specs are created or transitioned.

**Actual:** The section retains whatever was written at creation time. No swain-design step updates it when child specs are created or completed.

## Desired Outcomes

- EPICs are reliable as standalone coordination documents — a reader can see what specs exist without running specgraph
- The child specs section stays current automatically, not dependent on the agent remembering to update it

## External Behavior

Two possible fixes (choose one or both):

**A — swain-design hook:** When a SPEC is created with `parent-epic: EPIC-NNN`, update the parent EPIC's `## Child Specs` section with a linked reference. When a SPEC transitions, update its status indicator in the parent.

**B — rebuild-index.sh extension:** Add an EPIC child-specs refresh pass to `rebuild-index.sh` (or a new script) that scans for all SPECs with `parent-epic: EPIC-NNN` and regenerates the child specs section from frontmatter.

## Acceptance Criteria

- **Given** a SPEC is created with `parent-epic: EPIC-043`, **when** the creation completes, **then** EPIC-043's `## Child Specs` section contains a linked reference to the new SPEC.
- **Given** all child SPECs of an EPIC are Complete, **when** the EPIC's child specs section is read, **then** each entry shows the SPEC's current phase/status.
- **Given** `rebuild-index.sh epic` is run (or equivalent), **when** an EPIC has stale child spec entries (TBD or missing specs), **then** they are replaced with accurate linked references.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Must not break existing EPIC creation or SPEC creation workflows
- Should handle EPICs that already have manually-written child spec sections (don't clobber operator-authored content beyond the spec list)
- The child specs section format should match what specgraph produces for consistency

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-23 | — | Bug found during EPIC-043 retro |
