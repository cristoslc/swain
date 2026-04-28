---
title: "Scenario Planning Software — Financial What-If Modeling (2025 Landscape)"
source-url: https://www.farseer.com/blog/scenario-planning-software/
source-type: web-page
fetched: 2026-04-28
transcript-source: web-search-synthesis
---

# Scenario Planning Software — 2025 Landscape

**Sources:** farseer.com, golimelight.com, thecfoclub.com, epicflow.com, drivetrain.ai, indicio.com

## Summary

The 2025 scenario planning software market is dominated by financial modeling tools: Anaplan, Limelight, Cube, Mosaic, Farseer, Datarails. These are purpose-built for "best-case / base-case / worst-case" financial projections with adjustable assumptions. The UX patterns they have converged on are directly applicable to swain's scenario modeling question.

## Converged UX Patterns

### 1. Named Scenarios with Assumption Sets

Every tool in this category supports "create a named scenario" as a first-class operation. A scenario is a container for a named set of assumption overrides. The canonical workflow:

```
Base scenario: FY26 budget assumptions
Scenario A: "Optimistic" — 15% revenue growth, stable headcount
Scenario B: "Recession" — 5% revenue growth, 10% headcount reduction
Scenario C: "Expansion" — 25% revenue growth, 50% headcount increase
```

Each scenario shares the same model structure (the same rows, the same formula logic). Scenarios differ only in the values of specific input parameters.

### 2. Side-by-Side Comparison

Farseer (and most modern tools) show scenarios in a tabular or chart comparison view. You select 2–4 scenarios and see their outputs side by side. Differences are highlighted. The canonical view is:

```
Metric          | Base    | Optimistic | Recession
Revenue         | $10M    | $11.5M     | $10.5M
Operating Cost  | $7M     | $7M        | $6.3M
Net Income      | $3M     | $4.5M      | $4.2M
```

### 3. Promote to Plan

Once the operator selects a scenario, they "promote" it to the official plan. This is a one-click operation that replaces the canonical assumptions with the scenario's assumptions. The old plan becomes historical.

### 4. Assumption Audit Trail

Tools like Anaplan and Cube track which assumptions changed between scenarios and when. The audit trail answers: "Why is Scenario B's revenue different from Base? Because the growth rate assumption was changed from 10% to 5%."

## Monte Carlo and Bayesian Methods (Indicio)

Indicio (and similar tools) attach *probabilities* to scenarios rather than treating them as discrete alternatives. "Recession scenario has 30% probability" feeds into a weighted expected value calculation. This is a step beyond simple what-if — it computes a risk-adjusted outcome across the scenario distribution.

## Relevance to swain

The financial scenario planning UX converges on a clear model:
1. **Named scenarios** = containers for assumption overrides.
2. **Shared structure** = the canonical artifact graph.
3. **Comparison view** = `swain chart --compare=scenario-A,scenario-B`.
4. **Promote to canonical** = merge a scenario's assumptions into the main artifact tree.
5. **Audit trail** = git history of scenario files.

The "promote to plan" operation is swain's equivalent of "merge the scenario branch back to trunk." This makes scenarios reversible explorations rather than permanent forks.

**Key lesson:** Scenarios should be promotable. The operator explores in a scenario; when they commit to a direction, they promote it to canonical. This preserves reversibility and reduces decision anxiety.
