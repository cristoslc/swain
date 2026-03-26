---
title: "Per-Vision and Per-Initiative Roadmap Slices"
artifact: SPEC-143
track: implementable
status: Complete
author: cristos
created: 2026-03-21
last-updated: 2026-03-22
type: feature
parent-epic: ""
parent-initiative: INITIATIVE-005
linked-artifacts:
  - SPEC-108
  - SPEC-109
  - SPEC-115
  - SPEC-120
  - SPEC-124
  - SPEC-144
  - VISION-001
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: "gh#84"
swain-do: required
---

# Per-Vision and Per-Initiative Roadmap Slices

## Problem Statement

`chart.sh roadmap` generates a single project-wide ROADMAP.md. Operators working on a specific Vision or Initiative must mentally filter the full roadmap to find their scope — there is no way to see a focused roadmap slice for a single Vision or Initiative. Meanwhile, the vision definition already expects a manual `roadmap.md` supporting doc per Vision folder, creating a maintenance burden and staleness risk when the auto-generated project roadmap diverges from hand-written Vision roadmaps.

## Desired Outcomes

Operators gain scoped situational awareness: each Vision and Initiative gets an auto-generated roadmap slice that shows only the work relevant to that artifact. This eliminates the need to manually maintain per-Vision `roadmap.md` files (currently expected by the vision definition) and ensures roadmap slices stay fresh because they are computed from the same graph data as the project-wide roadmap.

The vision definition's expectation of a manual `roadmap.md` per Vision folder is superseded by auto-generated slices — reducing operator maintenance burden while improving accuracy.

## External Behavior

### New subcommand: `chart.sh roadmap --scope <ARTIFACT-ID>`

**Input:** A Vision or Initiative artifact ID (e.g., `VISION-001`, `INITIATIVE-005`).

**Output:** A `roadmap.md` file written to the artifact's folder (e.g., `docs/vision/Active/(VISION-001)-Foo/roadmap.md`) containing:

1. **Intent summary** — the artifact's title followed by a one-line description. The script checks for a `brief-description` frontmatter field (SPEC-144) first; if absent, writes a `{{INTENT: <ARTIFACT-ID>}}` placeholder. The swain-roadmap skill post-processes placeholders by reading source artifacts and replacing them with extracted summaries.
2. **Child artifact table** — clickable links to all direct children (Initiatives for Visions; Epics and direct SPECs for Initiatives), with current phase and progress ratio.
3. **Progress indicator** — aggregate completion ratio (e.g., `3/7 children complete`) and a simple text-based progress bar.
4. **Recent activity** — the last 3 git commits whose messages reference any child artifact ID (via `git log --oneline --all --grep`).
5. **Eisenhower subset** — the relevant rows from the project-wide Eisenhower tables, filtered to children of the scoped artifact.

**Project-wide roadmap integration:** When `chart.sh roadmap` runs (no `--scope` flag), it also regenerates all per-Vision and per-Initiative slices. This keeps slices fresh whenever the project roadmap refreshes.

**swain-roadmap skill:** The swain-roadmap skill gains a `--scope` pass-through: `swain-roadmap VISION-001` generates and opens just that slice.

### Harmonization with vision definition

The vision definition currently says:
> Every Vision SHOULD include an `architecture-overview.md` and a `roadmap.md`.

This SPEC supersedes the manual `roadmap.md` expectation. After implementation:
- The vision definition is updated to say the `roadmap.md` is **auto-generated** by `chart.sh roadmap --scope`.
- Existing manual `roadmap.md` files in Vision folders are replaced on first regeneration (with a one-time backup to `roadmap.manual-backup.md` if they contain non-generated content).

## Acceptance Criteria

### AC1: Scoped roadmap generation for Visions

**Given** a Vision artifact exists with child Initiatives and Epics,
**When** `chart.sh roadmap --scope VISION-NNN` is run,
**Then** a `roadmap.md` is written to the Vision's folder containing intent summary, child table with links, progress indicator, and recent commits.

### AC2: Scoped roadmap generation for Initiatives

**Given** an Initiative artifact exists with child Epics and/or direct SPECs,
**When** `chart.sh roadmap --scope INITIATIVE-NNN` is run,
**Then** a `roadmap.md` is written to the Initiative's folder containing intent summary, child table with links, progress indicator, and recent commits.

### AC3: Project-wide roadmap regenerates all slices

**Given** multiple Visions and Initiatives exist,
**When** `chart.sh roadmap` is run (no `--scope` flag),
**Then** the project-wide ROADMAP.md is generated AND all per-Vision and per-Initiative `roadmap.md` slices are regenerated.

