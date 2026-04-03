---
title: "Artifact Model Audit + Extraction + Naming Rules"
artifact: SPIKE-056
track: implementable
status: Proposed
author: cristos
created: 2026-04-04
priority-weight: critical
parent-epic: EPIC-056
type: research
swain-do: required
---

# SPIKE-056: Artifact Model Audit + Extraction + Naming Rules

## Goal

1. Audit actual artifact types in swain (correct ADR-003 misclassifications)
2. Design artifact ID extraction from purpose text
3. Define naming rules per track (container vs implementable vs standing)

## Context

ADR-003 has incorrect artifact model:
- Lists SPIKE as Container (should be Implementable)
- Missing INITIATIVE (should be Container)
- Missing TRAIN (should be Standing)

Worktree naming depends on correct track classification:
- **Implementable/Standing:** Use artifact title (hard collision)
- **Container:** Ask for purpose slug (soft collision)

## Research Questions

1. **Artifact type audit:**
   - What types actually exist in docs/?
   - What are their correct tracks?
   - Confirm with operator (user interview for ADR-025)

2. **Artifact ID extraction:**
   - Regex for SPEC-NNN, EPIC-NNN, etc.
   - Handle multiple IDs in purpose text (pick first? container?)
   - Case insensitive? (spec-054 vs SPEC-054)

3. **Title extraction:**
   - Parse frontmatter `title:` field
   - Slugify for worktree name
   - Handle special characters

4. **Naming rules:**
   - Implementable: `${ID}-${title-slug}`
   - Container: `${ID}-${purpose-slug}-${timestamp}`
   - Standing: `${ID}-${title-slug}`

5. **Collision detection:**
   - Hard: block if exists
   - Soft: warn + offer resume/new

## Acceptance Criteria

- [ ] **SPIKE-056-AC1: Artifact type audit complete**
  - List all types in docs/
  - Correct track assignment
  - Operator confirmation

- [ ] **SPIKE-056-AC2: Extraction regex tested**
  - Handles SPEC-NNN, EPIC-NNN, VISION-NNN, etc.
  - Edge cases: multiple IDs, no ID, typo (spec054)

- [ ] **SPIKE-056-AC3: Title extraction working**
  - Parse frontmatter
  - Slugify correctly

- [ ] **SPIKE-056-AC4: Naming rules documented**
  - Per-track naming logic
  - Collision detection rules

- [ ] **SPIKE-056-AC5: ADR-025 user interview completed**
  - Operator confirmed type→track mapping

## Implementation Plan

1. **Audit docs/** — list all artifact types
2. **Operator interview** — confirm ADR-025 mapping
3. **Build extraction regex** — test on edge cases
4. **Build title slugifier** — handle special chars
5. **Document naming rules** — per track
6. **Test collision detection** — hard vs soft

## Evidence

- docs/ directory structure
- ADR-003 (current, incorrect model)
- ADR-025 (proposed correction)
- Existing worktree naming (swain-worktree-name.sh)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-04 | — | Drafted for EPIC-056 |
