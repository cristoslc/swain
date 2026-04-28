---
title: "1000minds MCDA — Sensitivity Analysis as the Core Scenario UX"
source-url: https://www.1000minds.com/decision-making/what-is-mcdm-mcda
source-type: web-page
fetched: 2026-04-28
transcript-source: web-fetch
---

# 1000minds MCDA — Multi-Criteria Decision Analysis

**Source:** https://www.1000minds.com/decision-making/what-is-mcdm-mcda

## Summary

MCDA tools model decisions as alternatives × criteria matrices. The operator specifies options (alternatives), evaluation dimensions (criteria), and importance weights. The tool scores and ranks alternatives. The core "scenario" primitive is **sensitivity analysis**: vary one weight or score and watch the ranking change. This is the best-established UX pattern for "what if assumption X changes?"

## The Primitives

### Alternatives and Criteria Matrix

```
           | Cost | Speed | Security | Maintainability
-----------|------|-------|----------|----------------
Option A   |  8   |   6   |    9     |      7
Option B   |  5   |   9   |    6     |      8
Option C   |  7   |   7   |    7     |      6
```

Criteria have weights (e.g., Security = 0.4, Cost = 0.3, Speed = 0.2, Maintainability = 0.1). Weighted scores rank alternatives.

### Sensitivity Analysis (The Scenario Primitive)

Sensitivity analysis asks: "How much does the ranking change if I adjust a weight or a score?" The operator moves a slider (e.g., increase Security weight from 0.4 to 0.6) and the ranking updates in real time. This answers: "Is Option A still best if security matters more than cost?"

Key insight from 1000minds: "fewer than a dozen criteria is usually sufficient, with 5–8 fairly typical." Scope is bounded — MCDA works because the criteria space is small enough to enumerate.

### PAPRIKA (Pairwise Preference Elicitation)

1000minds uses pairwise questions to elicit weights indirectly: "Between Alternative X (low cost, medium security) and Alternative Y (high cost, high security), which do you prefer?" This builds weights from choices, not direct numeric input.

## Operator Invocation

1. Define alternatives (the options under consideration).
2. Define criteria (the evaluation dimensions).
3. Set weights (directly or via pairwise questions).
4. Review ranked outcomes.
5. Run sensitivity analysis: move sliders, watch ranks change.
6. Find the "tipping point" — the weight at which the ranking flips.

## Relevance to swain Scenario Modeling

MCDA's sensitivity analysis is the cleanest prior art for swain's use case. The swain equivalent would be:
- **Alternatives** = different ADR activation states (ADR-X active vs. superseded).
- **Criteria** = swain chart annotations (priority-weight, phase, parent chain).
- **Sensitivity** = "show me the artifact tree when I flip ADR-X's status."

The "tipping point" concept is powerful: not just "show me alternative scenario B" but "show me *at what ADR boundary* the artifact tree changes meaningfully."

**Key lesson:** Sensitivity analysis (single-variable sweep) is more useful than full scenario enumeration. Start with "flip one ADR/assumption" before modeling "flip N at once."
