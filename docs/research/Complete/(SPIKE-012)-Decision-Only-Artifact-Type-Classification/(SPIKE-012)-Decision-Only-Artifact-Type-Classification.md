---
title: "Decision-Only Artifact Type Classification"
artifact: SPIKE-012
status: Complete
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
question: "Which artifact types are decision-only across their entire lifecycle, what does 'no meaningful implementation phase' mean for each, and what is the correct swain-status treatment at each phase?"
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

Which artifact types are decision-only across their entire lifecycle, what does "no meaningful implementation phase" mean for each, and what is the correct swain-status treatment at each phase?

## Go / No-Go Criteria

**Go:** A definitive classification table is produced that maps each artifact type to: (a) decision-only vs. implementation-capable, and (b) the correct swain-status action hint and bucket (Decisions / Implementation / Omit) for each lifecycle phase.

**No-Go:** Some types are ambiguous — their phases mix human and agent work. In that case, produce a per-phase table and recommend a conservative classification (prefer Decisions over Implementation for ambiguous phases).

## Pivot Recommendation

If no-go: use the per-phase conservative table to fix SPEC-010. Accept some over-classification into Decisions as preferable to false Implementation signals.

## Findings

### Methodology

Read every artifact type definition in `skills/swain-design/references/*-definition.md`. For each type, examined each lifecycle phase to determine whether it involves agent-implementable work (code, config, executable procedures) or is purely human judgment/decision.

### Type-Level Classification

| Artifact Type | Classification | Rationale |
|---------------|----------------|-----------|
| **VISION** | decision-only | Strategic positioning, audience, success metrics — fundamentally human decisions at every phase |
| **JOURNEY** | decision-only | End-to-end user workflow narrative, pain point identification — discovery/research, never implemented directly |
| **PERSONA** | decision-only | User archetype definition and validation through research — reference artifact, no implementation |
| **ADR** | decision-only | Records a decision already made with context and consequences — implementation happens in downstream SPECs |
| **EPIC** | implementation-capable | Coordinates child SPECs/STORYs; Active/Testing phases have agent work in flight |
| **SPEC** | implementation-capable | Core implementation unit; carries `swain-do: required`; Testing phase is agent verification |
| **STORY** | implementation-capable | User-facing requirement; carries `swain-do: required`; Ready phase triggers agent implementation |
| **SPIKE** | implementation-capable | Time-boxed investigation; Active phase is agent-driven research/prototyping |
| **RUNBOOK** | implementation-capable | Executable procedures (agentic or manual); Draft and Active phases involve agent authoring/execution |
| **DESIGN** | implementation-capable | Wireframes, flows, diagrams; Draft phase involves agent-assisted creation |

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
| DESIGN | Draft | Implementation | create wireframes and flows |
| DESIGN | Approved | Omit | — |
| BUG | any | Decisions | triage and fix |

**Terminal phases** (Abandoned, Archived, Retired, Superseded, Deprecated, Complete, Implemented, Validated for Persona/Journey) are always **Omit** — no action needed.

### Verdict: GO

A definitive classification was produced. No types are ambiguous — every phase maps cleanly to a single bucket. The key insight: four types (VISION, JOURNEY, PERSONA, ADR) are decision-only at _every_ phase. The remaining six have at least one implementation-capable phase, but some of their phases are still decision-only (e.g., SPEC Draft is a decision, SPEC Testing is implementation).

### Implementation Recommendation for SPEC-010

Replace the current `is_decision` function (which checks type+status combinations) with a two-level lookup:

1. **Type-level guard:** If type is in `{VISION, JOURNEY, PERSONA, ADR}`, always route to Decisions (or Omit for terminal phases). Never route to Implementation.
2. **Phase-level guard:** For implementation-capable types, use the per-phase bucket mapping above.

This eliminates the "fall-through to Implementation" bug — decision-only types can never escape to the wrong bucket regardless of phase.

### Edge Cases

- **BUG** type specs: Always Decisions (triage requires human judgment even though fix is agent work). The agent implements after triage, but the decision to fix and how to scope is human.
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
