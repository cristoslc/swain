---
title: "Lifecycle State Machine Tools"
artifact: SPEC-084
track: implementation
status: Proposed
type: feature
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
parent-epic: EPIC-033
depends-on-artifacts:
  - SPEC-082
  - SPEC-083
acceptance-criteria:
  - "`lifecycle_transition` enforces valid transitions per artifact type (refuses invalid ones with clear error)"
  - "Successful transitions: update frontmatter status, move directory via git mv, add lifecycle table row"
  - "`lifecycle_status` returns current phase and list of valid next phases"
  - State machines match definitions in skills/swain-design/references/*-definition.md
  - Transition errors include the reason and valid alternatives
swain-do: required
linked-artifacts:
  - SPEC-082
  - SPEC-083
  - SPEC-085
  - SPEC-090
---

# Lifecycle State Machine Tools

## Context

Deterministic enforcement of artifact lifecycle transitions. This is the key advantage MCP has over skill-only instructions — the server programmatically refuses invalid transitions. Skills can instruct an agent to move a SPEC from Proposed to Active, but only the state machine server can guarantee the agent does not accidentally move a SPEC directly to Complete or skip the In-Review phase. State machine definitions are sourced from the existing `skills/swain-design/references/*-definition.md` files to stay canonical.

## Scope

**In scope:**
- `lifecycle_transition`: validate that the requested transition is legal per the artifact type's state machine definition; if valid, move the directory to the new phase folder via `git mv`, update the frontmatter `status` field, and append a row to the lifecycle table in the artifact file
- `lifecycle_status`: given an artifact ID, return its current phase and the list of valid next phases available from that state
- State machine definitions covering all artifact types: Vision, Initiative, Epic, Spec, Spike, ADR, and any others defined in `skills/swain-design/references/`

**Out of scope:**
- Chart and aggregate queries (SPEC-085)
- Specwatch / adr-check integration (future)

## Acceptance Criteria

- `lifecycle_transition` enforces valid transitions per artifact type (refuses invalid ones with clear error)
- Successful transitions: update frontmatter status, move directory via git mv, add lifecycle table row
- `lifecycle_status` returns current phase and list of valid next phases
- State machines match definitions in skills/swain-design/references/*-definition.md
- Transition errors include the reason and valid alternatives

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-19 | | Initial creation |
