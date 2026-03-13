---
name: swain-design
description: Create, validate, and transition documentation artifacts (Vision, Epic, Story, Spec, Spike, ADR, Persona, Runbook, Design, Journey) through lifecycle phases. Handles spec writing, feature planning, epic creation, user stories, ADR drafting, research spikes, persona definition, runbook creation, design capture, architecture docs, phase transitions, implementation planning, cross-reference validation, and audits. Chains into swain-do for implementation tracking on SPEC/STORY; decomposes EPIC/VISION/JOURNEY into children first.
license: UNLICENSED
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Skill
metadata:
  short-description: Manage spec artifact creation and lifecycle
  version: 1.6.0
  author: cristos
  source: swain
---

# Spec Management

This skill defines the canonical artifact types, phases, and hierarchy. Detailed definitions and templates live in `skills/swain-design/references/`. If the host repo has an AGENTS.md, keep its artifact sections in sync with the skill's reference data.

## Artifact type definitions

Each artifact type has a definition file (lifecycle phases, conventions, folder structure) and a template (frontmatter fields, document skeleton). **Read the definition for the artifact type you are creating or transitioning.**

| Type | What it is | Definition | Template |
|------|-----------|-----------|----------|
| Product Vision (VISION-NNN) | Top-level product direction — goals, audience, and success metrics for a competitive or personal product. | [definition](references/vision-definition.md) | [template](references/vision-template.md.template) |
| User Journey (JOURNEY-NNN) | End-to-end user workflow with pain points that drive epics and specs. | [definition](references/journey-definition.md) | [template](references/journey-template.md.template) |
| Epic (EPIC-NNN) | Large deliverable under a vision — groups related specs and stories with success criteria. | [definition](references/epic-definition.md) | [template](references/epic-template.md.template) |
| User Story (STORY-NNN) | User-facing requirement under an epic, written as "As a... I want... So that..." | [definition](references/story-definition.md) | [template](references/story-template.md.template) |
| Agent Spec (SPEC-NNN) | Technical implementation specification with acceptance criteria. Supports `type: feature \| enhancement \| bug`. Parent epic is optional. | [definition](references/spec-definition.md) | [template](references/spec-template.md.template) |
| Research Spike (SPIKE-NNN) | Time-boxed investigation with a specific question and completion gate. | [definition](references/spike-definition.md) | [template](references/spike-template.md.template) |
| Persona (PERSONA-NNN) | Archetypal user profile that informs journeys and stories. | [definition](references/persona-definition.md) | [template](references/persona-template.md.template) |
| ADR (ADR-NNN) | Single architectural decision — context, choice, alternatives, and consequences (Nygard format). | [definition](references/adr-definition.md) | [template](references/adr-template.md.template) |
| Runbook (RUNBOOK-NNN) | Step-by-step operational procedure (agentic or manual) with a defined trigger. | [definition](references/runbook-definition.md) | [template](references/runbook-template.md.template) |
| Design (DESIGN-NNN) | UI/UX interaction design — wireframes, flows, and state diagrams for user-facing surfaces. | [definition](references/design-definition.md) | [template](references/design-template.md.template) |

## Creating artifacts

### Error handling

When an operation fails (missing parent, number collision, script error, etc.), consult [references/troubleshooting.md](references/troubleshooting.md) for the recovery procedure. Do not improvise workarounds — the troubleshooting guide covers the known failure modes.

### Workflow

