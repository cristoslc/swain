---
title: "ROI Scoring Engine"
artifact: EPIC-066
track: container
status: Proposed
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
parent-vision: VISION-004
parent-initiative: INITIATIVE-021
priority-weight: ""
success-criteria:
  - graph.py parses appraisal-goals, serves-goals, and cost-estimate into the node dict
  - priority.py computes ROI from weighted value / cost
  - Leverage computed as transitive downstream ROI with cycle protection and depth decay
  - chart.sh recommend output shows roi, leverage, and served axes alongside existing fields
  - Artifacts without appraisal data produce identical scores to current formula
  - priority-weight demoted to tiebreaker when ROI data is present
depends-on-artifacts:
  - EPIC-064
  - EPIC-065
  - SPIKE-054
linked-artifacts:
  - SPIKE-059
  - ADR-010
addresses: []
---

# ROI Scoring Engine

## Goal / Objective

Wire the value model (EPIC-064) and cost model (EPIC-065) into specgraph's scoring pipeline. The recommendation formula becomes `score = max(1, own_roi) × (1 + downstream_roi)` where leverage is transitive downstream return, not artifact count. Fully backwards compatible — no appraisal data means identical behavior to today.

## Desired Outcomes

`chart.sh recommend` shows work ranked by computed return. Each item displays its ROI, which axes it advances, what it costs, and how much downstream return it unlocks. The operator sees *why* something ranks where it does, not just a score. `priority-weight` survives as a tiebreaker and escape hatch for "I know this matters but can't articulate why yet."

## Scope Boundaries

**In scope:** graph.py field parsing, priority.py ROI computation, transitive leverage with depth decay (shaped by SPIKE-054), CLI output formatting, recommendation JSON output, backwards compatibility tests.

**Out of scope:** Value and cost schema (EPIC-064, EPIC-065), migration of existing artifacts (EPIC-067), portfolio-level views, value reconciliation.

## Child Specs

To be decomposed after EPIC-064 and EPIC-065 complete and SPIKE-054 answers its question.

## Key Dependencies

- EPIC-064 (value model) — need the schema to parse
- EPIC-065 (cost model) — need the cost composition to compute ROI
- SPIKE-054 (depth decay) — shapes the transitive leverage algorithm

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-06 | | Initial creation |
