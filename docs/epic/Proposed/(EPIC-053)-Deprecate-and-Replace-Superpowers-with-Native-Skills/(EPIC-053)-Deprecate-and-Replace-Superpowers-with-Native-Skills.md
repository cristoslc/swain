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
addresses: []
evidence-pool: ""
---

# Deprecate and Replace Superpowers with Native Skills

## Goal / Objective

Remove reliance on copied `superpowers` skills by internalizing core software engineering practices straight into Swain's native scripts.

## Desired Outcomes

Swain functions fully as a standalone agentic product. It holds onto the rigorous habits of chained skills without distributing closed content. The user has a faster looping time because agents stay in one skill longer.

## Progress

<!-- Auto-populated from session digests. See progress.md for full log. -->

## Scope Boundaries

**In scope:**
- Updates to `swain-design`, `swain-do`, and `swain-*` skills.
- Edits to `AGENTS.md` for error recovery.
- Stripping out script checks like `brainstorming.md`.

**Out of scope:**
- Changes to `swain-session` outputs.
- Modifying how `tk` ticket states work.

## Child Specs

- [SPEC-228](docs/spec/Proposed/SPEC-228-Remove-Vendored-Superpowers/SPEC-228-Remove-Vendored-Superpowers.md): Remove superpowers chained calls from `swain-*` skills.
- [SPEC-229](docs/spec/Proposed/SPEC-229-Native-Implementation-Planning/SPEC-229-Native-Implementation-Planning.md): Native Implementation Planning in `swain-do`.
- [SPEC-230](docs/spec/Proposed/SPEC-230-Native-Socratic-Discovery/SPEC-230-Native-Socratic-Discovery.md): Native Socratic Discovery in `swain-design`.
- [SPEC-231](docs/spec/Proposed/SPEC-231-Global-Debugging-Loop/SPEC-231-Global-Debugging-Loop.md): Global Debugging Loop in `AGENTS.md`.

## Key Dependencies

- ADR-021 guides the move away from chained skills.
- DESIGN-008 lays out the new boundaries.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-01 | TBD | Initial creation |
