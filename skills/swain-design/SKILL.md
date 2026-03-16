---
name: swain-design
description: Create, validate, and transition documentation artifacts (Vision, Initiative, Epic, Spec, Spike, ADR, Persona, Runbook, Design, Journey) through lifecycle phases. Handles spec writing, feature planning, epic creation, initiative creation, ADR drafting, research spikes, persona definition, runbook creation, design capture, architecture docs, phase transitions, implementation planning, cross-reference validation, and audits. Chains into swain-do for implementation tracking on SPEC; decomposes EPIC/VISION/INITIATIVE/JOURNEY into children first.
license: UNLICENSED
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Skill
metadata:
  short-description: Manage spec artifact creation and lifecycle
  version: 1.6.0
  author: cristos
  source: swain
---

<!-- swain-model-hint: opus, effort: high — default for artifact creation; see per-section overrides below -->

# Spec Management

This skill defines the canonical artifact types, phases, and hierarchy. Detailed definitions and templates live in `skills/swain-design/references/`. If the host repo has an AGENTS.md, keep its artifact sections in sync with the skill's reference data.

## Artifact type definitions

Each artifact type has a definition file (lifecycle phases, conventions, folder structure) and a template (frontmatter fields, document skeleton). **Read the definition for the artifact type you are creating or transitioning.**

| Type | What it is | Definition | Template |
|------|-----------|-----------|----------|
| Product Vision (VISION-NNN) | Top-level product direction — goals, audience, and success metrics for a competitive or personal product. | [definition](references/vision-definition.md) | [template](references/vision-template.md.template) |
| Initiative (INITIATIVE-NNN) | Strategic grouping of Epics under a Vision — provides a mid-level container for prioritization and decision tracking. | [definition](references/initiative-definition.md) | [template](references/initiative-template.md.template) |
| User Journey (JOURNEY-NNN) | End-to-end user workflow with pain points that drive epics and specs. | [definition](references/journey-definition.md) | [template](references/journey-template.md.template) |
| Epic (EPIC-NNN) | Large deliverable under a vision or initiative — groups related specs with success criteria. | [definition](references/epic-definition.md) | [template](references/epic-template.md.template) |
| Agent Spec (SPEC-NNN) | Technical implementation specification with acceptance criteria. Supports `type: feature \| enhancement \| bug`. Parent epic is optional. | [definition](references/spec-definition.md) | [template](references/spec-template.md.template) |
| Research Spike (SPIKE-NNN) | Time-boxed investigation with a specific question and completion gate. | [definition](references/spike-definition.md) | [template](references/spike-template.md.template) |
| Persona (PERSONA-NNN) | Archetypal user profile that informs journeys and specs. | [definition](references/persona-definition.md) | [template](references/persona-template.md.template) |
| ADR (ADR-NNN) | Single architectural decision — context, choice, alternatives, and consequences (Nygard format). | [definition](references/adr-definition.md) | [template](references/adr-template.md.template) |
| Runbook (RUNBOOK-NNN) | Step-by-step operational procedure (agentic or manual) with a defined trigger. | [definition](references/runbook-definition.md) | [template](references/runbook-template.md.template) |
| Design (DESIGN-NNN) | UI/UX interaction design — wireframes, flows, and state diagrams for user-facing surfaces. | [definition](references/design-definition.md) | [template](references/design-template.md.template) |

## Choosing the right artifact type

When the user's request doesn't name a specific type, infer it from their intent:

| User intent | Artifact | Signal words |
|-------------|----------|-------------|
| Product direction, why we exist | **Vision** | "product direction", "what should we build", "north star" |
| Strategic direction, group related work | **Initiative** | "focus on", "security effort", "group these epics", "strategic", "track" |
| Ship a feature or deliverable | **Epic** | "build X", "add Y feature", "implement Z" |
| One implementation unit | **Spec** | "fix this", "add a flag", "refactor", "small change", "bug" |
| Research question | **Spike** | "should we", "investigate", "compare options", "what's the best way" |
| Record a decision | **ADR** | "decided to", "choosing between", "why did we" |

