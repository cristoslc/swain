---
source-id: "architect-elevator"
title: "The Architect Elevator -- Visiting the Upper Floors"
type: web
url: "https://martinfowler.com/articles/architect-elevator.html"
fetched: 2026-03-29T00:00:00Z
hash: "db263f279988e0e03a240a272379faabb6afebf7bd08084844b8f5d204b81ecb"
---

# The Architect Elevator -- Visiting the Upper Floors

**Author:** Gregor Hohpe
**Published:** 24 May 2017
**Capability:** Cap 8 -- Design from the Business

## Content

Many large organizations see their IT engine separated by many floors from the executive penthouse, which separates business and digital strategy from the vital work of carrying it out. The primary role of an architect is to ride the elevators between the penthouse and engine room, stopping wherever needed.

### The Architect Elevator Metaphor

The elevator spans from a company's engine room to the penthouse where upper management defines strategy. In traditional organizations, countless layers of management separate the upper floors from the lower ones. Information passed by taking the stairs suffers the "telephone game" effect: messages lose meaning as they pass through stations.

Two major problems for architects and developers:
1. Difficult to obtain support or funding for innovation because upper floors don't see the need
2. Even when new technologies are rolled out, existing processes and politics prevent realizing expected benefits

### Cloud-Ready Applications Demand Run-Time Architecture

Modern applications are expected to update with zero downtime, scale horizontally, and be resilient against hardware and software failure. Open source projects increasingly focus on application run-time management and monitoring (Docker, Kubernetes, Prometheus, Hystrix). Modern architects must be well-versed in run-time architecture considerations.

### Automate Software Manufacturing to Reduce Time-to-Value

Jack Reeves concluded a quarter century ago that coding is design work, not production work. What should be industrialized is the production of software: assembly and distribution of software artifacts. The real business benefit of cloud computing lies in a fully automated tool chain that minimizes the time a code change takes to reach production.

### Minimize Up-Front Decision Making

Making critical decisions at the beginning of a project is the worst time -- least is known. Project risk can be reduced by minimizing irreversible decisions. This can be achieved through flexible design, modularity that localizes scope of later changes, or fending off bureaucrats who demand up-front decisions.

### Sell Architecture Options

"Architecture is selling options." Financial options give the right, but not the obligation, to buy at a future date for a set price. Architecture options work similarly: invest so you can change your mind later at a known cost. In volatile technology and business environments, the value of architecture options goes up (per Black-Scholes model logic).

### Make Architecture Fit for Purpose

Architecture is rarely good or bad -- it's either fit or unfit for purpose. The purpose depends on context: commercial agreements, skills availability, installed base. Finding the appropriate context requires visiting many floors of the organization.

### Validate Decisions Through Feedback Loops

The "ivory tower" anti-pattern: architects define how developers should build software without developing any themselves, with no feedback on effectiveness or cost of decisions. Most complex systems can only function by means of feedback loops. Architects should find out whether "reusable" APIs really fostered reuse, whether common frameworks sped up development.

### Architect the Organization Alongside Technology Evolution

DevOps, cloud, and big data can only deliver full value if organizational structure evolves alongside technology. The behavior of organizational systems is subject to similar forces as technical systems:
- Synchronization points reduce throughput (meetings are the organizational equivalent)
- Layering manages complexity and gains flexibility but increases latency (true for both technical and organizational systems)

### Remove Blockers at the Right Floor

Many organizations equate "fast" with "low quality." You must explain that "quick" can mean "clean" before winning management's heart for frequent deployments. Changing behavior requires changing beliefs, which must happen at the upper levels.

### ArchOps: Build a Vertical Architecture Team

Build a "vertical" architecture team comprising architects from many levels: enterprise, strategic, solution, and technology specialists. Like attaching an elevator to an existing skyscraper that only has stairs.

## Relevance to Intent-Evidence Loop

Hohpe's elevator metaphor maps directly to the **translation problem** between architectural intent and business intent. Architecture intent that cannot be communicated to the penthouse will not receive investment. Business intent that cannot be translated to the engine room will not be implemented correctly.

The "architecture as options" framing connects to the loop: options are intent with explicit uncertainty. The value of options increases when the environment is volatile -- exactly when reconciliation (checking whether options should be exercised) becomes most important.

The feedback loop emphasis directly reinforces the trove's core thesis: without evidence flowing back from execution to inform intent revision, architectural decisions become ivory-tower pronouncements disconnected from reality.
