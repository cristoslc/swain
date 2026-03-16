---
title: "Vision-Rooted Chart Hierarchy"
artifact: SPEC-052
track: implementable
status: Active
author: cristos
created: 2026-03-15
last-updated: 2026-03-15
type: feature
parent-epic: ""
parent-initiative: INITIATIVE-005
linked-artifacts:
  - EPIC-018
  - EPIC-013
  - SPIKE-021
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# Vision-Rooted Chart Hierarchy

## Problem Statement

Specgraph and swain-session present artifact data through multiple disconnected views — flat lists, dependency closures, summary tables — none of which consistently show how work traces back to a Vision. The operator's primary question is "which Epic should I move forward?" but the tooling answers "here's a flat list of ready specs." Artifacts without Vision ancestry appear in a neutral "Unparented" section rather than being flagged as unanchored work. The result: the operator must mentally reconstruct the hierarchy to make strategic decisions, and orphaned work goes unnoticed.

## External Behavior

### New command: `swain chart`

`swain chart` is the single entry point for all artifact graph queries, subsuming the current `specgraph` CLI. It presents a vision-rooted hierarchy tree as its default output, with lenses that filter and annotate the tree for different decision contexts.

#### Priority-weight cascade

The `priority-weight` field (high/medium/low) currently exists on Visions and Initiatives. This spec extends it to **Epics**, so epics within the same initiative can be sorted by priority. The cascade becomes:

Vision → Initiative (can override) → Epic (can override) → Spec (inherits)

When an Epic has no `priority-weight`, it inherits from its parent Initiative or Vision. When set, the Epic's weight is used for itself and its children. This enables the operator to say "within Operator Situational Awareness, do Vision-Rooted Chart Hierarchy before Postflight Summaries."

Changes required: epic definition and template updated to include optional `priority-weight` field; `priority.py` updated to check Epic level in the cascade.

#### Core display

Every artifact traces its parent edges up to a Vision root. Titles are the primary label; IDs are hidden by default (`--ids` to show). Status icons prefix the title. A legend appears at the bottom.

```
Swain                                                 high
├── Operator Situational Awareness                    high
│   ├── → Vision-Rooted Hierarchy Display             2 specs
│   └── ⊘ Worktree-Aware Session Bookmarks            3 specs, 1 blocked
├── Security & Trust                                  medium
│   └── · Security Gates in swain-do                  1 spec
└── Multi-Agent Orchestration                         medium

=== Inbox ===
#47  Add --dry-run to swain-sync
#52  tk crash on circular deps

=== Unanchored ===
⚠ Evaluate alternative TUI frameworks [no Vision ancestry]

---
→ ready   ⊘ blocked   · in progress   ✓ complete (hidden by default)
```

Intermediate ancestors (Initiatives, Epics) are included for structural completeness even if they weren't in the lens's result set; these render without annotations (dimmed/muted). When an intermediate level is missing (e.g., Spec directly under Initiative, no Epic), the tree flattens — showing the direct connection.

#### Depth control

Depth is numeric. Default is 2 (Vision = 0, Initiative = 1, Epic = 2). At default depth, Epics are leaf nodes annotated with child counts (e.g., `3 specs, 1 spike`). Higher depth values drill into Specs, Spikes, Designs, etc.

Depth defaults:
- **Strategic depth** = 2 (Vision → Initiative → Epic). Used when the operator is choosing *what* to prioritize.
- **Execution depth** = 4 (full tree to Specs, Spikes, Designs). Used when the operator is checking *how* a chosen Epic is progressing.

Depth precedence (highest wins):
1. `--depth N` — explicit flag, always wins
2. Focus lane — if `swain-session` focus is set, use execution depth (4); if unset, use strategic depth (2)
3. Command default — each lens defines a sensible default (see Lenses table)

`--detail` is an alias for `--depth 4` (execution depth).

#### Phase filtering

- `--phase active,ready` — include only artifacts in these phases
- `--hide-terminal` — shorthand: exclude Complete, Abandoned, Superseded, etc.
- Default: hide terminal-phase artifacts (override with `--all`)

#### Lenses

Lenses define which nodes to include, how to annotate them, their sort order, and their default depth. Sort order is lens-dependent — siblings at each level are ordered by the lens's metric, not alphabetically.

