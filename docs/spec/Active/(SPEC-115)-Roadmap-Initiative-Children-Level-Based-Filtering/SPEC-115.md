---
title: "Roadmap Initiative children use level-based filtering, not type-based"
artifact: SPEC-115
track: implementable
status: Active
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
type: bug
parent-epic: ""
parent-initiative: INITIATIVE-005
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Roadmap Initiative children use level-based filtering, not type-based

## Problem Statement

`collect_roadmap_items()` in `roadmap.py` filters Initiative children by type (`== "EPIC"`), which means SPECs attached directly to an Initiative (via `parent-initiative`) are invisible in ROADMAP.md. The work hierarchy explicitly allows SPECs to attach directly to Initiatives for small work — the roadmap should reflect this.

## External Behavior

**Before:** An Initiative's progress counter only counts SPECs nested under child Epics. Direct-child SPECs (those with `parent-initiative` set but no `parent-epic`) are excluded from the progress ratio and do not appear in ROADMAP.md at all.

**After:** An Initiative's progress counter includes all 1-deep children regardless of type. Any artifact that is a direct child of an Initiative (Epic, SPEC, Spike, etc.) contributes to that Initiative's progress and visibility in ROADMAP.md.

## Acceptance Criteria

- Given a SPEC with `parent-initiative: INITIATIVE-NNN` and no `parent-epic`, when `chart.sh roadmap` runs, then the SPEC is counted in that Initiative's progress ratio.
- Given an Initiative with 2 child Epics (each containing 1 SPEC) and 1 direct child SPEC, when the roadmap is generated, then the progress counter reflects 3 total items (not 2).
- Given a direct-child SPEC of an Initiative that is Complete, when the roadmap is generated, then the SPEC counts toward the Initiative's `children_complete`.

## Reproduction Steps

1. Create a SPEC with `parent-initiative: INITIATIVE-005` and `parent-epic: ""` (e.g., [SPEC-114](../../Complete/(SPEC-114)-Trunk-Release-Branch-Model/SPEC-114.md)).
2. Run `bash skills/swain-design/scripts/chart.sh roadmap`.
3. Observe that ROADMAP.md's progress ratio for INITIATIVE-005 does not include the direct-child SPEC.

## Severity

medium

## Expected vs. Actual Behavior

**Expected:** All 1-deep children of an Initiative (Epics AND direct SPECs) are included in the progress ratio and appear in ROADMAP.md.

**Actual:** Only children with `type == "EPIC"` are included. Direct-child SPECs are silently dropped.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- The fix is in `roadmap.py:collect_roadmap_items()`, lines 121-126.
- Change the type filter (`== "EPIC"`) to a level-based approach: iterate all 1-deep children of an Initiative and count progress accordingly.
- For non-Epic children (direct SPECs), count the child itself as 1 total / 1 complete (if resolved), rather than recursing into `_spec_progress()` which expects an Epic parent.
- Do not change `_CONTAINER_TYPES` or the top-level iteration filter — Initiatives and Epics are still the only roadmap *items*. The change is how an Initiative tallies its children's progress.

## Implementation Approach

1. In the `elif atype == "INITIATIVE"` block, remove the `if cnode.get("type", "").upper() == "EPIC"` guard.
2. For each child: if it's an Epic, call `_spec_progress()` as before. If it's any other type (SPEC, Spike, etc.), count 1 toward total and check `_node_is_resolved()` for complete.
3. Add/update tests to cover direct-child SPECs in Initiative progress.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | — | Initial creation |
