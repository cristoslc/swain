---
name: swain-design
description: Create, validate, and transition documentation artifacts (Vision, Initiative, Epic, Spec, Spike, ADR, Persona, Runbook, Design, Journey) through lifecycle phases. Handles spec writing, feature planning, epic creation, initiative creation, ADR drafting, research spikes, persona definition, runbook creation, design capture, architecture docs, phase transitions, implementation planning, cross-reference validation, and audits. Also invoke to update frontmatter fields, re-parent an artifact under a different epic or initiative, or set priority on a Vision or Initiative. Chains into swain-do for implementation tracking on SPEC; decomposes EPIC/VISION/INITIATIVE/JOURNEY into children first.
license: UNLICENSED
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Skill
metadata:
  short-description: Manage spec artifact creation and lifecycle
  version: 1.7.0
  author: cristos
  source: swain
---

<!-- swain-model-hint: opus, effort: high — default for artifact creation; see per-section overrides below -->

# Spec Management

<!-- session-check: SPEC-121 -->
Before proceeding with any state-changing operation, check for an active session:
```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)" && bash "$REPO_ROOT/.agents/bin/swain-session-check.sh" 2>/dev/null
```
If the JSON output has `"status"` other than `"active"`, inform the operator: "No active session — start one with `/swain-init`?" Proceed if they dismiss.

