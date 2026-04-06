---
title: "Chart Is The Canonical Hierarchy Interface"
artifact: ADR-022
track: standing
status: Active
author: cristos
created: 2026-04-02
last-updated: 2026-04-06
linked-artifacts:
  - INITIATIVE-002
  - EPIC-013
  - EPIC-056
  - DESIGN-013
  - SPEC-239
  - SPEC-241
depends-on-artifacts: []
evidence-pool: ""
---

# Chart Is The Canonical Hierarchy Interface

## Context

Swain now exposes graph queries through `chart`. The old `specgraph.sh` name still exists, but `chart.sh` is the preferred entry point.

The new hierarchy materializer needs one upstream interpreter. It must not parse frontmatter or re-create parent rules on its own. If it does, Swain gets two hierarchy engines that can drift.

## Decision

`chart` is the canonical command surface for hierarchy queries and normalized graph output. Any feature that needs resolved hierarchy must consume `chart` output instead of parsing frontmatter or calling legacy shell wrappers.

The hierarchy materializer is a projection layer only:

- it consumes normalized hierarchy data from `chart`
- it writes lifecycle-scoped child-view symlinks and `_unparented/` repair surfaces
- it does not interpret frontmatter directly
- it does not implement a second graph engine

## Alternatives Considered

**Keep saying "specgraph" everywhere and let new features call `specgraph.sh`.** Rejected because the repo already positions `chart` as the canonical CLI. New work should not deepen the split between current interface and legacy alias.

**Let the materializer parse frontmatter directly.** Rejected because it duplicates parent resolution, invalid-parent handling, and future hierarchy changes in a second place.

**Make the materializer call either `chart` or `specgraph.sh` opportunistically.** Rejected because compatibility shims are not a stable architectural contract.

## Consequences

Positive:

- One public graph interface for operators and scripts
- One hierarchy interpreter upstream of all materialized views
- Future hierarchy changes land in one place

Negative:

- `chart` must expose stable machine-readable output
- Older docs that say "specgraph CLI" will describe legacy naming, not the preferred surface

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-02 | — | Initial creation |
| Active | 2026-04-06 | 30391a5a | Approved by operator |
