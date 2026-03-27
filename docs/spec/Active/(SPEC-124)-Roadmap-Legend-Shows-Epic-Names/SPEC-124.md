---
title: "Roadmap legend should display epic names alongside initiative names"
artifact: SPEC-124
track: implementable
status: Active
author: operator
created: 2026-03-21
last-updated: 2026-03-21
type: bug
parent-epic: ""
parent-initiative: INITIATIVE-005
linked-artifacts: []
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# Roadmap legend should display epic names alongside initiative names

## Problem Statement

The `chart.sh roadmap` command generates a ROADMAP.md quadrant chart whose legend groups epics under their parent initiative. The legend currently shows only the initiative name with epic short IDs (e.g., `*Agent Runtime Efficiency* — [E31](...)`), which hides the epic name entirely. This makes it difficult for the operator to identify what each epic is about without clicking through to the epic file.

## External Behavior

**Input:** `chart.sh roadmap` reads epic and initiative artifacts to build the quadrant chart legend.

**Current output:** Legend lines read like:
```
*Agent Runtime Efficiency* — [E31](...)
```

**Expected output:** For single-epic initiatives, the legend should read:
```
*Agent Runtime Efficiency - Skill Audit Remediation* — [E31](...)
```

For multi-epic initiatives, epics can be listed as a group under the initiative heading (current behavior is acceptable for this case).

**Affected file:** `.claude/skills/swain-design/scripts/chart.sh` (the `roadmap` subcommand's legend-generation logic).

## Acceptance Criteria

- **Given** an initiative with exactly one epic, **when** `chart.sh roadmap` generates the legend, **then** the legend line shows `*INITIATIVE_NAME - EPIC_NAME*` format.
- **Given** an initiative with multiple epics, **when** `chart.sh roadmap` generates the legend, **then** the epics are listed under the initiative heading (existing grouping behavior preserved).
- **Given** an epic with no parent initiative, **when** `chart.sh roadmap` generates the legend, **then** the epic name is shown directly (no change to current unparented behavior).

## Reproduction Steps

1. Run `bash .claude/skills/swain-design/scripts/chart.sh roadmap`
2. Open the generated `ROADMAP.md`
3. Observe the legend section — epic names are absent; only initiative names and epic short IDs appear

## Severity

low

## Expected vs. Actual Behavior

**Expected:** Single-epic initiative legend entries show `*Initiative Name - Epic Name* — [E##](...)` so the operator can identify the epic at a glance.

**Actual:** Legend entries show `*Initiative Name* — [E##](...)` which hides the epic name, requiring the operator to follow the link to identify the epic.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Only the legend-generation logic in `chart.sh roadmap` needs to change.
- The quadrant chart itself (Mermaid syntax) is unaffected — this is purely a legend/key formatting change.
- Multi-epic initiative grouping behavior should remain unchanged.
- Non-goal: restructuring the entire roadmap output format.

## Implementation Approach

1. Locate the legend-generation block in `chart.sh` (the `roadmap` subcommand).
2. When building legend entries, count how many epics belong to each initiative.
3. For single-epic initiatives: concatenate `INITIATIVE_NAME - EPIC_NAME` as the label.
4. For multi-epic initiatives: keep the current grouping format.
5. Test with both single-epic and multi-epic initiatives to verify formatting.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-21 | — | Initial creation |
