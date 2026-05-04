---
title: "DMN — Decision Model and Notation"
source-url: https://camunda.com/dmn/
source-type: web-page
fetched: 2026-04-28
transcript-source: web-search-synthesis
---

# DMN — Decision Model and Notation

**Sources:** camunda.com, omg.org, wikipedia.org, capitalone.com

## Summary

DMN (Decision Model and Notation) is an OMG standard for modeling business decision logic. It separates decisions from process flow (BPMN) and captures them as Decision Requirements Diagrams (DRDs) and decision tables. DMN is designed for executable rule engines, not scenario planning — but its graph model and FEEL expression language have direct relevance to swain's scenario question.

## Key Primitives

### Decision Requirements Diagram (DRD)

A DRD is a directed graph of decisions and their input dependencies:

```
[Customer Age] ──┐
                 ├──→ [Eligibility Decision] ──→ [Final Offer Decision]
[Credit Score] ──┘
```

Each node is a named decision. Edges are "required input" relationships. The graph makes dependencies between decisions explicit and queryable.

### Decision Tables

Each decision node can be represented as a table mapping input conditions to output values:

| Customer Age | Credit Score | → Eligibility |
|-------------|-------------|---------------|
| < 18        | any         | Ineligible    |
| ≥ 18        | < 600       | Manual review |
| ≥ 18        | ≥ 600       | Eligible      |

### FEEL (Friendly Enough Expression Language)

FEEL is DMN's expression language. It can express conditional logic, date arithmetic, and list comprehensions. It evaluates against input data at runtime.

## Scenario Modeling in DMN

DMN is designed for *execution*, not scenario comparison. A DMN engine evaluates the DRD against a specific input context and returns an output. To compare scenarios:
- You would need to run the same DRD against two different input contexts (e.g., "credit policy A" vs. "credit policy B").
- DMN tools (Camunda, Drools) support this for automated testing — you define test cases with expected outputs.
- No native "what-if explorer" exists in DMN tooling. Test case comparison is the closest analog.

## Relevance to swain Scenario Modeling

DMN's DRD is a direct structural analog to swain's artifact dependency graph. Both are directed graphs where nodes are decisions and edges are dependency relationships. Two DMN lessons apply:

1. **Graph as queryable structure:** A DRD makes "what depends on what" explicit and machine-queryable. swain's ADR graph already has this structure; scenarios would leverage it.
2. **Input context as scenario parameter:** DMN evaluates against an "input context." swain's analog is the "scenario file" — a named set of ADR state overrides that acts as the evaluation context for `swain chart`.

**Key lesson:** DMN's "input context as scenario parameter" pattern is the right model for swain. A scenario is not a copy of the graph — it is a named input context (set of ADR states) evaluated against the canonical graph.
