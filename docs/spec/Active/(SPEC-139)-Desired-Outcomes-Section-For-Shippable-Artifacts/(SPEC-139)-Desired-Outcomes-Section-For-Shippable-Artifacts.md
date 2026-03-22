---
title: "Desired Outcomes Section for Shippable Artifacts"
artifact: SPEC-139
track: implementable
status: Active
author: operator
created: 2026-03-21
last-updated: 2026-03-21
type: enhancement
parent-epic:
parent-initiative:
linked-artifacts: []
depends-on-artifacts: []
addresses:
  - PERSONA-001
  - PERSONA-002
evidence-pool:
source-issue:
priority-weight: high
swain-do: required
---

# Desired Outcomes Section for Shippable Artifacts

## Problem Statement

Swain artifacts that produce shippable changes — SPECs, EPICs, and INITIATIVEs — lack a standard section that articulates *why the work matters* and *how completion advances our aspirations*. Existing outcome-oriented sections serve adjacent but distinct purposes:

- **SPEC Acceptance Criteria** answer "what must be true?" — testable conditions, not stakeholder impact.
- **EPIC Goal/Objective** describes the deliverable aim, not who benefits or how.
- **EPIC/INITIATIVE `success-criteria`** (frontmatter) captures measurable KPIs — necessary but not sufficient to convey impact.
- **INITIATIVE Strategic Focus** explains direction and timing ("what and why now"), not downstream effects on personas.

None of these answer the "so what?" question: *How does completing this artifact make our personas and stakeholders better off? How does it drive us toward our aspirations?*

Without this, artifacts can pass all verification gates while remaining disconnected from the product direction they're meant to serve.

## External Behavior

### Section name: "Desired Outcomes"

A new body section titled **"Desired Outcomes"** is added to three artifact templates:

| Artifact | Placement | Relationship to existing sections |
|----------|-----------|----------------------------------|
| **SPEC** | After Problem Statement, before External Behavior | Complementary — Problem Statement says what's wrong; Desired Outcomes says what's better when it ships. Acceptance Criteria remain the testable gate; Desired Outcomes is the aspirational framing. |
| **EPIC** | After Goal/Objective, before Scope Boundaries | Complementary — Goal/Objective says what we're building; `success-criteria` says how we measure it; Desired Outcomes says who benefits and how the world improves. |
| **INITIATIVE** | After Strategic Focus, before Scope Boundaries | Complementary — Strategic Focus says what direction and why now; Desired Outcomes says how completing this initiative advances personas toward their aspirations. |

### Section content guidance

The Desired Outcomes section answers:

1. **Who benefits?** — Name the personas, stakeholders, or user segments affected. Reference [PERSONA-001](../../persona/Active/(PERSONA-001)-Swain-Project-Developer/(PERSONA-001)-Swain-Project-Developer.md) and [PERSONA-002](../../persona/Active/(PERSONA-002)-AI-Coding-Agent/(PERSONA-002)-AI-Coding-Agent.md) by ID when applicable.
2. **What changes for them?** — Describe the qualitative improvement in their experience, capability, or confidence. This is aspirational, not metric-driven — though metrics may support the narrative.
3. **How does this drive us toward our aspirations?** — Connect the artifact's completion to the parent Vision or Initiative's direction. For standalone artifacts, articulate the aspiration directly.

### What Desired Outcomes is NOT

- Not a duplication of Acceptance Criteria (those remain the testable contract).
- Not a metrics dashboard (those belong in `success-criteria` frontmatter or Vision Success Metrics).
- Not a stakeholder sign-off gate — it is authored by the artifact creator and evolves with understanding.

### Template placeholder text

**SPEC:**
> How does shipping this spec make our personas better off? Who benefits and what changes for them? Connect to the parent epic/initiative's aspirations, or articulate the aspiration directly for standalone specs.

**EPIC:**
> Who benefits when this epic ships, and how? What qualitative improvements do our personas experience? How does this advance the parent initiative or vision's direction?

**INITIATIVE:**
> How does completing this initiative advance our personas toward their aspirations? What does the world look like for our stakeholders when this direction is fully realized?

### Existing artifact migration

Existing artifacts are not bulk-migrated. The section is added to templates and enforced through two channels:

