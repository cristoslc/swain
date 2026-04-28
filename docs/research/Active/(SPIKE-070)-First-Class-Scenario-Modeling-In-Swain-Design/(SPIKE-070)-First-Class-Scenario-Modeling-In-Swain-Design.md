---
title: "First-Class Scenario Modeling in swain-design"
artifact: SPIKE-070
track: container
status: Active
author: Cristos L-C
authored-by: Claude Opus 4.7 (1M context)
created: 2026-04-26
last-updated: 2026-04-28
parent-initiative: INITIATIVE-002
question: "Should swain-design treat scenario modeling — alternative artifact trees under varying assumptions, ADR sets, or constraints — as a first-class feature? What would the data model, UX, and integration with existing supersession and roadmap views look like?"
gate: Pre-MVP
risks-addressed:
  - Operators cannot easily compare strategic forks before committing.
  - ADR supersession history loses the "what would the tree have looked like" alternatives.
  - Roadmap reasoning is single-track; counterfactuals live only in operator memory.
evidence-pool: "scenario-modeling-prior-art@e1ca9829"
trove: scenario-modeling-prior-art@e1ca9829
---

# First-Class Scenario Modeling in swain-design

## Summary

<!-- Populated at Active → Complete transition. Lead with verdict (Go / No-Go / Hybrid / Conditional), then 1–3 sentences. -->

## Hypothesis

Operators pick better when they can see forks side by side. Today, swain-design renders one tree. Forks live only in superseded ADRs and dropped epics. There is no way to ask "what if ADR-X were active?" or "how do priorities shift if we relax Y?"

If we make scenarios a first-class dimension, we expect:

- Faster, more confident strategic pivots — operators see the downstream tree change before they commit.
- A natural home for "what-if" reasoning that today gets lost in chat or scratchpads.
- Better ADR authorship — alternatives can be modeled, not just described in prose.

## Question

Should scenario modeling become a first-class aspect of swain-design — and if so, what is the minimum viable shape?

Sub-questions:

1. What does "scenario" mean in swain's data model? Branch of the artifact graph, an overlay, or a frontmatter dimension?
2. How does it interact with existing ADR supersession and Initiative roadmaps?
3. How does an operator invoke and consume scenarios? CLI, chart view, or interactive picker?
4. What is the smallest prototype that proves or kills the idea?

## Method

The investigation runs in four threads. Each produces a short note in this folder.

1. **Prior art scan.** Survey scenario planning and decision tools. Cynefin, war-gaming, decision trees, feature flags, config overlays (Kustomize, Helm values), and any AI-coding tools that model forks. Capture the primitive name and the operator surface.
2. **Data model sketch.** Draft 2–3 candidate models. Examples: a `scenario` frontmatter field that filters the chart; an overlay file (`scenarios/<name>.yaml`) that pins ADR states and priority overrides; a fully branched graph with scenario-scoped IDs. Note tradeoffs against supersession.
3. **UX sketch.** Walk through 2–3 operator stories end to end. "Compare a tree under ADR-046 active vs. superseded." "See priorities if INITIATIVE-018 is paused." "Fork the tree, edit, then promote one branch to canonical." Pick the smallest invocation surface (e.g., `swain chart --scenario=foo`).
4. **Integration check.** Walk existing supersession back-refs, drift resolution, and roadmap rendering. List what breaks or needs extending if scenarios become real.

Time-box: 2 working sessions, ~4 hours total. Stop sooner if any thread surfaces a fatal objection.

## Go / No-Go Criteria

**Go (proceed to EPIC):**
- At least one data model survives the integration check without forcing breaking changes to ADR supersession.
- The UX sketch shows an invocation surface an operator would actually use — single command, no new mental model larger than "scenarios are like git branches for artifacts".
- The minimum prototype is implementable in under one week of focused work.

**No-Go (stop):**
- Every data model breaks supersession or roadmap rendering.
- The smallest viable UX requires 3+ new commands or a new artifact type beyond `scenario`.
- Prior art shows the pattern is well-known to fail in similar tools.

**Hybrid (narrow scope):**
- Scenarios work as a chart-only filter (read-only overlay) but full branching is too costly. Recommend a smaller epic that ships the read-only path and defers branching.

## Pivot Recommendation

If the gate fails, do not drop the question. Two narrower fallbacks:

1. **ADR alternatives section.** Extend the ADR template with a structured "Alternatives considered" block. Link to artifacts that *would* have been created. Cheap, no graph changes.
2. **Roadmap forks document.** A standing `docs/roadmap-forks.md` captures named forks in prose. Manual diffs against the canonical tree. Zero tooling cost. Pure doc discipline.

## Findings

<!-- Populated during Active phase. Each method thread gets a subsection. -->

### Thread 1 — Prior art

**Status: Complete.** See trove `scenario-modeling-prior-art@e1ca9829` for all 10 sources.

**Key findings:**

Two distinct primitives emerged across all tools: *projection* (same model, different display filter — covered by existing `swain chart` lenses) and *scenario* (different input assumptions, same schema, different computed graph — unmet by any existing tool).

**Convergence across six tool categories:**
- *ADR tooling* (adr-tools, Log4brains, pyadr): zero tools model the counterfactual artifact tree. Supersession is a linear chain; the alternative tree is prose-only. Confirmed gap.
- *Config management* (Kustomize, Helm): the **overlay-as-delta** pattern — scenarios express only the diff from base, never a full copy. This is the recommended data model primitive.
- *Feature flags* (LaunchDarkly, Unleash): **named activation states + dependency-aware re-evaluation**. Key risk: flag/scenario lifecycle is mandatory to prevent stale scenario debt.
- *Decision modeling* (DMN, MCDA/1000minds): DMN's **input context as scenario parameter** is the right framing. MCDA's **sensitivity analysis** (sweep one variable, find the tipping point) is more useful than full scenario enumeration.
- *Strategic planning* (Wardley Maps, Anaplan, Farseer): scenarios must be **promotable to canonical** — the "promote to plan" pattern keeps scenarios as reversible explorations. Wardley Maps' key insight: model *where* scenarios diverge, not just *what* they contain.
- *Knowledge graph tools* (Obsidian, Roam, Logseq): exhausted the "query/filter" solution space for projection. Structural alternatives (scenarios) are genuinely absent — confirming the gap is real and unserved.

**Recommended primitive:** a named YAML overlay file that pins specific artifact-graph inputs (ADR states, priority weights) to non-canonical values, evaluated against the canonical graph. Invocation: `swain chart --scenario=name`. Comparison: `swain chart --compare=canonical,name`.

**Feeds into:** Thread 2 (the overlay YAML model is the leading candidate), Thread 3 (`--scenario` and `--compare` flags are the target surface), Thread 4 (dependency-aware re-evaluation and scenario lifecycle are the two integration design concerns).

### Thread 2 — Data model

### Thread 3 — UX

### Thread 4 — Integration

## Acceptance

This spike is complete when:

- All four method threads have a note in this folder.
- The Summary section leads with a verdict (Go / No-Go / Hybrid).
- The recommendation names a concrete next artifact — either an EPIC with a rough spec count, the narrowed Hybrid scope, or the No-Go pivot.
- The operator has reviewed and accepted, modified, or rejected the verdict.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-26 | pending | Initial creation, attached to INITIATIVE-002 |
