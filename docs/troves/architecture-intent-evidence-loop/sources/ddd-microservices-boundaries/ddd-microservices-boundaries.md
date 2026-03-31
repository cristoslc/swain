---
source-id: "ddd-microservices-boundaries"
title: "DDD & Microservices: At Last, Some Boundaries!"
type: media
url: "https://www.youtube.com/watch?v=yPvef9R3k-M"
fetched: 2026-03-29T00:00:00Z
hash: "e9d2933135377e5603b804fdfeca6f7ce101aed65cb07512a7229bcf05fe278f"
---

# DDD & Microservices: At Last, Some Boundaries!

**Speaker:** Eric Evans
**Format:** Conference talk (~50 min)
**Capability:** Cap 2 -- Find Boundaries

## Key Points

Eric Evans, creator of Domain-Driven Design, explores how DDD's strategic design patterns -- particularly Bounded Contexts -- provide the principled boundary-finding mechanism that microservices architecture desperately needs.

### The Boundary Problem in Microservices

- Microservices require clear boundaries but provide no built-in method for finding them
- Poor boundaries lead to distributed monoliths -- all the costs of distribution with none of the benefits
- The number one failure mode of microservices adoption is getting the boundaries wrong

### Bounded Contexts as Service Boundaries

- Bounded Contexts from DDD provide a disciplined approach to finding service boundaries
- A Bounded Context defines a linguistic boundary -- where a particular model and its ubiquitous language apply
- Service boundaries should align with linguistic boundaries, not technical layers

### Context Mapping

- Context Maps describe relationships between Bounded Contexts
- Integration patterns (Shared Kernel, Customer-Supplier, Conformist, Anti-Corruption Layer, etc.) define how contexts interact
- The choice of integration pattern has profound architectural implications

### Strategic vs. Tactical Design

- Strategic design (finding boundaries, defining relationships) matters more than tactical design (implementation patterns within a boundary)
- Most teams focus too much on tactical patterns and too little on strategic ones
- Getting the strategic design right is the highest-leverage architectural activity

### Autonomy and Coupling

- Well-drawn boundaries maximize team autonomy
- Poorly drawn boundaries create coupling that propagates across the entire system
- The cost of a wrong boundary is proportional to the coupling it creates

## Relevance to Intent-Evidence Loop

Evans' work on boundaries connects to every phase of the loop:
- **Intent**: Bounded Contexts encode where models apply and how they interact
- **Execution**: Teams organized around well-drawn boundaries can work autonomously
- **Evidence**: Coupling metrics and change propagation patterns reveal whether boundaries are well-placed
- **Reconciliation**: When evidence shows coupling across boundaries, it signals that the intent (the boundary placement) needs revision

This directly supports the trove's finding that architecture encodes the WHY behind structural decisions -- boundary placement decisions are among the most consequential and hardest to re-derive from code alone.
