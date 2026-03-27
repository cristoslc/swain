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
trove: "docs/troves/critical-path-analysis"
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

### Sub-question 1: Semantics — what "critical path" means in swain's context

Traditional CPM (DuPont, 1950s) assumes: (a) fixed task durations, (b) deterministic dependencies, (c) constrained resources. Agent-native work violates all three — durations are variable, agents can parallelize substeps elastically, and compute is not a fixed resource pool.

**Adaptation**: treat CPM as **structural analysis** rather than duration-based scheduling. Instead of weighting edges by time, weight them by **dependency depth** (count of edges) or by **relative size** (complexity tier: low/medium/high mapped to 1/2/3). The critical path becomes "the longest chain of sequential dependencies" rather than "the sequence that takes the most wall-clock time." This is still useful because:
- It identifies which work **cannot be parallelized** regardless of how many agents you throw at it
- It answers "what's the minimum number of sequential steps to complete this EPIC?" — a question about structure, not duration
- It degrades gracefully: if duration estimates are available (e.g., from historical throughput), they can be layered on. If not, the structural analysis still holds.

**Float** adapts cleanly: a task with zero structural float is one where any delay (in terms of completing it later in the sequence) propagates to the overall chain. A task with positive float has slack — other paths are longer.

### Sub-question 2: Value layer — where it helps

**Within a SPEC plan** — **Low value**. Mike Cohn's insight applies directly: within a short, focused piece of work (a SPEC plan is typically 5-15 tasks over 1-3 sessions), agents naturally see the critical path through `tk ready` and `tk blocked`. Formal CPM adds ceremony without changing behavior. The iteration is too short for drift to accumulate.

**Across SPECs within an EPIC** — **Medium-high value**. An EPIC may have 5-15 SPECs with `depends-on-artifacts` edges. Today, `chart.sh ready` shows which SPECs are unblocked, but doesn't distinguish between a ready SPEC that gates 8 downstream SPECs (zero float) and a ready SPEC that gates nothing (high float). Longest-path analysis on the SPEC dependency DAG would surface this distinction, helping the operator answer: "which SPEC should we start next to minimize overall EPIC completion time?"

**Across artifacts (Vision → Initiative → Epic → Spec)** — **Medium value**. The full artifact graph is a DAG. `chart.sh deps` and `chart.sh impact` already traverse it. Adding a `critical` lens that highlights the longest dependency chain would show stakeholders the project-level critical path — useful for roadmap communication and "what slips if X slips?" questions.

**Stakeholder communication** — **High value**. This is the primary use case, not agent scheduling. Operators need to:
1. Answer "what's on the critical path?" when reporting to stakeholders
2. Justify resource allocation ("we need to prioritize SPEC-X because it's on the critical path")
3. Assess impact of delays ("if SPEC-X slips by a week, what else slips?")
4. Identify where to add resources to pull in the timeline (crash the critical path)

None of these require duration estimates — they work with structural analysis alone. `chart.sh` already has the dependency data; it just needs the longest-path computation and a way to present it.

### Sub-question 3: Home — where it should live

**Recommended: `chart.sh` as primary, with `tk` as optional secondary.**

| Tool | What it computes | Why |
|------|-----------------|-----|
| `chart.sh critical` | Artifact-level critical path across the EPIC/Initiative/Vision graph | This is where the stakeholder communication value lives. The artifact DAG is already built by specgraph. Add a `critical` lens that runs longest-path and highlights the chain. |
| `chart.sh impact <ID>` | Already exists — shows what an artifact blocks. Enhance to show float. | Minimal change: annotate each blocked artifact with its float value (how much slack it has). |
| `tk critical` (optional) | Task-level critical path within a plan | Lower priority. Only useful for large plans (15+ tasks). Could be a `--critical` flag on `tk dep tree`. |

**Not recommended as primary homes:**
- `swain-do` — orchestration should consume critical path data, not compute it. swain-do reads from tk and chart.sh.
- `swain-status` / `swain-roadmap` — these are presentation layers. They should display critical path data computed by chart.sh, not compute it themselves.
- A new dedicated tool — unnecessary. The infrastructure exists in chart.sh and tk.

### Sub-question 4: Minimum viable implementation

**MVI: `chart.sh critical` lens** — a new subcommand that:

1. Reads the artifact dependency graph (already built by `specgraph build`)
2. Filters to non-terminal artifacts (exclude Complete, Abandoned, Superseded)
3. Runs longest-path on the DAG using topological sort + DP (O(V+E))
4. Outputs the critical path as a highlighted tree, with float annotations on non-critical branches

**Scope estimate**: ~100 lines of Python in the specgraph module. The DAG and topological sort infrastructure already exist (specgraph builds and traverses the artifact graph). The new code is: (a) longest-path DP pass, (b) float computation (difference between each node's longest-path-to-sink and the overall longest path), (c) output formatting for the `critical` lens.

This is ≤1 SPEC of medium complexity, fitting the go criteria.

**Optional follow-on**: `--critical` flag on `tk dep tree` for task-level analysis within large plans.

### Sub-question 5: Computed priority relationship

**Synergistic, not prerequisite.** Critical path and computed priority solve related but distinct problems:

- **Critical path** answers: "which items, if delayed, delay everything?" (structural importance)
- **Computed priority** answers: "which item should I work on next?" (urgency scoring)

They're independently useful but more powerful together:
- A computed priority formula could include critical-path membership as a factor: `urgency = base_priority + (on_critical_path ? boost : 0) + age_factor + blocked_count_factor`
- Float could inversely weight priority: tasks with zero float score higher than tasks with high float, all else equal
- Neither requires the other to deliver value. Critical path analysis is useful for stakeholder communication even without computed priority. Computed priority (e.g., Taskwarrior-style urgency) is useful for agent scheduling even without critical path.

**Recommendation**: implement critical path first (this spike → SPEC). Computed priority can be a separate spike/SPEC that incorporates critical path data as one input signal among several.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-22 | 555c81b | Initial creation; user-requested |
| Active | 2026-03-23 | — | Findings populated from trove critical-path-analysis@463a776 |
