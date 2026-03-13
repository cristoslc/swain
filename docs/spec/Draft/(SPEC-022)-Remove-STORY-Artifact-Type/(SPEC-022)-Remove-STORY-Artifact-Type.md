---
title: "Remove STORY Artifact Type"
artifact: SPEC-022
status: Complete
type: enhancement
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
parent-epic: EPIC-008
implementation-commits:
  - 00f11b2
linked-artifacts:
  - ADR-003
  - SPEC-004
  - SPEC-006
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Remove STORY Artifact Type

## Problem Statement

ADR-003 drops the STORY artifact type — SPECs with `type: feature` absorb user-facing requirements. The STORY definition, template, list file, and all cross-references must be removed.

## External Behavior

### Files to remove

- `skills/swain-design/references/story-definition.md`
- `skills/swain-design/references/story-template.md.template`
- `docs/story/list-story.md` (if exists)
- `docs/story/` directory (if exists and empty after migration)

### Cross-reference cleanup

- Remove STORY from the artifact type table in `swain-design/SKILL.md`
- Remove STORY from `relationship-model.md` ER diagram
- Remove STORY from specgraph.sh type handling
- Remove STORY from specwatch.sh type handling
- Update AGENTS.md to remove STORY references
- Update any artifact frontmatter that references STORY types

### Existing STORY artifacts

If any STORY artifacts exist, they must be converted to SPECs with `type: feature` before removal. (Check `docs/story/` for existing artifacts.)

## Acceptance Criteria

- **Given** the removal is complete, **when** searching for "STORY" in definition/template files, **then** no results are found
- **Given** the removal is complete, **when** specgraph runs, **then** it does not reference STORY as a type
- **Given** the removal is complete, **when** creating artifacts via swain-design, **then** STORY is not an available type
- **Given** existing STORY artifacts exist, **when** removal runs, **then** they are converted to SPECs first

## Scope & Constraints

- BUG type is already handled by SPEC-004/SPEC-006 — no additional BUG removal needed here
- This spec can run in parallel with SPEC-018 since it's a deletion, not a rewrite

## Implementation Approach

1. Check for existing STORY artifacts in `docs/story/`
2. Convert any existing STORYs to SPECs if needed
3. Remove story-definition.md and story-template.md.template
4. Update SKILL.md, relationship-model.md, AGENTS.md
5. Update specgraph.sh and specwatch.sh
6. Run specwatch to verify clean state

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-13 | 232369c | Initial creation |
