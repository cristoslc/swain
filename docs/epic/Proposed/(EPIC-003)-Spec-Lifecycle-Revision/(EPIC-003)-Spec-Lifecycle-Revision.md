---
title: "Spec Lifecycle Revision"
artifact: EPIC-003
status: Proposed
author: cristos
created: 2026-03-12
last-updated: 2026-03-12
parent-vision: VISION-001
success-criteria:
  - Spec lifecycle phases are reduced to a clear, minimal set with no underused states
  - Lifecycle model is consistent across artifact types where applicable
  - Transition tooling (specwatch, spec-verify) is updated to match revised lifecycle
  - Existing specs migrate cleanly with no broken references
depends-on:
  - EPIC-002
addresses: []
evidence-pool: ""
---

# Spec Lifecycle Revision

## Goal / Objective

Revise the Agent Spec lifecycle to eliminate underused phases, simplify the state machine, and align lifecycle semantics across artifact types. The current six-state lifecycle (Draft → Review → Approved → Testing → Implemented → Deprecated) has phases that add friction without clear value — in practice, specs skip Review and the Approved → Testing transition is ambiguous. This epic produces a tighter lifecycle that matches how swain-design is actually used.

## Scope Boundaries

### In scope

- **Phase consolidation** — evaluate each lifecycle state for actual usage; remove or merge phases that don't carry their weight (e.g., Review may fold into Draft/Approved, Testing may merge with verification gating)
- **Cross-type alignment** — audit lifecycle definitions across Specs, Epics, Spikes, and ADRs; standardize phase naming and transition semantics where they overlap
- **Tooling updates** — update specwatch, spec-verify, specgraph, and swain-design SKILL.md to enforce the revised lifecycle
- **Folder structure** — adjust phase subdirectories under `docs/spec/` to match the new lifecycle
- **Migration** — provide a migration path for existing artifacts (SPEC-001 through SPEC-003)
- **Reference docs** — update `spec-definition.md`, templates, and implementation-plans guide

### Out of scope

- Changes to the artifact type system itself (covered by EPIC-002)
- New artifact types or frontmatter fields beyond lifecycle-related changes
- External issue integration lifecycle (covered by EPIC-002)

## Child Specs

Updated as Agent Specs are created under this epic.

## Key Dependencies

- EPIC-002 — the type system unification (especially BUG → SPEC folding) may influence which lifecycle states are needed
- Existing approved specs (SPEC-002, SPEC-003) should migrate cleanly to the revised lifecycle

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-12 | — | Initial creation |
