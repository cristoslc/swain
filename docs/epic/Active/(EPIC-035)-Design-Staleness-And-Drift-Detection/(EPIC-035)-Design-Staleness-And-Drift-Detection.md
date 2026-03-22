---
title: "Design Staleness and Drift Detection"
artifact: EPIC-035
track: container
status: Active
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
parent-vision: VISION-001
parent-initiative: INITIATIVE-005
priority-weight: ""
success-criteria:
  - DESIGN artifacts detect when tracked source files change (STALE), move (MOVED), or disappear (BROKEN)
  - Design Intent section preserves original vision as write-once Goals/Constraints/Non-goals
  - Alignment decisions cascade from Epic to child SPECs — operator is only prompted on violations
  - design-check.sh integrates into specwatch scan and swain-sync pipelines
  - artifact-refs replaces enriched linked-artifacts v2 across TRAIN and DESIGN definitions
depends-on-artifacts: []
addresses: []
evidence-pool: design-staleness-drift@c3fd9fb
linked-artifacts:
  - DESIGN-005
  - SPEC-094
  - SPEC-095
  - SPEC-096
  - SPEC-097
  - SPEC-145
  - SPEC-146
---

# Design Staleness and Drift Detection

## Goal / Objective

Keep DESIGN artifacts current with application state by detecting bidirectional drift (code changes without design updates, and design evolution without code catching up). Preserve original design vision through a structured Design Intent section. Protect operator alignment decisions by checking derived SPECs against design constraints rather than re-asking.

## Scope Boundaries

**In scope:**
- `sourcecode-refs` frontmatter field with blob SHA pinning
- `artifact-refs` rename (from enriched `linked-artifacts` v2)
- `rel` type vocabulary (`linked`, `documents`, `aligned`)
- Design Intent section in DESIGN template (Goals, Constraints, Non-goals)
- `design-check.sh` script (CURRENT / STALE / MOVED / BROKEN detection)
- Integration hooks: specwatch, swain-sync, swain-design transitions
- Relationship model updates for new edge types
- Decision protection: alignment cascading from Epic → child SPECs

**Out of scope:**
- Frontmatter schema versioning (`schema: v2`) and template compression
- Code-level visual drift detection (CSS tokens, DOM snapshots)
- `rel` type vocabulary as a formal schema file

## Child Specs

- SPEC-094: Frontmatter Schema — artifact-refs, sourcecode-refs, rel types
- SPEC-095: Design Intent Template Section
- SPEC-096: design-check.sh — Blob SHA Drift Detection
- SPEC-097: Integration Hooks and Decision Protection

## Key Dependencies

None — builds on existing tooling patterns (train-check.sh, specwatch.sh).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-19 | -- | Created from brainstorming session; design doc approved |
