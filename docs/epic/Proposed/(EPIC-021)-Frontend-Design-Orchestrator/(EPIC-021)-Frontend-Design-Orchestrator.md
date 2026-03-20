---
title: "Product Design Orchestrator"
artifact: EPIC-021
track: container
status: Proposed
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
parent-vision: VISION-001
parent-initiative: INITIATIVE-007
success-criteria:
  - A new `swain-design` skill operates as a product design practice — UX thinking, user journey awareness, and visual design — not just code generation
  - Orchestrates across three systems: Anthropic's frontend design plugin, superpowers' frontend-design skill, and impeccable.style
  - Integrates with swain's DESIGN artifact type for capturing design decisions, rationale, and UX flows alongside implementation
  - Considers user journeys (JOURNEY artifacts) when designing interfaces — screens serve flows, not just features
  - Produces consistent, high-quality output regardless of which underlying system handles a given task
  - Style decisions from impeccable.style are applied automatically — the operator doesn't manually translate design tokens into code
  - Routes to the right underlying system based on what's being asked (UX flow, component design, layout, styling, full-page design)
  - Works when only a subset of the three systems is available (graceful degradation)
depends-on-artifacts:
  - SPIKE-023
  - EPIC-019
addresses: []
trove: ""
---

# Product Design Orchestrator

## Goal / Objective

Build `swain-design` as a product design skill that combines UX thinking, user journey awareness, and frontend implementation. The persona is a senior product developer — someone who owns both "right thing built" and "thing built right." They understand the product vision well enough that their implementation decisions are product-informed, and they write code well enough that the result is maintainable and secure. Not a PM (they don't own the roadmap), not a junior dev (they don't just build what's specified) — they build what's *right*.

The skill ties together three systems:

1. **Anthropic's frontend design plugin** — Claude's built-in frontend generation capabilities
2. **Superpowers' `frontend-design` skill** — distinctive, production-grade UI generation that avoids generic AI aesthetics
3. **impeccable.style** — an external design system / style guide for consistent visual language

And connects them to swain's artifact system:

4. **DESIGN artifacts** — captures design decisions, rationale, component inventories, and interaction patterns as reviewable artifacts
5. **JOURNEY artifacts** — the skill reads existing user journeys to understand how a screen fits into the broader flow, ensuring interfaces serve user goals rather than isolated features

The operator invokes `swain-design` for any product design work — from "design the onboarding flow" (UX/journey-level) to "build this settings page" (component-level) — and the skill brings the right combination of thinking and tooling to bear.

This skill name becomes available after EPIC-019 renames the current `swain-design` to `swain-strategize`.

## Scope Boundaries

**In scope:**
- New skill: `swain-design` (product design orchestrator)
- Integration with Anthropic's frontend design plugin
- Integration with superpowers' `frontend-design` skill
- Integration with impeccable.style design tokens and style system
- Integration with DESIGN and JOURNEY artifact types from swain-strategize
- UX-aware design: the skill considers user flows, not just individual screens
- Routing logic: which system handles which type of request (UX flow vs. component vs. styling)
- Style enforcement: impeccable.style decisions applied consistently across all outputs
- Graceful degradation when a system is unavailable

**Out of scope:**
- Modifying the underlying systems (Anthropic plugin, superpowers skill, impeccable.style itself)
- Backend code generation
- Design system creation (impeccable.style is the design system; this skill consumes it)
- User research or persona creation (that's swain-strategize's domain)

## Child Specs

_To be created after SPIKE-023 resolves the integration strategy._

## Key Dependencies

- **SPIKE-023** — must determine how the three systems integrate before implementation
- **EPIC-019** — must complete the `swain-design` → `swain-strategize` rename to free the skill name

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Initial creation; gated on SPIKE-023 and EPIC-019 |
