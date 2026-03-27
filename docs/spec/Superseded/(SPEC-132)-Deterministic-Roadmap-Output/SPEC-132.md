---
title: "specgraph: deterministic roadmap output based on priorities"
artifact: SPEC-132
track: implementable
status: Superseded
superseded-by: SPEC-108
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
type: feature
parent-epic: EPIC-038
parent-initiative: ""
linked-artifacts:
  - SPEC-103
  - SPEC-104
  - SPEC-105
  - SPEC-106
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: "gh#81"
swain-do: required
---

# specgraph: deterministic roadmap output based on priorities

## Problem Statement

Swain has a prioritization mechanism (priority-weight on Visions/Initiatives/Epics, cascading to children, scored by unblock count) but no way to render the resulting order as a visual roadmap. Operators need a deterministic, priority-sorted view grouped at the Initiative/Epic level — Vision grouping doesn't work because of multi-homing, and Spec-level is too granular.

## External Behavior

**Command:** `chart.sh roadmap [--format mermaid-gantt|mermaid-flowchart|both] [--focus VISION-ID] [--json]`

**Inputs:** Graph cache (nodes + edges), priority weights, dependency edges.

**Output:** A Mermaid Gantt chart, flowchart, or both (default: Gantt) showing:
- Non-terminal Initiatives and Epics, ordered by computed priority score (descending)
- Dependency arrows between items that have `depends-on` relationships
- Grouping by Initiative when one exists; standalone Epics as their own group
- Each item annotated with its priority weight and number of child specs (total / complete)

**Preconditions:** Graph cache exists or can be rebuilt.

**Constraints:**
- Output must be deterministic given the same graph state (sorted by score, then ID as tiebreaker)
- Must not render individual SPECs — Epics are the leaf level
- Visions appear only as section headers in Gantt, not as task bars
- Multi-homed artifacts (Epic under multiple Initiatives) appear once, under their primary parent

## Acceptance Criteria

- **Given** a graph with prioritized Initiatives and Epics, **When** `chart.sh roadmap` runs, **Then** output is valid Mermaid Gantt syntax with items sorted by priority score descending
- **Given** Epics with `depends-on` relationships, **When** `chart.sh roadmap --format mermaid-flowchart` runs, **Then** output is a Mermaid flowchart with dependency arrows and priority-sorted layout
- **Given** `--format both`, **When** the command runs, **Then** both Gantt and flowchart are output, separated by a blank line
- **Given** `--focus VISION-ID`, **When** the command runs, **Then** only Initiatives/Epics under that Vision are included
- **Given** the same graph state across two runs, **When** `chart.sh roadmap` runs both times, **Then** output is byte-identical
- **Given** `--json`, **When** the command runs, **Then** output is a JSON array of `{id, title, score, weight, children_total, children_complete, depends_on, group}` sorted by score
- **Given** an Epic with no parent Initiative, **When** `chart.sh roadmap` runs, **Then** it appears as its own section (not grouped under a missing Initiative)
- Progress ratio (complete/total child specs) appears in each Epic's label

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Does NOT add calendar dates — this is a logical ordering, not a timeline
- Does NOT render SPECs — Epic is the leaf node
- Does NOT introduce new frontmatter fields — uses existing `priority-weight` and `depends-on-artifacts`
- Gantt "durations" are uniform placeholders (e.g., `1d`) since we don't estimate effort

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | | Promoted from gh#81 |
| Superseded | 2026-03-20 | | Superseded by SPEC-108 — architectural decomposition |
