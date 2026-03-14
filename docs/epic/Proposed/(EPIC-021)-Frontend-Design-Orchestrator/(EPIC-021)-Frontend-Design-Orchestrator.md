---
title: "Frontend Design Orchestrator"
artifact: EPIC-021
track: container
status: Proposed
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
parent-vision: VISION-001
success-criteria:
  - A new `swain-design` skill orchestrates frontend work across three systems: Anthropic's frontend design plugin, superpowers' frontend-design skill, and impeccable.style
  - The orchestrator produces consistent, high-quality frontend output regardless of which underlying system handles a given task
  - Style decisions from impeccable.style are applied automatically — the operator doesn't manually translate design tokens into code
  - The skill routes to the right underlying system based on what's being asked (component generation, layout, styling, full-page design)
  - Works when only a subset of the three systems is available (graceful degradation)
depends-on-artifacts:
  - SPIKE-023
  - EPIC-019
addresses: []
evidence-pool: ""
---

# Frontend Design Orchestrator

## Goal / Objective

Build `swain-design` as a frontend orchestrator skill that ties together three design systems:

1. **Anthropic's frontend design plugin** — Claude's built-in frontend generation capabilities
2. **Superpowers' `frontend-design` skill** — distinctive, production-grade UI generation that avoids generic AI aesthetics
3. **impeccable.style** — an external design system / style guide for consistent visual language

The operator invokes `swain-design` for any frontend work, and the skill routes to the appropriate system (or combines them) based on the request. The goal is a single entry point that produces frontend output with consistent quality and style.

This skill name becomes available after EPIC-019 renames the current `swain-design` to `swain-commission`.

## Scope Boundaries

**In scope:**
- New skill: `swain-design` (frontend orchestrator)
- Integration with Anthropic's frontend design plugin
- Integration with superpowers' `frontend-design` skill
- Integration with impeccable.style design tokens and style system
- Routing logic: which system handles which type of request
- Style enforcement: impeccable.style decisions applied consistently across all outputs
- Graceful degradation when a system is unavailable

**Out of scope:**
- Modifying the underlying systems (Anthropic plugin, superpowers skill, impeccable.style itself)
- Backend code generation
- Design system creation (impeccable.style is the design system; this skill consumes it)

## Child Specs

_To be created after SPIKE-023 resolves the integration strategy._

## Key Dependencies

- **SPIKE-023** — must determine how the three systems integrate before implementation
- **EPIC-019** — must complete the `swain-design` → `swain-commission` rename to free the skill name

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Initial creation; gated on SPIKE-023 and EPIC-019 |
