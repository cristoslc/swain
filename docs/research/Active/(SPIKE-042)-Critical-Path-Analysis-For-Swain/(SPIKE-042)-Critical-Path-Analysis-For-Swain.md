---
title: "Critical Path Analysis for Swain"
artifact: SPIKE-042
track: container
status: Active
author: cristos
created: 2026-03-22
last-updated: 2026-03-22
question: "Where would critical path analysis add value in swain's dependency model, and what is the minimum viable implementation?"
gate: Pre-MVP
risks-addressed:
  - "Dependency Awareness scored 4/5 — no critical path analysis at either task or artifact layer"
  - "Agents sequence work by readiness, not by impact on overall completion time"
  - "Multi-agent parallelism decisions are ad-hoc — no data on which work is blocking vs. slack"
  - "Operators lack a critical-path view for stakeholder communication — cannot answer 'what's on the critical path?' or 'what slips if X slips?'"
evidence-pool: "docs/troves/critical-path-analysis"
trove: critical-path-analysis@463a776
---

# Critical Path Analysis for Swain

## Summary

<!-- Final-pass section: populated when transitioning to Complete. -->

## Question

Where would critical path analysis add value in swain's dependency model, and what is the minimum viable implementation?

Swain tracks dependencies at two granularities — task-level (`tk dep`, `tk ready`, `tk blocked`) and artifact-level (`depends-on-artifacts`, `chart.sh ready`) — but neither layer computes critical paths. The [swain-ecosystem-extended-analysis](../../troves/task-management-systems/sources/swain-ecosystem-extended-analysis/swain-ecosystem-extended-analysis.md) identified this as the primary remaining gap in Dependency Awareness (4/5). Among surveyed systems, only blizzy78 (in-memory, 28/50 overall) provides critical path support.

This spike investigates five sub-questions:

1. **Semantics** — What does "critical path" mean in an agent-native, artifact-driven context versus traditional project management? Traditional CPM assumes fixed task durations and resource constraints. Agent work has variable duration, parallelizable substeps, and elastic compute. What adaptation is needed?

2. **Value layer** — Where would critical path analysis actually help? Consider both agent-facing and operator-facing consumers:
   - **Within a SPEC plan** — task scheduling and parallelism decisions during implementation
   - **Across SPECs within an EPIC** — sequencing SPECs to minimize EPIC completion time
   - **Across artifacts** — identifying which artifact-level dependencies gate downstream work (Vision → Initiative → Epic → Spec chains)
   - **Stakeholder communication** — giving operators a clear answer to "what's on the critical path?", "what slips if X slips?", and "where should we add resources to pull in the timeline?" This is a first-class use case, not a byproduct of agent scheduling.
   - Some combination of the above

3. **Home** — Where should it live?
   - `tk` — task-level critical path (extends existing `tk dep` / `tk ready`)
   - `chart.sh` — artifact-level critical path (extends existing dependency graph)
   - `swain-do` — orchestration-level, informing agent dispatch decisions
   - `swain-status` / `swain-roadmap` — operator-facing, surfacing critical path in dashboards and stakeholder views
   - A new dedicated tool
   - Multiple integration points

4. **Minimum viable implementation** — What is the smallest useful version? A topological sort with longest-path calculation over the existing DAG? A `--critical` flag on `tk dep` or `chart.sh`? A `critical` lens on `swain chart`?

5. **Computed priority relationship** — The trove also identified "no computed priority" as a gap (Priority System 3/5). Is critical path analysis a prerequisite for computed priority (critical path items should score higher), orthogonal (they solve different problems), or synergistic (each is independently useful but more powerful together)?

## Go / No-Go Criteria

- **Go**: At least one value layer (sub-question 2) shows a concrete scenario where critical path information would change an agent's scheduling decision OR an operator's stakeholder communication, AND a minimum viable implementation can be scoped to ≤1 SPEC of medium complexity.
- **No-Go**: Critical path analysis provides no actionable information beyond what `tk ready` and `chart.sh ready` already surface, OR the minimum viable implementation requires foundational changes to swain's dependency model.

## Pivot Recommendation

If no-go: improve the existing readiness model instead — enhance `tk ready` with depth-aware ordering (prefer tasks whose dependents have the most transitive downstream work) without full CPM. This would capture ~80% of the scheduling benefit without the conceptual overhead of critical path.

## Findings

<!-- Populated during Active phase. -->

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-22 | — | Initial creation; user-requested |
