# Swain Artifact Types

Swain supports 11 artifact types, managed by the **swain-design** skill. Each artifact has a unique ID prefix, a defined lifecycle (phases), and a specific role in the project hierarchy.

## Artifact Overview

| # | Artifact | ID Format | What It Is | Lifecycle Phases |
|---|----------|-----------|------------|------------------|
| 1 | **Product Vision** | `VISION-NNN` | Top-level product direction -- goals, audience, success metrics. The highest-level artifact. | Draft -> Active -> Sunset |
| 2 | **User Journey** | `JOURNEY-NNN` | End-to-end user workflow with pain points that drive epics and specs. | Draft -> Validated -> Archived |
| 3 | **Epic** | `EPIC-NNN` | Large strategic initiative that decomposes into Specs and Stories. The coordination layer between Vision and feature-level work. | Proposed -> Active -> Testing -> Complete |
| 4 | **User Story** | `STORY-NNN` | User-facing requirement in "As a / I want / So that" format with acceptance criteria. Atomic unit of user requirements. | Draft -> Ready -> Implemented |
| 5 | **Agent Spec** | `SPEC-NNN` | Technical implementation specification -- a behavior contract with acceptance criteria. Precise enough for an agent to build from. | Draft -> Review -> Approved -> Testing -> Implemented -> Deprecated |
| 6 | **Research Spike** | `SPIKE-NNN` | Time-boxed investigation to reduce uncertainty. Produces knowledge, not shippable code. | Planned -> Active -> Complete |
| 7 | **Persona** | `PERSONA-NNN` | Archetypal user profile (Alan Cooper model) that informs Journeys and Stories. | Draft -> Validated -> Archived |
| 8 | **ADR** | `ADR-NNN` | Architecture Decision Record (Nygard format) -- context, decision, alternatives, consequences. One decision per document. | Draft -> Proposed -> Adopted -> Retired / Superseded |
| 9 | **Runbook** | `RUNBOOK-NNN` | Step-by-step operational procedure (agentic or manual) with a defined trigger and run log. | Draft -> Active -> Archived |
| 10 | **Bug** | `BUG-NNN` | Structured defect report with severity, affected artifacts, and reproduction steps. | Reported -> Active -> Fixed -> Verified (or Declined) |
| 11 | **Design** | `DESIGN-NNN` | UI/UX interaction design -- wireframes, flows, state diagrams for user-facing surfaces. | Draft -> Approved -> Retired / Superseded |

All artifacts also support an **Abandoned** phase, reachable from any active state, to signal intentional non-pursuit without deleting the record.

## Hierarchy and Relationships

The artifacts form a structured hierarchy with cross-references:

```
VISION
  |-- JOURNEY (end-to-end user workflows, with pain points)
  |     |-- PERSONA (linked user archetypes)
  |
  |-- EPIC (strategic initiatives)
        |-- SPEC (technical implementation)
        |-- STORY (user-facing requirements)
        |-- SPIKE (research, can attach to any artifact)
        |-- ADR (architectural decisions, cross-cutting)
        |-- DESIGN (interaction design, cross-cutting)
        |-- RUNBOOK (operational procedures, cross-cutting)
        |-- BUG (defect reports, independent but references affected artifacts)
```

Key relationship rules:
- **Mandatory hierarchy**: VISION owns EPICs and JOURNEYs. EPICs own SPECs and STORYs.
- **Cross-cutting references**: ADRs, PERSONAs, RUNBOOKs, DESIGNs, and SPIKEs link to multiple artifact types but are not owned by any single one.
- **Pain point traceability**: JOURNEYs contain pain points (`JOURNEY-NNN.PP-NN`) that EPICs, SPECs, and STORYs can reference via `addresses:` in frontmatter.
- **BUGs are independent**: they sit outside the Epic hierarchy and reference affected artifacts.

## Tracking Tiers

The artifacts fall into four tiers for execution tracking (via swain-do):

| Tier | Artifacts | Tracking Rule |
|------|-----------|---------------|
| **Implementation** | SPEC, STORY, BUG | swain-do plan **required** before writing code |
| **Coordination** | EPIC, VISION, JOURNEY | Decompose into implementable children first; track the children |
| **Research** | SPIKE | swain-do optional, recommended for complex multi-thread investigations |
| **Reference** | ADR, PERSONA, RUNBOOK, DESIGN | No execution tracking expected |

## File Organization

All artifacts live under `docs/<type>/<Phase>/` with phase subdirectories that reflect the artifact's current lifecycle state. Phase transitions move the artifact (via `git mv`) to the new phase directory. Each artifact type maintains a lifecycle index at `docs/<type>/list-<type>.md`.

| Artifact | Directory | Format |
|----------|-----------|--------|
| Vision | `docs/vision/<Phase>/` | Folder: `(VISION-NNN)-<Title>/` |
| Journey | `docs/journey/<Phase>/` | Folder: `(JOURNEY-NNN)-<Title>/` |
| Epic | `docs/epic/<Phase>/` | Folder: `(EPIC-NNN)-<Title>/` |
| Story | `docs/story/<Phase>/` | Single file: `(STORY-NNN)-<Title>.md` |
| Spec | `docs/spec/<Phase>/` | Folder: `(SPEC-NNN)-<Title>/` |
| Spike | `docs/research/<Phase>/` | Folder: `(SPIKE-NNN)-<Title>/` |
| Persona | `docs/persona/<Phase>/` | Folder: `(PERSONA-NNN)-<Title>/` |
| ADR | `docs/adr/<Phase>/` | Single file: `(ADR-NNN)-<Title>.md` |
| Runbook | `docs/runbook/<Phase>/` | Folder: `(RUNBOOK-NNN)-<Title>/` |
| Bug | `docs/bug/<Phase>/` | Single file: `(BUG-NNN)-<Title>.md` |
| Design | `docs/design/<Phase>/` | Folder: `(DESIGN-NNN)-<Title>/` |
