---
title: "Structurizr Perspectives — Annotation Overlays on Architecture Diagrams"
source-url: https://docs.structurizr.com/ui/diagrams/perspectives
source-type: web-page
fetched: 2026-04-28
transcript-source: web-fetch
---

# Structurizr Perspectives

**Source:** https://docs.structurizr.com/ui/diagrams/perspectives

## Summary

Structurizr's "perspectives" feature lets operators annotate elements and relationships with arbitrary named properties, then view the same diagram through each perspective as a lens. It is an overlay system on one canonical model — not a branching or forking system.

## The Primitive: Named Perspective Annotations

A perspective is a named annotation attached to an element or relationship. Each element can carry multiple perspectives. Example:

```dsl
component PaymentService {
  perspectives {
    Security "High risk — PCI scope"
    Performance "P99 < 50ms"
    Ownership "Team: Payments"
  }
}
```

The workspace (model + views + docs) remains singular. Perspectives do not change structure — they annotate it.

## Operator Invocation

- In the UI: click the **binoculars button** to select a perspective by name.
- In iframe embeds: append `?perspective=Security` to the URL.
- The diagram re-renders, highlighting elements whose perspective value matches, and graying out elements with no annotation for that perspective.

## What It Shows

Each perspective-switched view highlights a quality characteristic (security posture, performance tier, ownership, tech debt rating, compliance flag). It does not show an alternative structural model — elements and relationships are fixed. The overlay changes emphasis, not structure.

## Limitations vs. Full Model Branching

- **Single model:** Perspectives annotate the one canonical model. You cannot show "what the model looks like with component X removed."
- **No structural alternatives:** You can highlight "security risk = high" but cannot show "what if we replaced component X with Y."
- **No comparison view:** No side-by-side diff between two perspectives.
- **Read-only filter:** Perspectives are static display filters, not interactive "what-if" levers.

## Relevance to swain Scenario Modeling

Structurizr's perspectives are the closest prior art in architecture tooling to swain's question. They solve the "multiple lenses on one model" problem but not the "alternative models under different assumptions" problem. The primitive (named annotation + filter overlay) is simple and low-cost. The gap (no structural alternatives, no comparison) is exactly what swain's scenario feature would need to fill.

**Key lesson:** Separate "projection" (same model, different display filter) from "scenario" (alternative model under different assumptions). These are distinct primitives.
