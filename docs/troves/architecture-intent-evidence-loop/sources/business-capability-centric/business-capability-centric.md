---
source-id: "business-capability-centric"
title: "Business Capability Centric"
type: web
url: "https://martinfowler.com/bliki/BusinessCapabilityCentric.html"
fetched: 2026-03-29T00:00:00Z
hash: "a3d3010a29fc1b7d6001033592c6581ed028fccdc34ca4ab7d7b96c3ff568cfd"
---

# Business Capability Centric

**Author:** Sriram Narayan
**Published:** 8 June 2016
**Source:** martinfowler.com
**Capability:** Cap 8 -- Design from the Business (Go Deeper)

## Content

A business-capability centric team is one whose work is aligned long-term to a certain area of the business. The team lives as long as the business-capability is relevant. This contrasts with project teams that only last as long as project scope delivery.

### Examples of Business Capabilities

- **E-commerce**: buying and merchandising, catalog, marketing, order management, fulfilment, customer service
- **Insurance**: policy administration, claims administration, new business
- **Telecom**: network management, service provisioning and assurance, billing, revenue management

These may be further divided into fine-grained capabilities for manageable team sizes.

### "Think-It, Build-It, Run-It" Teams

Business-capability centric teams own problems end-to-end. They don't hand over to other teams for testing, deploying, or supporting. They own the IT systems (applications, APIs, data) that primarily support their capability. Technology platforms may be shared across teams.

### Team Sizing and Portfolio Management

Team size is determined periodically based on IT strategy. This is a different kind of portfolio management: budget as team capacity allocated across long-lived business-capabilities, not funds allocated across short-lived projects. Teams need to be outcome-oriented to maximize potential.

### Boundary Drawing

Each team owns a cohesive subset of the application landscape. Some applications are cross-capability by nature (e.g., end-to-end customer journey). Outcome-orientation is a good guiding principle: can each parcel be held responsible for a business outcome expressed as a business metric?

### Conway's Law Alignment

Some worry that a single team managing several systems acts against Conway's Law. But Conway's law isn't against a single team being responsible for multiple related components. It allows for high cohesion of component ownership and low coupling between teams.

### Implications for Headcount

Business-capability centric configuration may require slightly greater headcount than project-centric. However, project-centric models compromise architectural integrity because each project team only cares about delivering its scope by the promised date. Shortcuts include:
- Ad-hoc integrations with dependent systems
- Integrating with systems meant to be sunsetted
- Tacking on quick-and-dirty code

### Strategic and Utility Capabilities

Capabilities may be categorized as strategic or utility. Utility capabilities (payroll, accounting, HR) are often delivered with packaged software -- "think-it, buy-it, configure-it, run-it" teams. Strategic capabilities warrant higher investment in custom development.

## Relevance to Intent-Evidence Loop

Business-capability centric organization is the **organizational expression of bounded contexts**. When teams are aligned to capabilities, the intent encoded in their architecture naturally serves a coherent business purpose.

The project-centric failure mode (compromising architectural integrity because teams don't live with consequences) illustrates what happens when the **feedback loop is broken**: execution produces evidence of shortcuts, but because the project team disbands, there's no reconciliation mechanism to correct the drift. Long-lived capability teams provide the sustained attention that reconciliation requires.

For swain as a solo developer project, business capabilities still matter at a smaller scale: the Vision hierarchy should align with the capabilities that swain provides (intent management, execution tracking, evidence collection, reconciliation).