### AC4: Progress indicator accuracy

**Given** an Initiative with 5 child Epics where 2 are Complete,
**When** a scoped roadmap is generated,
**Then** the progress indicator shows `2/5 children complete` (or equivalent).

### AC5: Recent activity section

**Given** child artifacts with matching git commits,
**When** a scoped roadmap is generated,
**Then** the "Recent activity" section shows the last 3 commits whose messages reference any child artifact ID.

### AC6: Vision definition harmonized

**Given** the vision definition references a manual `roadmap.md`,
**When** this SPEC is complete,
**Then** the vision definition is updated to reference auto-generated `roadmap.md` slices via `chart.sh roadmap --scope`.

### AC7: --focus flag replaced by --scope

**Given** the existing `--focus` argument on `chart.sh roadmap`,
**When** this SPEC is complete,
**Then** `--focus` is removed and `--scope` covers its use case (Vision-level filtering with the new slice output).

### AC8: Existing manual roadmaps backed up

**Given** a Vision folder contains a manually-written `roadmap.md`,
**When** `chart.sh roadmap --scope` writes to that folder for the first time,
**Then** the existing file is backed up to `roadmap.manual-backup.md` before being overwritten.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC1: Scoped Vision roadmap | `chart.sh roadmap --scope` writes roadmap.md to Vision folder with intent, child table, progress, commits | PASS |
| AC2: Scoped Initiative roadmap | render_scoped_roadmap handles Initiative children (Epics + direct SPECs) | PASS |
| AC3: Project-wide regenerates slices | `_write_all_slices()` called from no-scope path in chart_cli.py | PASS |
| AC4: Progress accuracy | Progress indicator computed from child completion ratios | PASS |
| AC5: Recent activity | `_get_recent_commits()` greps git log for child artifact IDs | PASS |
| AC6: Vision definition harmonized | vision-definition.md updated to reference auto-generated slices | PASS |
| AC7: --focus replaced by --scope | `--scope` flag in chart_cli.py; `collect_roadmap_items` uses scope param | PASS |
| AC8: Manual roadmap backup | `_write_scoped_slice` backs up non-generated roadmap.md before overwriting | PASS |

## Scope & Constraints

**In scope:**
- `chart.sh roadmap --scope <ID>` subcommand for Visions and Initiatives
- Replacement of existing `--focus` flag with `--scope`
- All-slices regeneration on project-wide `chart.sh roadmap` run (no opt-out)
- Intent summary: `brief-description` field > `{{INTENT}}` placeholder (swain-roadmap post-processes)
- `swain-roadmap` skill `--scope` pass-through and `{{INTENT}}` replacement
- Vision definition update (harmonization)
- One-time backup of existing manual roadmaps

**Out of scope:**
- Per-Epic roadmap slices (Epics are leaf-level in the roadmap hierarchy)
- Calendar-based scheduling or effort estimation
- Interactive or drag-and-drop roadmap editing
- Changes to the project-wide ROADMAP.md format itself

**Constraints:**
- Must use the same graph data and rendering pipeline as the project-wide roadmap (no separate data source)
- Slices must be deterministic (same graph state = same output)
- Must not break existing `chart.sh roadmap` behavior when run without `--scope`

## Implementation Approach

1. **RED:** Write tests for `chart.sh roadmap --scope VISION-NNN` — verify it produces a `roadmap.md` in the correct folder with required sections.
2. **GREEN:** Add `--scope` flag parsing to chart.sh roadmap subcommand. Filter `collect_roadmap_items()` output to the subtree rooted at the scoped artifact. Generate the slice with intent summary, child table, progress bar, recent commits, and Eisenhower subset.
3. **RED:** Write tests for Initiative-scoped slices — verify direct SPECs (not just Epics) appear in the child table.
4. **GREEN:** Ensure the Initiative path handles both Epic children and direct SPEC children (leveraging [SPEC-115](../(SPEC-115)-Roadmap-Initiative-Children-Level-Based-Filtering/SPEC-115.md)'s level-based filtering).
5. **RED:** Write tests for project-wide regeneration triggering all slices.
6. **GREEN:** In the no-`--scope` path, iterate all Visions and Initiatives and call the scoped generator for each.
7. **Harmonize:** Update vision-definition.md to reference auto-generated slices. Add backup logic for existing manual roadmaps.
8. **REFACTOR:** Extract shared rendering logic between project-wide and scoped paths.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-21 | — | Initial creation from gh#84 |
| Complete | 2026-03-22 | fb1601b | Retroactive close — implemented on worktree branch, merged with SPEC-120 conflict resolution |
