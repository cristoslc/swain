---
title: "Artifact-Aware Worktree Naming"
artifact: SPEC-251
track: implementable
status: Proposed
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-epic: EPIC-056
priority-weight: high
depends-on-artifacts:
  - ADR-025
linked-artifacts:
  - SPIKE-056
---

# SPEC-251: Artifact-Aware Worktree Naming

## Goal

Update `swain-worktree-name.sh` to generate worktree names based on artifact track (ADR-025). The naming rules differ by track to reflect the artifact's lifecycle semantics.

## Naming Rules (from ADR-025)

| Track | Pattern | Example |
|-------|---------|---------|
| Implementable (SPEC, SPIKE) | `${ID}-${title-slug}` | `spec-054-worktree-isolation` |
| Container (EPIC, INITIATIVE) | `${purpose-slug}-${timestamp}-${ID}-${title-slug}` | `migration-20260404-epic-012-materialized-parenting` |
| Standing (VISION, ADR, etc.) | `${ID}-${title-slug}` | `vision-001-safe-autonomy` |
| No artifact | `session-${timestamp}-${random}` | `session-20260404-143022-a7f3` |

## Deliverables

Update `skills/swain-session/scripts/swain-worktree-name.sh` to:
1. Extract artifact ID from purpose text (regex: `(SPEC|EPIC|SPIKE|VISION|INITIATIVE|ADR|DESIGN|JOURNEY|PERSONA|RUNBOOK|TRAIN)-\d+`)
2. Look up artifact frontmatter to get title and track
3. Slugify title (lowercase, replace non-alphanumeric with hyphens, trim)
4. Apply track-specific naming pattern
5. Fall back to `session-${timestamp}-${random}` when no artifact ID found

## Acceptance Criteria

- [ ] **AC1: Extracts artifact ID from purpose text**
  - "implement SPEC-054 lockfile schema" -> SPEC-054
  - "EPIC-012 migration work" -> EPIC-012
  - Case insensitive (spec-054 -> SPEC-054)
  - Multiple IDs: takes first container if present, else first

- [ ] **AC2: Implementable naming**
  - SPEC-054 with title "Worktree Isolation" -> `spec-054-worktree-isolation`
  - SPIKE-053 with title "EnterWorktree Migration" -> `spike-053-enterworktree-migration`

- [ ] **AC3: Container naming**
  - EPIC-012 with purpose "migration" -> `migration-YYYYMMDD-epic-012-materialized-parenting`
  - INITIATIVE-013 with purpose "safety" -> `safety-YYYYMMDD-initiative-013-concurrent-session-safety`

- [ ] **AC4: Standing naming**
  - ADR-025 with title "Artifact Model Correction" -> `adr-025-artifact-model-correction`

- [ ] **AC5: Fallback naming**
  - No artifact ID in text -> `session-YYYYMMDD-HHMMSS-XXXX`

- [ ] **AC6: Title lookup from frontmatter**
  - Reads `title:` field from artifact markdown file
  - Handles missing file gracefully (falls back to ID-only)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-04 | -- | Materialized for EPIC-056 |