1. Scan `docs/<type>/` (recursively, across all phase subdirectories) to determine the next available number for the prefix.
2. **For VISION artifacts:** Before drafting, ask the user whether this is a **competitive product** or a **personal product**. The answer determines which template sections to include and shapes the entire downstream decomposition. See the vision definition for details on each product type.
3. Read the artifact's definition file and template from the lookup table above.
4. Create the artifact in the correct phase subdirectory (usually the first phase — e.g., `docs/epic/Proposed/`, `docs/spec/Draft/`). Create the phase directory with `mkdir -p` if it doesn't exist yet. See the definition file for the exact directory structure.
5. Populate frontmatter with the required fields for the type (see the template).
6. Initialize the lifecycle table with the appropriate phase and current date. This is usually the first phase (Draft, Planned, etc.), but an artifact may be created directly in a later phase if it was fully developed during the conversation (see [Phase skipping](#phase-skipping)).
7. Validate parent references exist (e.g., the Epic referenced by a new Agent Spec must already exist).
8. **ADR compliance check** — run `skills/swain-design/scripts/adr-check.sh <artifact-path>`. Review any findings with the user before proceeding.
8a. **Alignment check** — run `skills/swain-design/scripts/specgraph.sh scope <artifact-id>` and assess per [skills/swain-design/references/alignment-checking.md](skills/swain-design/references/alignment-checking.md). Report blocking findings (MISALIGNED); note advisory ones (SCOPE_LEAK, GOAL_DRIFT) without gating the operation.
9. **Post-operation scan** — run `skills/swain-design/scripts/specwatch.sh scan`. Fix any stale references before committing.
10. **Index refresh step** — update `list-<type>.md` (see [Index maintenance](#index-maintenance)).

## Superpowers integration

When superpowers is installed, read [references/superpowers-integration.md](references/superpowers-integration.md) for brainstorming routing, thin SPEC format, and code review gate details. All integration is optional — swain functions fully without superpowers.

## Phase transitions

### Phase skipping

Phases listed in the artifact definition files are available waypoints, not mandatory gates. An artifact may skip intermediate phases and land directly on a later phase in the sequence. This is normal in single-user workflows where drafting and review happen conversationally in the same session.

- The lifecycle table records only the phases the artifact actually occupied — one row per state it landed on, not rows for states it skipped past.
- Skipping is forward-only: an artifact cannot skip backward in its phase sequence.
- **Abandoned** is a universal end-of-life phase available from any state, including Draft. It signals the artifact was intentionally not pursued. Use it instead of deleting artifacts — the record of what was considered and why it was dropped is valuable.
- Other end-of-life transitions (Sunset, Retired, Superseded, Archived, Deprecated) require the artifact to have been in an active state first — you cannot skip directly from Draft to Retired.

### Workflow

1. Validate the target phase is reachable from the current phase (same or later in the sequence; intermediate phases may be skipped).
2. **Move the artifact** to the new phase subdirectory using `git mv` (e.g., `git mv docs/epic/Proposed/(EPIC-001)-Foo/ docs/epic/Active/(EPIC-001)-Foo/`). Every artifact type uses phase subdirectories — see the artifact's definition file for the exact directory names.
3. Update the artifact's status field in frontmatter to match the new phase.
4. **ADR compliance check** — for transitions to active phases (Active, Approved, Ready, Implemented, Adopted), run `skills/swain-design/scripts/adr-check.sh <artifact-path>`. Review any findings with the user before committing.
4c. **Alignment check** — for transitions to active phases (Active, Approved, Ready, Adopted), run `skills/swain-design/scripts/specgraph.sh scope <artifact-id>` and assess per [skills/swain-design/references/alignment-checking.md](skills/swain-design/references/alignment-checking.md). Skip for backward-looking transitions (Testing, Implemented, Complete) unless content changed since last check. Skip for terminal-phase transitions (Abandoned, Retired, Superseded).
4a. **Verification gate (SPEC only)** — for `Testing → Implemented` transitions, run `skills/swain-design/scripts/spec-verify.sh <artifact-path>`. Address gaps before proceeding.
4b. **Code review gate (SPEC only)** — for `Testing → Implemented`, if superpowers code review skills are installed, request spec compliance + code quality reviews (see [references/superpowers-integration.md](references/superpowers-integration.md)). Not a hard gate.
5. Commit the transition change (move + status update).
6. Append a row to the artifact's lifecycle table with the commit hash from step 5.
7. Commit the hash stamp as a **separate commit** — never amend. Two distinct commits keeps the stamped hash reachable in git history and avoids interactive-rebase pitfalls.
8. **Post-operation scan** — run `skills/swain-design/scripts/specwatch.sh scan`. Fix any stale references.
9. **Index refresh step** — move the artifact's row to the new phase table (see [Index maintenance](#index-maintenance)).

### Completion rules

- An Epic is "Complete" only when all child Agent Specs are "Implemented" and success criteria are met.
- An Agent Spec is "Implemented" only when its implementation plan is closed (or all tasks are done in fallback mode) **and** its Verification table confirms all acceptance criteria pass (enforced by `spec-verify.sh`).
- An ADR is "Superseded" only when the superseding ADR is "Adopted" and links back.

## Evidence pool integration

During research phase transitions (Spike → Active, ADR → Proposed, Vision/Epic creation), check for existing evidence pools and offer to link or create one. Read [references/evidence-pool-integration.md](references/evidence-pool-integration.md) for the full hook, pool scanning, and back-link maintenance procedures.

## Execution tracking handoff

Artifact types fall into four tracking tiers based on their relationship to implementation work:

| Tier | Artifacts | Rule |
|------|-----------|------|
| **Implementation** | SPEC, STORY | Execution-tracking **must** be invoked when the artifact comes up for implementation — create a tracked plan before writing code |
| **Coordination** | EPIC, VISION, JOURNEY | Swain-design decomposes into implementable children first; swain-do runs on the children, not the container |
| **Research** | SPIKE | Execution-tracking is optional but recommended for complex spikes with multiple investigation threads |
| **Reference** | ADR, PERSONA, RUNBOOK, DESIGN | No execution tracking expected |

### The `swain-do` frontmatter field

Artifacts that need swain-do carry `swain-do: required` in their frontmatter. This field is:
- **Always present** on SPEC and STORY artifacts (injected by their templates)
- **Added per-instance** on SPIKE artifacts when swain-design assesses the spike is complex enough to warrant tracked research
- **Never present** on EPIC, VISION, JOURNEY, ADR, PERSONA, RUNBOOK, or DESIGN artifacts — orchestration for those types lives in the skill, not the artifact

When an agent reads an artifact with `swain-do: required`, it should invoke the swain-do skill before beginning implementation work.

When implementation begins on a SPEC, swain-design should keep the lifecycle state aligned with the real work:
- If the SPEC is not already Active, transition it to Active before handing off implementation tracking.
- If that SPEC has a parent EPIC and the EPIC is not already Active, transition the parent EPIC to Active as well.
- Treat both transitions as idempotent: if either artifact is already Active, leave it unchanged.

### What "comes up for implementation" means

The trigger is intent, not phase transition alone. An artifact comes up for implementation when the user or workflow indicates they want to start building — not merely when its status changes.

- "Let's implement SPEC-003" → invoke swain-do
- "Move SPEC-003 to Approved" → phase transition only, no tracking yet
- "Fix SPEC-007 (type: bug)" → invoke swain-do
- "Let's work on EPIC-008" → decompose into SPECs/STORYs first, then track the children

### Coordination artifact decomposition

When swain-do is requested on an EPIC, VISION, or JOURNEY:

1. **Swain-design leads.** Decompose the artifact into implementable children (SPECs, STORYs) if they don't already exist.
2. **Swain-do follows.** Create tracked plans for the child artifacts, not the container.
3. **Swain-design monitors.** The container transitions (e.g., EPIC → Complete) based on child completion per the existing completion rules.

### STORY and SPEC coordination

Under the same parent Epic, Stories define user-facing requirements and Specs define technical implementations. They connect through shared `addresses` pain-point references and their common parent Epic. When creating swain-do plans, tag tasks with both `spec:SPEC-NNN` and `story:STORY-NNN` labels when a task satisfies both artifacts.

## GitHub Issues integration

SPECs link to GitHub Issues via the `source-issue` frontmatter field. During phase transitions on linked SPECs, post comments or close the issue. Read [references/github-issues-integration.md](references/github-issues-integration.md) for promotion workflow, transition hooks, and backend abstraction.

## Status overview

For project-wide status, progress, or "what's next?" queries, defer to the **swain-status** skill (it aggregates specgraph + tk + git + GitHub issues). For artifact-specific graph queries (blocks, tree, ready, mermaid), use `skills/swain-design/scripts/specgraph.sh` directly — see [skills/swain-design/references/specgraph-guide.md](skills/swain-design/references/specgraph-guide.md).

## Auditing artifacts

When the user requests an audit, read [references/auditing.md](references/auditing.md) for the full two-phase procedure (pre-scan + parallel audit agents including ADR compliance).

## Implementation plans

Implementation plans bridge declarative specs and execution tracking. When implementation begins, read [references/implementation-plans.md](references/implementation-plans.md) for TDD methodology, superpowers integration, plan workflow, and fallback procedures.

---

# Reference material

Consult these files when a workflow step references them:

- **Artifact relationships:** [references/relationship-model.md](references/relationship-model.md) — ER diagram of type hierarchy and cross-references
- **Lifecycle table format:** [references/lifecycle-format.md](references/lifecycle-format.md) — commit hash stamping convention
- **Index maintenance:** [references/index-maintenance.md](references/index-maintenance.md) — `list-<type>.md` refresh rules
- **Tooling:** Scripts live in `skills/swain-design/scripts/`. See [references/specwatch-guide.md](references/specwatch-guide.md), [references/specgraph-guide.md](references/specgraph-guide.md), [references/adr-check-guide.md](references/adr-check-guide.md) for details.

## Session bookmark

After state-changing operations, update the bookmark: `bash "$(find . .claude .agents -path '*/swain-session/scripts/swain-bookmark.sh' -print -quit 2>/dev/null)" "<action> <artifact-ids>" --files <paths>`
