---
source-id: "translating-quality-attributes"
title: "Lesson 37: Translating Quality Attributes to Business Concerns"
type: media
url: "https://developertoarchitect.com/lessons/lesson37.html"
fetched: 2026-03-29T00:00:00Z
hash: "c43c53d019fe8962d7782198589220067745783baf918e84639a2aa57f80d7e1"
---

# Lesson 37: Translating Quality Attributes to Business Concerns

**Instructor:** Mark Richards
**Format:** Video lesson (~10 min)
**Capability:** Cap 3 -- Pressure-Test

## Content

Mark Richards addresses a critical communication gap in software architecture: the disconnect between how architects and business stakeholders discuss project goals.

### The Core Problem

- Architects talk in "-ilities" (scalability, reliability, maintainability, availability)
- Business stakeholders talk in terms of business needs (revenue, customer satisfaction, time-to-market, risk)
- This linguistic divide creates misalignment between architectural decisions and actual business objectives

### The Translation Framework

Richards demonstrates how to convert technical quality attributes into business language:

| Quality Attribute | Business Translation |
|---|---|
| Scalability | "Can we handle Black Friday traffic without turning away customers?" |
| Availability | "How much revenue do we lose per minute of downtime?" |
| Performance | "Will customers abandon their cart if the page takes too long?" |
| Maintainability | "How quickly can we add the features our competitors are shipping?" |
| Security | "What's our exposure if customer data is breached?" |

### Why Translation Matters

- Business stakeholders cannot prioritize what they don't understand
- Without translation, architects make priority decisions unilaterally
- When business understands the trade-offs in their own language, they can make informed decisions
- This creates alignment between architectural investment and business value

### The Architect as Translator

- Effective architects are skilled translators between technical and business domains
- Translation is bidirectional: architects must also understand business constraints in technical terms
- The quality of architectural decisions depends on the quality of this translation

### Referenced Resources

- *Fundamentals of Software Architecture* by Richards and Ford
- Software Architecture Monday video series

## Relevance to Intent-Evidence Loop

This lesson connects directly to the **Intent** phase: architecture intent must be expressed in terms both technical teams and business stakeholders can understand. If intent is encoded only in technical language, the reconciliation phase cannot involve business stakeholders in validating whether the architecture serves its purpose.

The translation problem also explains why the trove found that "architecture documents are amortized derivation" -- the translated understanding of WHY a quality attribute matters is expensive to re-derive and should be cached in the architectural record.
