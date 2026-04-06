---
title: "Transitive Leverage Depth Decay"
artifact: SPIKE-054
track: container
status: Proposed
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
question: "Should transitive downstream return be summed fully or decay with dependency depth, and if decay, what function?"
parent-vision: VISION-004
linked-artifacts:
  - SPIKE-059
  - INITIATIVE-021
  - EPIC-066
depends-on-artifacts: []
gate: Pre-Implementation
---

# Transitive Leverage Depth Decay

## Research Question

Should transitive downstream return be summed fully or decay with dependency depth, and if decay, what function?

## Context

SPIKE-059 established that leverage should be transitive downstream return — the sum of ROI of everything an artifact unblocks, recursively. If A unblocks B (roi=3) and B unblocks C (roi=5), A's leverage includes both.

The question is whether distant downstream return should count the same as immediate downstream return. Full sum means A gets leverage of 3+5=8. With decay, B's contribution of 5 might be discounted because it's two steps away.

## Arguments for full sum

- Simple, transparent, no tuning parameters
- If A truly blocks the entire chain, the full downstream value IS at stake
- The dependency graph already encodes the real blocking relationships

## Arguments for decay

- Distant downstream artifacts may have alternative paths (the dependency graph might not be the only way)
- Confidence in ROI estimates decreases with distance (transitive uncertainty)
- Without decay, a single deep chain can produce extreme leverage scores that dominate all other signals
- Prevents "leverage inflation" where everything near the root of a deep chain scores astronomically

## Candidate decay functions

1. **No decay (full sum):** `leverage = sum of all downstream ROI`
2. **Linear decay:** `leverage = sum(roi_i / depth_i)` — halves at depth 2, thirds at depth 3
3. **Geometric decay:** `leverage = sum(roi_i × 0.5^depth_i)` — halves at each step
4. **Capped depth:** Full sum up to depth N, then zero. Simple but cliff-edged.

## Research Approach

1. Build the transitive dependency graph for swain's current backlog
2. Compute leverage under each decay model
3. Compare rankings and check for pathological cases (extreme leverage scores, deep chains dominating)
4. Check whether the practical difference matters — if the backlog is shallow, decay may be irrelevant

## Lifecycle

| Phase | Date | Notes |
|-------|------|-------|
| Proposed | 2026-04-06 | Initial creation |
