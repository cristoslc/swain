---
title: "Normalize Artifact Lifecycle States"
artifact: EPIC-008
status: Proposed
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
parent-vision: VISION-001
success-criteria:
  - All 9 artifact types use the normalized lifecycle phases
  - STORY type is removed; SPECs with type field absorb its use cases
  - BUG type is removed; SPECs with type:bug absorb its use cases
  - Phase subdirectories renamed across all existing artifacts
  - swain-design templates, definitions, and scripts updated
  - swain-status, swain-do, specgraph, specwatch updated for new phases
  - swain-doctor detects old phase directories and offers migration
  - Existing artifacts migrated to new phase names with git history preserved
depends-on: []
addresses: []
evidence-pool: ""
source-issue: "github:cristoslc/swain#25"
---

# Normalize Artifact Lifecycle States

## Goal / Objective

Collapse the current 11 artifact types with inconsistent lifecycle phases into 9 types with three clean lifecycle tracks. This makes the system easier to learn, reduces the classification surface in tooling (specgraph, swain-status), and eliminates dead-weight phases like "Validated" that don't fit solo-dev workflows.

### Decided model

**Drop STORY** — SPECs with `type: feature` absorb user-facing requirements. **Drop BUG as a type** — SPECs with `type: bug` already cover this.

**9 artifact types in three lifecycle tracks:**

#### Implementable (SPEC)

Proposed → Ready → In Progress → Needs Manual Test → Complete

#### Containers (EPIC, SPIKE)

Proposed → Active → Complete

#### Standing (VISION, JOURNEY, PERSONA, ADR, RUNBOOK, DESIGN)

Proposed → Active → (Retired | Superseded)

**Universal terminal states** (available from any phase):
- **Abandoned** — intentionally not pursued
- **Retired** — served its purpose, wound down
- **Superseded** — replaced by a named successor

### Phase mapping from old to new

| Old phase | New phase | Notes |
|-----------|-----------|-------|
| Draft | Proposed | Universal rename |
| Planned | Proposed | SPIKE only |
| Review | (dropped) | Collapsed into Proposed |
| Approved | Ready | SPEC only |
| Active | Active | No change for containers/standing |
| Active | In Progress | SPEC only — "Active" on a SPEC becomes "In Progress" |
| Testing | Needs Manual Test | SPEC only |
| Implemented | Complete | SPEC only |
| Validated | (dropped) | JOURNEY/PERSONA — never fit solo-dev |
| Adopted | Active | ADR only |
| Complete | Complete | No change |
| Deprecated | Retired | Merged |
| Archived | Retired | Merged |
| Sunset | Retired | Merged |

## Scope Boundaries

**In scope:**
- Update all 10 artifact definition files and templates in swain-design/references/
- Update specgraph.sh, specwatch.sh, swain-status.sh for new phase names
- Update swain-do skill for SPEC lifecycle references
- Migrate all existing artifacts (git mv to new phase subdirectories, update frontmatter)
- Add swain-doctor detection for old phase directories with migration guidance
- Remove STORY type definition, template, and list file
- Update AGENTS.md artifact relationship model

**Out of scope:**
- Changing artifact numbering schemes
- Changing frontmatter field names (that's SPEC-009)
- Changing the specgraph dependency resolution logic (beyond phase name updates)

## Child Specs

To be decomposed. Expected children:

1. **SPEC: Update artifact definitions and templates** — rewrite the 9 definition files and templates with new lifecycle phases
2. **SPEC: Update tooling scripts** — specgraph, specwatch, swain-status, spec-verify for new phase names
3. **SPEC: Migrate existing artifacts** — git mv all artifacts to new phase subdirectories, update frontmatter
4. **SPEC: swain-doctor migration detection** — detect old phase dirs, offer automated migration
5. **SPEC: Remove STORY type** — delete definition, template, list file, update cross-references

## Key Dependencies

None — this is a foundational change that other work should wait on or coordinate with.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-13 | — | Initial creation from GitHub #25 decision |
