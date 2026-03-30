# Synthesis: TL Capability Map

## Overview

The TL Capability Map is a structured learning program for tech leads transitioning from application expertise to architectural thinking. It defines 11 capabilities organized in a deliberate dependency graph, each with situational framing, readiness criteria, practice exercises, and curated resources (80+ total across video, article, podcast, and book formats).

## Key Findings

### Capability structure follows a progression model

The 11 capabilities are not independent — they form a directed graph:
- **Gateway:** Cap 1 (Smell-Test Claims) is the entry point
- **Core analysis pair:** Cap 2 (Find Boundaries) + Cap 3 (Pressure-Test) are the analytical foundation
- **Operational extension:** Cap 4 (Think in Production) extends pressure-testing into day-2 concerns
- **Data discipline:** Cap 5 (Data Product Thinking) builds on boundary-finding — once you have boundaries, design what crosses them
- **Strategic context:** Cap 6 (Strategic Map) + Cap 7 (Scope the Problem) provide the business framing
- **Applied synthesis:** Cap 8 (Design from the Business) integrates strategic context and scoping into platform design
- **Capstone:** Cap 9 (Lead the Conversation) is the culmination — running working sessions, not just attending
- **Cross-cutting:** Cap 10 (Write to Drive Decisions) and Cap 11 (AI Partner) support all other capabilities

### Pedagogical approach: situation-based, not definition-based

Each capability is framed as a *situation* the learner will encounter ("someone says 'we need microservices for scalability'"), not as a topic to study. This grounds the learning in real work rather than abstract knowledge. The "You're Ready When" criteria are behavioral, not informational.

### Resource curation is opinionated and layered

Resources are split into "Start Here" (2-3 essentials) and "Go Deeper" (5-15 extended). The curation draws heavily from:
- **Mark Richards & Neal Ford** — Fundamentals of Software Architecture, Software Architecture: The Hard Parts
- **Ford, Parsons et al.** — Building Evolutionary Architectures (2nd ed)
- **Gregor Hohpe** — The Software Architect Elevator
- **Zhamak Dehghani** — Data Mesh
- **Martin Kleppmann** — Designing Data-Intensive Applications (2nd ed)
- **Will Larson** — An Elegant Puzzle
- **Simon Wardley** — Wardley Maps

### Themes across capabilities

| Theme | Capabilities | Core idea |
|-------|-------------|-----------|
| Trade-off analysis | 1, 3, 9 | Every architecture decision is a trade-off; "why" matters more than "how" |
| Boundary definition | 2, 5, 8 | Real boundaries own their data; test with data ownership, team alignment, cross-talk |
| Fitness functions | 3, 4 | Automated tests for architectural properties catch drift before crises |
| Business alignment | 6, 7, 8 | Capabilities (stable) -> Services (designed) -> Offerings (sold) |
| Communication as tool | 9, 10 | Writing drives decisions; vocabulary becomes natural through use, not memorization |
| AI skepticism | 11 | Treat AI as a junior colleague who's read everything but built nothing |

## Points of Agreement (across resources)

- Architecture is about trade-offs, not best practices
- Domain boundaries should be driven by data ownership and business context, not technical convenience
- Non-functional requirements are the real pressure on a design — vague NFRs are useless
- Observability and operability must be designed in, not added after
- Writing (ADRs, RFCs, scope statements) is a tool of influence, not documentation

## Gaps

- **No coverage of team dynamics** — Conway's Law is mentioned but team topology, cognitive load, and organizational design are not explicit capabilities
- **No hands-on coding exercises** — practice exercises are analytical (write an assessment, create a map) rather than implementation-based
- **Limited coverage of migration strategy** — Larson's "Migrations" chapter is referenced but there's no dedicated capability for executing a migration alongside a running system
- **Security architecture** — not addressed as a capability or cross-cutting concern
- **Cost modeling** — build-vs-buy is covered conceptually (Wardley) but no resources on actual cost analysis or TCO modeling
