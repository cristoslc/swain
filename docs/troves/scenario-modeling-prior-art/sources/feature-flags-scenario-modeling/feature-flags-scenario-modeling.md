---
title: "Feature Flags — Runtime Behavioral Branching"
source-url: https://launchdarkly.com/blog/feature-flags-beyond-the-boolean/
source-type: web-page
fetched: 2026-04-28
transcript-source: web-search-synthesis
---

# Feature Flags — Runtime Behavioral Branching

**Sources:** launchdarkly.com, getunleash.io, kameleoon.com

## Summary

Feature flag systems (LaunchDarkly, Unleash, Flagsmith) model runtime behavioral branches — code forks that activate for a subset of users or environments based on named flag states. They are the most widely deployed scenario modeling system in software. Their architecture has direct lessons for swain.

## The Primitive: Named Boolean (or Multi-Variant) Flag

A flag is a named toggle:
```
payments-v2-enabled: true (for: beta-users, canary-5%, prod-team)
payments-v2-enabled: false (for: everyone else)
```

Flags support targeting rules (user segment, environment, percentage rollout), scheduling (activate at date), and dependencies (flag B only evaluates when flag A is enabled).

## Flag Dependencies (Unleash)

Unleash's flag dependency system is the most relevant model for swain:
- Each flag can have one **parent** flag.
- Child flags only evaluate when their parent is enabled.
- Multiple child flags can share the same parent.

This creates a dependency tree of behavioral variants — structurally similar to swain's artifact graph. A scenario in Unleash is a named activation state of that dependency tree.

## A/B Testing as Scenario Comparison

A/B testing is feature flags' native comparison mode. Two variants (A and B) activate for different user populations simultaneously. Metrics measure which performs better. The comparison is data-driven and live — not a pre-computed diff.

Feature flags do not show "what the system would look like" statically. They run both variants simultaneously and measure.

## Limitations vs. Artifact Scenario Modeling

- **Runtime-only:** Flags branch code behavior, not documentation graphs. There is no "show me the ADR tree under flag state X."
- **No static diff:** No built-in tooling to diff "system under flag set A" vs. "system under flag set B" without deploying both.
- **Temporal:** Flags are removed after rollout; they are not permanent alternatives. Stale flags are tech debt.

## Relevance to swain Scenario Modeling

Feature flags give swain two useful patterns:
1. **Named activation states:** A scenario is a named set of flag values (ADR states, priority weights). Invoke by name: `swain chart --scenario=post-helm-refactor`.
2. **Dependency-aware evaluation:** When ADR-X changes state, re-evaluate all downstream artifacts that reference it — analogous to Unleash's parent/child dependency evaluation.

The key risk the flag ecosystem warns about: **flag proliferation and stale flags**. Scenarios will accumulate. swain needs a lifecycle for scenarios (proposed → active → archived) just as flags have a lifecycle (created → active → removed).

**Key lesson:** Named activation states + dependency-aware re-evaluation are the right flag-ecosystem patterns to borrow. But add a scenario lifecycle to prevent scenario debt.
