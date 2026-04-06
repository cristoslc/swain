---
title: "ROI Appraisal Model For Portfolio Economics"
artifact: SPIKE-052
track: container
status: Active
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
question: "Can a portfolio economics model with structured value axes (project-defined) and cost axes (framework-defined) produce better prioritization than priority-weight labels when applied to swain's existing backlog?"
parent-vision: VISION-004
linked-artifacts:
  - ADR-010
  - VISION-002
  - VISION-003
  - VISION-004
  - VISION-005
  - INITIATIVE-002
  - INITIATIVE-005
  - INITIATIVE-016
  - INITIATIVE-019
depends-on-artifacts: []
gate: Pre-Implementation
---

# ROI Appraisal Model For Portfolio Economics

## Research Question

Can a portfolio economics model with structured value and cost axes produce better prioritization than `priority-weight: high | medium | low` when applied to swain's existing backlog?

## Context

Swain currently prioritizes work with `priority-weight` (high/medium/low) cascaded through the parent chain, combined with structural leverage (`unblock_count`). The scoring formula is `score = unblock_count x priority_rank`. This captures what unblocks the most work and what the operator labeled important, but it has no concept of *value delivered* or *resources consumed*.

The result: every active Vision is `priority-weight: high`. Every Initiative that matters is `priority-weight: high`. The labels have collapsed — they no longer differentiate. When demand outpaces development capacity (which it always does for a solo operator), the system cannot distinguish "obviously worth doing" from "probably not worth doing."

## Core Thesis

Every swain project is a portfolio of strategic bets. The operator invests two scarce resources — attention and compute budget — across competing Visions. Each Vision is a bet that investing in a particular direction will produce returns the operator values. The framework should make these bets explicit, measurable, and comparable.

### Two kinds of axes

