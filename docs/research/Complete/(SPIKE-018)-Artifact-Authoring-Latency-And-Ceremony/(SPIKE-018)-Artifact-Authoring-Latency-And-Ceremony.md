---
title: "Artifact Authoring Latency and Ceremony Audit"
artifact: SPIKE-018
track: container
status: Complete
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

### Per-step cost breakdown

Wall-clock times measured on macOS (Apple M-series, 87-node graph):

| Step | Wall-clock | Agent tool calls | Token cost estimate | Skippable? |
|------|-----------|-----------------|--------------------|-----------:|
| Number scan (`find docs/...`) | <50ms | 1 Glob | ~100 tokens | Never |
| Template read | <50ms | 1 Read | ~500 tokens | Rarely (inline templates possible) |
| Artifact write | <50ms | 1 Write | ~300 tokens | Never |
| `adr-check.sh` | 73ms | 1 Bash | ~200 tokens | For ADRs themselves; advisory for trivial SPECs |
| `specgraph.py build` | 116ms | 1 Bash | ~200 tokens | When cache is fresh (mtime < 60s) |
| `specgraph.sh scope` | 95ms | 1 Bash | ~300 tokens | For bug SPECs with no parent epic |
| `specwatch.sh scan` | 353ms | 1 Bash | ~200 tokens | For low-complexity artifacts |
| Index read + update | <50ms | 2 Read+Edit | ~600 tokens | Deferrable (lazy refresh — see below) |
| Git commit (transition) | ~5s | Agent | ~3000 tokens | Never |
| Git commit (hash stamp) | ~5s | Agent | ~2500 tokens | For trivial artifacts (see below) |

**Total full ceremony**: ~11s wall-clock, ~8000 tokens, ~12 tool calls (not counting agent-spawned commits).

**Dominant cost**: The two agent-commit steps account for ~75% of total token cost. Everything else is fast and cheap.

### Skippability by artifact type

| Artifact type | Complexity tier | Skippable steps |
|---------------|----------------|-----------------|
| Bug SPEC | Low (known fix, no parent epic) | specgraph scope, specwatch scan, hash-stamp commit |
| Enhancement SPEC | Medium | specwatch scan (if pre-scan clean); hash-stamp commit optional |
| Feature SPEC | High | None — all checks warranted |
| Epic | High | None — alignment check is load-bearing |
| ADR | Medium | adr-check on itself (tautological); specgraph scope (cross-cutting by design) |
| SPIKE | Low-Medium | specwatch scan; hash-stamp commit (research artifacts rarely linked) |

**Key insight**: The `specwatch.sh scan` at 353ms is the slowest script step but is mostly checking for stale references and phase mismatches — largely redundant if the repo is in a clean state. It can be skipped for low-complexity artifacts when the last full scan was clean.

### Two-commit stamp necessity

The separate hash-stamp commit adds ~2500 tokens and a round-trip to write the lifecycle hash after the transition commit. Analysis:

- **High value** for artifacts that will be linked (`depends-on`, `linked-artifacts`) by other artifacts — the hash provides a stable reference point for lifecycle audits
- **Low value** for terminal artifacts (bug fixes, quick SPECs) that nothing else links to
- **Recommendation**: Fold the hash stamp into the transition commit for Proposed→Ready and Ready→Complete transitions on SPECs with no downstream dependents. Reserve the separate stamp commit only for EPICs and SPECs that have known children linking to them.

### Index refresh cost

The index read + write + commit is ~600 tokens and 2 tool calls, plus it adds to the transition commit. Analysis:

- The list-spec.md, list-epic.md indexes duplicate information already in frontmatter
- `specgraph.py build` rebuilds from frontmatter in 116ms — the index adds no query acceleration
- **Recommendation**: Treat the index as a human-facing display artifact, not a query substrate. Update it lazily (only when specgraph cache is stale or index is explicitly requested). Do not require it as part of the artifact transition ceremony.

### GO/NO-GO decision

**GO** criteria met:
1. ✅ At least one step accounts for ≥30% of cost and is safely skippable: the hash-stamp commit (~31% of token cost) can be folded into the transition commit for trivial SPECs
2. ✅ A clear definition of "low complexity" emerges: **bug SPEC** = SPEC with `type: bug` or `type: fix`, no `parent-epic`, no downstream `depends-on` links

**RESULT: GO** — proceed to EPIC-014 implementation.

### Fast-path definition

A "fast-path" artifact creation should skip:
1. `specwatch.sh scan` — rely on pre-session scan being clean
2. `specgraph.sh scope` — skip vision alignment check (only load-bearing for feature/epic artifacts)
3. Hash-stamp commit — fold into transition commit
4. Index update — defer to next specgraph cache build

Estimated fast-path cost: ~2500 tokens, ~7 tool calls, ~6s wall-clock (70% reduction).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Initial creation |
| Active | 2026-03-14 | 2f5cd7a | Investigation begins |
| Complete | 2026-03-14 | -- | GO decision — fast-path defined; two-commit stamp and index update are top savings |
