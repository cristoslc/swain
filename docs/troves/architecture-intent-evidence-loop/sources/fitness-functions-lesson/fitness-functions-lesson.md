---
source-id: "fitness-functions-lesson"
title: "Lesson 73: Architecture Fitness Functions"
type: media
url: "https://developertoarchitect.com/lessons/lesson73.html"
fetched: 2026-03-29T00:00:00Z
hash: "605549ac359c31a45935b1ce522ee0f2711ef14bef35cf357e26231b0ea3d878"
---

# Lesson 73: Architecture Fitness Functions

**Instructor:** Mark Richards
**Published:** November 18, 2019
**Format:** Video lesson (~10 min)
**Capability:** Cap 3 -- Pressure-Test

## Content

Mark Richards explains architecture fitness functions as tools for measuring architectural qualities. Fitness functions provide an objective measurement of architectural characteristics such as scalability, reliability, performance, and other quality attributes.

### What Are Architecture Fitness Functions?

- An architecture fitness function provides an objective, measurable assessment of some architectural characteristic
- They move architectural governance from subjective opinion to objective measurement
- Fitness functions can be automated, making continuous architectural validation possible

### Types of Fitness Functions

- **Atomic** fitness functions: test a single architectural characteristic in isolation
- **Holistic** fitness functions: test multiple characteristics together, accounting for trade-offs
- **Triggered** fitness functions: run on specific events (deployment, commit, etc.)
- **Continuous** fitness functions: run constantly, monitoring ongoing compliance

### Practical Applications

- Code metrics (cyclomatic complexity, coupling) as fitness functions for maintainability
- Performance benchmarks as fitness functions for responsiveness
- Dependency analysis as fitness functions for modularity
- Security scans as fitness functions for security posture

### Connection to Evolutionary Architecture

- Fitness functions are the key enabler of evolutionary architecture
- They allow architecture to change safely by providing continuous feedback on whether changes preserve desired properties
- Without fitness functions, architectural drift goes undetected until it causes problems

### Referenced Resources

- *Building Evolutionary Architecture* by Ford, Parsons, and Kua
- *Fundamentals of Software Architecture* by Richards and Ford
- *Software Architecture: The Hard Parts* by Richards, Ford, et al.

## Relevance to Intent-Evidence Loop

Fitness functions are the **bridge between Intent and Evidence**. They encode architectural intent as executable specifications, then produce evidence of conformance or violation. This is exactly the "reconciliation" mechanism the trove identifies as critical: structured comparison of what was intended vs. what can be observed.

In swain's context, fitness functions could serve as the automated component of the Reconciliation phase -- continuously checking whether the codebase conforms to architectural intent encoded in ADRs and the component catalog.
