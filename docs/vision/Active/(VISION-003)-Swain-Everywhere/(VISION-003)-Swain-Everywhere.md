---
title: "Swain Everywhere"
artifact: VISION-003
track: standing
status: Active
product-type: personal
author: cristos
created: 2026-03-18
last-updated: 2026-03-18
priority-weight: high
depends-on-artifacts:
  - VISION-001
evidence-pool: ""
---

# Swain Everywhere

## Target Audience

Myself — across every surface where I interact with AI agents. Secondarily, friends and colleagues who want swain's decision-support patterns in their own workflows without adopting Claude Code CLI.

## Problem Statement

Swain's decision-support and implementation-alignment capabilities are locked to a single runtime: Claude Code CLI with vendored skills. This means:

- When I use Claude web or Claude desktop, I lose swain's artifact model, lifecycle management, and structured decision-making
- Friends and colleagues who don't use Claude Code CLI can't benefit from swain at all
- If I adopt a different agent runtime (or use multiple), swain doesn't travel with me
- The value swain provides — structured thinking, artifact-driven alignment, phased execution — is runtime-independent in principle but runtime-dependent in practice

## Existing Landscape

- **Claude Code skills** (current home) — full swain experience, but requires CLI + vendored skill files + bash scripting
- **Claude web Projects** — supports system prompts and file uploads, no script execution
- **Claude desktop** — supports MCP servers and Projects, emerging plugin model
- **Other agent runtimes** — varying extension models (AGENTS.md, tool plugins, MCP adoption in progress)
- **No existing solution** packages a decision-support artifact system portably across AI agent surfaces

## Build vs. Buy

No existing product covers this need. The question is not build-vs-buy but **how much to build**: swain's patterns may be expressible as structured prompts (minimal build), MCP servers (moderate build), or a portable runtime layer (significant build). Research spikes will determine the right tier.

## Maintenance Budget

Low. This is a personal tool — each additional surface must be maintainable without becoming a second job. Preferred: one canonical source of truth with thin projections per surface, rather than N independent implementations. Any approach that requires maintaining parallel codebases for each runtime is disqualified.

## Success Metrics

- I can use swain's core decision-support patterns from Claude web or Claude desktop within 30 days
- A friend can adopt swain's artifact model without installing Claude Code CLI
- Adding a new runtime surface takes days, not weeks
- The canonical skill source remains the single source of truth

## Non-Goals

- Replacing VISION-001 (what swain IS) — this Vision is about distribution, not redefinition
- Building a general-purpose agent framework — swain is a decision-support system, not a runtime
- Achieving feature parity across all surfaces — degraded-but-useful beats absent
- Commercial distribution or marketplace presence

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-18 | | Initial creation — research phase |
