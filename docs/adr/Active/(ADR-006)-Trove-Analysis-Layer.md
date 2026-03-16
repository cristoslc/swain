---
title: "Trove Analysis Layer"
artifact: ADR-006
track: standing
status: Active
author: cristos
created: 2026-03-16
last-updated: 2026-03-16
linked-artifacts:
  - SPEC-055
  - INITIATIVE-005
  - VISION-001
depends-on-artifacts: []
evidence-pool: "trove:slop-creep"
---

# Trove Analysis Layer

## Context

Swain-search troves collect and normalize external sources into a `sources/` directory, track provenance in `manifest.yaml`, and distill cross-source themes in `synthesis.md`. This structure answers "what did we learn?" but not "what does it mean for us?"

While extending the `slop-creep` trove, we produced an application-specific analysis — how the trove's findings apply to VISION-001 and active initiatives. This analysis is qualitatively different from the synthesis: the synthesis is a neutral distillation of what sources say; the analysis is a judgment about what the sources mean for specific artifacts and decisions in this project.

Without a formal layer for this, analyses either get mixed into `synthesis.md` (conflating research with judgment), placed in the referencing artifact (orphaning them from the source provenance they cite), or created ad-hoc with no discoverability.

## Decision

Add an **analysis layer** to the trove schema: a new `analyses` section in `manifest.yaml` and a corresponding `analysis/` directory alongside `sources/`. Each analysis is a separate markdown file that references specific sources by ID and scopes itself to specific artifacts or decisions.

The three-layer structure becomes:

| Layer | Directory/file | Purpose | Perspective |
|-------|---------------|---------|-------------|
| **Sources** | `sources/` | Normalized originals | What was said |
| **Synthesis** | `synthesis.md` | Neutral thematic distillation | What the sources collectively say |
| **Analysis** | `analysis/` | Application-specific interpretation | What it means for this project |

Zero-to-many analyses per trove. Each analysis must cite the sources it draws from via `sources-referenced` in both the manifest entry and the analysis file's frontmatter.

## Alternatives Considered

### 1. Keep analysis inline in synthesis.md

Simpler — no schema change needed. But conflates two distinct cognitive tasks: summarizing what sources say (editorial) and judging what they mean for the project (strategic). A trove with 5 sources and 3 different analyses would produce an unreadably long synthesis. Worse, the synthesis becomes project-specific and loses its value as a neutral reference.

### 2. Put analysis in the referencing artifact, not the trove

The artifact (e.g., VISION-001) would contain a section analyzing the trove. This keeps analysis close to the decision it informs, but severs it from source provenance. When the trove is refreshed (new sources added, stale sources updated), analyses stored in the artifact don't know they might be invalidated. Keeping analyses in the trove means they're co-located with the sources they cite and can be flagged as stale during refresh.

### 3. A separate analysis artifact type outside troves

A new top-level artifact type (ANALYSIS-NNN) that cross-references troves and other artifacts. This is the most flexible but adds a new artifact type to the already-substantial type system. The analysis layer is tightly coupled to trove sources — it doesn't make sense as a standalone entity. Keeping it inside the trove preserves the co-location principle.

## Consequences

**Positive:**
- Clear separation of concerns: sources (what was said), synthesis (what sources agree/disagree on), analysis (what it means here)
- Analyses are discoverable via `manifest.yaml` — other artifacts and agents can find relevant analyses without reading every trove file
- Source citations in analyses create a traceable chain from judgment back to evidence
- Trove refresh can flag analyses whose cited sources have changed content
- Multiple artifacts can have independent analyses of the same trove without conflict

**Accepted downsides:**
- Manifest schema grows — `analyses` section adds complexity to an already non-trivial YAML file
- Analysis files need their own normalization format and frontmatter schema
- The distinction between synthesis and analysis requires judgment — borderline cases will exist (addressed by the rule: synthesis never mentions project-specific artifacts by ID; analysis always does)

**Migration:**
- Backfill the existing `slop-creep` trove manifest with its ad-hoc analysis
- No other troves have analyses yet — this is additive, not breaking

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-16 | — | Created alongside SPEC-055; decision adopted based on slop-creep trove experience |
