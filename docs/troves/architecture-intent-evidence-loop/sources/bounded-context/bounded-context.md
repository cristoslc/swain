---
source-id: "bounded-context"
title: "Bounded Context"
type: web
url: "https://martinfowler.com/bliki/BoundedContext.html"
fetched: 2026-03-29T00:00:00Z
hash: "1e8d864a4ed1370ba34542891cdd51d4dee14b4ddbbe73387d63c9b0fb5746a7"
---

# Bounded Context

**Author:** Martin Fowler
**Published:** 15 January 2014
**Capability:** Cap 2 -- Find Boundaries

## Content

Bounded Context is a central pattern in Domain-Driven Design. It is the focus of DDD's strategic design section which is all about dealing with large models and teams. DDD deals with large models by dividing them into different Bounded Contexts and being explicit about their interrelationships.

DDD is about designing software based on models of the underlying domain. A model acts as a Ubiquitous Language to help communication between software developers and domain experts. It also acts as the conceptual foundation for the design of the software itself -- how it's broken down into objects or functions. To be effective, a model needs to be unified -- that is to be internally consistent so that there are no contradictions within it.

As you try to model a larger domain, it gets progressively harder to build a single unified model. Different groups of people will use subtly different vocabularies in different parts of a large organization. The precision of modeling rapidly runs into this, often leading to a lot of confusion. Typically this confusion focuses on the central concepts of the domain.

Early in my career I worked with an electricity utility -- here the word "meter" meant subtly different things to different parts of the organization: was it the connection between the grid and a location, the grid and a customer, the physical meter itself (which could be replaced if faulty). These subtle polysemes could be smoothed over in conversation but not in the precise world of computers. Time and time again I see this confusion recur with polysemes like "Customer" and "Product".

In those younger days we were advised to build a unified model of the entire business, but DDD recognizes that we've learned that "total unification of the domain model for a large system will not be feasible or cost-effective" (Eric Evans, Domain-Driven Design). So instead DDD divides up a large system into Bounded Contexts, each of which can have a unified model -- essentially a way of structuring Multiple Canonical Models.

Bounded Contexts have both unrelated concepts (such as a support ticket only existing in a customer support context) but also share concepts (such as products and customers). Different contexts may have completely different models of common concepts with mechanisms to map between these polysemic concepts for integration. Several DDD patterns explore alternative relationships between contexts.

Various factors draw boundaries between contexts. Usually the dominant one is human culture, since models act as Ubiquitous Language, you need a different model when the language changes. You also find multiple contexts within the same domain context, such as the separation between in-memory and relational database models in a single application. This boundary is set by the different way we represent models.

DDD's strategic design goes on to describe a variety of ways that you have relationships between Bounded Contexts. It's usually worthwhile to depict these using a context map.

### Further Reading

The canonical source for DDD is Eric Evans's book *Domain-Driven Design*. Bounded Context opens part IV (Strategic Design).

Vaughn Vernon's *Implementing Domain-Driven Design* focuses on strategic design from the outset. Chapter 2 talks in detail about how a domain is divided into Bounded Contexts and Chapter 3 is the best source on drawing context maps.

Verraes and Wirfs-Brock talk about some of the subtleties of delineating Bounded Contexts, in particular where a context may need to split for reasons that are as much about history and human relationships as they are about domain concepts.

William Kent's *Data and Reality* contains a short description of the polyseme of Oil Wells that remains relevant.

Eric Evans describes how an explicit use of a bounded context can allow teams to graft new functionality in legacy systems using a bubble context.

## Relevance to Intent-Evidence Loop

Bounded contexts are fundamentally about managing the boundaries of **Intent** -- where one model's vocabulary ends and another's begins. In swain's architecture, this maps directly to the component catalog and how different parts of the system maintain internally consistent models while mapping between them at boundaries.

The polyseme problem (same word, different meanings) is exactly the kind of structural concern that tests don't catch but architecture must encode -- reinforcing the trove's finding that architecture matters MORE in the agentic era because agents need explicit boundary definitions to avoid introducing structurally-wrong solutions.
