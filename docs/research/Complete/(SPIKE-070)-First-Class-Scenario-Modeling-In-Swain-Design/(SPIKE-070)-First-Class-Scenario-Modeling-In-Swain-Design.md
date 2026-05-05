---
title: "First-Class Scenario Modeling in swain-design"
artifact: SPIKE-070
track: container
status: Complete
author: Cristos L-C
authored-by: Claude Opus 4.7 (1M context), DeepSeek V4 Pro (open code)
created: 2026-04-26
last-updated: 2026-04-29
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

**Go — documented git branching process. No new tooling required.**

The YAML overlay was designed for long-lived scenarios consulted across weeks. That use case does not apply. The actual need is point-in-time impact analysis. "If we switch from X to Y, what artifacts change? What code do those artifacts reference?" You need the actual edits on disk to measure the diff, trace source code references, and estimate work. The overlay cannot produce a diff. It can flag artifacts but cannot show what changed.

A documented git branching convention covers the real use case with zero new code. The scenario is a branch. The edits are real frontmatter changes. `git diff` at the end gives an impact report: every changed file, every source code reference, every shifted roadmap. The trunk-drift concern from the earlier analysis does not apply here. Trunk moving is the point. You want to see what the existing artifact set would need to adapt, not what new trunk work would not exist.

The drift detection generalization from the session — `drift(artifact, graph)` with graph as a parameter — remains useful as a standalone improvement. It is scoped separately, not tied to scenario modeling.

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

All criteria pass under the revised verdict (git branching convention).

**Go:**
- The use case is point-in-time impact analysis, not standing what-if queries.
- Git branches already produce the needed output: real diffs showing changed artifacts, traceable to code via `sourcecode-refs`.
- No new tooling, schema, or CLI surface is required.
- A documented convention is implementable immediately — zero lines of code.

**No-Go (for YAML overlay):**
- The use case the overlay was designed for (long-lived standing scenarios) was explicitly ruled out by the operator.
- Without that use case, the overlay adds 160 lines of code that produce the wrong output (flags instead of diffs).

## Pivot Recommendation

If the git branching convention is insufficient in practice, revisit the YAML overlay design (Capture-070) — but only if a concrete pain point from the git approach surfaces. Do not pre-build for hypothetical future needs.

The drift detection generalization (`drift(artifact, graph)` accepting a graph parameter) remains a useful standalone improvement. Scope it as a separate item, not tied to scenario modeling.

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

**Feeds into:** Thread 2 (git branching is the leading candidate), Thread 3 (all UX is git operations the operator already knows), Thread 4 (no integration needed — existing tooling works on any branch).

### Thread 2 — Data model

**Status: Complete.** Verdict: documented git branching process. No new schema.

The YAML overlay (Candidate 2 from the earlier analysis) was designed for long-lived standing scenarios consulted across weeks. That use case was ruled out: the operator does not anticipate long-lived scenarios as an immediate need.

The real use case is point-in-time impact analysis:

> "If we switch from hexagonal to microkernel, what artifacts get updated and what is the measurable code impact from those updates?"

This requires actual edits on disk — you need to see the diff, trace `sourcecode-refs` in changed artifacts, and estimate the work. The overlay can flag "SPEC-330 premise shifted" but cannot produce a diff. Git branches give you exactly the right output:

1. Branch from trunk.
2. Edit frontmatter to reflect the counterfactual world.
3. `git diff` shows every file that changed, and every initiative/epic roadmap that shifted.
4. `grep sourcecode-refs` in changed files estimates code impact.

**The trunk-drift concern from the earlier analysis does not apply here.** When new specs land on trunk while the scenario branch is active, those specs exist independent of the scenario. They would exist in the counterfactual world too. This is a point-in-time analysis of the *existing* artifact set, not a standing what-if that must track trunk.

#### Recommendation

Use a documented git branching convention. No new schema, no new tooling, no new CLI flags. The convention is described in Thread 3.

### Thread 3 — UX

**Status: Complete.** The operator prompts; the agent acts. The operator never touches git.

The operator surfaces a question and the agent does everything: branch, edit, validate, measure, and report. The operator's only role is to review and decide.

#### Operator surface

The operator says one thing:

> "What if ADR-046 had stood?"

That is it. No branch names, no file edits, no `git diff`. The agent owns the rest.

#### Agent workflow

1. Confirm the counterfactual: *"You want to see the artifact tree if ADR-046 were Active instead of Superseded?"*
2. Branch: `scenario/<name>` derived from the question.
3. Walk the supersession graph. Identify every artifact the flip touches — paired ADRs, paired Designs, initiative/epic roadmaps that reference them.
4. Apply frontmatter edits on the branch. Status flips, back-reference updates. No file creates or deletes.
5. Run `swain chart`. Confirm the tree resolves.
6. Present the impact:
   - Number of artifacts changed.
   - Which initiative/epic roadmaps shifted.
   - Source code paths referenced (from `sourcecode-refs` in changed files).
7. Offer: accept (merge to trunk), compare side-by-side (add a worktree for trunk), or reject (delete the branch).

#### Operator feedback loops

If the operator disagrees with the edit set — "also flip DESIGN-034" or "don't touch INITIATIVE-005" — the agent adjusts and re-runs. Iteration is conversational. The agent is in the scenario branch, the operator is steering.

#### Side-by-side comparison

If the operator wants to compare against trunk, the agent adds a worktree:

```
git worktree add ../swain-trunk trunk
```

The operator now has two views: the scenario branch in the current terminal, trunk in the worktree. The agent runs `swain chart` in both. The operator reads the diff the agent already produced — they don't need to navigate two directories.

#### Cleanup

The agent handles both outcomes:

- **Accepted:** merge to trunk, commit, push.
- **Rejected:** delete the branch.

The operator says "accept" or "reject" — that is the extent of their involvement.

### Branch naming convention

All scenario branches live under `scenario/`:

```
scenario/<kebab-case-name>
```

Examples: `scenario/adr-046-active`, `scenario/pre-helm-refactor`, `scenario/no-automated-intake`.

The agent derives the name from the operator's question. The prefix lets `git branch --list 'scenario/*'` enumerate all past and active scenarios.

### Thread 4 — Integration

**Status: Complete.** No integration needed.

With the git branching convention, there is nothing to integrate. All existing tooling — `swain chart`, `swain roadmap`, specwatch, drift resolution, phase transitions, artifact creation, index refresh — already operate against the current branch. A scenario branch is just a git branch. Everything works by default.

The drift detection generalization the session explored — `drift(artifact, graph)` with graph as a parameter — is a useful standalone improvement to the canonical drift machinery. It surfaced during scenario analysis but is not a scenario dependency. It can be scoped as a separate SPEC or chore.

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
