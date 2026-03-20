---
source-id: microsoft-decision-log
type: web
url: https://microsoft.github.io/code-with-engineering-playbook/design/design-reviews/decision-log/
fetched: 2026-03-19
---

# Design Decision Log — Microsoft Engineering Fundamentals Playbook

Microsoft recommends tracking design decisions as Architecture Decision Records (ADRs) per Michael Nygard's format. They do not distinguish between "architecture" and "design" decisions — all significant decisions use the same ADR format.

## Key Points

- ADRs track changes even as team composition changes over time
- Context and consequences are documented alongside the decision
- Status lifecycle: Proposed → Accepted → Deprecated → Superseded
- ADRs can incorporate trade studies and engineering feasibility spikes
- Stored in version control (git), often in `doc/adr/`
- A `decision-log.md` provides an executive summary table pointing to individual ADRs
- ADRs can be submitted as PRs in "Proposed" status for team review before acceptance

## Implication for DDR Question

Microsoft's playbook does NOT create a separate "DDR" artifact type. It uses ADRs for all decisions including design decisions. This aligns with the industry consensus that decision records are a general-purpose pattern, not domain-specific.
