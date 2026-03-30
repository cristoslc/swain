---
source-id: "good-enough-architecture"
title: "'Good Enough' Architecture"
type: media
url: "https://www.youtube.com/watch?v=PzEox3szeRc"
fetched: 2026-03-29T00:00:00Z
hash: "d4876de01412da7bac4e57758a454ba8f78e8e9036d02aacf0b7295d2fc8d2a5"
---

# "Good Enough" Architecture

**Speaker:** Stefan Tilkov
**Format:** Conference talk (~42 min)
**Capability:** Cap 1 -- Smell-Test Claims

## Key Points

Stefan Tilkov challenges the notion that architecture must be comprehensive and complete before implementation begins. He advocates for "good enough" architecture -- the minimal set of decisions needed to make progress while preserving the ability to change course.

### The Danger of Over-Architecture

- Over-architecture is as harmful as under-architecture
- Speculative generality -- building for hypothetical future needs -- wastes effort and adds accidental complexity
- Many architectural decisions can and should be deferred until more information is available

### What Makes Architecture "Good Enough"?

- Good enough architecture addresses the constraints that actually matter now
- It explicitly identifies which decisions are reversible vs. irreversible
- Reversible decisions should be made quickly and changed if needed
- Irreversible decisions deserve careful analysis and documentation

### Architecture as a Living Thing

- Architecture is not a one-time activity but an ongoing practice
- Systems evolve, and their architecture must evolve with them
- The cost of changing architecture later is often lower than the cost of getting it "right" upfront
- Feedback from production usage is essential for architectural evolution

### Pragmatism Over Purism

- Pragmatic trade-offs beat theoretically pure solutions
- Context determines what "good enough" means -- a startup has different needs than a bank
- The architect's role is to find the appropriate level of rigor for the situation

### Team Autonomy and Architecture

- Architecture decisions should be made as close to the implementation as possible
- Centralized architecture governance should focus on cross-cutting concerns, not micro-decisions
- Teams that own their architecture tend to make better decisions because they live with the consequences

## Relevance to Intent-Evidence Loop

Tilkov's "good enough" framing directly addresses the **Reconciliation** challenge: how do you know when intent is sufficiently specified? The answer is feedback loops -- deploy, observe, adjust. This aligns with the finding that architecture documents are caches that need validity checking through reconciliation.

The emphasis on reversible vs. irreversible decisions connects to ADR practice in swain: ADRs encode irreversible decisions (high-stakes intent), while lower-stakes decisions can live in code and be discovered through evidence.
