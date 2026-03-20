---
source-id: productic-designing-against-drift
type: web
url: https://www.productic.net/leadership/design-ops/designing-against-drift-when-good-products-decay/
fetched: 2026-03-19
---

# Designing Against Drift: When Good Products Decay

Source: Productic (2026)

## Definition

Drift occurs when the gap between stated intent and actual implementation grows incrementally, often invisibly, until the original vision becomes unrecognisable. It's not a sudden break — it's compound decay.

## Drift Manifestations

- **Design systems**: component proliferation, spacing inconsistencies, duplicate implementations
- **Data models**: metrics redefined differently by different teams
- **Roadmaps**: feature accretion dilutes original strategy
- **AI systems**: probability overwhelms intent — systems revert to training data patterns

## Why Drift Is Inevitable

- **Entropy is default** — order requires energy
- **Local optimization beats global vision** — each team solves their immediate problem
- **Compound effect** — small deviations multiply
- **No single moment of failure** — no alarm triggers

## The Airbnb Example

By 2016, Airbnb discovered fragmentation everywhere after teams independently made locally-optimal decisions. Karri Saarinen led the DLS (Design Language System) consolidation: "We wound up with many different kinds with some inconsistencies" even in core components. Required dedicated team and months of focused work.

## Prevention Framework: "Encode Intent as Constraints"

1. **Design tokens** — not just values but constraints (reject out-of-range values)
2. **Schema validation** — data definitions enforced, not just documented
3. **Decision records** — decisions encoded, not just remembered
4. **Version control** — semantic versioning so teams know when to upgrade

## Drift Detection Tools

- CSS Stats — colour and typography inconsistencies
- Design system linters — token usage enforcement
- Schema validation tools — data consistency
- Component usage analytics — design system adoption tracking
- Automated testing — UI consistency
- Monitoring dashboards — unique colour values, component proliferation, pattern adherence

## Key Insight: "Encode Intent as Constraints"

The most important takeaway: intent must be encoded as machine-checkable constraints, not just documented as human-readable prose. Decision records capture the *why*, but constraints enforce the *what*.
