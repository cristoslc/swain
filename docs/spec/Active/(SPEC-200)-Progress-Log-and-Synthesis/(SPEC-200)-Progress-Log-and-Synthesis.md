---
title: "Progress Log and Synthesis"
artifact: SPEC-200
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
  - SPEC-199
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Progress Log and Synthesis

## Problem Statement

EPICs and Initiatives have no record of how work has progressed. The artifact shows what's planned and (at completion) a retrospective, but nothing in between. The operator must piece together progress from git log and artifact states.

## Desired Outcomes

Each EPIC and Initiative accumulates a progress log from session digests. A living synthesis section in the artifact itself gives readers a current-state summary without reading the full log. The artifact becomes self-contained — reading it tells you not just what's planned but how it's going.

## External Behavior

### Progress log (progress.md)

Each EPIC and Initiative gets a `progress.md` file in its artifact directory. After a session digest is generated (SPEC-199), swain-retro reads `artifacts_touched` and appends a dated entry to each referenced artifact's progress log.

**Path:** `docs/epic/Active/(EPIC-049)-Context-Rich-Progress-Tracking/progress.md`

**Format:**
```markdown
# Progress Log

## 2026-03-31
Implemented readability enforcement (SPEC-194) end-to-end. All 17 tests pass. Released v0.23.0-alpha.

## 2026-03-30
Created SPEC and implementation plan. Decomposed into 7 tasks across two chunks.
```

Each entry is 2-3 sentences: what happened and what it means for the goal. Created on first session digest that touches the artifact.

### Progress synthesis (## Progress section)

Each EPIC and Initiative gets a `## Progress` section in the artifact itself. After appending to the progress log, swain-retro reads the full log and regenerates this section. It replaces itself each time — always current, never a growing list.

The synthesis answers: what's done, what's in flight, what's left.

### Template changes

EPIC and Initiative templates gain an empty `## Progress` section, placed after Desired Outcomes and before Scope Boundaries.

## Acceptance Criteria

1. **Given** a session digest that references an EPIC, **when** swain-retro processes it, **then** a dated entry is appended to that EPIC's `progress.md`.

2. **Given** an EPIC with a `progress.md` containing 3+ entries, **when** the synthesis runs, **then** the `## Progress` section in the artifact is replaced with a current-state summary.

3. **Given** an EPIC with no prior progress log, **when** the first session digest references it, **then** `progress.md` is created and the `## Progress` section is populated.

4. **Given** an Initiative with child EPICs that have progress logs, **when** a session digest references the Initiative, **then** the Initiative's progress synthesis reflects child EPIC progress.

5. **Given** the EPIC template, **when** a new EPIC is created, **then** it includes an empty `## Progress` section.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- In scope: progress.md creation/append, `## Progress` section generation, EPIC and Initiative template changes
- Out of scope: displaying progress in dashboards (that's SPEC-202), the context utility (that's SPEC-201)
- Depends on SPEC-199 for the session digest as input

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | _pending_ | Initial creation |
