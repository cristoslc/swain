---
title: "Trove Analysis Layer"
artifact: SPEC-055
track: implementable
status: Active
author: cristos
created: 2026-03-16
last-updated: 2026-03-16
type: feature
parent-epic: ""
parent-initiative: INITIATIVE-005
linked-artifacts:
  - ADR-006
  - VISION-001
depends-on-artifacts: []
addresses: []
evidence-pool: "trove:slop-creep"
source-issue: ""
swain-do: required
---

# Trove Analysis Layer

## Problem Statement

Swain-search troves have a two-layer structure (sources + synthesis) that captures research but not its application. When a trove informs project decisions, the interpretive analysis has no formal home — it either gets mixed into the neutral synthesis, placed in the referencing artifact (severing it from source provenance), or created ad-hoc without discoverability. ADR-006 decides to add a formal analysis layer; this spec implements it.

## External Behavior

### 1. Manifest schema — `analyses` section

A new top-level `analyses` key in `manifest.yaml`, parallel to `sources`:

```yaml
analyses:
  - analysis-id: "swain-vision-application"
    title: "Application to Swain Vision & Initiatives"
    scope:
      - VISION-001
      - INITIATIVE-005
      - INITIATIVE-007
    sources-referenced:
      - boristane-slop-creep-enshittification
      - stopsloppypasta-ai
    created: 2026-03-16
    author: cristos
```

**Fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `analysis-id` | Yes | Slug-based ID, matches filename in `analysis/` |
| `title` | Yes | Human-readable title |
| `scope` | Yes | List of artifact IDs this analysis informs |
| `sources-referenced` | Yes | List of source IDs cited (must exist in `sources` section) |
| `created` | Yes | ISO date |
| `author` | Yes | Who wrote the analysis |

### 2. Analysis file format

Analysis files live in `analysis/<analysis-id>.md` with frontmatter:

```yaml
---
analysis-id: "swain-vision-application"
title: "Slop Creep Trove — Application to Swain Vision & Initiatives"
trove: slop-creep
created: 2026-03-16
author: cristos
scope:
  - VISION-001
  - INITIATIVE-005
  - INITIATIVE-007
sources-referenced:
  - boristane-slop-creep-enshittification
  - stopsloppypasta-ai
---
```

Body is free-form markdown. Convention: organize by artifact scope (one h2 per artifact or decision area), with inline citations to source IDs.

**Distinguishing rule:** synthesis never mentions project-specific artifact IDs; analysis always does.

### 3. Swain-search modes — new Analyze mode

Add an **Analyze** mode to swain-search alongside Create, Extend, Refresh, and Discover:

| Signal | Mode |
|--------|------|
| User says "analyze", "what does this mean for", "apply to", "how does this relate to" | **Analyze** — create an analysis against an existing trove |

Analyze mode workflow:
1. Read the existing trove's `manifest.yaml` and `synthesis.md`
2. Identify the scope — which artifacts or decisions the analysis targets (ask user if ambiguous)
3. Read the relevant sources from `sources/`
4. Draft the analysis with citations to source IDs
5. Write to `analysis/<analysis-id>.md`
6. Append entry to `analyses` section in `manifest.yaml`
7. Report what was created

### 4. Create/Extend modes — optional analysis

After completing source collection and synthesis in Create or Extend mode, offer:

> Sources collected and synthesis generated. Would you like to analyze how these findings apply to specific artifacts? (This creates an analysis in the trove's `analysis/` directory.)

If yes, proceed with Analyze mode. If no, skip — analyses are never mandatory.

### 5. Trove directory structure (updated)

```
docs/troves/<trove-id>/
  manifest.yaml          # provenance, sources, AND analyses
  synthesis.md           # neutral thematic distillation
  sources/               # normalized originals
    <source-id>/
      <source-id>.md
  analysis/              # application-specific interpretations
    <analysis-id>.md
```

## Acceptance Criteria

1. **Given** a trove with sources, **when** the user invokes Analyze mode, **then** an analysis file is created in `analysis/` with correct frontmatter (analysis-id, scope, sources-referenced) and the manifest's `analyses` section is updated.

2. **Given** an analysis manifest entry, **when** `sources-referenced` contains a source-id that doesn't exist in `sources`, **then** swain-search warns about the broken reference.

3. **Given** a trove with zero analyses, **when** the manifest is read, **then** the `analyses` key is either absent or an empty list — both are valid.

4. **Given** Create or Extend mode completes, **when** synthesis is generated, **then** the user is offered the option to create an analysis (not forced).

5. **Given** the `slop-creep` trove with its existing ad-hoc `analysis/swain-vision-application.md`, **when** migration runs, **then** the manifest is backfilled with the correct `analyses` entry and the analysis file's frontmatter matches the manifest.

6. **Given** `manifest-schema.md` in swain-search references, **when** SPEC-055 is complete, **then** the schema documentation includes the `analyses` section with field descriptions.

7. **Given** `normalization-formats.md` in swain-search references, **when** SPEC-055 is complete, **then** a new "Analysis" section documents the analysis file format.

8. **Given** the swain-search SKILL.md, **when** SPEC-055 is complete, **then** Analyze mode is documented with its signal words, workflow, and graceful fallback.

## Verification

<!-- Populated when entering Testing phase. -->

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

**In scope:**
- Manifest schema extension (`analyses` section)
- Analysis file format and frontmatter schema
- Analyze mode in swain-search skill instructions
- Optional analysis prompt in Create/Extend modes
- Reference documentation updates (manifest-schema.md, normalization-formats.md)
- Migration of slop-creep trove

**Out of scope:**
- Stale-analysis detection during Refresh mode (future enhancement — flag analyses whose cited sources have changed hash)
- Analysis diffing or versioning beyond git
- Automated analysis generation (analyses require operator judgment)

**Files to modify:**
- `.claude/skills/swain-search/SKILL.md` — add Analyze mode, update Create/Extend
- `.claude/skills/swain-search/references/manifest-schema.md` — add `analyses` section
- `.claude/skills/swain-search/references/normalization-formats.md` — add Analysis format
- `docs/troves/slop-creep/manifest.yaml` — backfill migration
- `docs/troves/slop-creep/analysis/swain-vision-application.md` — verify frontmatter conformance

## Implementation Approach

### TDD cycle 1: Manifest schema documentation
- Update `manifest-schema.md` with `analyses` section, field descriptions, and example
- Verify the schema example YAML is valid

### TDD cycle 2: Analysis normalization format
- Add "Analysis" section to `normalization-formats.md`
- Document frontmatter fields, body conventions, and the distinguishing rule (synthesis = no artifact IDs; analysis = always artifact IDs)

### TDD cycle 3: Swain-search skill instructions
- Add Analyze mode to the mode detection table in SKILL.md
- Write Analyze mode workflow (steps 1-7)
- Update Create/Extend modes with optional analysis prompt
- Add Analyze mode to Discover mode output (show analysis count per trove)

### TDD cycle 4: Migration
- Backfill `slop-creep/manifest.yaml` with `analyses` entry
- Verify `slop-creep/analysis/swain-vision-application.md` frontmatter conforms to the new schema
- Validate `sources-referenced` entries exist in the `sources` section

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-16 | — | Created alongside ADR-006; scope and design decisions settled in conversation |