1. **Organic adoption:** When an existing artifact is next substantively edited (phase transition, scope change, or content revision), the author SHOULD add a Desired Outcomes section — but this is guidance at edit time, not a gate.
2. **Audit remediation:** The swain-design audit (Phase 2 parallel agents) checks all active SPEC, EPIC, and INITIATIVE artifacts for the presence of a Desired Outcomes section. Missing sections are reported as findings. Remediation involves the audit agent drafting a Desired Outcomes section for each artifact based on its Problem Statement/Goal/Strategic Focus and parent chain context — presented to the operator for review before committing.

### Audit integration

The **Naming & structure validator** audit agent (see `references/auditing.md`) gains an additional check:

- For every artifact with `track: implementable` or `track: container` whose type is SPEC, EPIC, or INITIATIVE: verify the document body contains a `## Desired Outcomes` heading. Missing sections are reported as structure findings with severity "advisory" (not blocking).

The audit report groups these findings under a **"Missing Desired Outcomes"** heading with a table:

| Artifact | Type | Status | Parent | Suggested action |
|----------|------|--------|--------|-----------------|
| SPEC-042 | SPEC | Active | EPIC-012 | Draft from Problem Statement + EPIC-012 Goal |
| EPIC-023 | EPIC | Active | INITIATIVE-004 | Draft from Goal/Objective + INITIATIVE-004 Strategic Focus |

**Audit remediation workflow:**
1. The audit agent reads the artifact's existing outcome-adjacent sections (Problem Statement, Goal/Objective, Strategic Focus) and parent chain context.
2. It drafts a Desired Outcomes section following the content guidance (Who benefits? What changes? How does this advance aspirations?).
3. Drafts are presented to the operator in batch for review — not auto-committed.
4. Approved drafts are inserted at the correct position in each artifact and committed.

## Acceptance Criteria

- Given the SPEC template, when a new SPEC is created, then the template includes a "Desired Outcomes" section between Problem Statement and External Behavior with the SPEC placeholder text.
- Given the EPIC template, when a new EPIC is created, then the template includes a "Desired Outcomes" section between Goal/Objective and Scope Boundaries with the EPIC placeholder text.
- Given the INITIATIVE template, when a new INITIATIVE is created, then the template includes a "Desired Outcomes" section between Strategic Focus and Scope Boundaries with the INITIATIVE placeholder text.
- Given an existing SPEC/EPIC/INITIATIVE without a Desired Outcomes section, when a phase transition or substantive edit occurs, then the agent does not block the operation for lacking the section (soft guidance, not hard gate).
- Given a swain-design audit is run, when the Naming & structure validator inspects active SPEC/EPIC/INITIATIVE artifacts, then it reports any artifact missing a `## Desired Outcomes` heading as an advisory finding.
- Given audit findings include missing Desired Outcomes sections, when the operator reviews the audit report, then each finding includes a drafted Desired Outcomes section based on the artifact's existing content and parent chain context, presented for operator approval before committing.

## Verification

<!-- Populated when entering Testing phase. -->

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- **In scope:** SPEC, EPIC, and INITIATIVE templates only — these are the "shippable change-producers."
- **Out of scope:** VISION (has Success Metrics), SPIKE (has Go/No-Go Criteria), ADR, DESIGN, PERSONA, JOURNEY, RUNBOOK, TRAIN — these are standing/research artifacts with their own outcome framing.
- **Audit-driven retroactive adoption** — audits flag missing sections and draft remediation for operator review. No bulk migration outside audit context.
- **No hard gates** — Desired Outcomes is authored guidance, not a verification gate like Acceptance Criteria.
- **No new frontmatter fields** — this is a body section, not metadata.

## Implementation Approach

Three template files to edit, one definition file to update for awareness:

1. Edit `spec-template.md.template` — add Desired Outcomes section after Problem Statement.
2. Edit `epic-template.md.template` — add Desired Outcomes section after Goal/Objective.
3. Edit `initiative-template.md.template` — add Desired Outcomes section after Strategic Focus.
4. Update `SKILL.md` artifact creation guidance if needed to mention the new section in authoring workflow.
5. Update `references/auditing.md` — add the Desired Outcomes presence check to the Naming & structure validator agent's responsibilities.
6. Implement audit remediation workflow — the audit agent drafts sections for artifacts missing Desired Outcomes, using parent chain context, and presents them for operator review.

Template edits are single section insertions with placeholder text — minimal risk, no structural changes to frontmatter or lifecycle. The audit integration extends an existing agent's checklist with one additional heading check and a remediation path.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-21 | — | Initial creation |
