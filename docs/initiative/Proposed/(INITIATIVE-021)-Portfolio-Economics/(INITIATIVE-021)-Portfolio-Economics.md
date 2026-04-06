---
title: "Portfolio Economics"
artifact: INITIATIVE-021
track: container
status: Proposed
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
parent-vision: VISION-004
priority-weight: high
success-criteria:
  - Every active Vision has declared appraisal-goals with structured axis weights
  - Recommendation scoring uses ROI (weighted value / cost) instead of priority-weight as primary signal
  - The operator can answer "which work has the best return?" from chart.sh recommend output
  - Leverage reflects downstream return, not artifact count
  - Existing artifacts without appraisal data score identically to current behavior
depends-on-artifacts: []
linked-artifacts:
  - SPIKE-052
  - ADR-010
  - VISION-002
  - VISION-003
  - VISION-005
addresses: []
---

# Portfolio Economics

## Strategic Focus

Ground swain's prioritization in portfolio economics instead of arbitrary priority labels. Every swain project is a portfolio of strategic bets competing for two scarce resources: operator attention and compute budget. The operator declares what returns they value (project-specific axes), estimates impact and cost on their work, and the system computes return so "obviously worth doing" separates from "probably not worth doing."

This initiative replaces gut-feel `priority-weight: high | medium | low` with a structured appraisal model adapted from strategic portfolio management, WSJF, and multi-criteria decision analysis — compressed for a solo operator with AI agents.

SPIKE-052 validated the model against swain's live backlog. Axis-weighted ROI differentiates work that priority labels cannot: all four active Visions are "high priority" but they bet on different axes at different intensities. The model makes this visible and computable.

## Desired Outcomes

The operator sits down, runs `chart.sh recommend`, and sees work ranked by computed return — not by labels they set weeks ago and forgot the reasoning behind. Each recommendation shows which value axes it advances, what it costs in attention and compute, and how much downstream return it unlocks. The operator makes allocation decisions grounded in the same logic a portfolio manager uses: fund the bets with the best risk-adjusted returns, re-evaluate when returns don't materialize.

Agents creating artifacts are guided by the appraisal model. A new Spec prompts for `serves-goals` and `cost-estimate` the same way it prompts for acceptance criteria. Work that serves no declared goal is flagged as "unappraised" — visible, not hidden.

## Key Concepts

**Value axes are project-specific.** Declared in PURPOSE.md (for the meta-project) or by Visions (for product direction). Swain provides the structure; each project provides the axes. Swain's own axes: alignment, safety, sustainability.

**Cost axes are framework-structural.** Baked into swain's operating model: operator-attention and compute-budget. Every swain project has these because swain *is* the opinion that development works this way.

**ROI = weighted value / cost.** Value is impact-on-axis multiplied by the Vision's axis weight, summed across served axes. Cost combines operator-attention and compute-budget estimates. The ratio is return.

**Leverage = transitive downstream return.** Replaces `unblock_count`. An artifact's leverage is the sum of ROI of everything it unblocks, recursively. This makes leverage a function of the value model.

**Score = max(1, own_roi) × (1 + downstream_roi).** Own return floored at 1 so leverage always multiplies something. Pure infrastructure (zero own-return, high downstream return) still scores well.

## Scope Boundaries

**In scope:** PURPOSE.md appraisal philosophy, frontmatter schema (appraisal-goals, serves-goals, cost-estimate), graph.py parsing, priority.py ROI + transitive leverage, CLI output, artifact definitions, templates, ADR, migration tooling for existing artifacts.

**Out of scope:** Portfolio-level views (attention distribution across Visions, bet performance dashboards), exit criteria on Visions, value reconciliation ("is the bet paying off?"), the fourth question ("is this bet still worth making?"). These are enabled by this initiative but scoped as follow-on work.

## Child Epics

- EPIC-056: Appraisal Value Model — PURPOSE.md axes, Vision appraisal-goals, serves-goals on children
- EPIC-057: Framework Cost Model — cost axes, cost-estimate field, composition formula
- EPIC-058: ROI Scoring Engine — graph.py parsing, priority.py rewrite, transitive leverage, CLI output
- EPIC-059: Backlog Appraisal Bootstrap — apply estimates to existing artifacts, migration tooling

## Research (Spikes)

- SPIKE-052: ROI Appraisal Model For Portfolio Economics (Active — validated the model)
- SPIKE-053: Cost Axis Composition Model (Proposed — how do attention and compute combine?)
- SPIKE-054: Transitive Leverage Depth Decay (Proposed — full sum vs diminishing returns at depth?)

## Key Dependencies

- SPIKE-053 and SPIKE-054 should complete before EPIC-058 (scoring engine) begins — their answers shape the formula
- EPIC-056 and EPIC-057 can proceed in parallel — value model and cost model are independent
- EPIC-058 depends on both EPIC-056 and EPIC-057 — the scoring engine needs both models settled
- EPIC-059 depends on EPIC-058 — can't bootstrap estimates until the schema and tooling exist

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-06 | | Initial creation from SPIKE-052 findings |
