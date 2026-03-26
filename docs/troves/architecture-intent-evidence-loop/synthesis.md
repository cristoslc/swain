# Architecture Intent-Evidence Loop: Trove Synthesis

## Core Thesis

Swain's foundational architecture rests on a four-phase loop: **Intent -> Execution -> Evidence -> Reconciliation -> Intent**. This loop is not a process framework — it's a claim about what kinds of things exist in a project management system and how they relate.

- **Intent** — what has been decided (specs, ADRs, component catalog, architectural constraints)
- **Execution** — where intent meets reality (agents implementing, building, migrating)
- **Evidence** — what can be observed (git history, test results, dependency graphs, session outputs)
- **Reconciliation** — structured comparison of intent vs. evidence (drift reports, retros, compliance checks)

## Key Findings

### Architecture matters MORE in the agentic era, but differently

Traditional justifications (human navigability, cognitive load management) matter less. New justifications:
1. Non-functional properties (operability, debuggability, failure modes) are structural, not behavioral — tests don't cover them
2. Architecture encodes WHY behind structural decisions — without it, agents introduce correct-but-structurally-wrong solutions
3. Chesterton's fence scales with agent velocity — 10x code production means 10x blast radius when removing things with non-obvious purpose
4. Data contracts verify external behavior only — boundary violations, coupling decisions, and resilience patterns are architectural

### Architecture documents are amortized derivation

Re-derivation from code is expensive (tokens, time, reliability). Architecture documents are caches of structural understanding. The cache validity problem is where reconciliation becomes important. The agentic era makes the cache more valuable because agents consume structural understanding at higher volume.

### The four-vision structure is lopsided

Stress-testing one vision per loop leg revealed:
- **Evidence (Observable Reality)** has the most independent gravity (9/10) — swain's biggest gap
- **Intent Authority** has real substance (7/10) but overlaps VISION-001
- **Reconciliation** is conceptually important (6/10) but defined by its dependencies
- **Execution** collapses into existing VISION-005 (4/10) — not enough independent mass

### The unified structure is stronger

One root vision naming the full loop, with boundary-focused initiatives/epics:
- Preserves the insight (the loop) as a single concept
- Decomposes work along boundaries where pain actually lives
- Avoids bureaucracy for a solo developer
- Initiatives for upstream boundaries (schema problems), Epics for downstream (deliverables)

### VISION-004 is inside the loop

Operator Cognitive Support is not orthogonal — the reconciliation->intent boundary is fundamentally about how many findings the operator can absorb per session. This needs explicit positioning.

## Related Troves

- `likec4` — LikeC4 architecture-as-code tool; its MCP server could serve as the graph query layer for the intent/evidence system
- `session-decision-support` — evidence pool for VISION-004
- `design-staleness-drift` — early reconciliation work

## Disciplines for Further Research

1. Ontology engineering — maintaining authoritative declarations alongside derived facts
2. Configuration management (systems engineering) — CMDB "catalog that doesn't drift" failure modes
3. Double-entry bookkeeping — 500 years of parallel representations + discrepancy surfacing
4. Control theory — feedback lag, gain, stability in reconciliation loops
5. Archival science — provenance, appraisal, context of creation vs. use
6. Ethnomethodology — invisible labor of maintaining records

## Open Questions

- Does Observable Reality deserve standalone vision status or is it an initiative under the unified root?
- Should VISION-004 be explicitly positioned inside the loop?
- Should VISION-005 absorb execution-fidelity concerns?
- What's the migration path for existing children of the current visions?
- Lightest-touch option: evolve VISION-001 with loop vocabulary rather than creating new visions?
