---
title: "Decision-Only Artifact Type Classification"
artifact: SPIKE-012
status: Complete
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
question: "Which artifact types can the agent fully transition through their lifecycle without human decision-making, and what is the correct swain-status treatment at each phase?"
gate: Pre-SPEC-010-implementation
risks-addressed:
  - Misclassifying a type as decision-only when some of its phases are legitimately agent-implementable
  - Hiding artifacts that do need attention from the operator (over-filtering)
depends-on: []
linked-artifacts:
  - SPEC-010
  - EPIC-006
evidence-pool: ""
---

# Decision-Only Artifact Type Classification

## Question

Which artifact types can the agent fully transition through their lifecycle without human decision-making, and what is the correct swain-status treatment at each phase?

## Go / No-Go Criteria

**Go:** A definitive classification table is produced that maps each artifact type to: (a) decision-only vs. implementation-capable, and (b) the correct swain-status action hint and bucket (Decisions / Implementation / Omit) for each lifecycle phase.

**No-Go:** Some types are ambiguous — their phases mix human and agent work. In that case, produce a per-phase table and recommend a conservative classification (prefer Decisions over Implementation for ambiguous phases).

## Pivot Recommendation

If no-go: use the per-phase conservative table to fix SPEC-010. Accept some over-classification into Decisions as preferable to false Implementation signals.

## Findings

### Methodology

Read every artifact type definition in `skills/swain-design/references/*-definition.md`. For each type, examined each lifecycle phase to determine whether it involves agent-implementable work (code, config, executable procedures) or is purely human judgment/decision.

### Type-Level Classification

The classification is based on whether the agent can fully transition the artifact through its lifecycle phases without needing human decision-making at each gate.

| Artifact Type | Classification | Rationale |
|---------------|----------------|-----------|
| **EPIC** | agent-autonomous | Agent coordinates child specs, tracks progress, transitions phases based on child completion |
| **SPEC** | agent-autonomous | Core implementation unit; agent writes code, runs tests, verifies acceptance criteria |
| **STORY** | agent-autonomous | User-facing requirement; agent implements, tests, and completes |
| **RUNBOOK** | agent-autonomous | Executable procedures; agent authors, tests, and activates |
| **SPIKE** | sometimes autonomous | Agent can drive research/prototyping in Active phase, but go/no-go verdict may need human judgment depending on the spike |
| **VISION** | needs human | Strategic positioning, audience, success metrics — fundamentally human decisions at every phase |
| **JOURNEY** | needs human | End-to-end user workflow narrative, pain point identification — requires human creative direction |
| **PERSONA** | needs human | User archetype definition — requires human insight and validation |
| **ADR** | needs human | Records a decision already made — the decision itself is human; implementation happens in downstream SPECs |
| **DESIGN** | needs human | Wireframes, flows, interaction patterns — requires human creative direction, same as JOURNEY |

### Per-Phase Bucket Mapping

This table defines where each artifact type + phase combination should appear in swain-status output.

| Type | Phase | Bucket | Action Hint |
|------|-------|--------|-------------|
| VISION | Draft | Decisions | align on goals and audience |
| VISION | Active | Decisions | decompose into epics |
| VISION | Sunset | Omit | — |
| JOURNEY | Draft | Decisions | map pain points and opportunities |
| JOURNEY | Validated | Omit | — |
| PERSONA | Draft | Decisions | validate with user research |
| PERSONA | Validated | Omit | — |
| ADR | Draft | Decisions | form recommendation |
| ADR | Proposed | Decisions | review and decide |
| ADR | Adopted | Omit | — |
| EPIC | Proposed | Decisions | activate and decompose into specs |
| EPIC | Active | Implementation | work on child specs |
| EPIC | Testing | Implementation | verify acceptance criteria |
| SPEC | Draft | Decisions | review and approve |
| SPEC | Review | Decisions | complete review |
| SPEC | Approved | Implementation | create implementation plan |
| SPEC | Testing | Implementation | complete verification |
| STORY | Draft | Decisions | refine acceptance criteria |
| STORY | Ready | Implementation | create implementation plan |
| SPIKE | Planned | Decisions | begin investigation |
| SPIKE | Active | Implementation | complete investigation |
| SPIKE | Complete | Omit | — |
| RUNBOOK | Draft | Implementation | author and test procedure |
| RUNBOOK | Active | Implementation | execute and record results |
| DESIGN | Draft | Decisions | create wireframes and flows |
| DESIGN | Review | Decisions | review design with user |
| DESIGN | Approved | Decisions | validate design direction |
| DESIGN | Active | Omit | — |
**Terminal phases** (Abandoned, Archived, Retired, Superseded, Deprecated, Complete, Implemented, Validated for Persona/Journey) are always **Omit** — no action needed.

### Verdict: GO

A definitive classification was produced. The key insight: five types (VISION, JOURNEY, PERSONA, ADR, DESIGN) need human decision-making at every lifecycle phase — the agent cannot autonomously transition them. Four types (EPIC, SPEC, STORY, RUNBOOK) are agent-autonomous. SPIKE is sometimes autonomous depending on the investigation's complexity.

### Implementation Recommendation for SPEC-010

Replace the current `is_decision` function (which checks type+status combinations) with a two-level lookup:

1. **Type-level guard:** If type is in `{VISION, JOURNEY, PERSONA, ADR, DESIGN}`, always route to Decisions (or Omit for terminal phases). Never route to Implementation.
2. **Phase-level guard:** For agent-autonomous types, use the per-phase bucket mapping above. For SPIKE, route Planned to Decisions (human decides when to start) and Active to Implementation.

This eliminates the "fall-through to Implementation" bug — decision-only types can never escape to the wrong bucket regardless of phase.

### Edge Cases

- **SPEC type:bug**: Uses SPEC lifecycle. Triage (Draft/Review) is Decisions; implementation (Approved onward) is Implementation — same as any SPEC. BUG as a standalone type was removed per SPEC-004 and SPEC-006.
- **SPIKE Complete**: Omit, not Decisions. The findings are already written; no operator action is pending. If the operator needs to make a go/no-go call, that happens via the downstream artifact (ADR, SPEC), not the spike itself.
- **VISION Active**: Decisions with hint "decompose into epics" — not Implementation, even though epics may be in flight. The Vision itself is not being implemented.

## Sources

- `skills/swain-design/references/vision-definition.md`
- `skills/swain-design/references/journey-definition.md`
- `skills/swain-design/references/epic-definition.md`
- `skills/swain-design/references/spec-definition.md`
- `skills/swain-design/references/story-definition.md`
- `skills/swain-design/references/spike-definition.md`
- `skills/swain-design/references/persona-definition.md`
- `skills/swain-design/references/adr-definition.md`
- `skills/swain-design/references/runbook-definition.md`
- `skills/swain-design/references/design-definition.md`

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-13 | — | Initial creation |
| Active | 2026-03-13 | 8433c14 | Investigation conducted |
| Complete | 2026-03-13 | 8433c14 | GO verdict — definitive classification produced |
