---
source-id: "think-like-architect"
title: "How to Think Like an Architect"
type: media
url: "https://www.youtube.com/watch?v=W7Krz__jJUg"
fetched: 2026-03-29T00:00:00Z
hash: "f5661e5fc21b5bb4dd3ff90384ba381c00d56784456bd0ccb63bc521c4bf48d9"
---

# How to Think Like an Architect

**Speaker:** Mark Richards
**Format:** Conference talk (~45 min)
**Capability:** Cap 1 -- Smell-Test Claims

## Key Points

Mark Richards explores the fundamental mindset shift required when moving from developer to architect roles. The talk addresses how architects must think differently about systems, trade-offs, and decisions.

### Architectural Thinking vs. Developer Thinking

- Developers focus on solving specific problems; architects focus on understanding the problem space holistically
- Architectural thinking requires analyzing trade-offs rather than seeking optimal solutions
- Every architecture decision involves trade-offs -- there is no "best" architecture, only "least worst" for a given context

### The Role of Trade-Off Analysis

- Architects must develop the ability to analyze and articulate trade-offs clearly
- Trade-offs exist across multiple dimensions: cost, time, complexity, scalability, maintainability
- Good architects make trade-offs explicit rather than implicit
- Documentation of trade-offs (the "why") is as important as the decision itself

### Architecture Characteristics

- Architecture is defined by the characteristics that matter most for a given system
- Not all quality attributes are equally important -- prioritization is essential
- The architect's job is to identify which "-ilities" matter most and design accordingly

### Breadth vs. Depth of Knowledge

- Architects need technical breadth more than depth
- Understanding the landscape of available solutions matters more than mastering one
- The "knowledge pyramid" -- developers have deep knowledge in a narrow area; architects have broader but shallower knowledge across many areas

### First Law of Software Architecture

- "Everything in software architecture is a trade-off" -- if you think you've found something that isn't a trade-off, you haven't identified the trade-off yet
- Corollary: "Why is more important than how" -- understanding why a decision was made is more valuable than knowing what was decided

## Relevance to Intent-Evidence Loop

This talk directly supports the **Intent** phase of the loop. Architecture decisions encode intent, and Richards' emphasis on documenting trade-offs aligns with swain's philosophy that architecture documents are "amortized derivation" -- caches of structural understanding that prevent costly re-derivation.

The "first law" reinforces why reconciliation matters: if every decision is a trade-off, then evidence of how those trade-offs play out in production is essential for validating (or revising) architectural intent.
