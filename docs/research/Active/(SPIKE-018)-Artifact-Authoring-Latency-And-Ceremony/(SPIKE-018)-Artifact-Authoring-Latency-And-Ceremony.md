---
title: "Artifact Authoring Latency and Ceremony Audit"
artifact: SPIKE-018
track: container
status: Active
author: cristos
created: 2026-03-14
last-updated: 2026-03-14

question: "Which steps in the swain-design authoring workflow contribute the most latency and token cost, and which can be safely skipped or deferred for low-complexity artifacts?"
gate: Pre-EPIC-014
risks-addressed:
  - Ceremony cost exceeds value for simple artifacts, reducing willingness to file
  - Skipping the wrong checks causes quality regressions
evidence-pool: ""
---

# Artifact Authoring Latency and Ceremony Audit

## Question

Which steps in the swain-design authoring workflow contribute the most latency and token cost, and which can be safely skipped or deferred for low-complexity artifacts?

## Go / No-Go Criteria

**GO** (proceed to EPIC-014 implementation):
- At least one step accounts for ≥30% of authoring cost and is safely skippable for ≥1 artifact type/complexity tier
- A clear, non-arbitrary definition of "low complexity" artifact emerges (e.g., bug SPEC with no parent epic, no linked artifacts)

**NO-GO** (abandon EPIC-014):
- Every step is load-bearing for every artifact type — no safe fast path exists
- Complexity tiers are too context-dependent to define statically

## Pivot Recommendation

If no fast path emerges: instead of tiered ceremony, invest in script performance (parallelizing adr-check + specgraph scope call, caching specwatch results) so the full ceremony is faster rather than shorter.

## Findings

*(Populated during Active phase.)*

### Dimensions to measure

1. **Per-step cost** — token and wall-clock time for each authoring step:
   - Number scan (`find docs/...`)
   - Template read
   - Artifact write
   - `adr-check.sh` run
   - `specgraph.sh scope` run
   - `specwatch.sh scan` run
   - Index read + update
   - Git commit (transition)
   - Git commit (hash stamp)

2. **Skippability by type** — for each step, which artifact types/complexity tiers can safely skip it:
   - Bug SPECs: no parent epic, no vision alignment, known fix — which checks add value?
   - Feature SPECs: alignment check is load-bearing; adr-check is advisory
   - Epics: all checks warranted
   - ADRs: alignment check adds noise (ADRs are cross-cutting by design)

3. **Two-commit stamp necessity** — is the separate hash-stamp commit necessary for all artifact types, or only for artifacts that will be linked from other artifacts?

4. **Index refresh cost** — the index read + write + commit is ~3 tool calls per artifact. Is a lazy-refresh acceptable (e.g., update index only when queried)?

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Initial creation |
| Active | 2026-03-14 | 2f5cd7a | Investigation begins |
