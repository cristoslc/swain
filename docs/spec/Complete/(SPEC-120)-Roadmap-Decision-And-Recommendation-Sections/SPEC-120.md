---
title: "ROADMAP.md Decision and Recommendation Sections"
artifact: SPEC-120
track: implementable
status: Complete
author: cristos
created: 2026-03-20
last-updated: 2026-03-21
type: feature
parent-epic: EPIC-039
parent-initiative: INITIATIVE-019
linked-artifacts:
  - SPEC-118
  - SPEC-169
  - SPEC-123
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# ROADMAP.md Decision and Recommendation Sections

## Problem Statement

ROADMAP.md shows Eisenhower quadrants and Gantt timelines but doesn't synthesize "what needs an operator decision right now" or "what's the single highest-leverage next item."

## External Behavior

**Before:** ROADMAP.md contains Eisenhower quadrant tables, Gantt timelines, and dependency graphs. The operator must scan all sections to figure out what needs attention.

**After:** chart.sh roadmap adds two new sections at the top of ROADMAP.md:

- **Decisions** section: items requiring operator input (activate or drop, needs decomposition, ready to complete), bucketed into "Decisions Waiting on You" vs "Implementation Ready (agent can handle)". When empty, explicitly states "No decisions needed right now."
- **Recommended Next** callout: the single highest-leverage item by unblock score, with a one-line rationale.

These sections use existing specgraph data (recommend, decision-debt commands). No new data sources needed.

## Acceptance Criteria

### AC1: Decisions section above Eisenhower tables

**Given** chart.sh roadmap is run
**When** ROADMAP.md is generated
**Then** a Decisions section appears above the existing Eisenhower quadrant tables

### AC2: Decisions bucketed into operator vs agent

**Given** the Decisions section
**When** there are pending decisions
**Then** they are bucketed into "Decisions Waiting on You" and "Implementation Ready (agent can handle)"

### AC3: Empty state handled

**Given** the Decisions section
**When** no decisions are pending
**Then** the section reads "No decisions needed right now"

### AC4: Recommended Next shows top item

**Given** chart.sh roadmap is run
**When** ROADMAP.md is generated
**Then** a Recommended Next callout shows the single highest-leverage item with a one-line rationale

### AC5: Existing content unchanged

**Given** the existing ROADMAP.md sections (quadrant, Gantt, dependency graph)
**When** the new sections are added
**Then** existing content is unchanged in structure and data

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC1: Decisions above Eisenhower | ROADMAP.md line 13 ("Decisions Waiting on You") appears before Eisenhower tables; test_roadmap_markdown_decisions_before_eisenhower passes | PASS |
| AC2: Operator vs agent buckets | ROADMAP.md has "Decisions Waiting on You" (line 13) and "Implementation Ready (agent can handle)" (line 40); test_decisions_section_proposed_epic_in_operator_bucket and test_decisions_section_active_spec_in_implementation_bucket pass | PASS |
| AC3: Empty state | test_decisions_section_empty_state confirms "No decisions needed right now" output when no decisions exist | PASS |
| AC4: Recommended Next | ROADMAP.md line 9 shows "Recommended Next" with top item and rationale; test_recommendation_shows_top_item and test_recommendation_includes_rationale pass | PASS |
| AC5: Existing content unchanged | ROADMAP.md retains Timeline (line 165) and Blocking Dependencies (line 227); test_roadmap_markdown_preserves_existing_sections passes; 485/486 existing tests pass (1 pre-existing failure) | PASS |

## Scope & Constraints

**In scope:**
- New Decisions section in ROADMAP.md
- New Recommended Next callout in ROADMAP.md
- Integration with existing specgraph recommend and decision-debt commands

**Out of scope:**
- SESSION-ROADMAP.md (SPEC-118)
- Session lifecycle (SPEC-169)
- New data sources or specgraph commands

**Constraints:**
- Must use existing specgraph data only -- no new data sources
- Existing ROADMAP.md content must not change
- Sections must be placed at the top, before existing content

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | -- | Initial creation |
| Complete | 2026-03-21 | c933d46 | All ACs verified; 13 tests pass |
