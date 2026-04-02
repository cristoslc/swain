---
title: "Deprecate and Replace Superpowers with Native Skills"
artifact: EPIC-053
track: container
status: Proposed
author: Assistant
created: 2026-04-01
last-updated: 2026-04-01
parent-vision: VISION-002
parent-initiative: ""
priority-weight: high
success-criteria:
  - All existing `swain-*` skills drop their `superpowers` chaining lines.
  - Socratic mode exists inside `swain-design`.
  - Planning tables live inside `swain-do`.
  - Verification gates run before marking tasks done in `swain-do`.
  - Agents read a generic debug rule inside `AGENTS.md`.
  - `ADR-021` passes the `adr-check.sh` consistency scan.
depends-on-artifacts:
  - ADR-021
  - DESIGN-009
addresses: []
evidence-pool: ""
---

# Deprecate and Replace Superpowers with Native Skills

## Goal / Objective

Remove code that relies on external `superpowers` skills. Put basic engineer habits into Swain's normal scripts.

## Desired Outcomes

Swain works as a full tool. We keep the strict habits of chained skills. But we drop the closed files. The user waits less time because the agent uses fewer tools.

## Progress

<!-- Auto-populated from session digests. See progress.md for full log. -->

## Scope Boundaries

**In scope:**
- Updates to `swain-design`, `swain-do`, and `swain-*` skills.
- Edits to `AGENTS.md` for error paths.
- Scrubbing script checks like `brainstorming.md`.

**Out of scope:**
- Major system redesigns.
- Changing `tk` state flags.

## Child Specs

- [SPEC-228](../../../spec/Proposed/(SPEC-228)-Remove-Vendored-Superpowers/(SPEC-228)-Remove-Vendored-Superpowers.md): Remove superpowers chained calls from `swain-*` skills.
- [SPEC-229](../../../spec/Proposed/(SPEC-229)-Native-Implementation-Planning/(SPEC-229)-Native-Implementation-Planning.md): Native Implementation Planning in `swain-do`.
- [SPEC-230](../../../spec/Proposed/(SPEC-230)-Native-Socratic-Discovery/(SPEC-230)-Native-Socratic-Discovery.md): Native Socratic Discovery in `swain-design`.
- [SPEC-231](../../../spec/Proposed/(SPEC-231)-Global-Debugging-Loop/(SPEC-231)-Global-Debugging-Loop.md): Global Debugging Loop in `AGENTS.md`.

## Key Dependencies

- ADR-021 forces the stop to chained tasks.
- DESIGN-008 lines up new boundaries.
- DESIGN-009 details the new user interaction pathways.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-01 | TBD | Initial creation |
