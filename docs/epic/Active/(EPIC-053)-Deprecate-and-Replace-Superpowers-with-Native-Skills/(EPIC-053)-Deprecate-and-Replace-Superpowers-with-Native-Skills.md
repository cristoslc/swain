---
title: "Deprecate and Replace Superpowers with Native Skills"
artifact: EPIC-053
track: container
status: Active
author: Assistant
created: 2026-04-01
last-updated: 2026-04-01
parent-vision: VISION-002
parent-initiative: ""
priority-weight: high
success-criteria:
  - Skills drop external chains.
  - Socratic mode exists in design.
  - Planning tables live in do.
  - Test gates run in do.
  - Agents read a generic debug rule.
  - ADR logic passes the check.
depends-on-artifacts:
  - ADR-021
  - DESIGN-009
  - DESIGN-010
  - DESIGN-011
addresses: []
evidence-pool: ""
---

# Deprecate and Replace Superpowers with Native Skills

## Goal / Objective

Remove code that relies on external skills. Put basic engineer habits into Swain's normal scripts.

## Desired Outcomes

Swain works as a full tool. We keep the strict habits of chained skills. But we drop the closed files. The user waits less time. The agent uses fewer tools.

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

- [SPEC-228](../../../spec/Active/(SPEC-228)-Remove-Vendored-Superpowers/(SPEC-228)-Remove-Vendored-Superpowers.md): Remove external calls from swain skills.
- [SPEC-229](../../../spec/Active/(SPEC-229)-Native-Implementation-Planning/(SPEC-229)-Native-Implementation-Planning.md): Native plan steps in swain do.
- [SPEC-230](../../../spec/Active/(SPEC-230)-Native-Socratic-Discovery/(SPEC-230)-Native-Socratic-Discovery.md): Native Socratic tests in swain design.
- [SPEC-231](../../../spec/Active/(SPEC-231)-Global-Debugging-Loop/(SPEC-231)-Global-Debugging-Loop.md): Global debug loop in the agent root.
- [SPEC-232](../../../spec/Active/(SPEC-232)-swain-teardown-Skill-and-Session-Chain/(SPEC-232)-swain-teardown-Skill-and-Session-Chain.md): swain-teardown skill and session chain (SPEC-232).

## Key Dependencies

- ADR-021 stops linked tools.
- DESIGN-008 lines up new limits.
- DESIGN-009 holds Socratic details.
- DESIGN-010 holds the checklist.
- DESIGN-011 holds global crash plans.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-01 | TBD | Initial creation |
| Active | 2026-04-02 | TBD | Approved and transitioned |
