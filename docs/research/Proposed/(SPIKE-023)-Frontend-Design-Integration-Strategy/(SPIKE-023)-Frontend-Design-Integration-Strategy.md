---
title: "Product Design Integration Strategy"
artifact: SPIKE-023
track: container
status: Proposed
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
question: "How should swain-design (product design orchestrator) integrate three generation systems (Anthropic's plugin, superpowers' frontend-design, impeccable.style) with swain's artifact system (DESIGN and JOURNEY types) to produce UX-aware product design — not just frontend code?"
gate: Pre-development
risks-addressed:
  - Building an orchestrator that adds overhead without adding value over using each system directly
  - Style inconsistency when different systems generate different parts of the frontend
  - Tight coupling to a specific system that may change or be deprecated (especially Anthropic's plugin)
  - impeccable.style integration approach that doesn't scale to real component libraries
  - Treating design as code generation rather than product thinking — losing the UX/journey context
linked-artifacts:
  - EPIC-021
  - EPIC-019
trove: ""
---

# Product Design Integration Strategy

## Summary

<!-- Populated when transitioning to Complete. -->

## Question

How should swain-design (product design orchestrator) integrate three generation systems (Anthropic's plugin, superpowers' frontend-design, impeccable.style) with swain's artifact system (DESIGN and JOURNEY types) to produce UX-aware product design — not just frontend code?

The skill's persona is a senior product developer — someone who owns both "right thing built" and "thing built right." They understand the product vision well enough that their implementation decisions are product-informed, and they write code well enough that the result is maintainable and secure. The skill should think about user flows and design rationale, not just component markup.

## Go / No-Go Criteria

**GO (build orchestrator):**
- Each system has a clear, non-overlapping responsibility in the orchestration
- impeccable.style tokens/conventions can be injected as context into the generation systems without manual translation
- The orchestrator adds measurable value: fewer style inconsistencies, less manual correction, or faster iteration than using each system ad-hoc

**NO-GO (use systems independently):**
- The three systems overlap so heavily that an orchestrator just adds indirection
- impeccable.style is too opinionated or too loose to serve as a shared style foundation
- Anthropic's plugin and superpowers' skill produce fundamentally incompatible output that can't be harmonized

## Investigation Areas

### 1. Capability mapping

For each of the three systems, document:
- What types of frontend work it handles well (components, layouts, full pages, animations, responsive design)
- What inputs it expects (prompts, design tokens, mockups, existing code)
- What outputs it produces (React, vanilla HTML/CSS, Tailwind, other)
- Known limitations or aesthetic tendencies

Build a matrix showing where capabilities overlap and where they're complementary.

### 2. impeccable.style evaluation

Fetch and evaluate https://impeccable.style/:
- What does it provide? (design tokens, CSS variables, component patterns, typography scales, color palettes)
- In what format? (CSS custom properties, JSON tokens, Tailwind config, Figma tokens)
- How would its tokens be injected into Anthropic's plugin and superpowers' skill as generation context?
- Is it actively maintained? What's the update cadence?

### 3. Anthropic frontend design plugin assessment

Evaluate Anthropic's built-in frontend design capabilities:
- What is the plugin's interface? (MCP tool, built-in artifact, system prompt extension)
- How does it accept style constraints? (system prompt, tool parameters, reference files)
- Can it consume external design tokens (e.g., impeccable.style) as input?
- What's the output quality for components vs. full pages?

### 4. Superpowers frontend-design skill assessment

Evaluate the superpowers `frontend-design` skill:
- What does it do that the Anthropic plugin doesn't?
- How does it enforce "distinctive, production-grade" output? (prompt engineering, templates, validation)
- Can it accept external style tokens as input?
- What's the integration surface? (skill invocation, chaining, context injection)

### 5. Orchestration architecture options

Given findings from areas 1–4, evaluate:

**Option A — Router model:**
swain-design routes each request to the best system based on request type. No system talks to another. impeccable.style tokens are injected into whichever system handles the request.

**Option B — Pipeline model:**
impeccable.style provides tokens → superpowers' skill generates the component → Anthropic's plugin refines or integrates it. Sequential pipeline.

**Option C — Overlay model:**
Anthropic's plugin or superpowers' skill generates the base output. swain-design then applies impeccable.style as a post-processing pass (style correction, token replacement).

**Option D — Thin wrapper:**
swain-design is just a prompt enhancer — it prepends impeccable.style context to the user's request and delegates entirely to one of the two generation systems. Minimal orchestration.

### 6. DESIGN and JOURNEY artifact integration

Evaluate how the skill connects to swain's artifact system:
- How should the skill read JOURNEY artifacts to understand where a screen fits in a user flow?
- Should designing a screen automatically create or update a DESIGN artifact capturing the rationale?
- What's the right handoff between swain-strategize (which creates JOURNEY and DESIGN artifacts) and swain-design (which consumes and extends them)?
- Can DESIGN artifacts serve as a component inventory — tracking what's been designed, what patterns exist, what's reusable?

### 7. Graceful degradation

What happens when a system is unavailable?
- Anthropic plugin not available (different runtime, older Claude version)
- superpowers not installed
- impeccable.style offline or removed
- No JOURNEY or DESIGN artifacts exist yet

Can the orchestrator still produce useful output with any single system present?

## Findings

<!-- Populated during Active phase. -->

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Initial creation; informs EPIC-021 |
