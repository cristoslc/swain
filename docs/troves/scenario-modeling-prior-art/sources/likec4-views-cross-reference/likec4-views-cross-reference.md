---
title: "LikeC4 — Predicate Views and Dynamic Scenarios (Cross-Reference)"
source-url: https://likec4.dev
source-type: cross-reference
fetched: 2026-04-28
transcript-source: trove-cross-reference
related-trove: likec4
---

# LikeC4 — Views and Dynamic Scenarios

**Cross-reference from trove:** `likec4`
**Primary synthesis:** `docs/troves/likec4/synthesis.md`

## Relevant Excerpts for Scenario Modeling

### Predicate-Based Views (Projections)

LikeC4's static views are computed from predicates — include/exclude/where rules that filter the model. Each view is a named projection of the same underlying model:

```dsl
view payment-flow {
  include payments.*
  include users where tag = #external
  exclude internal.*
}
```

Multiple views of the same model can coexist. This is the "projection" pattern: same data, different display filter.

### Dynamic Views (Sequence Scenarios)

LikeC4's dynamic views describe interaction scenarios — sequences of steps, parallel blocks, and notes:

```dsl
dynamic view checkout-flow {
  user -> frontend "add to cart"
  frontend -> payments "initiate checkout"
  payments -> bank "authorize"
  bank -> payments "approved"
  payments -> frontend "confirmed"
}
```

A dynamic view is a named scenario describing how the system behaves under a specific use case. Multiple dynamic views describe different scenarios (happy path, error path, refund path).

### Deployment Views (Environment Variants)

Deployment views map logical elements to infrastructure via `instanceOf`. Different deployment views can model dev, staging, and prod environments — the closest LikeC4 gets to "same model, different assumptions."

### MCP Server (Agent-Queryable Model)

LikeC4 ships an MCP server with `diff`, `ancestors`, `descendants`, and `path-finding` tools. An agent can query "what changed between view A and view B?" This is exactly what swain's scenario diff would need.

## Relevance to swain Scenario Modeling

LikeC4's three view types map directly to swain's scenario modeling problem:

| LikeC4 | swain equivalent |
|--------|-----------------|
| Static view (predicate filter) | `swain chart` lens (ready, debt, etc.) |
| Dynamic view (sequence scenario) | Execution scenario (walkthrough of a specific EPIC/SPEC flow) |
| Deployment view (environment variant) | ADR scenario (different ADR activation states) |

LikeC4 has not solved "alternative structural models under different assumptions" either — its views are projections of one model, not forks. But its MCP server's `diff` capability is the agent-facing interface swain would want to expose for scenario comparison.

**Key lesson:** LikeC4's view taxonomy is a clean model. swain already has the "static view" (chart lenses). "Dynamic views" and "deployment views" are the gaps — the scenario feature would fill the deployment-view gap (alternative assumptions) and potentially the dynamic-view gap (execution scenarios).
