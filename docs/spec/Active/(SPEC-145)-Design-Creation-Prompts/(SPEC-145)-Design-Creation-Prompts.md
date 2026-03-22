---
title: "Design Creation Prompts"
artifact: SPEC-145
track: implementable
status: Active
author: cristos
created: 2026-03-21
last-updated: 2026-03-21
priority-weight: ""
type: enhancement
parent-epic: EPIC-035
parent-initiative: ""
linked-artifacts:
  - SPEC-097
  - SPEC-134
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Design Creation Prompts

## Problem Statement

DESIGN is the only artifact type in swain with no proactive creation triggers. SPECs get suggested during EPIC decomposition, SPIKEs get suggested when uncertainty is detected, ADRs get flagged by `adr-check.sh` — but DESIGNs are only created when the operator explicitly asks. This means design documentation only exists for surfaces the operator already knows need it, missing surfaces where the operator hasn't yet realized a design would help.

[EPIC-035](../../../epic/Active/(EPIC-035)-Design-Staleness-And-Drift-Detection/(EPIC-035)-Design-Staleness-And-Drift-Detection.md)'s existing child SPECs (094–097) assume DESIGNs already exist — they protect and detect drift on existing designs. Nobody prompts the operator to create one in the first place. This is the gap between "DESIGNs are useful" and "DESIGNs actually get created."

## Desired Outcomes

Operators of swain-managed projects get timely, low-noise nudges to create DESIGN artifacts at the moments when design documentation would be most valuable — during EPIC and SPEC authoring, when the shape of the work is fresh and the cost of capture is lowest. This closes the creation gap that [EPIC-035](../../../epic/Active/(EPIC-035)-Design-Staleness-And-Drift-Detection/(EPIC-035)-Design-Staleness-And-Drift-Detection.md)'s drift detection machinery depends on: you can't detect drift on a DESIGN that was never written.

## External Behavior

During EPIC and SPEC creation workflows in swain-design, the agent evaluates whether the new artifact has design-surface implications and, if so, surfaces an advisory prompt suggesting a linked DESIGN artifact.

### Hook 1: EPIC creation

**When** a new EPIC is created,
**Then** the agent scans the EPIC's scope/goal sections for design-surface signals and asks:

> This epic touches {domain} surfaces. Consider creating a `domain: {domain}` DESIGN to anchor the design decisions before implementation begins. Create one now?

**Interactive mode:** If the operator accepts, chain into DESIGN creation with the EPIC pre-linked via `artifact-refs` with `rel: [aligned]`. If declined, proceed silently.

**Autonomous mode:** When running in a non-interactive context (dispatched agent, batch processing), create the DESIGN automatically — the signal detection is high-confidence enough that waiting for operator confirmation would block the workflow. The created DESIGN is marked `Proposed` so the operator can review at their convenience.

### Hook 2: SPEC creation

**When** a new SPEC is created,
**Then** the agent checks:
1. Does the SPEC's parent EPIC (if any) have a linked DESIGN? If yes, skip — design coverage already exists upstream.
2. Does the SPEC's scope section mention interaction surfaces, data schemas, or API contracts? If yes, prompt:

> This spec modifies {domain} surfaces with no linked DESIGN. Create a `domain: {domain}` DESIGN, or is this covered elsewhere?

**Interactive mode:** If the operator says it's covered, record a note and move on. If they want a DESIGN, chain into creation.

**Autonomous mode:** Create a `Proposed` DESIGN automatically when signals are detected and no upstream coverage exists.

### Signal detection

Design-surface signals are keyword/pattern matches against the artifact's scope and goal sections:

| Domain | Signals |
|--------|---------|
| `interaction` | UI, screen, flow, wireframe, component, page, dialog, form, layout, navigation |
| `data` | schema, entity, model, data flow, migration, contract, data product, pipeline |
| `system` | API, endpoint, interface, boundary, SLA, webhook, integration, protocol |

The agent classifies the strongest signal into one domain. If multiple domains match, mention all and let the operator choose. If no signals match, skip silently.

## Acceptance Criteria

**Given** an EPIC being created whose goal mentions "new dashboard UI,"
**When** swain-design completes the creation workflow,
**Then** it prompts: "This epic touches interaction surfaces. Consider creating a `domain: interaction` DESIGN..." before the post-operation scan step.

**Given** a SPEC being created under an EPIC that already has a `rel: [aligned]` DESIGN,
**When** swain-design evaluates design-surface signals,
**Then** it skips the prompt — upstream design coverage exists.

**Given** a SPEC being created with no parent EPIC whose scope mentions "data pipeline schema changes,"
**When** swain-design completes the creation workflow,
**Then** it prompts suggesting a `domain: data` DESIGN.

**Given** an EPIC whose goal is purely operational ("migrate CI to GitHub Actions"),
**When** swain-design evaluates design-surface signals,
**Then** no prompt is shown — no design-surface signals detected.

**Given** the operator declines the DESIGN creation prompt,
**When** the EPIC/SPEC creation continues,
**Then** no DESIGN is created and no further prompting occurs for that artifact.

## Verification

<!-- Populated when entering Testing phase -->

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

**In scope:**
- Advisory prompts in EPIC and SPEC creation workflows (SKILL.md behavioral guidance)
- Signal detection keyword table (embedded in SKILL.md, not a separate script)
- Pre-linking created DESIGNs via `artifact-refs` with `rel: [aligned]`
- Skip logic when upstream DESIGN coverage exists

**Out of scope:**
- Prompts during SPIKE, ADR, or other non-implementation artifact creation
- Retroactive prompts for existing EPICs/SPECs (that's [SPEC-146](../(SPEC-146)-Design-Coverage-Audit-Lens/(SPEC-146)-Design-Coverage-Audit-Lens.md)'s audit lens)
- Script-based signal detection — this is agent behavioral guidance in SKILL.md, not a new tool

## Implementation Approach

### TDD Cycle 1: SKILL.md EPIC creation hook
- Add a design-surface evaluation step to the EPIC creation workflow (between step 7 and step 8)
- Include the signal detection keyword table
- Define the prompt format and accept/decline flow
- Add `artifact-refs` pre-linking when operator accepts

### TDD Cycle 2: SKILL.md SPEC creation hook
- Add a design-surface evaluation step to the SPEC creation workflow
- Include upstream coverage check (parent EPIC → linked DESIGNs)
- Define the skip logic and prompt format

### TDD Cycle 3: Integration verification
- Verify prompts fire correctly during EPIC/SPEC creation (manual walkthrough)
- Verify skip logic works when upstream DESIGN exists
- Verify no false positives on non-design EPICs/SPECs

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-21 | -- | Initial creation |
