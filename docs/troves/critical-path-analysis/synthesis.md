# Critical Path Analysis — Synthesis

## Key findings

### CPM is fundamentally a longest-path-on-DAG computation
The critical path method reduces to finding the longest weighted path in a directed acyclic graph. The algorithm (topological sort + dynamic programming) runs in O(V+E), making it tractable even for large dependency graphs. Swain already maintains DAGs at two layers — task-level (`tk dep`) and artifact-level (`depends-on-artifacts`) — so the computational substrate exists. (wikipedia-cpm, algocademy-longest-path-dag)

### Stakeholder communication is a first-class CPM use case, not a byproduct
Multiple sources emphasize that CPM's value extends well beyond scheduling optimization. It provides a **shared visual language** for discussing project progress, a framework for answering "what slips if X slips?", and a basis for informed resource allocation decisions. CPA reports are described as "effective communication tools for stakeholder presentations." (meegle-cpm-stakeholder-communication, cio-wiki-cpa)

### Critical path within short iterations is unnecessary — across iterations it matters
Mike Cohn's experience over 11+ years of agile projects: within a 2-4 week iteration, teams naturally see and manage the critical path through daily standups and planning. The iteration is short enough that formal CPM adds no value. But across iterations (or across teams), **rolling lookahead planning** — a 5-minute look at the next 1-3 iterations — helps identify dependencies that create a project-level critical path. (mountain-goat-agile-critical-path)

### Traditional CPM assumes fixed durations — agent work doesn't have them
CPM's primary limitation in agile/agent contexts: it relies on accurate, fixed task duration estimates. Agent work has variable duration, parallelizable substeps, and elastic compute. This is a fundamental mismatch that any swain adaptation must address. Options: use relative size estimates, historical throughput data, or treat CPM as a structural analysis tool (identifying the longest dependency chain by count, not duration). (meegle-cpm-stakeholder-communication, mountain-goat-agile-critical-path)

### Float/slack identification may be more valuable than the critical path itself
Identifying tasks with zero float (critical) vs. positive float (can slip) helps agents and operators prioritize. Non-critical tasks with high float can have resources reallocated without affecting the timeline. This maps to swain's existing `tk ready` concept but adds depth: a ready task on the critical path is more urgent than a ready task with high float. (wikipedia-cpm, meegle-cpm-stakeholder-communication)

## Points of agreement

- **CPM improves project visibility** — all sources agree on this as a primary benefit
- **The algorithm is well-understood and efficient** — O(V+E) on DAGs, no exotic data structures needed
- **Visualization is essential** — Gantt charts, network diagrams, and highlighted critical paths are how stakeholders consume CPM data
- **CPM should be continuously updated** — it's not a one-time analysis; the critical path shifts as work progresses

## Points of disagreement

- **Value in agile contexts**: Mountain Goat argues CPM is mostly unnecessary in agile (short iterations make it obvious); traditional PM sources (Meegle, CIO Wiki) argue it can be adapted. The resolution likely depends on project complexity and stakeholder needs.
- **Duration estimates**: CPM classically requires them. In agent-native contexts, durations are unreliable. Sources don't resolve this tension — it's a gap specific to the agent-native domain.

## Gaps

- **No sources discuss CPM in agent-native contexts** — all sources assume human teams. The adaptation of CPM concepts to autonomous agents (variable speed, elastic parallelism, non-human coordination costs) is unexplored territory.
- **Computed priority from critical path** — traditional CPM doesn't directly compute priority scores, though the relationship is implicit (critical path items are highest priority). No source formalizes this as a priority computation.
- **Multi-layer CPM** — swain has two dependency layers (task and artifact). No source discusses running CPM across multiple graph layers simultaneously. This is a novel aspect of the swain context.

## Related trove

The `task-management-systems` trove contains the swain ecosystem extended analysis that identified this gap, plus the blizzy78 source (only surveyed system with critical path support). That trove covers the task management landscape; this trove focuses on CPM theory and adaptation.
