---
title: "Chart Critical Path Lens"
artifact: SPEC-160
track: implementable
status: Active
author: cristos
created: 2026-03-23
last-updated: 2026-03-23
type: feature
parent-epic: ""
parent-initiative: INITIATIVE-019
linked-artifacts:
  - SPIKE-042
depends-on-artifacts: []
addresses: []
evidence-pool: "docs/troves/critical-path-analysis"
source-issue: ""
swain-do: required
---

# Chart Critical Path Lens

## Problem Statement

Swain tracks artifact dependencies at two levels (task via `tk dep` and artifact via `depends-on-artifacts`) but neither computes critical paths. `chart.sh ready` shows unblocked artifacts but cannot distinguish a ready artifact gating 8 downstream items (zero float) from one gating nothing (high float). Operators cannot answer "what's on the critical path?" or "what slips if X slips?" — questions central to stakeholder communication.

## Desired Outcomes

Operators can visualize the critical path through the artifact dependency graph and communicate it to stakeholders. Agents and operators can make better prioritization decisions by seeing float annotations on non-critical branches. The Dependency Awareness gap identified in the swain ecosystem extended analysis (scored 4/5) is addressed.

## External Behavior

**New subcommand:** `chart.sh critical [--scope <ARTIFACT-ID>] [--json]`

**Inputs:**
- The artifact dependency graph (already built by `specgraph build`)
- Optional `--scope` flag to root the analysis at a specific EPIC/Initiative/Vision (default: full graph)
- Optional `--json` flag for structured output

**Outputs:**
- Tree view with critical path highlighted (asterisk or color marker on critical nodes)
- Float annotation on each non-critical artifact: `(float: N)` where N is the structural slack
- Summary line: "Critical path: N artifacts, depth M" and the artifact IDs on the path

**Preconditions:**
- Graph cache must be built (`specgraph build` or existing `.agents/specgraph-cache.json`)
- Only non-terminal artifacts are included (exclude Complete, Abandoned, Superseded)

**Algorithm:**
1. Filter the artifact DAG to non-terminal nodes
2. Topological sort
3. Forward pass: compute longest path to each node (structural depth — edge count, not weighted by duration)
4. Backward pass: compute latest start for each node
5. Float = latest start − earliest start (zero float = on critical path)

**Postconditions:**
- No changes to artifacts or the graph cache — this is a read-only analysis lens

## Acceptance Criteria

- **AC1**: Given an artifact graph with at least two parallel paths of different depths, when `chart.sh critical` is run, then the longer path is identified as the critical path and the shorter path's artifacts show positive float values.
- **AC2**: Given `--scope EPIC-NNN`, when run, then only the subgraph rooted at that EPIC is analyzed and displayed.
- **AC3**: Given `--json`, when run, then output is valid JSON with fields: `critical_path` (ordered list of artifact IDs), `artifacts` (map of ID → `{float, on_critical_path, depth}`).
- **AC4**: Given terminal artifacts (Complete, Abandoned) in the graph, when run, then they are excluded from the analysis.
- **AC5**: Given a graph with a single linear path (no parallel branches), when run, then all artifacts show float 0 and all are on the critical path.
- **AC6**: Given `chart.sh impact <ID>` on an artifact on the critical path, the output should indicate the artifact is on the critical path (enhancement to existing command).

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- **Structural analysis only** — edge count, not duration-weighted. Duration estimates are unreliable for agent work. This is a deliberate simplification per [SPIKE-042](../../../research/Active/(SPIKE-042)-Critical-Path-Analysis-For-Swain/(SPIKE-042)-Critical-Path-Analysis-For-Swain.md) findings.
- **Read-only** — no writes to artifacts or graph cache.
- **Existing specgraph infrastructure** — builds on the graph already constructed by `specgraph build`. No new data model.
- **Not in scope**: task-level critical path within tk plans (potential follow-on). Not in scope: Gantt chart visualization (presentation layer concern for swain-roadmap).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-23 | — | Created from SPIKE-042 findings |
