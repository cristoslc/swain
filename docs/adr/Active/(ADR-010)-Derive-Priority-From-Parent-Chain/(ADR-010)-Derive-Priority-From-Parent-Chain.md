---
title: "Derive Priority From Parent Chain"
artifact: ADR-010
track: standing
status: Active
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
linked-artifacts:
  - ADR-009
  - INITIATIVE-013
  - INITIATIVE-008
  - INITIATIVE-010
  - VISION-001
  - VISION-002
  - VISION-003
depends-on-artifacts: []
trove: ""
---

# Derive Priority From Parent Chain

## Context

The prioritization layer uses a three-bucket `priority-weight` model (`high`/`medium`/`low`). The recommendation engine scores decisions as `unblock_count × vision_weight`, with vision weight cascading down through initiatives as a flat inheritance — every artifact under a `high` vision gets the same weight.

This creates two problems:

1. **No intra-tier differentiation.** When multiple initiatives under the same vision are all `high`, the model cannot express which matters more. The only tiebreakers are decision debt and artifact ID, neither of which reflects operator intent.

2. **No compositional signal.** An initiative serving two high-priority visions should rank higher than one serving a single high-priority vision, but the flat cascade model doesn't capture this. Multi-parent relationships (an initiative under multiple visions) lose signal because only one weight is inherited.

## Decision

Replace the flat weight cascade with a **recursive additive model**. Each artifact declares a local weight via the existing `priority-weight` field (high/medium/low, mapped to 1/0/-1). The effective `priority-rank` is computed — never stored — by summing local weights up the entire ancestry chain.

### Mapping

```yaml
priority-weight: high    →  +1
priority-weight: medium  →   0  (default when omitted)
priority-weight: low     →  -1
```

### Formula

```
priority_rank(artifact) = local_weight(self) + sum(priority_rank(p) for p in parents)
```

This is recursive: each parent's rank already includes its own ancestors. The computation walks the full parent chain to the vision layer.

### Scoring

The recommendation engine uses the computed rank:

```
score = unblock_count × max(1, priority_rank)
```

Floor of 1 ensures negative-rank artifacts still score (just minimally), rather than being zeroed out or inverted.

### Multi-parent support

Artifacts with multiple parents sum all parents' ranks. An initiative serving two visions accumulates weight from both. This is the key compositional property: artifacts at the intersection of multiple strategic directions naturally rank higher.

`parent-vision` (and conceptually other parent fields) becomes a list to support this. Specgraph resolves all parent edges when computing rank.

### Examples

| Chain | Computation | Rank |
|-------|------------|------|
| VISION-001(high) → INIT-001(high) → EPIC(medium) → SPEC(high) | 1+1+0+1 | 3 |
| VISION-001(high) → INIT-005(high) → EPIC(medium) → SPEC(medium) | 1+1+0+0 | 2 |
| VISION-001(high) + VISION-002(high) → INIT-010(high) | 1+1+1 | 3 |
| VISION-003(high) → INIT-013(low) | 1+(-1) | 0 |
| VISION-001(high) → INIT-015(high) → EPIC(low) | 1+1+(-1) | 1 |

INIT-001's descendants (rank 2+ before the spec's own weight) naturally sort above INIT-005's descendants (also rank 2 at the initiative level) only when downstream artifacts differentiate — which is exactly how it should work. The operator's intent is expressed by setting local weights at whatever level matters.

### Defaults and migration

- Omitted `priority-weight` = medium = 0. Existing artifacts contribute nothing to the sum — current behavior is preserved.
- No new frontmatter fields. The existing `priority-weight` field is the only input.
- `priority-rank` is never stored in frontmatter — it is computed by specgraph on demand.
- No migration required. All existing artifacts default to 0 and the sum-based model produces identical relative ordering to the current flat cascade for single-parent chains.

## Alternatives Considered

**Tier-base + additive bonus (ADR-009 v1).** Widened tier bases (10/20/30) with a separate `priority-rank` integer field as a bonus within each tier. Rejected because it introduced a second frontmatter field, required tier-inversion guards, and didn't capture multi-parent composition. The recursive model achieves the same differentiation with zero new fields.

**Ordered list in a config file.** Operator maintains a sorted list of initiative IDs; position = rank. Rejected because it lives outside the artifact, doesn't compose with the graph model, and makes priority invisible when reading individual artifacts.

**Numeric-only model (drop weight tiers).** Replace high/medium/low with a raw integer. Rejected because the labels carry semantic meaning ("this is parked" vs. "this is active") and the -1/0/1 mapping preserves that while still being computable.

**Cached rank in frontmatter.** Store the computed rank in each artifact to avoid recomputation. Rejected because cached values go stale when any ancestor's weight changes, requiring a cascade update mechanism. Specgraph already walks parent chains for unblock counts — adding a sum is trivial.

## Consequences

**Positive:**
- No new frontmatter fields — uses existing `priority-weight` with a new numeric mapping.
- Multi-parent artifacts naturally accumulate strategic weight from all ancestors.
- Operators express intent at whatever level matters (vision, initiative, epic, or spec) and the math composes.
- Zero migration: omitting weights everywhere produces rank 0 for all artifacts, falling back to pure leverage-based ranking.
- Computed rank means no stale cached values to maintain.

**Accepted downsides:**
- The numeric mapping changes from high=3/medium=2/low=1 to high=1/medium=0/low=-1. Code that hardcodes the old values (specgraph scoring, swain-status rendering) needs updating.
- Negative ranks are possible (e.g., a low artifact under a low vision = -2). The `max(1, priority_rank)` floor in scoring handles this, but operators may find negative ranks unintuitive if exposed.
- Multi-parent support requires specgraph changes to accept list-valued `parent-vision` and sum across all parent edges.
- Cycle detection becomes necessary if many-to-many parent relationships are allowed at multiple levels. Specgraph must guard against infinite recursion in rank computation.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | Initial creation (tier-base + bonus model) |
| Active | 2026-03-20 | Revised: recursive ancestry summation replaces tier-base model |
