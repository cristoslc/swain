---
source-id: "quality-worth-cost"
title: "Is High Quality Software Worth the Cost?"
type: web
url: "https://martinfowler.com/articles/is-quality-worth-cost.html"
fetched: 2026-03-29T00:00:00Z
hash: "71981a5201286fbbedfcb227b503a02322e494d8b03442d7b8565eccf64919dc"
---

# Is High Quality Software Worth the Cost?

**Author:** Martin Fowler
**Published:** 29 May 2019, updated 29 January 2024
**Capability:** Cap 1 -- Smell-Test Claims (Go Deeper)

## Content

A common debate in software development projects is between spending time improving software quality versus concentrating on releasing more valuable features. Fowler argues this question misses the point: high quality software is actually cheaper to produce.

### External vs. Internal Quality

- **External quality**: UI, defects -- visible to users and customers
- **Internal quality**: architecture, code structure -- invisible to users

Users can judge external quality. They cannot perceive internal quality. So why pay more for it?

### Internal Quality Makes Enhancement Easier

Programmers spend most of their time modifying existing code. Internal quality determines how easily they can:
- Understand how existing code works
- Determine where new features fit into the flow
- Make changes without introducing defects
- Avoid the compounding effect of **cruft** (the difference between current code and how it would ideally be)

### The Cruft Accumulation Problem

- Poor internal quality causes rapid cruft buildup
- Cruft slows feature development progressively
- Even the best teams create some cruft -- it's inherent in working with uncertainty
- The difference is that the best teams keep cruft under control through testing, refactoring, and continuous integration

### The Pseudo-Graph

Fowler presents a visualization:
- **Low internal quality**: rapid initial progress that slows dramatically over time
- **High internal quality**: slightly slower start that maintains or even accelerates velocity
- The lines cross quickly -- within weeks, not months

### The Cost Inversion

The "cost" of high internal quality software is negative. The usual trade-off between cost and quality does not apply to internal software quality. High internal quality reduces the cost of future features. This is counter-intuitive but critical to understand.

### Even the Best Teams Create Cruft

A tech lead on a widely successful project confessed the architecture wasn't great. His explanation: "we made good decisions, but only now do we understand how we should have built it." Software exists in a world of uncertainty -- customers learn as the software is built, building blocks change every few years.

### DORA Studies on Elite Teams

State of DevOps Report research shows elite teams:
- Update production many times a day
- Push code changes from development to production in less than an hour
- Have significantly lower change failure rates
- Recover from errors much more quickly
- Correlate with higher organizational performance

This disproves the bimodal myth that you must choose between speed and reliability.

### Measuring Low Internal Quality Effects

A study by Adam Tornhill and Markus Borg (2022) using CodeScene found:
- Resolving issues in low quality code took more than twice as long
- Low quality code had 15 times higher defect density

## Relevance to Intent-Evidence Loop

This article provides the economic argument for the entire loop. Architecture (intent) is not overhead -- it's an investment that reduces the cost of future work. Evidence of quality (or cruft) should feed back into intent revision through reconciliation.

The pseudo-graph directly maps to the trove's "amortized derivation" concept: the upfront cost of encoding intent in architecture documents pays for itself by preventing costly re-derivation. The cruft accumulation problem shows what happens when the reconciliation phase fails to detect and address drift between intent and reality.

The DORA findings provide empirical evidence that the speed-vs-quality trade-off is false -- exactly the kind of "smell test" that Cap 1 teaches architects to apply.
