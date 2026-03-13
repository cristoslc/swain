---
title: "Update Artifact Definitions and Templates"
artifact: SPEC-018
status: Complete
type: enhancement
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
parent-epic: EPIC-008
linked-artifacts:
  - ADR-003
depends-on-artifacts: []
implementation-commits:
  - 50b7e38
  - 00f11b2
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Update Artifact Definitions and Templates

## Problem Statement

ADR-003 normalizes 11 artifact types into 9 types across three lifecycle tracks. The definition files and templates in `skills/swain-design/references/` still reflect the old per-type lifecycle phases. They must be rewritten to match the decided model before tooling or existing artifacts can be migrated.

## External Behavior

### Definition file changes

Rewrite lifecycle phases in each definition file:

**Implementable track (SPEC):**
- `spec-definition.md`: Proposed -> Ready -> In Progress -> Needs Manual Test -> Complete
- Phase subdirectories: `Proposed/`, `Ready/`, `InProgress/`, `NeedsManualTest/`, `Complete/`
- Remove: Draft, Review, Approved, Testing, Implemented, Deprecated

**Container track (EPIC, SPIKE):**
- `epic-definition.md`: Proposed -> Active -> Complete
- `spike-definition.md`: Proposed -> Active -> Complete
- Phase subdirectories: `Proposed/`, `Active/`, `Complete/`
- Remove: Planned (SPIKE), Draft (if used)

**Standing track (VISION, JOURNEY, PERSONA, ADR, RUNBOOK, DESIGN):**
- Each definition: Proposed -> Active -> (Retired | Superseded)
- Phase subdirectories: `Proposed/`, `Active/`, `Retired/`, `Superseded/`
- Remove: Draft, Validated (JOURNEY/PERSONA), Adopted (ADR), Deprecated, Archived, Sunset

**All types:** Add universal terminal states: Abandoned, Retired, Superseded (available from any phase).

### Template changes

Update the `status` default in each template:
- All templates: `status: Proposed` (replaces Draft/Planned)
- SPEC template: keep `type` field, update phase list in lifecycle table
- Remove STORY template (handled by SPEC-022)

### SKILL.md update

Update the artifact type table in `swain-design/SKILL.md` to reflect 9 types and three tracks. Update phase transition docs and completion rules.

### Relationship model update

Update `references/relationship-model.md` ER diagram to remove STORY, BUG. Update lifecycle track descriptions.

## Acceptance Criteria

- **Given** a new SPEC is created, **when** using the template, **then** its initial status is "Proposed" and the lifecycle table shows "Proposed" as the first phase
- **Given** a new EPIC is created, **when** using the template, **then** its lifecycle is Proposed -> Active -> Complete
- **Given** a new SPIKE is created, **when** using the template, **then** its lifecycle is Proposed -> Active -> Complete (not Planned)
- **Given** a new ADR is created, **when** using the template, **then** its lifecycle is Proposed -> Active -> (Retired | Superseded) — not Draft -> Adopted
- **Given** any definition file, **when** read, **then** it describes exactly the phases from ADR-003's three-track model
- **Given** the SKILL.md file, **when** read, **then** it lists 9 artifact types (no STORY, no standalone BUG) and references three lifecycle tracks

## Scope & Constraints

- Changes only definition files, templates, SKILL.md references, and relationship-model.md
- Does NOT migrate existing artifacts (that's SPEC-020)
- Does NOT update scripts (that's SPEC-019)
- Does NOT remove STORY type files (that's SPEC-022)

## Implementation Approach

1. Rewrite each definition file's lifecycle section and phase subdirectory list
2. Update each template's default status to "Proposed"
3. Update SKILL.md artifact type table and phase transition documentation
4. Update relationship-model.md
5. Run specwatch to verify no new stale references

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-13 | 232369c | Initial creation |
