# TRAIN Artifact Type & Documentation Viewer Design

**Date:** 2026-03-19
**Scope:** SPEC-091 (TRAIN Artifact Type) + Documentation Viewer (new SPEC) + INITIATIVE + EPIC + DESIGN artifacts
**Status:** Approved

## Context

Swain has artifact types for technical planning (SPECs, SPIKEs, ADRs), user experience (JOURNEYs, PERSONAs, DESIGNs), and operational procedures (RUNBOOKs), but no artifact type for human-facing training materials. When a feature ships, the knowledge of how to use it lives only in commit messages, spec acceptance criteria, and tribal memory.

A [retro on 2026-03-19](../../swain-retro/2026-03-19-spike-findings-not-back-propagated.md) found that downstream artifacts go stale when upstream SPIKEs invalidate assumptions. Training materials are especially vulnerable — stale docs actively teach operators the wrong thing.

## Artifact Hierarchy

```
VISION-001: Swain
│
├── SPEC-091: TRAIN Artifact Type (standalone, swain-design scope)
│   No parent epic — single well-scoped spec.
│
└── INITIATIVE-NNN: swain-stage Redesign
    │   Browser-based project control surface. Docs viewer is the first panel;
    │   future panels include status dashboard, artifact graph, worktree-aware
    │   branch diffing. Replaces the tmux-based swain-stage.
    │
    ├── DESIGN-NNN: swain-stage Interaction Design
    │   Full UI vision: greyed-out nav tabs for future panels,
    │   non-404 placeholder pages, responsive layout.
    │
    ├── EPIC-NNN: User Documentation System
    │   └── SPEC-NNN: Documentation Viewer (depends-on: SPEC-091)
    │       Rip out existing swain-stage. Docsify with custom swain theme.
    │
    ├── EPIC: (future) Status Dashboard Panel
    ├── EPIC: (future) Artifact Graph Visualization
    └── ...
```

SPEC-091 is standalone under VISION-001 (attached via `parent-vision`). It does not belong under the swain-stage Initiative — it's a swain-design artifact type extension, not a presentation concern.

## Design Decision 1: Audience

TRAIN is for **product documentation** — end users of products built with swain. Swain is itself a swain-built product, so swain's own docs are the first instance, but the primary design target is product documentation broadly.

## Design Decision 2: Type Taxonomy (Diataxis MVP)