**Initiative vs Epic** — the key distinction:
- **Initiative**: a *direction* with multiple deliverables. "Harden security" is an initiative — it spans scanning, gates, policies. The operator steers it.
- **Epic**: a *deliverable* with multiple specs. "Build the scanning tool" is an epic — it has clear completion criteria. Agents execute it.
- **Rule of thumb**: if the work needs 2+ epics to describe, it's an Initiative. If it needs 2+ specs, it's an Epic. If it's one spec, just create the spec.

**Spec under Initiative (small work path)** — bugs, minor enhancements, and chores that relate to an Initiative's direction but don't warrant an Epic can attach directly to the Initiative via `parent-initiative`. If small work clusters, suggest promoting it to an Epic.

## Updating artifact metadata

When the operator asks to update a field on an existing artifact (e.g., "set VISION-001 priority to high", "re-parent EPIC-017 under INITIATIVE-001"):

1. Read the artifact's definition file to confirm the field name and valid values
2. Edit the frontmatter field directly (e.g., `priority-weight: high`)
3. Update the `last-updated` date
4. Run `bash skills/swain-design/scripts/chart.sh build` to refresh the graph cache
5. Commit the change

**Common updates:**
- `priority-weight` on Visions, Initiatives, and Epics — accepts `high`, `medium`, or `low`. Cascades: Vision → Initiative (can override) → Epic (can override) → Spec (inherits nearest). Affects downstream recommendation scoring and sibling sort order in `swain chart`.
- `parent-initiative` on Epics and Specs — re-parents them under an Initiative. A Spec can have `parent-epic` OR `parent-initiative`, never both.
- `parent-vision` on Initiatives — attaches to a Vision.

When the operator says "priority" or "weight" in the context of a Vision or Initiative, they mean the `priority-weight` frontmatter field.

## Creating artifacts

### Error handling

When an operation fails (missing parent, number collision, script error, etc.), consult [references/troubleshooting.md](references/troubleshooting.md) for the recovery procedure. Do not improvise workarounds — the troubleshooting guide covers the known failure modes.

### Complexity tier detection (SPEC-045)

Before running the full authoring ceremony, classify the artifact into a complexity tier:

**Low complexity (fast-path eligible)**:
- SPEC with `type: bug` or `type: fix` and no `parent-epic` and no downstream `depends-on` links
- SPIKE with no `parent-epic`
- Any artifact where the user uses language like "quick", "simple", "trivial", or "fast"

**Medium/High complexity (full ceremony)**:
- Feature SPECs (`type: feature`)
- Any SPEC or SPIKE with a `parent-epic`
- EPICs, INITIATIVEs, Visions, Journeys, ADRs — always full ceremony
- Any artifact where the user describes significant architectural decisions

When fast-path applies, output: `[fast-path] Skipped: specwatch scan, scope check, index update`

### Workflow

