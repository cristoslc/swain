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

<!-- Pending operator review before transitioning to Complete. Verdict drafted below. -->

**Go (narrow scope).** The gap is real and confirmed across six tool categories — no existing tool models the counterfactual artifact tree under alternative ADR states. The right primitive is a named YAML overlay file evaluated against the canonical graph at query time, not a git branch (which stales silently on low-touch long-lived scenarios) and not a full copy. Implementation is ~100 lines across two files, well within the one-week threshold. v1 ships `--scenario` and `--compare` flags on `swain chart` with field-only overrides. Cascade and schema validation are v2, gated on observed need.

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

**Status: In progress.** Candidate models under evaluation.

#### Candidate 0 — Git branch per scenario

The simplest approach: create a named branch (`scenario/no-adr-048`), edit ADR frontmatter directly, and run `swain chart` on that branch. Comparison via git worktrees (two branches checked out simultaneously).

**Strengths:**
- Zero new tooling. Operators know git. Lifecycle (create, name, abandon, merge-to-promote) is already there.
- Any `swain chart` invocation already works against a branch's state.
- Short-lived scenarios (hours to a day) feel natural here.

**Staling problem — long-lived, low-touch:**
The scenario branch doesn't drift because people commit to it. It drifts because **trunk moves and the scenario doesn't follow**. The scenario sits dormant for weeks. In that time, trunk gains new specs, completes epics, and transitions ADRs. When the operator wants to consult the scenario again, `swain chart` on the branch answers "what would the tree look like 3 weeks ago under these assumptions" — not "what would the tree look like *today*." That is the wrong answer.

To get the right answer, the operator must first rebase the scenario branch onto trunk. That means resolving conflicts in the same frontmatter edits that define the scenario — on files that may have changed for unrelated reasons. This maintenance cost lands at the moment the operator wants to use the scenario, not while it was idle.

**Scattered delta:** A scenario like "ADR-046 active instead of superseded" isn't one file edit. It requires reverting ADR-046, ADR-048 (which superseded it), DESIGN-032 (moved to Superseded/), and back-references in ~25 initiative/epic roadmaps. The delta is semantically simple but physically scattered.

**Verdict on Candidate 0:** Sufficient for short-lived exploration (hours). Breaks down for standing "what-if" questions consulted across weeks or months.

#### Candidate 1 — Git patch file on trunk

A `.patch` file stored in `docs/scenarios/` on trunk. To consult: `git apply docs/scenarios/no-adr-048.patch`, run `swain chart`, `git restore .`. Since it applies to HEAD, it is always current-trunk-aware — no rebase needed.

**Strengths:** Same delta semantics as the overlay YAML, but uses git's native format. No new schema.

**Weaknesses:** Git patches are fragile against context-line changes. Even whitespace or unrelated frontmatter edits in surrounding lines break `git apply`. Patches operate at the file/line level — they cannot validate that an override makes semantic sense (e.g., preventing a patch that sets an ADR to an invalid status). Ugly to author by hand.

**Verdict on Candidate 1:** Conceptually right (delta on trunk HEAD) but too fragile for long-lived scenarios on files that evolve frequently.

#### Candidate 2 — Overlay YAML (leading candidate)

A named YAML file in `docs/scenarios/` on trunk. Evaluated against the canonical graph at query time:

```yaml
# docs/scenarios/no-adr-048.yaml
scenario: no-adr-048
description: "Tree under ADR-046 active (pre-helm-refactor)"
overrides:
  ADR-046: { status: Active }
  ADR-048: { status: Superseded }
  DESIGN-032: { status: Active }
  DESIGN-033: { status: Superseded }
```

`swain chart --scenario=no-adr-048` applies the overlay to whatever trunk looks like *today* and computes the alternative graph. The overlay has no state of its own — it is a stateless lens, perpetually fresh.

**Strengths:**
- Always current: the overlay applies to HEAD. Three weeks of trunk evolution don't require any maintenance on the scenario file.
- Domain-aware: the schema knows what fields are overridable (`status`, `priority-weight`). Invalid overrides are caught at parse time.
- Human-readable and hand-authorable. Small file for simple scenarios.
- Composable: multiple overlays can be stacked for complex scenarios.
- Promotable: "adopt this scenario" means merging the frontmatter changes to trunk and deleting the overlay file.

**Cost to implement:** A defined schema for overridable fields, `swain chart` accepting `--scenario` and `--compare` flags, and the overlay-apply step in the graph computation. Thread 4 will assess whether `chart.sh` / `chart_cli.py` can absorb this cleanly.

**Verdict on Candidate 2:** Correct primitive for standing scenarios. Implementation cost is bounded.

#### Recommendation

Use **Candidate 0** (git branch) for ad-hoc, short-lived exploration — it costs nothing and operators already know how. Build **Candidate 2** (overlay YAML) for standing scenarios that will be consulted across sessions and weeks. These are not competing — they serve different time horizons.

### Thread 3 — UX

**Status: Complete.**

#### Invocation surface

Two flags on `swain chart`. No new commands, no new artifact types.

```
swain chart --scenario=<name>       # apply overlay, render tree
swain chart --compare=<a>,<b>       # render both, show divergence
```

`<name>` resolves to `docs/scenarios/<name>.yaml` in the repo root.

#### Story 1 — "What does the tree look like if ADR-046 had not been superseded?"

The operator wants to understand what the EPIC-018 implementation path would have looked like if the original microkernel topology decision had stood.