**Value axes are project-specific.** They come from the project's PURPOSE — what returns the operator cares about. Different projects have different value axes. Swain's own axes (derived from PURPOSE.md's three problems) are:

- **Alignment** — decisions are captured, agents act on them, drift is detected
- **Safety** — agent actions are contained, mistakes have bounded blast radius
- **Sustainability** — operator attention is managed, decisions are closeable, cognitive load is bounded

Another project using swain might declare `revenue`, `reliability`, `user-experience`. The framework provides the structure for declaring and measuring against axes, not the axes themselves.

**Cost axes are framework-structural.** They come from swain's operating model (solo operator + AI agents) and apply to every project:

- **Operator attention** — cognitive load, decision time, context switching. Finite per day, doesn't scale, doesn't carry over.
- **Compute budget** — tokens, API calls, CI minutes. Finite per period but scalable (spend more money to get more).

These are baked into swain because swain *is* the opinion that this is how development works: a human decides, agents execute, both cost something.

### The formula

```
value = sum(impact_on_axis × vision_axis_weight for each axis served)
cost  = weighted_cost(operator_attention, compute_budget)
roi   = value / cost
```

Leverage replaces `unblock_count` with **transitive downstream return** — the sum of ROI of all artifacts this one unblocks, recursively. This makes leverage a function of value, not just graph topology.

```
score = max(1, own_roi) × (1 + downstream_roi)
```

The `max(1, ...)` floor means leverage always has something to multiply — pure infrastructure with zero own-return but high downstream return still scores well.

## Validation: Applying the Model to Swain's Backlog

### Step 1: Swain's value axes (from PURPOSE.md)

| Axis | Description | Source in PURPOSE.md |
|------|-------------|---------------------|
| alignment | Decisions captured, agents act on them, drift detected | "The gap between human decisions and agent execution widens silently over time" |
| safety | Agent actions contained, mistakes bounded | "Agents run with the operator's authority but without the operator's judgment" |
| sustainability | Operator attention managed, decisions closeable | "The operator's cognitive resources are finite" |

These map directly to the three problems PURPOSE already names. They're not forced — they're what PURPOSE already says, just formalized as axes.

### Step 2: Vision axis weights

Applying structured axis weights to the four active Visions:

| Vision | alignment | safety | sustainability | Rationale |
|--------|-----------|--------|---------------|-----------|
| VISION-002 Safe Autonomy | 0 | 3 | 1 | Primarily a safety bet (sandbox, containment). Minor sustainability gain (unattended agents reduce operator burden). |
| VISION-003 Swain Everywhere | 2 | 0 | 2 | Portability improves alignment (swain's decision model travels with the operator) and sustainability (consistent process reduces cognitive switching). Not a safety bet. |
| VISION-004 Operator Cognitive Support | 1 | 0 | 3 | Primarily sustainability (session budgets, walk-away signals). Minor alignment benefit (bounded sessions prevent drift from fatigue). |
| VISION-005 Trustworthy Agent Governance | 3 | 2 | 1 | Primarily alignment (enforced process compliance, not just advisory). Significant safety component (governance prevents process violations that could cause damage). Minor sustainability. |

**Observation:** The axis weights naturally differentiate the Visions. All four are currently `priority-weight: high`, but the model reveals they're betting on different axes at different intensities. VISION-005 is the heaviest alignment bet. VISION-004 is the heaviest sustainability bet. VISION-002 is the heaviest safety bet. VISION-003 is a balanced alignment+sustainability bet.

### Step 3: Initiative appraisal

Applying serves-goals and cost estimates to four representative Initiatives:

**INITIATIVE-002 Artifact System Maturity** (parent: VISION-001, but most work is complete)

| Axis | Impact | Rationale |
|------|--------|-----------|
| alignment | 3 | Artifacts ARE the alignment mechanism — this initiative built the document model |
| safety | 0 | Not a safety initiative |
| sustainability | 2 | Better tooling (specgraph, lifecycle normalization) reduces operator cognitive overhead |

Cost: operator-attention: M, compute-budget: M (mostly complete — remaining work is EPIC-055)

**INITIATIVE-005 Operator Situational Awareness** (parent: VISION-001)

| Axis | Impact | Rationale |
|------|--------|-----------|
| alignment | 1 | Seeing state is not the same as enforcing alignment, but it surfaces drift |
| safety | 0 | Not a safety initiative |
| sustainability | 3 | Directly reduces "where are we?" cognitive burden |

Cost: operator-attention: M, compute-budget: S

**INITIATIVE-016 Agent Implementation Reliability** (parent: VISION-001)

| Axis | Impact | Rationale |
|------|--------|-----------|
| alignment | 2 | Agents verify assumptions before committing — output matches intent more reliably |
| safety | 1 | Prevents broken scripts from landing (bounded damage) |
| sustainability | 1 | Fewer broken-script debugging sessions |

Cost: operator-attention: S, compute-budget: S (small initiative — two artifacts)

**INITIATIVE-019 Session-Scoped Decision Support** (parent: VISION-004)

| Axis | Impact | Rationale |
|------|--------|-----------|
| alignment | 1 | Bounded sessions prevent fatigue-induced drift |
| safety | 0 | Not a safety initiative |
| sustainability | 3 | This IS the sustainability mechanism — session budgets, walk-away signals |

Cost: operator-attention: L, compute-budget: M (rebuilds swain-session from scratch)

### Step 4: Return calculation

Using VISION-004's axis weights (alignment:1, safety:0, sustainability:3) for INITIATIVE-019:

```
value = (impact_alignment × weight_alignment) + (impact_safety × weight_safety) + (impact_sustainability × weight_sustainability)
      = (1 × 1) + (0 × 0) + (3 × 3)
      = 1 + 0 + 9
      = 10
```

Cost mapping (using same t-shirt scale as before: XS=1, S=2, M=3, L=5, XL=8):
```
cost = operator_attention(L=5) + compute_budget(M=3) = 8
roi  = 10 / 8 = 1.25
```

Using VISION-001's axis weights (would need to be declared — for now assuming alignment:3, safety:1, sustainability:2) for INITIATIVE-016:

```
value = (2 × 3) + (1 × 1) + (1 × 2) = 6 + 1 + 2 = 9
cost  = operator_attention(S=2) + compute_budget(S=2) = 4
roi   = 9 / 4 = 2.25
```

**Observation:** INITIATIVE-016 has better ROI than INITIATIVE-019 despite being "smaller." It delivers solid value across axes at low cost. INITIATIVE-019 delivers higher absolute value but costs more. Both are currently `priority-weight: high` — the model differentiates them.

### Step 5: Leverage comparison

INITIATIVE-016 has two children: SPIKE-036 (Active) and SPEC-126 (Proposed, depends on SPIKE-036). If SPEC-126 has ROI of ~2.0, then SPIKE-036's leverage = 2.0.

INITIATIVE-019 has multiple child Epics with significant downstream specs. Its leverage would be much higher — it's a gateway to the entire session infrastructure.

So even though INITIATIVE-016 has better own-ROI, INITIATIVE-019 might score higher when leverage is factored in:
```
INIT-016 score = max(1, 2.25) × (1 + 2.0)  = 2.25 × 3.0  = 6.75
INIT-019 score = max(1, 1.25) × (1 + 15.0) = 1.25 × 16.0 = 20.0  (hypothetical)
```

This feels correct — INITIATIVE-019 is a big bet that unlocks a lot. INITIATIVE-016 is a small bet with efficient returns. Both are worth doing, but if forced to choose, the gateway bet wins.

## Findings

### What works

1. **Axis weights naturally differentiate what priority-weight cannot.** All four Visions are "high priority" but they're betting on different axes at different intensities. The model makes this visible.

2. **ROI separates efficient bets from expensive ones.** INITIATIVE-016 vs INITIATIVE-019 — both valuable, but the model shows which is a better *deal* per unit of investment.

3. **Leverage captures gateway value.** INITIATIVE-019's high leverage reflects that it unlocks the session infrastructure. A naive ROI comparison would undervalue it.

4. **Cost axes feel real.** The operator-attention vs. compute-budget split captures a distinction the operator actually makes. "This is cheap in tokens but expensive in my time" is a different cost profile from "this is expensive in tokens but I barely have to think about it."

5. **Value axes come naturally from PURPOSE.** Alignment, safety, sustainability aren't forced — they're what PURPOSE already declares as the three problems swain solves.

### What needs more thought

1. **VISION-001 (Swain, superseded by PURPOSE) is the parent of most Initiatives.** It's not an active Vision — it was superseded. The hierarchy hasn't been re-parented. This means most Initiatives would inherit axis weights from a dead Vision. The model would surface this as a problem to fix, which is arguably a feature, but it complicates a cold-start rollout.

2. **Cost axis weighting.** Is `total_cost = operator_attention + compute_budget` the right composition? Should they be weighted differently? The operator might value attention more than compute budget (attention doesn't scale, tokens do). Maybe `total_cost = (attention × 2) + compute_budget`? Or let the operator set cost axis weights in project settings?

3. **Granularity of impact scores (0-3) may be too coarse.** With three value axes scored 0-3, composite value ranges 0-9 per axis-weight level. Combined with t-shirt costs, ROI has limited resolution. Is this enough to differentiate? The sample above suggests yes for big-picture ranking, but it may struggle with closely-ranked items.

4. **Bootstrapping effort.** Applying value and cost estimates to 19 active Initiatives and 4 active Visions is not trivial. Agents could propose estimates, but the operator must validate them. Is there a lighter on-ramp?

5. **How cost axes compose.** Simple sum? Weighted sum? Max (bottleneck model — the most expensive axis dominates)? This choice matters because it determines whether a task that's cheap in attention but expensive in compute is treated differently from one that's cheap in compute but expensive in attention.

## Recommendation

The model earns its complexity. The axis-weighted approach produces better differentiation than priority-weight labels, and the cost axes capture a real distinction. Proceed to implementation with:

1. PURPOSE.md declares the appraisal philosophy and swain's own value axes
2. Vision frontmatter adds `appraisal-goals` (structured axis weights)
3. Initiative/Epic/Spec frontmatter adds `serves-goals` (impact per axis) and `cost-estimate` (per cost axis)
4. priority.py computes ROI from weighted impact / cost, leverage from transitive downstream ROI
5. ADR documents the decision
6. Existing `priority-weight` demoted to tiebreaker/escape-hatch, not primary signal

### Open questions for implementation

- Cost composition model (sum vs weighted sum vs bottleneck)
- Cost axis weights (should operator set these in project config?)
- Depth decay for transitive leverage (full sum vs diminishing returns at depth?)
- Migration path for existing artifacts (agent-proposed estimates with operator review?)

## Lifecycle

| Phase | Date | Notes |
|-------|------|-------|
| Active | 2026-04-06 | Initial creation |
