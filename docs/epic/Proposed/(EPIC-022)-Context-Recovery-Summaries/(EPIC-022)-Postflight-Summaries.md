---
title: "Context Recovery Summaries"
artifact: EPIC-022
track: container
status: Proposed
author: cristos
created: 2026-03-14
last-updated: 2026-04-15
parent-vision: VISION-001
parent-initiative: INITIATIVE-005
success-criteria:
  - swain produces artifact-aware context recovery output for any reorientation moment
  - Output works in two modes — skill-completion (postflight) and session-resumption (recap)
  - Both modes produce the same structured content: what happened, project state delta, and what's next
  - Content is expressed in artifact terms (SPEC IDs, goals, epic progress) not file/commit terms
  - Output is portable — renderable in any system that can consume swain's text output
  - Output is lightweight — 3-5 lines, flow-preserving, not a full dashboard dump
  - The operator can request the full dashboard if they want more detail
  - Works across all swain skills that have a meaningful completion event (swain-do, swain-design, swain-search, swain-sync, etc.)
  - Session-resumption mode is invokable manually and from any host system (not tied to Claude Code telemetry)
  - Invocation mechanism determined by SPIKE-024
depends-on-artifacts:
  - SPIKE-024
addresses:
  - "github:cristoslc/swain#51"
trove: "claude-code-recap@d4461a536a6a5282440e44314bed0ab1db108983"
---

# Context Recovery Summaries

## Goal / Objective

Give operators artifact-aware context recovery at any reorientation moment. Two
moments need this:

1. **Skill completion (postflight)** — the operator was deep in a swain
   activity and needs to resurface. What just happened in project terms? What's
   the highest-leverage next move?
2. **Session resumption (recap)** — the operator returns to a session after
   stepping away. Where were we? What's still open?

Both moments produce the same structured content. The trigger differs; the
output format does not.

Claude Code ships its own `/recap` (v2.1.108). Swain's version is different in
two ways: it speaks in artifact terms (SPEC-042 implemented, EPIC-017
unblocked) instead of code/file terms, and it is portable — it works in any
system that can consume swain's text output, not only within Claude Code.

This addresses GH #51 (subagent-driven-development completion summaries lack
context) as a special case of the broader problem: any reorientation moment is
a chance for swain to surface project-level context the operator has lost.

## Scope Boundaries

**In scope:**
- Context recovery output in swain-status (invokable by swain skills and by the operator directly).
- Two invocation modes: skill-completion (postflight) and session-resumption (recap).
- Artifact-aware content — reads the artifact(s) just worked on, summarizes in project terms.
- Recommendation — reuses swain-status's existing recommendation logic, scoped to what changed.
- Flow-preserving output design — lightweight, not a wall of data.
- Portability — output is plain text, consumable outside Claude Code.
- Integration points in swain skills that have meaningful completion events.
- SPIKE-024 to resolve design questions before implementation.

**Out of scope:**
- Detecting inactivity or "away" state (that is a host-system concern, not swain's).
- Modifying non-swain skills (superpowers skills are dependencies, not targets).
- Full dashboard redesign (context recovery complements the dashboard, not replaces it).
- Automated next-action execution (output recommends, operator decides).

## Child Specs

_To be created after SPIKE-024 resolves design questions._

Anticipated specs:
1. Context recovery output format — structured content for both modes.
2. Invocation protocol — how skills pass context to postflight; how the operator invokes recap.
3. Integration into swain-do, swain-design, swain-search, swain-sync completion paths.

## Key Dependencies

- **[SPIKE-024](../../research/Proposed/(SPIKE-024)-Postflight-Summary-Design/(SPIKE-024)-Postflight-Summary-Design.md)** — must resolve invocation mechanism, "in flow" definition, and context-passing protocol.
- **swain-status** — context recovery lives here; needs skill-creator to determine best modification approach.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Initial creation; gated on SPIKE-024. |
| Proposed | 2026-04-15 | — | Scope expanded: owns both skill-completion and session-resumption modes; renamed to reflect broader scope; trove linked. |