| Lens | Node selection | Annotation | Sort | Default mode |
|------|---------------|------------|------|-------------|
| *(none / default)* | All non-terminal | Status icon (→ ⊘ · ✓) | alphabetical | strategic |
| `ready` | Unblocked artifacts | → marker | by unblock count | execution |
| `recommend` | Scored by priority × unblock count | score | by score desc | strategic |
| `attention` | Per-vision git activity summary (reuses existing `attention.py` per-vision computation) | commit count, last touch per vision | by recency | strategic |
| `debt` | Unresolved decisions (Proposed Spikes/ADRs/Epics) | age in days | by age desc | strategic |
| `unanchored` | Artifacts with no Vision ancestry | ⚠ marker | alphabetical | strategic |
| `status` | All, grouped by phase | phase label | by phase progression | strategic |

Vision-level nodes are also sorted by the lens metric (e.g., `recommend` surfaces the Vision with the highest-scoring descendants first).

#### Subsumed specgraph commands

`swain chart` replaces the `specgraph` CLI entirely. Low-level queries remain as subcommands:

| Old command | New command | Notes |
|-------------|------------|-------|
| `specgraph overview` | `swain chart` | Default behavior |
| `specgraph ready` | `swain chart ready` | Now tree-rooted |
| `specgraph next` | `swain chart ready --detail` | Ready + what they'd unblock |
| `specgraph recommend` | `swain chart recommend` | Now tree-rooted |
| `specgraph status` | `swain chart status` | Now tree-rooted |
| `specgraph decision-debt` | `swain chart debt` | Now tree-rooted |
| `specgraph attention` | `swain chart attention` | Now tree-rooted |
| `specgraph blocks <ID>` | `swain chart blocks <ID>` | Unchanged |
| `specgraph blocked-by <ID>` | `swain chart blocked-by <ID>` | Unchanged |
| `specgraph tree <ID>` | `swain chart deps <ID>` | Renamed for clarity (dependency closure, not hierarchy) |
| `specgraph scope <ID>` | `swain chart scope <ID>` | Now tree-rooted |
| `specgraph impact <ID>` | `swain chart impact <ID>` | Unchanged |
| `specgraph neighbors <ID>` | `swain chart neighbors <ID>` | Unchanged |
| `specgraph edges` | `swain chart edges` | Unchanged |
| `specgraph mermaid` | `swain chart mermaid` | Unchanged |
| `specgraph build` | `swain chart build` | Unchanged |
| `specgraph xref` | `swain chart xref` | Unchanged |

#### Output modes

- Default: tree display for humans
- `--flat` — old-style list output for scripting and piping
- `--json` — structured output for programmatic consumption
- `--ids` — show artifact IDs alongside titles

#### External issue inbox (follow-on)

Issues linked to a SPEC via `source-issue` appear in the tree under that SPEC's ancestry. Unlinked external issues (GitHub, Linear, Jira, ADO) require a data source adapter to discover and display — this is deferred to a follow-on spec. The `=== Inbox ===` section in the display example above illustrates the target UX; this spec establishes the tree structure that inbox items will eventually plug into.

**Data model extension:** The `linked-artifacts` and `source-issue` frontmatter fields will accept URLs (not just `#NNN` shorthand) for tracker-agnostic linking. This changes the contract for frontmatter parsing in `graph.py` — the parser must recognize URL values and extract a display label (e.g., issue title via API, or the URL itself as fallback).

#### Unanchored section

Artifacts that cannot trace parent edges to a Vision appear in `=== Unanchored ===` (replaces the current "Unparented" label). The term "unanchored" distinguishes ancestry gaps from the existing "drift" concept in `attention.py` (which measures *inactivity* drift — visions not receiving commits). Unanchored items show their partial ancestry if one exists (e.g., a Spec under an Epic that has no Initiative or Vision — show the Epic too, so the operator can see where the chain breaks). Each unanchored item is prefixed with ⚠.

### Surface integrations

#### swain-session bookmark

When displaying a bookmark, show the artifact's Vision ancestry as a breadcrumb:
`Swain > Operator Situational Awareness > Vision-Rooted Hierarchy Display`

On session resume, the operator immediately sees *where in the strategy* they left off.

#### swain-status dashboard

Replace the flat artifact summary with a vision-rooted tree (strategic depth by default, respects focus lane). tk task counts roll up to parent Spec/Epic nodes as annotations.

#### swain-do execution tracking

When showing task context for a claimed ticket, include the ancestry breadcrumb so the agent/operator sees how the task connects to strategy.

### Unanchored enforcement

#### At display time
All `swain chart` lenses render the Unanchored section for artifacts without Vision ancestry.

#### At creation time (swain-design)
When creating an artifact that has no path to a Vision, warn:
`⚠ No Vision ancestry — this artifact will appear as Unanchored`

Do not block creation. Offer to attach: `Attach to an existing Initiative or Epic? [candidates]`

