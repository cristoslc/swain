---
title: "Unified SPEC Type System"
artifact: SPEC-004
status: Testing
author: cristos
created: 2026-03-12
last-updated: 2026-03-12
parent-epic: EPIC-002
linked-research:
  - SPIKE-003
linked-adrs: []
depends-on: []
addresses:
  - JOURNEY-001.PP-01
evidence-pool:
swain-do: required
---

# Unified SPEC Type System

## Problem Statement

SPECs currently require `parent-epic`, forcing organizational overhead for standalone work (enhancements, small features, bugs). The separate BUG artifact type duplicates SPEC's lifecycle with minor template differences. SPIKE-003 found that agents fill out full SPEC ceremony regardless of scope — the friction is the mandatory epic, not the format.

## External Behavior

**Inputs:**
- `type` frontmatter field: `feature` (default) | `enhancement` | `bug`
- `parent-epic` frontmatter field: now optional (empty string or omitted = standalone)

**Outputs:**
- SPECs with `type: bug` include conditional sections: Reproduction Steps, Severity, Expected/Actual Behavior
- SPECs without `parent-epic` appear in specgraph as standalone nodes under an "(Unparented)" group
- specwatch no longer flags missing `parent-epic` as an error

**Postconditions:**
- BUG artifact type is fully removed: definition file, template, folder structure, references in SKILL.md, AGENTS.md, and all tooling
- All documentation references to "11 artifact types" updated to "10 artifact types"
- Artifact relationship model in SKILL.md updated (BUG entity removed, SPEC gains bug-specific edges)

## Acceptance Criteria

1. **Given** a SPEC with `parent-epic: ""`, **when** specwatch runs, **then** no error is reported for missing parent
2. **Given** a SPEC with `type: bug`, **when** the SPEC is created via swain-design, **then** the template includes Reproduction Steps, Severity, and Expected/Actual Behavior sections
3. **Given** a SPEC with `type: feature` (or type omitted), **when** created, **then** no bug-specific sections appear
4. **Given** specgraph runs with standalone SPECs in the repo, **when** `overview` is called, **then** standalone SPECs appear under an "(Unparented)" group
5. **Given** the BUG definition and template files, **when** this spec is implemented, **then** they are deleted and all references removed
6. **Given** swain-design SKILL.md, **when** reviewed after implementation, **then** BUG is absent from the artifact table, relationship model, and tracking tiers
7. **Given** AGENTS.md, **when** reviewed after implementation, **then** no references to BUG as a standalone artifact type

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| Empty parent-epic tolerated by specwatch | specwatch scan returns clean with SPEC-005/006 having no parent-epic issues | Pass |
| type:bug template includes bug sections | spec-template.md.template contains conditional Reproduction Steps, Severity, Expected/Actual sections | Pass |
| type:feature omits bug sections | Jinja2 conditional only renders bug sections when type=="bug" | Pass |
| Standalone SPECs in specgraph overview | specgraph overview shows "(Unparented)" group with EPIC-002, EPIC-004 | Pass |
| BUG definition and template deleted | Files no longer exist in skills/swain-design/references/ | Pass |
| BUG absent from SKILL.md | No BUG in artifact table, relationship model, or tracking tiers | Pass |
| BUG absent from AGENTS.md | No BUG references in artifact listings | Pass |

## Scope & Constraints

- Only the SPEC artifact type changes — no other artifact types are modified
- Existing SPECs with `parent-epic` set continue to work unchanged
- The `type` field is informational metadata, not a lifecycle gate — it doesn't change phase transitions
- BUG removal is part of this spec (not deferred) per SPIKE-003 decision

## Implementation Approach

1. **TDD cycle 1 — optional parent-epic:** Modify specwatch to tolerate missing parent-epic. Test: create a SPEC without parent-epic, run specwatch, assert clean.
2. **TDD cycle 2 — type field:** Add `type` to SPEC template with conditional bug sections. Test: create type:bug and type:feature SPECs, verify correct sections.
3. **TDD cycle 3 — specgraph standalone grouping:** Update specgraph to group unparented SPECs. Test: run overview with mix of parented/unparented SPECs.
4. **Cleanup pass:** Delete BUG definition, template, folder. Remove BUG references from SKILL.md, AGENTS.md, relationship model, tracking tiers. Update artifact count.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-12 | — | Initial creation |
| Approved | 2026-03-12 | b566127 | Design validated during EPIC-002 + SPIKE-003 |
| Testing | 2026-03-12 | — | All tasks complete, verification populated |