This skill defines the canonical artifact types, phases, and hierarchy. Detailed definitions and templates live in `references/` (relative to this skill's directory). If the host repo has an AGENTS.md, keep its artifact sections in sync with the skill's reference data.

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
| Design (DESIGN-NNN) | Standing design document covering interaction (UI/UX), data architecture, or system contracts. Domain selected via `domain: interaction \| data \| system` frontmatter field. | [definition](references/design-definition.md) | [template](references/design-template.md.template) |
| Training Document (TRAIN-NNN) | Structured learning material (how-to, reference, quickstart) that teaches humans how to use a feature or workflow. Tracks alongside source artifacts via commit-pinned `linked-artifacts` for staleness detection. | [definition](references/train-definition.md) | [template](references/train-template.md.template) |

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
| Create training or documentation | **Train** | "how-to guide", "tutorial", "reference doc", "onboarding", "walkthrough", "training material", "teach someone" |

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
4. Run `bash "$(git rev-parse --show-toplevel 2>/dev/null || pwd)/.agents/bin/chart.sh" build` to refresh the graph cache
5. Commit the change

**Common updates:**
- `priority-weight` on Visions, Initiatives, Epics, and Specs — accepts `high`, `medium`, or `low`. Cascades: Vision → Initiative (can override) → Epic (can override) → Spec (can override). Affects downstream recommendation scoring and sibling sort order in `swain chart`.
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

1. Determine the next available number for the prefix by running:
   ```bash
   bash "$(git rev-parse --show-toplevel 2>/dev/null || pwd)/.agents/bin/next-artifact-id.sh" <PREFIX>
   ```
   This scans ALL local branches and the working tree to prevent ID collisions across worktree sessions (SPEC-193). If the script is unavailable, fall back to scanning `docs/<type>/` on the current HEAD — but note this risks collisions in worktree workflows.
2. **For VISION artifacts:** Before drafting, ask the user whether this is a **competitive product** or a **personal product**. The answer determines which template sections to include and shapes the entire downstream decomposition. See the vision definition for details on each product type.
2a. **For DESIGN artifacts:** First, ask which domain this design covers: `interaction` (UI/UX — screens, flows, states), `data` (data architecture — entities, schemas, flows, invariants), or `system` (system contracts — API boundaries, behavioral guarantees, integration interfaces). Default to `interaction` if unclear. Then prompt for Design Intent content — Context (one sentence anchoring the design to its purpose), Goals (what experience or guarantee we're trying to create), Constraints (reviewable boundaries), and Non-goals (what we explicitly decided not to do). This section is write-once: it is set at creation and not updated as the mutable sections evolve. Use the domain-specific template sections from the DESIGN template.
3. Read the artifact's definition file and template from the lookup table above.
4. Create the artifact in the correct phase subdirectory. Create the phase directory with `mkdir -p` if it doesn't exist yet. See the definition file for the exact directory structure.
5. Populate frontmatter with the required fields for the type (see the template).
6. Initialize the lifecycle table with the appropriate phase and current date, using this rule:
   - **User-requested → `Active`**: if the user explicitly asked for this artifact (e.g., "new SPIKE about X", "write a spec for Y"), create it directly in `Active`. The user has already decided they want this work — `Proposed` adds no value.
   - **Agent-suggested → `Proposed`**: if the agent creates the artifact on its own initiative (e.g., suggesting a SPIKE while the user asked for an EPIC, decomposing a Vision into child Epics), create it in `Proposed`. The user hasn't explicitly committed — `Proposed` signals "here's what I recommend, please confirm."
   - **Fully developed in-session → later phase**: an artifact may be created directly in a later phase if it was fully developed during the conversation (see [Phase skipping](#phase-skipping)).
6.5. **Hyperlink bare artifact ID references in body text** — after writing the artifact body, scan all text below the closing `---` frontmatter fence for bare artifact ID references matching the pattern `(SPEC|EPIC|INITIATIVE|VISION|SPIKE|ADR|PERSONA|RUNBOOK|DESIGN|JOURNEY|TRAIN)-[0-9]+`. For each bare ID that is:
   - **not** already inside a markdown link (`[...](...)`), and
   - **not** inside a code fence (`` ``` `` block) or inline code (`` ` ``backtick`` ` ``),

   resolve it with:
   ```bash
   bash "$(git rev-parse --show-toplevel 2>/dev/null || pwd)/.agents/bin/resolve-artifact-link.sh" <ARTIFACT-ID> <SOURCE-FILE>
   ```
   Replace the bare ID with `[ARTIFACT-ID](relative-path)`. If the script returns a non-zero exit code or empty output (artifact not found), leave the bare ID as-is — do not fail the operation. Frontmatter values must remain as plain IDs (YAML compatibility); only body text gets hyperlinks.
7. Validate parent references exist (e.g., the Epic referenced by a new Agent Spec must already exist).
7.5. **Same-type overlap check** — *(standing-track types only: DESIGN, Persona, Runbook)* scan `docs/<type>/Active/` for existing Active artifacts of the same type. Flag overlap if:
   - The new artifact's `linked-artifacts` references another artifact of the **same type** — this is a direct supersession signal.
   - The new artifact's scoping section (`Interaction Surface` for DESIGNs, `Trigger` for Runbooks, `Role` for Personas) describes a surface that overlaps with or subsumes an existing Active artifact's scope.
   If overlap is detected, ask the operator: "This overlaps with `<EXISTING-ID>` (`<title>`). Does the new artifact supersede it?" If yes, transition the existing artifact to Superseded (set `superseded-by`, update status, move to `Superseded/` directory, add lifecycle entry) as part of the same operation.
8. **ADR compliance check** — run `bash "$(git rev-parse --show-toplevel 2>/dev/null || pwd)/.agents/bin/adr-check.sh" <artifact-path>`. Review any findings with the user before proceeding.
8a. **Alignment check** — *(skip for fast-path tier)* run `bash "$(git rev-parse --show-toplevel 2>/dev/null || pwd)/.agents/bin/chart.sh" scope <artifact-id>` and assess per [references/alignment-checking.md](references/alignment-checking.md). Report blocking findings (MISALIGNED); note advisory ones (SCOPE_LEAK, GOAL_DRIFT) without gating the operation. When displaying scope chains or ancestry to the operator, use `artifact-context.sh` for each node to show plain-language names alongside IDs. Fall back to bare IDs if unavailable.
8b. **Unanchored check** — after validating parent references, check if the new artifact has a path to a Vision via parent edges. If not, warn: `⚠ No Vision ancestry — this artifact will appear as Unanchored in swain chart`. Offer to attach to an existing Initiative or Epic. Do not block creation.
9. **Post-operation scan** — *(skip for fast-path tier)* run `bash "$(git rev-parse --show-toplevel 2>/dev/null || pwd)/.agents/bin/specwatch.sh" scan`. This now also runs `design-check.sh` as part of the scan pipeline. Fix any stale references or design drift findings before committing.
10. **Index refresh step** — *(skip for fast-path tier; batch refresh at session end via `rebuild-index.sh`)* update `list-<type>.md` (see [Index maintenance](#index-maintenance)).

## Superpowers integration

When superpowers is installed, the following chains are **mandatory** — invoke the skills, do not skip them or do the work inline:

1. **Before creating Vision, Initiative, or Persona artifacts:** Invoke the `brainstorming` skill for Socratic exploration. Pass the artifact context (goals, audience, constraints). Capture brainstorming output into swain's artifact format with proper frontmatter and lifecycle table.

2. **When new feature work begins (brainstorming → artifacts → implementation):** Brainstorming explores the idea and produces a design doc. Brainstorming's terminal state is invoking **swain-design** to create formal artifacts (epic + specs). Then, for each SPEC coming up for implementation, invoke `writing-plans` per-spec. After `writing-plans` saves a plan file, invoke swain-do for plan ingestion. The chain is: brainstorming → **swain-design** → per-spec **writing-plans** → swain-do.

2b. **When an existing SPEC comes up for implementation (no brainstorming needed):** Invoke `writing-plans` with the SPEC's acceptance criteria and scope. After `writing-plans` saves a plan file, invoke swain-do for plan ingestion.

3. **For Testing → Implemented transitions:** Invoke `requesting-code-review` for spec compliance and code quality review (if the review skills are available).

**Detection:** `ls .agents/skills/brainstorming/SKILL.md .claude/skills/brainstorming/SKILL.md 2>/dev/null` — if at least one path exists, superpowers is available. Cache the result for the session.

Read [references/superpowers-integration.md](references/superpowers-integration.md) for thin SPEC format and full routing details. All integration is optional — swain functions fully without superpowers.

<!-- swain-model-hint: sonnet, effort: low — transitions are procedural -->
## Phase transitions

Phases are waypoints, not mandatory gates — artifacts may skip forward. Read [references/phase-transitions.md](references/phase-transitions.md) for phase skipping rules, the transition workflow (validate → move → commit → hash stamp), verification/review gates, and completion rules.

### Supersession specwatch-ignore maintenance

Whenever ANY artifact transitions to Superseded — whether via the phase transition workflow (step 5a in phase-transitions.md) or during artifact creation (same-type overlap detection) — append glob patterns to `.agents/specwatch-ignore` for the intentional backward references that the supersession creates. This prevents specwatch from flagging provenance links as warnings.

1. Create `.agents/specwatch-ignore` if it doesn't exist.
2. Append patterns for: (a) the superseded artifact path, (b) the superseding artifact path, (c) any ADR created as part of the same operation that references the superseded artifact.
3. Each entry gets a comment: `# <OLD-ID> superseded by <NEW-ID> (<YYYY-MM-DD>)`.
4. Deduplicate: skip patterns that already exist in the file.

```
# INITIATIVE-001 superseded by INITIATIVE-013 (2026-03-19)
docs/initiative/Superseded/(INITIATIVE-001)*
docs/initiative/Active/(INITIATIVE-013)*
```

This step runs **before** the back-reference update (step 5b) and specwatch scan (step 9 in the creation workflow, step 8 in phase-transitions.md) so the scan output is clean.

### Back-reference update on supersession

After specwatch-ignore maintenance (step 5a), update all non-terminal artifacts that reference the superseded artifact in frontmatter (`linked-artifacts`, `depends-on-artifacts`, `addresses`). See step 5b in [phase-transitions.md](references/phase-transitions.md) for the full procedure. Key points:

- **Check alignment before updating** — supersession often changes scope. Read the referencing artifact's context and compare against the successor. If the relationship doesn't hold for the successor, flag it for the operator instead of silently repointing.
- **Dedup** — if the successor is already in the list, remove the old entry instead of adding a duplicate.
- **Commit message provenance** — record what changed (e.g., "update EPIC-031 linked-artifacts: INITIATIVE-001 → INITIATIVE-013") so git history preserves the original reference.
- **Provenance links** from the superseding artifact itself go to specwatch-ignore, not rewritten.

### DESIGN lifecycle hooks

These hooks apply to DESIGN artifacts during phase transitions:

**On DESIGN creation:**
- Validate all `sourcecode-refs` paths exist at HEAD (if any are populated). Warn on broken paths before completing creation.

**On Proposed → Active transition:**
- Run `design-check.sh` on the DESIGN — all refs must be CURRENT.
- If any are STALE or BROKEN, warn the operator before completing the transition. Do not silently proceed with stale refs.

**On Active → Superseded transition:**
- The new (superseding) DESIGN should inherit `sourcecode-refs` from the old DESIGN with fresh pins via `--repin`.

### Decision protection hooks

These hooks are agent-level behavioral guidance — they are not enforced by scripts but by the agent following this skill file.

**SPEC Implementation transition:**
When a SPEC transitions to Implementation and has a linked DESIGN (via either side's `linked-artifacts` or `artifact-refs`):
- Surface the DESIGN's Design Intent section (Goals, Constraints, Non-goals) for alignment awareness. Present this to the operator so implementation stays within design boundaries.

**SPEC completion:**
When a SPEC completes and its implementation changed files tracked by a DESIGN's `sourcecode-refs`:
- Cross-reference changed files (from the SPEC's commits) against active DESIGNs' `sourcecode-refs`.
- If overlap is found: nudge the operator to update the DESIGN and re-pin via `design-check.sh --repin`.

**Alignment cascading:**
When an Epic has `artifact-refs` with `rel: [aligned]` pointing to a DESIGN:
- When child SPECs are created or modified, check scope against the DESIGN's Constraints and Non-goals.
- Traversal path: SPEC → parent EPIC → `artifact-refs` with `rel: [aligned]` → DESIGN → Design Intent.
- Only surface violations — silent pass for aligned SPECs.

**Design-to-code drift:**
When a DESIGN's mutable sections are modified but `sourcecode-refs` blobs haven't changed:
- Surface: "DESIGN-NNN evolved but tracked code hasn't caught up." Nudge the operator to reconcile.

### README reconciliation nudge

When transitioning a Vision, Design, Journey, or Persona to a new phase, emit a soft signal if the transition changes the project's public-facing claims:

> README.md may need updating to reflect this change.

This is informational, not blocking — the operator can dismiss it.

**Trigger conditions** — nudge when:
- A Vision transitions to Active (new direction) or Abandoned (dropped direction)
- A Design transitions to Active (new interaction model, data architecture, or system contract) or Superseded (replaced)
- A Journey transitions to Active (new user flow) or Abandoned (deprecated path)
- A Persona transitions to Active (new audience) or Abandoned (dropped audience)

**Brainstorming context** — when the `brainstorming` skill runs for a project that has a README but no artifacts (or a thin artifact tree — fewer than 3 Active Visions, Designs, Journeys, or Personas combined), it should use the README as the starting context for Socratic exploration. The README's claims, audience, and described behavior seed the brainstorming conversation instead of starting from scratch.

Detection for brainstorming context:
```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
ACTIVE_COUNT=$(find "$REPO_ROOT/docs" -path "*/Active/*" -name "*.md" 2>/dev/null | grep -cE "(VISION|DESIGN|JOURNEY|PERSONA)" || echo "0")
HAS_README=$( [ -f "$REPO_ROOT/README.md" ] && echo "yes" || echo "no" )
```
If `HAS_README=yes` and `ACTIVE_COUNT < 3`, pass README content to brainstorming as primary context.

## Trove integration

During research phase transitions (Spike Proposed -> Active, ADR Proposed -> Active, Vision/Epic creation), check for existing troves and offer to link or create one. Read [references/trove-integration.md](references/trove-integration.md) for the full hook, trove scanning, and back-link maintenance procedures.

## Execution tracking handoff

When implementation begins on a SPEC, invoke swain-do. Read [references/execution-tracking-handoff.md](references/execution-tracking-handoff.md) for the four-tier tracking model, `swain-do: required` frontmatter field, intent triggers, and coordination artifact decomposition.

## GitHub Issues integration

SPECs link to GitHub Issues via the `source-issue` frontmatter field. During phase transitions on linked SPECs, post comments or close the issue. Read [references/github-issues-integration.md](references/github-issues-integration.md) for promotion workflow, transition hooks, and backend abstraction.

<!-- swain-model-hint: sonnet, effort: low — status queries are data aggregation -->
## Status overview

For project-wide status, progress, or "what's next?" queries, defer to the **swain-session** skill (it aggregates swain chart + tk + git + GitHub issues). For artifact-specific graph queries, use `bash "$(git rev-parse --show-toplevel 2>/dev/null || pwd)/.agents/bin/chart.sh"` — see [references/specgraph-guide.md](references/specgraph-guide.md). The default output is a vision-rooted hierarchy tree; lenses (`ready`, `recommend`, `debt`, `unanchored`, etc.) filter and annotate the tree for different decision contexts.

<!-- swain-model-hint: opus, effort: high — audits require deep cross-artifact analysis -->
## Auditing artifacts

When the user requests an audit, read [references/auditing.md](references/auditing.md) for the full two-phase procedure (pre-scan + parallel audit agents including ADR compliance). Include an **unanchored check** pass: run `bash "$(git rev-parse --show-toplevel 2>/dev/null || pwd)/.agents/bin/chart.sh" unanchored` and report any artifacts without Vision ancestry as domain-level findings alongside alignment and ADR compliance results.

## Implementation plans

Implementation plans bridge declarative specs and execution tracking. When implementation begins, read [references/implementation-plans.md](references/implementation-plans.md) for TDD methodology, superpowers integration, plan workflow, and fallback procedures.

---

# Reference material

Consult these files when a workflow step references them:

- **Artifact relationships:** [references/relationship-model.md](references/relationship-model.md) — ER diagram of type hierarchy and cross-references
- **Lifecycle table format:** [references/lifecycle-format.md](references/lifecycle-format.md) — commit hash stamping convention
- **Index maintenance:** [references/index-maintenance.md](references/index-maintenance.md) — `list-<type>.md` refresh rules
- **Tooling:** Scripts live in `scripts/` (relative to this skill's directory). See [references/specwatch-guide.md](references/specwatch-guide.md), [references/specgraph-guide.md](references/specgraph-guide.md), [references/adr-check-guide.md](references/adr-check-guide.md) for details.

## Session bookmark

After state-changing operations, update the bookmark: `bash "$(git rev-parse --show-toplevel 2>/dev/null || pwd)/.agents/bin/swain-bookmark.sh" "<action> <artifact-ids>" --files <paths>`