#### In swain-design audit
Add an unanchored check pass alongside the existing alignment check and ADR compliance check. Scans for artifacts with no Vision ancestry and reports them as domain-level findings.

### Shared tree renderer

A `VisionTree` renderer (Python) that all lenses and surface integrations consume.

**Inputs:**
- `nodes` — set of artifact IDs to display
- `depth` — integer (default 2)
- `phase_filter` — optional set of phases to include
- `annotations` — dict of artifact_id to annotation string
- `sort_key` — callable for sibling ordering (default: alphabetical by title)

**Returns:** `list[str]` — lines of rendered output. Callers join with newlines for terminal display, or post-process for `--flat`/`--json` modes. The renderer itself is format-agnostic — `--flat` and `--json` are handled by the CLI layer, not the renderer.

**Rendering rules:**
- Walk parent edges up to Vision root
- Include intermediate ancestors for structural completeness (dimmed, no annotation)
- Flatten when intermediate levels are missing
- Elbow connectors (├── └── │) with indentation
- Titles as primary labels, IDs secondary
- Legend at bottom

## Acceptance Criteria

1. Given `swain chart` is run with no arguments, when Visions exist with child artifacts, then the output shows a tree rooted at each Vision with titles as primary labels and a legend at the bottom.

2. Given an artifact has no parent-edge path to a Vision, when any `swain chart` lens is run, then the artifact appears in the `=== Unanchored ===` section with ⚠ prefix.

3. Given `--depth 2` (default), when an Epic has child Specs, then the Epic is a leaf node annotated with child counts (e.g., `3 specs, 1 spike`).

4. Given `--depth 3` or `--detail`, when an Epic has child Specs, then individual Specs appear as tree children.

5. Given `swain chart recommend` is run, when artifacts have different priority scores, then siblings at every tree level are sorted by score descending (not alphabetically).

6. Given `swain chart ready` is run, then only unblocked artifacts appear in the tree, shown within their Vision ancestry, with → prefix.

7. Given `--flat` is passed to any lens, then the output is a plain list (no tree connectors) suitable for piping.

8. Given `--json` is passed, then structured JSON output is returned.

9. Given a swain-session bookmark references an artifact, when the bookmark is displayed, then the Vision ancestry breadcrumb is shown (e.g., `Swain > Operator Situational Awareness > ...`).

10. Given swain-status renders its dashboard, then it uses the vision-rooted tree at strategic depth, respecting the focus lane.

11. Given an artifact is created via swain-design with no Vision ancestry, then a warning is emitted: `⚠ No Vision ancestry — this artifact will appear as Unanchored`.

12. Given swain-design audit is run, then unanchored detection is included alongside alignment and ADR compliance checks.

13. Given `swain chart` is run with `--ids`, then artifact IDs appear alongside titles.

14. Given all existing `specgraph` subcommands, then each has a corresponding `swain chart` subcommand that produces equivalent or improved output.

15. Given a tk ticket is claimed and its parent SPEC has Vision ancestry, when swain-do shows task context, then the Vision ancestry breadcrumb is displayed (e.g., `Swain > Operator Situational Awareness > ...`).

16. Given two Epics under the same Initiative have different `priority-weight` values, when `swain chart recommend` is run, then the higher-priority Epic sorts first among its siblings.

## Scope & Constraints

**In scope:**
- `swain chart` CLI and tree renderer
- All lens implementations (default, ready, recommend, attention, debt, unanchored, status)
- Extend `priority-weight` to Epics (epic definition, template, priority.py cascade)
- Subsumption of all specgraph commands
- Display-time unanchored detection
- Creation-time unanchored warning in swain-design
- Unanchored check in swain-design audit
- URL-based `linked-artifacts` and `source-issue` (data model extension)
- swain-session breadcrumb integration
- swain-status tree integration
- swain-do ancestry breadcrumb
- `--flat`, `--json`, `--ids` output modes

**Out of scope:**
- External issue inbox discovery (GitHub/Linear/Jira API integration) — follow-on spec
- External issue promotion workflow (inbox item to spec/epic) — follow-on spec
- Feedback loop to external trackers (commenting, state transitions on promotion) — follow-on spec
- Rendering technology for scope progress bars (EPIC-018 / SPIKE-021 concern)
- swain-doctor unanchored detection (domain concern, not functional health)

**Constraints:**
- Must not require external installs beyond what's already vendored
- Graph engine reuses existing parser/cache from specgraph Python package
- `specgraph.sh` becomes a deprecated alias for `swain chart` during migration

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-15 | — | Initial creation via brainstorming |
