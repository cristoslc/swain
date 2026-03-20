---
source-id: well-architected-ddr-guide
type: web
url: https://www.well-architected-guide.com/documents/design-decision-records-ddrs-guide/
fetched: 2026-03-19
---

# Design Decision Records (DDRs) Guide

A Design Decision Record (DDR) is a tool used to document the key decisions made during the design and development of a project. By capturing the context, reasoning, and consequences of decisions, DDRs help teams maintain alignment, improve communication, and provide a historical record of how and why certain choices were made.

## DDR Structure

1. **Overview** — Title, Date, Status (Proposed/Accepted/Rejected/Superseded)
2. **Context** — Background summary + goals/objectives
3. **Decision** — Decision statement + alternatives considered (with pros/cons)
4. **Reasoning** — Rationale + evaluation criteria
5. **Consequences** — Impact, risks, trade-offs, mitigation strategies
6. **Follow-up** — Action items, review dates, related decisions

## Key Observations

- DDRs are structurally identical to ADRs (Architecture Decision Records) in the Nygard format
- The guide positions DDRs as covering "design and development" decisions broadly — not specifically UI/UX design
- Status lifecycle mirrors ADRs: Proposed → Accepted → Superseded
- The template includes "Alternatives Considered" with explicit pros/cons — same pattern as ADRs
- No differentiation between architectural decisions and interaction design decisions
