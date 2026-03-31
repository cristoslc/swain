---
source-id: "microservice-boundaries"
title: "Identify Microservice Boundaries"
type: web
url: "https://learn.microsoft.com/en-us/azure/architecture/microservices/model/microservice-boundaries"
fetched: 2026-03-29T00:00:00Z
hash: "d88a3d326187f54d23ce918e149559b434829cd84be5216f38c97901aeae3e19"
---

# Identify Microservice Boundaries

**Source:** Azure Architecture Center (Microsoft)
**Capability:** Cap 2 -- Find Boundaries (Go Deeper)

## Content

Architects and developers struggle to define the correct size for a microservice. Guidance often emphasizes avoiding extremes, but that advice can be vague. Starting from a carefully designed domain model makes it easier to define the correct size and scope.

### From Domain Model to Microservices

A systematic approach:

1. **Start with a bounded context.** Functionality in a microservice shouldn't span more than one bounded context. If a microservice mixes different domain models, refine your domain analysis.

2. **Examine aggregates.** Aggregates are often good candidates for microservices because:
   - Derived from business requirements, not technical concerns
   - High functional cohesion
   - A boundary of persistence
   - Loosely coupled

3. **Consider domain services.** Stateless operations across multiple aggregates are good microservice candidates. Typical example: a workflow that includes several microservices.

4. **Consider nonfunctional requirements.** Team size, data types, technologies, scalability, availability, and security requirements may cause you to split or merge microservices.

### Validation Criteria

After identifying microservices, validate against:
- **Single responsibility**: Each service has one
- **No chatty calls**: Excessive inter-service communication suggests wrong boundaries
- **Small enough**: Can be built by a small team working independently
- **No deployment coupling**: Each service deployable independently
- **Not tightly coupled**: Can evolve independently
- **Data consistency**: Service boundaries designed to avoid data integrity problems

### Drone Delivery Example

The article walks through a running example:
- **Delivery** and **Package** are obvious microservice candidates (aggregates)
- **Scheduler** and **Supervisor** are domain services coordinating other microservices
- **Drone** and **Account** belong to other bounded contexts -- options include direct calls or mediating microservices
- **Ingestion** service added for nonfunctional reasons (load leveling)
- **Delivery History** separated because data storage requirements for historical analysis differ from in-flight operations

### Cross-Boundary Considerations

When dealing with other bounded contexts, consider:
- Network overhead of direct calls
- Whether the other context's data schema suits this context
- Whether an anti-corruption layer is needed for legacy systems
- Team structure and communication cost

### Pragmatic Advice

Domain-driven design is an iterative process. When in doubt, start with more coarse-grained microservices. Splitting is easier than refactoring functionality across existing microservices.

## Relevance to Intent-Evidence Loop

This article provides a **practical decision framework** for the boundary-finding that the Intent phase requires. The validation criteria are essentially a checklist of intent qualities: each criterion can be checked against evidence from the running system.

The pragmatic "start coarse, split later" advice aligns with the trove's finding about "good enough" architecture: initial intent should be broad, with reconciliation (comparing actual coupling, chattiness, deployment friction against intent) driving refinement over time.

The nonfunctional requirements step is particularly relevant -- it shows how evidence from production (throughput needs, data storage patterns) feeds back into boundary decisions, completing the loop.
