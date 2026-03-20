---
title: "Status roadmap integration"
artifact: SPEC-111
track: implementable
status: Complete
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
type: feature
parent-epic: EPIC-038
parent-initiative: ""
linked-artifacts:
  - SPEC-103
depends-on-artifacts:
  - SPEC-108
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Status roadmap integration

## Problem Statement

swain-status has no awareness of the Eisenhower-prioritized roadmap. Operators must separately run `chart.sh roadmap` and read ROADMAP.md to see priority decisions.

## External Behavior

swain-status conditionally refreshes ROADMAP.md when stale, then surfaces the top decision items from the Do First and Schedule quadrants inline in its output. A `--json` flag on `chart.sh roadmap` emits the SPEC-108 data model as JSON for consumption by swain-status and other tools. Focus lane filtering narrows output to a single Vision when set.

## Acceptance Criteria

- swain-status refreshes ROADMAP.md if stale (newer docs/*.md files exist)
- `chart.sh roadmap --json` outputs the data model as JSON (from SPEC-108)
- swain-status surfaces top 3–5 decision items from Do First and Schedule quadrants
- Focus lane filtering: when set, only items under that Vision appear
- Items with operator decisions (activate/drop, decompose, complete) are shown as actionable prompts
- Refresh is skipped if ROADMAP.md is newer than all `docs/**/*.md` files

## Verification

<!-- Populated when entering Testing phase. Maps each acceptance criterion
     to its evidence: test name, manual check, or demo scenario.
     Leave empty until Testing. -->

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

swain-status reads the roadmap data; it does not own the roadmap generation pipeline. Staleness check is based on file modification timestamps, not content hash. Focus lane is an existing concept; this spec adds roadmap awareness to it, not the concept itself.

## Implementation Approach

1. Implement `chart.sh roadmap --json` by serializing SPEC-108's `collect_roadmap_items()` output to JSON.
2. In swain-status, add a staleness check comparing ROADMAP.md mtime against `docs/**/*.md` mtimes.
3. Trigger `chart.sh roadmap` when stale.
4. Parse the JSON output, extract top 3–5 items from Do First and Schedule quadrants.
5. Apply focus lane filter if set.
6. Render actionable prompts for items carrying operator decisions.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 |  | Initial creation |
| Complete | 2026-03-20 | d99b8c4 | ROADMAP.md staleness check and Decisions Needed section added to swain-status |
