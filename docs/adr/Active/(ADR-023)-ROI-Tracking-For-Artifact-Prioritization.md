---
title: "ROI Tracking For Artifact Prioritization"
artifact: ADR-023
track: standing
status: Active
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
linked-artifacts:
  - ADR-010
depends-on-artifacts: []
---

# ROI Tracking For Artifact Prioritization

## Context

Swain's prioritization model uses `priority-weight: high | medium | low` with a scoring formula of `unblock_count x priority_rank`. This captures structural leverage (what unblocks the most work) and operator-assigned priority (which direction matters more), but it has no concept of *value* or *cost*.

The result is that priority labels are arbitrary. "High" means "I think this is important" — but important relative to what? Two high-priority items are treated as equal even when one delivers transformative capability at low cost and the other is marginal work at high cost. When demand outpaces development capacity (which it always does for a solo operator), the system cannot distinguish "obviously worth doing" from "probably not worth doing."

## Decision

Add ROI (return on investment) tracking to the artifact hierarchy. This introduces two new frontmatter fields and an appraisal framework in PURPOSE.md.

### Appraisal dimensions

Value is assessed on three dimensions (defined in PURPOSE.md):

- **Capability** (0-3) — does this enable something the system cannot do today?
- **Efficiency** (0-3) — does this reduce ongoing cost?
- **Risk reduction** (0-3) — does this prevent or bound a potential loss?

Composite value is the sum of all three dimensions (range 0-9).

### New frontmatter fields

**`value-estimate`** — an object with keys `capability`, `efficiency`, `risk-reduction`, each scored 0-3. Available on VISION, INITIATIVE, EPIC, and SPEC. Cascades down the parent chain (nearest ancestor with a value wins, same as priority-weight).

**`cost-estimate`** — a t-shirt size (XS/S/M/L/XL) mapped to numeric values: XS=1, S=2, M=3, L=5, XL=8. Available on INITIATIVE, EPIC, and SPEC. Not on VISION — cost requires concrete scope to estimate. The scale is non-linear because large work carries disproportionate coordination overhead.

### ROI calculation

```
roi = composite_value / cost_numeric
```

Range: 0.0 (no value data) to 9.0 (maximum value, minimum cost). When no value-estimate exists on the artifact or any ancestor, ROI is 0.0 — treated as "no data," not "no value."

### Scoring integration

The recommendation formula becomes:

```
roi_multiplier = max(1.0, roi) if roi > 0.0 else 1.0
score = unblock_count x priority_rank x roi_multiplier
```

Key properties:
- **Backwards compatible.** When no ROI data exists, `roi_multiplier = 1.0` and the formula reduces to the original.
- **Amplifying, not replacing.** ROI multiplies the existing score — it rewards high-return work without penalizing work that hasn't been appraised yet.
- **ROI as tiebreaker.** When scores are equal, higher ROI sorts first, before sort_order and decision debt.

### Example

| Artifact | Unblocks | Priority Rank | Value (C+E+R) | Cost | ROI | Score |
|----------|----------|---------------|---------------|------|-----|-------|
| SPEC-A | 3 | 2 | 2+3+1=6 | M(3) | 2.0 | 3x2x2.0 = 12.0 |
| SPEC-B | 3 | 2 | 1+0+0=1 | L(5) | 0.2 | 3x2x1.0 = 6.0 |
| SPEC-C | 3 | 2 | (none) | (none) | 0.0 | 3x2x1.0 = 6.0 |

SPEC-A ranks first — same structural leverage, same priority, but much higher return. SPEC-B and SPEC-C score the same because ROI below 1.0 floors to 1.0 (low ROI never penalizes).

## Alternatives Considered

**Numeric priority instead of ROI.** Replace h/m/l with a 1-10 scale. Rejected because a single number still collapses value and cost into an opaque judgment. Two fields that compose into a ratio are more honest and auditable.

**Effort estimation in hours/days.** Use time estimates instead of t-shirt sizes. Rejected because time precision is false for solo-operator work. T-shirt sizes express relative magnitude without pretending to be accurate.

**Mandatory ROI on all artifacts.** Require value and cost estimates everywhere. Rejected because it creates friction. Most artifacts inherit from their parent chain. Explicit estimates belong where the operator has a clear judgment — usually at the Initiative or Epic level.

**ROI as a filter instead of a multiplier.** Only show items above an ROI threshold. Rejected because it hides work from the operator. Better to rank by ROI and let the operator see the full picture.

## Consequences

**Positive:**
- Prioritization is grounded in value and cost, not arbitrary labels.
- The three appraisal dimensions force honest assessment — "why does this matter?" has a structured answer.
- Fully backwards compatible — existing artifacts without ROI data score exactly as before.
- ROI cascades through the parent chain, so appraising a Vision or Initiative automatically benefits all children.
- The operator can override at any level, same as priority-weight.

**Accepted downsides:**
- Two new optional fields add schema complexity. Mitigated by making them optional and cascading.
- Value assessment is still subjective. This is by design — the goal is structured subjectivity, not false objectivity.
- The non-linear cost scale (XS=1 through XL=8) is a modeling choice that may need tuning. The Fibonacci-adjacent progression is defensible but not universal.
- ROI multiplier floors at 1.0, meaning low-ROI work is never penalized below baseline. This is conservative — an operator who wants to deprioritize low-ROI work should set `priority-weight: low` explicitly.

## Lifecycle

| Phase | Date | Notes |
|-------|------|-------|
| Active | 2026-04-06 | Initial creation |
