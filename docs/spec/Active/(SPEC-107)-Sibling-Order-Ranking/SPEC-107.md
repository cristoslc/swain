---
title: "Sibling order ranking for epics and specs"
artifact: SPEC-107
track: implementable
status: Active
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
type: feature
parent-epic: ""
parent-initiative: INITIATIVE-005
linked-artifacts:
  - SPEC-102
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Sibling order ranking for epics and specs

## Problem Statement

The current priority scoring formula (score = unblock_count x vision_weight) produces many ties — most Epics score 0 because they don't block anything. Within the same weight tier, there's no way to differentiate between siblings (e.g., 5 medium-weight Epics under the same Initiative all score 0). This causes the quadrant chart to pile items at identical coordinates and the Gantt to show them as equally urgent when the operator may have clear preferences about relative ordering.

## External Behavior

**Inputs:** A new optional frontmatter field `sort-order` (integer, default 0) on Epics and Specs. Higher values sort earlier among siblings.

**How it works:**
- `sort-order` only affects ranking among siblings that share the same parent (Epics under the same Initiative, Specs under the same Epic)
- It does NOT change the Eisenhower quadrant classification or the vision weight cascade
- The roadmap scoring formula becomes: `score = (unblock_count x vision_weight) + sort_order_tiebreaker` where the tiebreaker is normalized to a 0-1 range among siblings
- Agents can suggest sort-order values based on dependency analysis; operators can override manually
- Items with `sort-order: 0` (default) sort alphabetically by ID as the final tiebreaker (current behavior)

## Acceptance Criteria

- **Given** two Epics under the same Initiative with the same weight and score, **When** one has `sort-order: 10` and the other has `sort-order: 5`, **Then** the first appears higher in recommendation order and earlier in the Gantt
- **Given** an Epic with no `sort-order` field, **When** scored, **Then** it defaults to 0 (backward compatible)
- **Given** the quadrant chart, **When** items have different sort-orders, **Then** their Y-axis positions within the same weight tier reflect the ordering (higher sort-order = higher position)
- The `sort-order` field is parsed by specgraph's graph builder and available in the node data

## Scope & Constraints

- Does NOT replace vision_weight or unblock_count — it's a local tiebreaker only
- Does NOT require a new artifact type or lifecycle phase
- Affects: `specgraph/graph.py` (parse field), `specgraph/priority.py` (incorporate in scoring), `specgraph/roadmap.py` (use in jitter/positioning)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | | Initial creation |
