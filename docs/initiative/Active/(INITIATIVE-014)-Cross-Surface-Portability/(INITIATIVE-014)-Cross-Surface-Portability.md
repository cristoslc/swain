---
title: "Cross-Surface Portability"
artifact: INITIATIVE-014
track: container
status: Active
author: cristos
created: 2026-03-18
last-updated: 2026-03-18
parent-vision: VISION-003
priority-weight: high
success-criteria:
  - Swain's core decision-support patterns usable from Claude web or Claude desktop
  - A non-CLI user can adopt swain's artifact model
  - Research spikes completed with phased recommendations
  - Approach selected and first surface delivered
depends-on-artifacts: []
addresses: []
trove: ""
linked-artifacts:
  - EPIC-032
  - EPIC-033
  - VISION-001
  - VISION-002
---

# Cross-Surface Portability

## Strategic Focus

Investigate and implement the most effective way to make swain's decision-support capabilities available across AI agent surfaces beyond Claude Code CLI. Priority order: Claude web/desktop (personal use), Claude Code (friend adoption), other agent runtimes, standalone.

The core question: how much of swain's value can be projected onto each surface, and what's the minimum build required to get there?

## Scope Boundaries

**In scope:**
- Research into each target surface's extension model
- Feasibility spikes for packaging approaches (prompts, MCP, portable core)
- Phased recommendation for implementation order
- First surface delivery (likely Claude web/desktop)

**Out of scope:**
- Redefining what swain is (VISION-001's domain)
- Sandbox/safe autonomy concerns (VISION-002's domain)
- Commercial distribution or marketplace presence
- Feature parity across all surfaces — degraded-but-useful is acceptable

## Child Epics

- **EPIC-032** — Cross-Runtime Documentation (Proposed): test and document swain's existing cross-runtime compatibility
- **EPIC-033** — Swain MCP Server (Proposed): build the MCP server with Tools, Prompts, and Resources for portable artifact lifecycle management

## Small Work (Epic-less Specs)

_None yet._

## Key Dependencies

- Research spikes must complete before approach selection
- Understanding of Claude web/desktop extension models (evolving rapidly)
- MCP specification stability (if MCP approach selected)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-18 | | Initial creation — research phase |