Based on research into documentation type frameworks, adopting the [Diataxis framework](https://diataxis.fr/) (Procida) — the most widely adopted system in open source (Django, Ubuntu/Canonical, Python, Kubernetes).

Diataxis defines four types on a 2x2 matrix (practical/theoretical x learning/working). MVP uses three:

| train-type | Diataxis quadrant | User need | Example |
|---|---|---|---|
| `how-to` | Practical + Working | "I need to accomplish X right now" | "How to configure credential scoping" |
| `reference` | Theoretical + Working | "What does this parameter do?" | "Artifact type reference" |
| `quickstart` | Practical + Learning | "Get me running in under 10 minutes" | "Your first swain project" |

Key Diataxis rule: **never mix types in a single document.** A how-to that starts explaining "why" becomes neither a good how-to nor a good explanation.

`tutorial` and `explanation` are not defined at launch. Add when demand emerges.

## Design Decision 3: Enriched `linked-artifacts` with Relationship Types

**Design bet — fallback ready.** If this feels wrong during implementation, revert to a separate `dependencies` field.

### Problem

TRAIN needs commit-pinned dependencies for staleness tracking. Putting these in both `linked-artifacts` and a separate `dependencies` field duplicates the same relationship in two places.

### Solution

Enrich `linked-artifacts` to support optional attributes per entry. Each item can be a plain string (backward compatible) or an object with explicit relationship type and optional commit pinning:

```yaml
linked-artifacts:
  - artifact: SPEC-067
    rel: [documents]
    commit: abc1234
    verified: 2026-03-19
  - artifact: RUNBOOK-002
    rel: [documents]
    commit: def5678
    verified: 2026-03-19
  - DESIGN-003              # plain string = rel: linked (default)
```

### Relationship vocabulary

Codified in `relationship-model.md`:

| rel | Semantics | Commit-pinnable? | Currently modeled as |
|---|---|---|---|
| `linked` | Informational cross-reference (default) | no | `linked-artifacts` (plain string) |
| `depends-on` | Blocking. Gates readiness. | no | `depends-on-artifacts` field |
| `addresses` | Traceability. Resolves a pain point. | no | `addresses` field |
| `validates` | Operational. Verifies artifact works. | no | `validates` field |
| `documents` | Content dependency. Teaches humans about this artifact. | **yes** | new |

An entry can carry multiple rels (e.g., `rel: [documents, depends-on]`).

### Normalization

Existing separate fields (`depends-on-artifacts`, `addresses`, `validates`) continue working as-is. No migration now. A future normalization SPEC can merge everything into enriched `linked-artifacts` when it's worth the churn.

### specgraph parser change

Teach the parser to handle both string and object entries in `linked-artifacts`. Extract artifact ID from either format. When `rel` is present, map to edge types. Small change — does not affect existing artifacts.

## Design Decision 4: Staleness Detection

### `train-check.sh`

Standalone script. Reads each TRAIN's `linked-artifacts`, filters for entries with `documents` in `rel`, compares `commit` hash against the artifact file's current HEAD commit.

```
$ train-check.sh docs/train/Active/(TRAIN-001)-Getting-Started/
STALE: TRAIN-001 → SPEC-067 (pinned: abc1234, current: fed9876, 3 commits behind)
```

Exit 0 = all pins current. Exit 1 = drift found.

Called standalone, or by `specwatch.sh scan` (which adds a `train-check` pass for each TRAIN found under `docs/train/`). The `swain-sync` skill invokes `specwatch.sh scan` as part of its pipeline, so TRAINs get validated on every sync.

**Caller contract:**
- Accepts a path to a single TRAIN directory or no argument (scans all TRAINs under `docs/train/`)
- Requires `git` to be available; if not, exits with code 2 and a warning (graceful degradation)
- If the script is absent or not executable, specwatch skips the check with a warning (same pattern as adr-check.sh)

### Hooks

**SPEC completion hook** (phase-transitions.md):
1. Scan for TRAINs whose `linked-artifacts` contain this SPEC with `rel: documents`
2. If found: nudge to update existing TRAIN (strong preference over creating new)
3. If not found: no nudge (docs are optional per-SPEC)

**EPIC completion hook** (phase-transitions.md):
1. Scan for TRAINs linked to any SPEC under this EPIC
2. If found: nudge to update
3. If not found: "EPIC-NNN completed with no linked TRAIN. Consider documenting: [title]"
4. Agent/subagent/MCP tool drafts the TRAIN; operator reviews

**Back-propagation** (in-place modification of step 4e in phase-transitions.md):
Step 4e's sibling scan currently checks SPECs and EPICs in the same Vision/Initiative scope when a SPIKE completes. Extend the artifact types it considers to include TRAINs. If a TRAIN's content could be invalidated by the SPIKE's findings, surface as `IMPLICIT_CONFLICT` alongside other sibling findings.

### Default doc granularity

One TRAIN per EPIC minimum. Operator-overridable via swain config. Initiative-level vs. epic-level threshold is operator judgment for now.

## Design Decision 5: TRAIN Artifact Definition

**Lifecycle track:** Standing (Proposed → Active → Retired/Superseded/Abandoned)

**Hierarchy:** `parent-epic` OR `parent-initiative`, never both. Same pattern as SPEC. TRAINs without parents are valid but flagged as unanchored.

**Frontmatter:**

```yaml
---
title: "Getting Started with swain-box"
artifact: TRAIN-001
track: standing
status: Active
author: operator
created: 2026-03-19
last-updated: 2026-03-19
train-type: quickstart
audience: PERSONA-001
parent-epic: EPIC-NNN
parent-initiative:
linked-artifacts:
  - artifact: SPEC-067
    rel: [documents]
    commit: abc1234
    verified: 2026-03-19
  - artifact: RUNBOOK-002
    rel: [documents]
    commit: def5678
    verified: 2026-03-19
superseded-by:
---
```

**Template sections:**
- Prerequisites
- Learning Objectives
- Body (format varies by train-type)
- Key Takeaways
- Next Steps (links to related TRAINs or artifacts)

**Folder structure:** `docs/train/<Phase>/(TRAIN-NNN)-<Title>/`

## Design Decision 6: Documentation Viewer (swain-stage)

**Invocation:** `/swain-stage` (skill invocation)

**Technology:** Docsify with a custom swain theme. Zero-build — markdown rendered client-side, no static site generation step.

**Navigation:** Vision-first hierarchy, then by train-type within each vision:

```
VISION-001: Swain
├── How-to
│   ├── How to Create a SPEC
│   └── How to Run a Security Scan
├── Reference
│   └── Artifact Type Reference
└── Quickstart
    └── Your First Swain Project

VISION-002: Safe Autonomy
├── How-to
│   └── How to Configure Credential Scoping
└── Reference
    └── swain-box Runtime Options
```

TRAINs without Vision ancestry appear in an "Uncategorized" section.

**Staleness in the UI:** The viewer calls `train-check.sh` and surfaces drift inline — a banner on stale TRAINs showing which dependencies changed.

**swain-stage replacement:** Existing tmux code is deleted entirely. The skill is rewritten from scratch. Trigger changes from tmux layout commands to documentation browsing.

**Scope boundary:** One branch, current working directory. No worktree awareness, no multi-branch diffing. Those are future EPICs under the Initiative.

**DESIGN artifact:** A separate DESIGN-NNN captures the full swain-stage vision — greyed-out nav tabs for future panels (Status, Graph, etc.), non-404 placeholder pages for planned features.

## Files to Create

| Artifact | Type | Scope |
|---|---|---|
| INITIATIVE-NNN | Initiative | swain-stage Redesign, under VISION-001 |
| EPIC-NNN | Epic | User Documentation System, under Initiative |
| DESIGN-NNN | Design | swain-stage Interaction Design, under Initiative |
| SPEC-NNN | Spec | Documentation Viewer, under Epic |
| `train-definition.md` | Reference | Artifact type definition |
| `train-template.md.template` | Reference | Artifact template |
| `train-check.sh` | Script | Staleness detection |

## Files to Modify

| File | Change |
|---|---|
| SPEC-091 | Revise to reflect brainstorming decisions (train-types, parent-vision, acceptance criteria) |
| `SKILL.md` (swain-design) | Add TRAIN to artifact type table and "Choosing the right artifact type" |
| `rebuild-index.sh` | Add `train)  title="Training Documents" ;;` to the type title mapping (line ~37) |
| `relationship-model.md` | Add TRAIN node to ER diagram, add `documents` rel type, document enriched format schema |
| `phase-transitions.md` | Add SPEC/EPIC completion hooks for TRAIN nudging; modify step 4e to include TRAINs in sibling scan |
| `adr-check.sh` | Include `docs/train/` in compliance scanning (same as other artifact types) |
| `chart.sh` / specgraph parser | Handle enriched `linked-artifacts` entries (string or object); `chart.sh` already discovers types dynamically via frontmatter, so no type registration needed — but parser must handle enriched format |
| `specwatch.sh` | Add `train` to `TYPE_DIRS` for phase-fix; add `train-check` pass in `scan` subcommand; update frontmatter parser to handle enriched `linked-artifacts` object entries |
| `swain-sync` SKILL.md | Add `train` to rebuild-index type loop; add `docs/train/` to ADR compliance path list |
| swain-stage skill | Rip and replace entirely |

## Open Questions

- **Enriched `linked-artifacts` is a design bet.** If the `rel` tag model feels wrong during implementation, fall back to a separate `dependencies` field. The commit-pinning mechanism works the same either way.
- **Initiative-level doc granularity threshold** is TBD — operator judgment for now, may codify later.
- **Normalization timeline** for merging existing relationship fields into enriched `linked-artifacts` is unscoped.
