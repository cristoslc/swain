---
title: "Postflight Summaries"
artifact: EPIC-022
track: container
status: Proposed
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
parent-vision: VISION-001
parent-initiative: INITIATIVE-005
success-criteria:
  - swain-status supports a postflight mode that any swain skill can invoke on completion
  - Postflight produces a domain-context recap ("what just happened in project terms") and a recommendation ("what's next")
  - Output is lightweight — 3-5 lines, flow-preserving, not a full dashboard dump
  - The operator can request the full dashboard if they want more detail
  - Postflight supports keeping the operator in flow — surfaces just enough context to decide the next move without breaking momentum
  - Works across all swain skills that have a meaningful completion event (swain-do, swain-commission, swain-dispatch, swain-sync, etc.)
  - Invocation mechanism determined by SPIKE-024
depends-on-artifacts:
  - SPIKE-024
addresses:
  - "github:cristoslc/swain#51"
trove: ""
---

# Postflight Summaries

## Goal / Objective

Add a postflight summary mode to swain-status that helps operators recover context after completing a task. When the operator has been deep in implementation, research, or any other swain activity, they lose sight of the project-level picture. Postflight answers two questions:

1. **What just happened?** — a domain-context recap of the activity that just completed, in project terms (not file paths or commit hashes)
2. **What's next?** — a recommendation for the highest-leverage next action, same logic as swain-status's existing recommendation engine

The postflight is invoked by swain skills on completion — not by the operator directly. It's a 3-5 line output designed to preserve flow, not a dashboard. The operator can ask for the full status dashboard if they want the complete picture.

This addresses GH #51 (subagent-driven-development completion summaries lack context) as a special case of the broader problem: any skill's completion is a moment where the operator needs to resurface from the weeds to an oversight context.

## Scope Boundaries

**In scope:**
- Postflight mode in swain-status (invokable by other swain skills)
- Domain-context recap generation (reading the artifact that was just worked on, summarizing in project terms)
- Recommendation (reusing swain-status's existing recommendation logic, scoped to what changed)
- Flow-preserving output design (lightweight, not a wall of data)
- Integration points in swain skills that have meaningful completion events
- SPIKE-024 to resolve design questions before implementation

**Out of scope:**
- Modifying non-swain skills (superpowers skills are dependencies, not targets)
- Full dashboard redesign (postflight complements the dashboard, doesn't replace it)
- Automated next-action execution (postflight recommends, operator decides)

## Child Specs

_To be created after SPIKE-024 resolves design questions._

Anticipated specs:
1. Postflight mode in swain-status — recap + recommendation output
2. Invocation protocol — how skills pass context to postflight
3. Integration into swain-do, swain-commission, swain-dispatch, swain-sync completion paths

## Key Dependencies

- **SPIKE-024** — must resolve invocation mechanism, "in flow" definition, and context-passing protocol
- **swain-status** — postflight lives here; needs skill-creator to determine best modification approach

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Initial creation; gated on SPIKE-024 |