```bash
# Author the scenario file
cat > docs/scenarios/pre-helm-refactor.yaml << 'EOF'
scenario: pre-helm-refactor
description: "Tree under original microkernel topology (ADR-046 active)"
overrides:
  ADR-046: { status: Active }
  ADR-047: { status: Active }
  ADR-048: { status: Superseded }
  ADR-049: { status: Superseded }
  DESIGN-032: { status: Active }
  DESIGN-033: { status: Superseded }
EOF

# View the alternative tree
swain chart --scenario=pre-helm-refactor

# Compare against canonical
swain chart --compare=canonical,pre-helm-refactor
```

The compare output highlights nodes whose status, priority, or parent chain differs between views. The operator sees: "Under this scenario, SPEC-330 and SPEC-331 (Docker test infra) would not exist." That is the decision being examined.

#### Story 2 — "What floats up if INITIATIVE-018 is paused?"

Before a planning meeting, the operator wants to see how the roadmap re-ranks if swain-helm work is deprioritized.

```bash
cat > docs/scenarios/pause-018.yaml << 'EOF'
scenario: pause-018
description: "Roadmap without INITIATIVE-018 weight"
overrides:
  INITIATIVE-018: { priority-weight: low }
EOF

swain chart --scenario=pause-018 recommend
```

The `recommend` lens re-scores under the scenario's weights. The operator sees what moves up. No canonical files touched.

#### Story 3 — Explore, then promote

The operator iterates on the overlay file over several sessions. When a direction is decided, they promote: apply the overrides to the canonical artifact files, delete the scenario file, and commit. The scenario's git history records the exploration.

```bash
# When ready to commit to the direction:
# 1. Edit canonical ADR/DESIGN files to match scenario overrides
# 2. Delete the scenario file
# 3. swain sync  (commits, pushes)
```

Promotion is manual by design. The operator decides when exploration ends and decision begins.

#### Smallest viable surface

Three things ship in v1:
1. `docs/scenarios/` directory convention (no schema enforcement yet — plain YAML).
2. `swain chart --scenario=<name>` flag.
3. `swain chart --compare=<a>,<b>` flag (where `canonical` is a reserved name for the unmodified graph).

No new `swain scenario` command needed. The overlay file is self-describing. Lifecycle (create/iterate/promote/delete) maps to normal file operations.

### Thread 4 — Integration

**Status: Complete.**

#### Hook point in chart_cli.py / graph.py

`build_graph(repo_root)` in `specgraph/graph.py` iterates artifact files, parses frontmatter, and builds a `nodes` dict. The overlay applies cleanly as a post-parse mutation: after all nodes are built, iterate the overlay's `overrides` dict and update matching node fields in memory. No file is touched on disk.

`chart_cli.py` calls `_ensure_cache()` which reads or rebuilds the graph cache. Scenario mode must **skip the cache write** — a scenario-overlaid graph written to cache would corrupt the canonical view for all subsequent non-scenario calls. The change: if `--scenario` is present, build fresh, apply overlay, render, and exit without writing to cache. ~30 lines in `chart_cli.py`, ~20 lines in `graph.py`. No other files change.

#### Back-reference cascade — intentionally not cascading (v1)

When a scenario flips ADR-046 to Active, the 25 initiative/epic roadmap files still have `linked-artifacts` entries pointing to ADR-048. In scenario mode, those artifacts still show as linked to ADR-048 — the scenario override changes ADR-046's displayed status, not the reference graph's edges.

This means the scenario tree is *partially* counterfactual: statuses reflect the scenario, but cross-references reflect the canonical state. For v1 this is the right call — cascading reference rewrites would require a full reference-graph walk and introduce subtle correctness questions (which edges follow the scenario and which don't?). The limitation is visible: a compare output will show ADR-046 as Active while artifacts that *would* have referenced it still point at ADR-048.

Document this as a known v1 limitation. Cascade is v2, gated on observed operator need.

#### specwatch — one-line exclusion

specwatch scans for stale references. Scenario overlay files intentionally reference superseded artifacts (that's the point). Without exclusion, specwatch would flag every scenario file. Fix: add `docs/scenarios/**` to `.agents/specwatch-ignore`. One line.

#### What is unaffected

- **Phase transitions:** read and write canonical files. Scenario mode is read-only. No interaction.
- **Drift resolution:** runs on SPEC create/transition against the canonical parent. Unaffected.
- **Roadmap generation** (`ROADMAP.md`): renders canonical graph. Could add `--scenario` flag later, but not needed for v1.
- **ADR supersession back-reference updates:** the update-back-refs flow edits canonical files. Scenario files are never edited by this flow.
- **Artifact creation and index refresh:** unaffected — they operate on canonical files.

#### Breaking changes

None. All existing code paths are unchanged. `--scenario` is a new optional flag. Scenario files are new files in a new directory. The cache skip is additive logic. No existing tests need to change.

#### Implementation estimate

- `graph.py`: add optional `overlay: dict | None` param to `build_graph`, apply post-parse. ~20 lines.
- `chart_cli.py`: parse `--scenario` flag, load YAML, pass to `build_graph`, skip cache write. ~30 lines.
- `chart_cli.py`: `--compare` flag — call `build_graph` twice (once canonical, once with overlay), diff `nodes`, render side-by-side. ~50 lines.
- `specwatch-ignore`: one line.
- Schema / validation: optional for v1; add as a follow-on SPEC.

**Total: ~100 lines across 2 files + 1 config line.** Well within the "under one week" Go criterion.

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
