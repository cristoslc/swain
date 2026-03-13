---
title: "Normalize Artifact Lifecycle to Three Tracks"
artifact: ADR-003
status: Active
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
evidence-pool: ""
linked-artifacts:
  - EPIC-008
depends-on-artifacts: []
---

# Normalize Artifact Lifecycle to Three Tracks

## Context

Swain has 11 artifact types, each with its own lifecycle phases — some overlapping, some unique. The phase names are inconsistent: "Draft" vs "Planned" for first phase, "Implemented" vs "Complete" for terminal, "Validated" for a phase that doesn't apply in solo-dev workflows. Tools like specgraph and swain-status must special-case every type+phase combination, and SPIKE-012's classification exercise revealed the surface area is unnecessarily large.

Two types (STORY, BUG) were already identified as redundant: SPEC with `type: feature` absorbs stories (per SPEC-006), and SPEC with `type: bug` absorbs bugs (per SPEC-004).

The status quo makes the system harder to learn, harder to maintain in tooling, and harder to classify for agent autonomy.

## Decision

Collapse to **9 artifact types** organized into **three lifecycle tracks** with a shared vocabulary:

### Implementable (SPEC only)

Proposed → Ready → In Progress → Needs Manual Test → Complete

### Container (EPIC, SPIKE)

Proposed → Active → Complete

### Standing (VISION, JOURNEY, PERSONA, ADR, RUNBOOK, DESIGN)

Proposed → Active → (Retired | Superseded)

### Universal terminal states

Available from any phase on any type:
- **Abandoned** — intentionally not pursued
- **Retired** — served its purpose, wound down
- **Superseded** — replaced by a named successor

### Key normalizations

- **"Proposed" is the universal starting state** — replaces Draft, Planned
- **"Complete" is the universal success terminal** — replaces Implemented, Adopted
- **"Validated" is dropped** — doesn't fit solo-dev workflows
- **"Review" is dropped** — collapsed into Proposed (review happens conversationally before Ready)
- **Deprecated, Archived, Sunset merge into Retired** — one word for "no longer active"
- **STORY type dropped** — SPEC with `type: feature` covers user-facing requirements
- **BUG type remains dropped** — SPEC with `type: bug` covers defects (per SPEC-004, SPEC-006)
- **ADR "Adopted" becomes "Active"** — an adopted ADR is an active constraint

## Alternatives Considered

**A. Keep per-type lifecycles, just rename for consistency.** Would fix the naming problem but not the classification surface area. Every tool still needs per-type phase tables. Rejected because the complexity cost compounds as tooling grows.

**B. Two tracks (implementable vs everything else).** Considered merging containers and standing, but EPIC/SPIKE have a meaningful "Complete" state (all children done) that standing artifacts don't. Retired ≠ Complete — a vision doesn't "complete," it retires when replaced or obsolete.

**C. Single universal lifecycle for all types.** Too coarse. SPECs need phases like "Needs Manual Test" that are meaningless for a Vision or ADR. Forcing all types through the same pipe would create phases that are always skipped.

**D. Keep STORY as a separate type.** Stories add a layer of indirection (Story → Spec) without clear value in a solo-dev workflow. The `type: feature` field on SPEC captures user-facing intent without a separate artifact type.

## Consequences

**Positive:**
- Classification surface drops from ~40 type+phase combinations to ~18
- Tooling (specgraph, swain-status, specwatch) can branch on track, not individual type
- SPIKE-012's bucket mapping becomes a simple track lookup instead of a per-type table
- New contributors learn 3 tracks instead of 11 ad-hoc lifecycles
- Agent autonomy classification aligns cleanly with tracks: implementable = autonomous, container = coordination, standing = human decisions

**Negative:**
- **Breaking change** — every existing artifact must be migrated (directory renames, frontmatter updates)
- Phase subdirectory names change across the repo (e.g., `Draft/` → `Proposed/`, `Implemented/` → `Complete/`)
- Definition files, templates, and scripts all need rewriting
- External references to old phase names (documentation, saved links) break
- The STORY definition, template, and list file must be removed

**Mitigations:**
- EPIC-008 captures the full migration plan with swain-doctor detection of old directories
- swain-upgrade provides automated migration path
- Alias support (swain-push → swain-sync pattern) can apply to phase name aliases in tooling if needed

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Adopted | 2026-03-13 | 3d440c3 | Decision made during GitHub #25 triage; captured as EPIC-008 |
