---
title: "Cost Axis Composition Model"
artifact: SPIKE-053
track: container
status: Proposed
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
question: "How should operator-attention and compute-budget cost axes compose into a single cost value for ROI calculation?"
parent-vision: VISION-004
linked-artifacts:
  - SPIKE-052
  - INITIATIVE-021
  - EPIC-057
depends-on-artifacts: []
gate: Pre-Implementation
---

# Cost Axis Composition Model

## Research Question

How should operator-attention and compute-budget cost axes compose into a single cost value for ROI calculation?

## Context

SPIKE-052 established that cost has two axes: operator-attention (finite, doesn't scale) and compute-budget (finite but scalable with money). The ROI formula needs a single cost denominator. The composition choice matters because the two axes have different scarcity profiles.

## Candidate Models

### Simple sum
`cost = attention + compute`

Treats both axes as equally scarce. Simple, transparent. But one token-heavy task costing (S, XL) = 2+8 = 10 looks the same as one attention-heavy task costing (XL, S) = 8+2 = 10. In reality, attention is harder to replenish.

### Weighted sum
`cost = (attention × w_a) + (compute × w_c)`

Operator sets weights in project config (e.g., `w_a=2, w_c=1`). Allows expressing "I'm attention-constrained right now" vs "I have plenty of attention but tokens are expensive." More flexible, but adds a config surface.

### Bottleneck (max)
`cost = max(attention, compute)`

The most expensive axis dominates. A task that's XL in attention but XS in compute costs XL. Reflects that the binding constraint is what matters. Simple, but loses information (a task costing L,L scores the same as L,XS).

### Attention-dominant with compute floor
`cost = attention + max(1, compute / 2)`

Attention is the primary cost; compute contributes but at reduced weight. Reflects that attention is structurally scarcer. No config needed. But the halving factor is arbitrary.

## Research Approach

1. Apply each model to the four Initiatives appraised in SPIKE-052
2. Compare ROI rankings under each model
3. Check whether the ranking matches operator intuition
4. Look for cases where the models disagree and determine which disagreement is correct

## Lifecycle

| Phase | Date | Notes |
|-------|------|-------|
| Proposed | 2026-04-06 | Initial creation |
