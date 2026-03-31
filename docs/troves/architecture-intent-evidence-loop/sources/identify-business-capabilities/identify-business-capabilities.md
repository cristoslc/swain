---
source-id: "identify-business-capabilities"
title: "Identify Business Capabilities"
type: web
url: "https://martinfowler.com/articles/patterns-legacy-displacement/identify-business-capabilities.html"
fetched: 2026-03-29T00:00:00Z
hash: "df11f1d3fc8b000ae33d7d4504707f4fa89e76b13026359d998ba0f3cf431843"
---

# Identify Business Capabilities

**Authors:** Ian Cartwright, Rob Horn, and James Lewis
**Source:** Patterns of Legacy Displacement (martinfowler.com)
**Status:** Draft/Stub
**Capability:** Cap 8 -- Design from the Business

## Content

*Note: This page is a stub/draft within the Patterns of Legacy Displacement series. Content is limited but the framing is valuable.*

A well known technique when faced by a large problem is to break it up into smaller ones. The question is what should the smaller parts be? Horizontal layers based around logical separation of presentation, processing, and data management have known problems.

In the article defining microservices, the suggestion is made to "Organise around Business Capabilities" -- but what is a business capability?

### What Is a Business Capability?

A business capability represents something a business does or needs to do to achieve its objectives. Capabilities are relatively stable even as the organization, processes, and technology change around them.

### Types of Business Capability

The article identifies multiple types but the stub does not fully elaborate.

### Identification Methods

- **Collaborative Workshops**: Bringing together business and technical stakeholders
- **Wardley Mapping**: Using Wardley Maps to identify and classify capabilities by their evolution stage
- **Static Analysis**: Examining existing systems to extract implicit capabilities
- **Low-fi Methods**: Lightweight approaches suitable for getting started
- **Iterate and Iterate Again**: Capability identification is iterative, not a one-time exercise

### When to Use It

Business capability identification is the recommended starting point for:
- Structuring teams and software around stable organizational concepts
- Legacy displacement and modernization efforts
- Breaking monoliths into services

### Part of Patterns of Legacy Displacement

Related patterns in the series:
- Critical Aggregator
- Divert the Flow
- Event Interception
- Extract Product Lines
- Feature Parity
- Legacy Mimic
- Revert to Source
- Transitional Architecture

## Relevance to Intent-Evidence Loop

Business capabilities represent the **highest-level intent** in a system -- what the business exists to do. Identifying them correctly is prerequisite to drawing boundaries (Cap 2) and ensuring architecture serves business needs rather than technical convenience.

For swain, business capabilities are relevant to the Vision -> Initiative hierarchy: Visions should align with business capabilities, and Initiatives should decompose work along capability boundaries. This ensures the intent encoded in the architecture serves the right master.