1. Scan `docs/<type>/` (recursively, across all phase subdirectories) to determine the next available number for the prefix.
2. **For VISION artifacts:** Before drafting, ask the user whether this is a **competitive product** or a **personal product**. The answer determines which template sections to include and shapes the entire downstream decomposition. See the vision definition for details on each product type.
3. Read the artifact's definition file and template from the lookup table above.
4. Create the artifact in the correct phase subdirectory. Create the phase directory with `mkdir -p` if it doesn't exist yet. See the definition file for the exact directory structure.
5. Populate frontmatter with the required fields for the type (see the template).
6. Initialize the lifecycle table with the appropriate phase and current date, using this rule:
   - **User-requested → `Active`**: if the user explicitly asked for this artifact (e.g., "new SPIKE about X", "write a spec for Y"), create it directly in `Active`. The user has already decided they want this work — `Proposed` adds no value.
   - **Agent-suggested → `Proposed`**: if the agent creates the artifact on its own initiative (e.g., suggesting a SPIKE while the user asked for an EPIC, decomposing a Vision into child Epics), create it in `Proposed`. The user hasn't explicitly committed — `Proposed` signals "here's what I recommend, please confirm."
   - **Fully developed in-session → later phase**: an artifact may be created directly in a later phase if it was fully developed during the conversation (see [Phase skipping](#phase-skipping)).
7. Validate parent references exist (e.g., the Epic referenced by a new Agent Spec must already exist).
8. **ADR compliance check** — run `skills/swain-design/scripts/adr-check.sh <artifact-path>`. Review any findings with the user before proceeding.
8a. **Alignment check** — *(skip for fast-path tier)* run `bash skills/swain-design/scripts/chart.sh scope <artifact-id>` and assess per [skills/swain-design/references/alignment-checking.md](skills/swain-design/references/alignment-checking.md). Report blocking findings (MISALIGNED); note advisory ones (SCOPE_LEAK, GOAL_DRIFT) without gating the operation.
8b. **Unanchored check** — after validating parent references, check if the new artifact has a path to a Vision via parent edges. If not, warn: `⚠ No Vision ancestry — this artifact will appear as Unanchored in swain chart`. Offer to attach to an existing Initiative or Epic. Do not block creation.
9. **Post-operation scan** — *(skip for fast-path tier)* run `skills/swain-design/scripts/specwatch.sh scan`. Fix any stale references before committing.
10. **Index refresh step** — *(skip for fast-path tier; batch refresh at session end via `rebuild-index.sh`)* update `list-<type>.md` (see [Index maintenance](#index-maintenance)).

## Superpowers integration

When superpowers is installed, the following chains are **mandatory** — invoke the skills, do not skip them or do the work inline:

1. **Before creating Vision, Initiative, or Persona artifacts:** Invoke the `brainstorming` skill for Socratic exploration. Pass the artifact context (goals, audience, constraints). Capture brainstorming output into swain's artifact format with proper frontmatter and lifecycle table.

2. **When a SPEC comes up for implementation:** Invoke `brainstorming` with the SPEC's acceptance criteria and scope. Brainstorming chains into `writing-plans` automatically. After `writing-plans` saves a plan file, invoke swain-do for plan ingestion.

3. **For Testing → Implemented transitions:** Invoke `requesting-code-review` for spec compliance and code quality review (if the review skills are available).

**Detection:** `ls .agents/skills/brainstorming/SKILL.md .claude/skills/brainstorming/SKILL.md 2>/dev/null` — if at least one path exists, superpowers is available. Cache the result for the session.

Read [references/superpowers-integration.md](references/superpowers-integration.md) for thin SPEC format and full routing details. All integration is optional — swain functions fully without superpowers.

<!-- swain-model-hint: sonnet, effort: low — transitions are procedural -->
## Phase transitions

Phases are waypoints, not mandatory gates — artifacts may skip forward. Read [references/phase-transitions.md](references/phase-transitions.md) for phase skipping rules, the transition workflow (validate → move → commit → hash stamp), verification/review gates, and completion rules.

## Trove integration

During research phase transitions (Spike Proposed -> Active, ADR Proposed -> Active, Vision/Epic creation), check for existing troves and offer to link or create one. Read [references/trove-integration.md](references/trove-integration.md) for the full hook, trove scanning, and back-link maintenance procedures.

## Execution tracking handoff

When implementation begins on a SPEC, invoke swain-do. Read [references/execution-tracking-handoff.md](references/execution-tracking-handoff.md) for the four-tier tracking model, `swain-do: required` frontmatter field, intent triggers, and coordination artifact decomposition.

## GitHub Issues integration

SPECs link to GitHub Issues via the `source-issue` frontmatter field. During phase transitions on linked SPECs, post comments or close the issue. Read [references/github-issues-integration.md](references/github-issues-integration.md) for promotion workflow, transition hooks, and backend abstraction.

<!-- swain-model-hint: sonnet, effort: low — status queries are data aggregation -->
## Status overview

For project-wide status, progress, or "what's next?" queries, defer to the **swain-status** skill (it aggregates swain chart + tk + git + GitHub issues). For artifact-specific graph queries, use `bash skills/swain-design/scripts/chart.sh` — see [skills/swain-design/references/specgraph-guide.md](skills/swain-design/references/specgraph-guide.md). The default output is a vision-rooted hierarchy tree; lenses (`ready`, `recommend`, `debt`, `unanchored`, etc.) filter and annotate the tree for different decision contexts.

<!-- swain-model-hint: opus, effort: high — audits require deep cross-artifact analysis -->
## Auditing artifacts

When the user requests an audit, read [references/auditing.md](references/auditing.md) for the full two-phase procedure (pre-scan + parallel audit agents including ADR compliance). Include an **unanchored check** pass: run `bash skills/swain-design/scripts/chart.sh unanchored` and report any artifacts without Vision ancestry as domain-level findings alongside alignment and ADR compliance results.

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
