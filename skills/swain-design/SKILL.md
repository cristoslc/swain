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

This skill defines the canonical artifact types, phases, and hierarchy. Detailed definitions and templates live in `references/`. If the host repo has an AGENTS.md, keep its artifact sections in sync with the skill's reference data.

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
8. **ADR compliance check** — run `scripts/adr-check.sh <artifact-path>`. Review any findings with the user before proceeding.
8a. **Alignment check** — run `scripts/specgraph.sh scope <artifact-id>` and assess per [references/alignment-checking.md](references/alignment-checking.md). Report blocking findings (MISALIGNED); note advisory ones (SCOPE_LEAK, GOAL_DRIFT) without gating the operation.
9. **Post-operation scan** — run `scripts/specwatch.sh scan`. Fix any stale references before committing.
10. **Index refresh step** — update `list-<type>.md` (see [Index maintenance](#index-maintenance)).

## Superpowers integration

When superpowers (obra/superpowers) is installed alongside swain, certain artifact creation and transition workflows are modified. All integration is optional — swain functions fully without superpowers.

### Detection

Check whether superpowers skills exist:

```bash
ls .claude/skills/brainstorming/SKILL.md .agents/skills/brainstorming/SKILL.md .claude/skills/writing-plans/SKILL.md .agents/skills/writing-plans/SKILL.md 2>/dev/null
```

If at least one path exists for each skill, superpowers is available. Cache the result for the session — don't re-check on every operation.

### Brainstorming routing

When superpowers is detected AND a new artifact is being created, route through Socratic brainstorming for specific types:

| Artifact type | Brainstorming? | Rationale |
|---------------|---------------|-----------|
| **Vision** | Yes — full Socratic | Visions benefit from deep interrogation of goals, audience, and success metrics |
| **Persona** | Yes — full Socratic | Personas need probing to avoid shallow archetypes |
| **Epic** | Quick draft first, then offer | Epics often have enough context from their parent Vision |
| **Story** | No | Stories are derived from Epics/Journeys — the thinking already happened |
| **Spike** | No | Spikes define a question, not a design — brainstorming adds overhead |
| **ADR** | No | ADRs record a decision already made, not discover one |
| **SPEC** | No | SPECs capture decisions made at Epic/Vision level |
| **Bug, Runbook, Design, Journey** | No | Structured templates are sufficient |

When brainstorming is used, the output is still captured into swain's artifact format with proper frontmatter, lifecycle table, and parent references. Superpowers drives the conversation; swain owns the output structure.

### Thin SPEC format

When superpowers is detected, SPECs omit the "Implementation Approach" section. SPECs become thin contracts: acceptance criteria, scope, dependencies, ADR links, and verification gate. The detailed execution plan is generated by superpowers' `writing-plans` skill at implementation time, not stored in the SPEC.

When superpowers is NOT detected, SPECs retain the "Implementation Approach" section as the primary planning surface.

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
4. **ADR compliance check** — for transitions to active phases (Active, Approved, Ready, Implemented, Adopted), run `scripts/adr-check.sh <artifact-path>`. Review any findings with the user before committing.
4c. **Alignment check** — for transitions to active phases (Active, Approved, Ready, Adopted), run `scripts/specgraph.sh scope <artifact-id>` and assess per [references/alignment-checking.md](references/alignment-checking.md). Skip for backward-looking transitions (Testing, Implemented, Complete) unless content changed since last check. Skip for terminal-phase transitions (Abandoned, Retired, Superseded).
4a. **Verification gate (SPEC only)** — for `Testing → Implemented` transitions, run `scripts/spec-verify.sh <artifact-path>`. The script checks that every acceptance criterion has documented evidence in the Verification table. Address gaps before proceeding. See `spec-definition.md § Testing phase` for details.
4b. **Code review gate (SPEC only)** — for `Testing → Implemented` transitions, when superpowers' code review skills are available (`ls .claude/skills/requesting-code-review/SKILL.md .agents/skills/requesting-code-review/SKILL.md .claude/skills/receiving-code-review/SKILL.md .agents/skills/receiving-code-review/SKILL.md 2>/dev/null`), request both a spec compliance review (checking implementation against acceptance criteria) and a code quality review. If superpowers review skills are not available, this step is skipped — it is not a hard gate.
5. Commit the transition change (move + status update).
6. Append a row to the artifact's lifecycle table with the commit hash from step 5.
7. Commit the hash stamp as a **separate commit** — never amend. Two distinct commits keeps the stamped hash reachable in git history and avoids interactive-rebase pitfalls.
8. **Post-operation scan** — run `scripts/specwatch.sh scan`. Fix any stale references.
9. **Index refresh step** — move the artifact's row to the new phase table (see [Index maintenance](#index-maintenance)).

### Completion rules

- An Epic is "Complete" only when all child Agent Specs are "Implemented" and success criteria are met.
- An Agent Spec is "Implemented" only when its implementation plan is closed (or all tasks are done in fallback mode) **and** its Verification table confirms all acceptance criteria pass (enforced by `spec-verify.sh`).
- An ADR is "Superseded" only when the superseding ADR is "Adopted" and links back.

## Evidence pool integration

When research-heavy artifacts enter their active/research phase, check for existing evidence pools and offer to create or reuse one.

### Research phase hook

This hook fires during phase transitions for these artifact types:

| Artifact | Trigger phase | When to check |
|----------|--------------|---------------|
| **Spike** | Planned → Active | Investigation is starting — evidence is most valuable here |
| **ADR** | Draft → Proposed | Decision needs supporting evidence |
| **Vision** | At creation | Market research and landscape analysis |
| **Epic** | At creation or Proposed → Active | Scoping benefits from prior research |

When the trigger fires:

1. Scan `docs/evidence-pools/*/manifest.yaml` for pools whose tags overlap with the artifact's topic (infer tags from the artifact title, keywords, and linked artifacts).
2. If matching pools exist, present them:
   > Found N evidence pool(s) that may be relevant:
   > - `websocket-vs-sse` (5 sources, refreshed 2026-03-01) — tags: real-time, websocket, sse
   >
   > Link an existing pool, create a new one, or skip?
3. If no matches: "No existing evidence pools match this topic. Want to create one with swain-search?"
4. If the user wants a pool, invoke the **swain-search** skill (via the Skill tool) to create or extend one.
5. After the pool is committed, update the artifact's `evidence-pool` frontmatter field with `<pool-id>@<commit-hash>`.

### Back-link maintenance

When an artifact's `evidence-pool` frontmatter is set or changed:

1. Read the pool's `manifest.yaml`
2. Add or update the `referenced-by` entry for this artifact:
   ```yaml
   referenced-by:
     - artifact: SPIKE-001
       commit: abc1234
   ```
3. Write the updated manifest

This keeps the pool's manifest in sync with which artifacts depend on it. Back-links enable evidencewatch to detect when a pool is no longer referenced and can be archived.

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

SPECs can be linked to GitHub Issues via the `source-issue` frontmatter field. This enables bidirectional sync between swain's artifact workflow and GitHub's issue tracker.

### Promoting an issue to a SPEC

When the user wants to turn a GitHub issue into a SPEC:

1. Run `scripts/issue-integration.sh check` to verify `gh` CLI availability.
2. Run `scripts/issue-integration.sh promote <issue-url-or-ref>` to fetch issue data as JSON.
3. Create a new SPEC using the standard creation workflow, populating:
   - `source-issue: github:<owner>/<repo>#<number>` in frontmatter
   - Problem Statement from the issue body
   - Title from the issue title

Accepted reference formats:
- `github:<owner>/<repo>#<number>` (canonical)
- `https://github.com/<owner>/<repo>/issues/<number>` (URL, converted automatically)

### Transition hooks

During phase transitions on SPECs with a `source-issue` field, post notifications to the linked issue:

| Transition target | Action | Script command |
|-------------------|--------|---------------|
| Testing | Post comment | `issue-integration.sh transition-comment <source-issue> <artifact-id> Testing` |
| Implemented | Close issue | `issue-integration.sh transition-close <source-issue> <artifact-id>` |
| Abandoned | Post comment (do NOT close) | `issue-integration.sh transition-comment <source-issue> <artifact-id> Abandoned` |
| Other phases | Post comment | `issue-integration.sh transition-comment <source-issue> <artifact-id> <phase>` |

If `gh` CLI is unavailable, log a warning and continue the transition — issue sync is best-effort, not a gate.

### Backend abstraction

The `source-issue` value uses URL-prefix dispatch: `github:` routes to the GitHub backend (`gh` CLI). Future backends (Linear, Jira) would add new prefixes and implement the same operations: `promote`, `comment`, `close`. Core swain-design logic does not change when a backend is added.

## Status overview

For project-wide status, progress, or "what's next?" queries, defer to the **swain-status** skill (it aggregates specgraph + tk + git + GitHub issues). For artifact-specific graph queries (blocks, tree, ready, mermaid), use `scripts/specgraph.sh` directly — see [references/specgraph-guide.md](references/specgraph-guide.md).

## Auditing artifacts

When the user requests an audit, read [references/auditing.md](references/auditing.md) for the full two-phase procedure (pre-scan + parallel audit agents including ADR compliance).

## Implementation plans

Implementation plans bridge declarative specs and execution tracking. When implementation begins, read [references/implementation-plans.md](references/implementation-plans.md) for TDD methodology, superpowers integration, plan workflow, and fallback procedures.

---

# Reference material

The sections below define formats and rules referenced by the workflows above. Consult them when a workflow step points here.

## Artifact relationship model

```mermaid
erDiagram
    VISION ||--o{ EPIC : "parent-vision"
    VISION ||--o{ JOURNEY : "parent-vision"
    EPIC ||--o{ SPEC : "parent-epic"
    EPIC ||--o{ STORY : "parent-epic"
    JOURNEY ||--|{ PAIN_POINT : "PP-NN"
    PAIN_POINT }o--o{ EPIC : "addresses"
    PAIN_POINT }o--o{ SPEC : "addresses"
    PAIN_POINT }o--o{ STORY : "addresses"
    PERSONA }o--o{ JOURNEY : "linked-personas"
    PERSONA }o--o{ STORY : "linked-stories"
    ADR }o--o{ SPEC : "linked-adrs"
    ADR }o--o{ EPIC : "linked-epics"
    SPEC }o--o{ SPIKE : "linked-research"
    SPEC ||--o| IMPL_PLAN : "seeds"
    RUNBOOK }o--o{ EPIC : "validates"
    RUNBOOK }o--o{ SPEC : "validates"
    SPIKE }o--o{ ADR : "linked-research"
    SPIKE }o--o{ EPIC : "linked-research"
    DESIGN }o--o{ EPIC : "linked-designs"
    DESIGN }o--o{ STORY : "linked-designs"
    DESIGN }o--o{ SPEC : "linked-designs"
```

**Key:** Solid lines (`||--o{`) = mandatory hierarchy. Diamond lines (`}o--o{`) = informational cross-references. SPIKE can attach to any artifact type, not just SPEC. Any artifact can declare `depends-on:` blocking dependencies on any other artifact. Per-type frontmatter fields are defined in each type's template.

## Tooling

Scripts support artifact workflows. Each is in `scripts/` relative to this skill.

| Script | Default command | Purpose |
|--------|----------------|---------|
| `specwatch.sh` | `scan` | Stale reference detection + artifact/tk sync check. Run after every artifact operation. If `.agents/specwatch.log` reports issues, fix before committing. For log format and subcommands, read [references/specwatch-guide.md](references/specwatch-guide.md). |
| `specgraph.sh` | `overview` | Knowledge graph — hierarchy tree, alignment scope, impact analysis. Subcommands: `overview`, `scope`, `impact`, `neighbors`, `edges`, `blocks`, `blocked-by`, `tree`, `ready`, `next`, `mermaid`, `status`. For full reference, read [references/specgraph-guide.md](references/specgraph-guide.md). |
| `adr-check.sh` | `<artifact-path>` | ADR compliance — checks artifact against Adopted ADRs for relevance, dead refs to Retired/Superseded ADRs, and staleness. Exit 0 = clean, exit 1 = findings. If findings, read [references/adr-check-guide.md](references/adr-check-guide.md) for interpretation and content-level review procedure. |
| `spec-verify.sh` | `<artifact-path>` | Verification gate — checks a Spec's Verification table against its Acceptance Criteria. Gates `Testing → Implemented`. Exit 0 = all criteria covered, exit 1 = gaps or failures found, exit 2 = usage error. |
| `issue-integration.sh` | `check` | GitHub Issues integration — promote issues to SPECs, post transition comments, auto-close on Implemented. Backend-abstracted via URL prefix dispatch. |

## Lifecycle table format

Every artifact embeds a lifecycle table tracking phase transitions:

```markdown
### Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-02-24 | abc1234 | Initial creation |
| Active  | 2026-02-25 | def5678 | Dependency X satisfied |
```

Commit hashes reference the repo state at the time of the transition, not the commit that writes the hash stamp itself. Commit the transition first, then stamp the resulting hash into the lifecycle table and index in a second commit. This keeps the stamped hash reachable in git history.

## Index maintenance

Every doc-type directory keeps a single lifecycle index (`list-<type>.md`). **Refreshing the index is the final step of every artifact operation** — creation, content edits, phase transitions, and abandonment. No artifact change is complete until the index reflects it.

### What "refresh" means

1. Read (or create) `docs/<type>/list-<type>.md`.
2. Ensure one table per active lifecycle phase, plus a table for each end-of-life phase that has entries.
3. For the affected artifact, update its row: title, current phase, last-updated date, and commit hash of the change.
4. If the artifact moved phases, remove it from the old phase table and add it to the new one.
5. Sort rows within each table by artifact number.

### When to refresh

| Operation | Trigger |
|-----------|---------|
| Create artifact | New row in the appropriate phase table |
| Edit artifact content or frontmatter | Update last-updated date and commit hash |
| Transition phase | Move row between phase tables |
| Abandon / end-of-life | Move row to the end-of-life table |

## Session bookmark

After completing any state-changing operation (creating, transitioning, or updating artifacts), update the session bookmark via `swain-bookmark.sh`:

```bash
BOOKMARK="$(find . .claude .agents -path '*/swain-session/scripts/swain-bookmark.sh' -print -quit 2>/dev/null)"
bash "$BOOKMARK" "Transitioned SPEC-001 to Approved, created EPIC-002" --files docs/spec/...
```

- Note format: "{action} {artifact-ids}"
- Include changed artifact file paths via `--files`
