---
title: "Memory Architecture Spike"
artifact: SPIKE-044
track: container
status: Active
author: cristos
created: 2026-03-23
last-updated: 2026-03-23
parent-epic: EPIC-044
question: "Does swain benefit from a more sophisticated memory system, and if so, which approach delivers the highest value within swain's git-first constraints?"
gate: "Pre-implementation"
risks-addressed:
  - "Cross-artifact reasoning requires too many file reads, slowing agents and consuming context"
  - "Auto-memory drifts from the artifact layer, producing stale or contradictory guidance"
  - "Flat-file approach may be leaving value on the table vs. graph-connected knowledge"
evidence-pool:
  - "trove: agent-memory-systems@a824a13"
trove: "agent-memory-systems@a824a13"
---

# Memory Architecture Spike

## Summary

*Populated at completion with Go/No-Go verdict.*

## Question

Does swain benefit from a more sophisticated memory system beyond its current three layers (AGENTS.md/skills, artifact system, Claude Code auto-memory), and if so, which approach delivers the highest value within swain's git-first, no-external-services constraints?

## Investigation Areas

### Area 1: Generated Artifact Graph Index

**Hypothesis:** A pre-computed YAML file mapping artifact relationships (parent/child, depends-on, linked-artifacts, trove references) would make cross-artifact traversal significantly cheaper for agents.

**What to evaluate:**
- How many file reads does swain-status / swain-design / swain-do currently perform for cross-cutting queries? (Baseline measurement)
- What queries would a graph index answer in one read vs. N reads today?
- How large would the index be at current artifact count (304 nodes, 1425 edges per chart.sh)?
- Would materialized views (blocked, orphaned, ready-to-close) add value beyond the raw adjacency list?
- Build trigger: swain-doctor at session start, pre-commit hook, or on artifact transition?

**Prototype:** Generate `docs/artifact-graph.yaml` from frontmatter using a bash/python script. Test whether swain-status and swain-design can use it to reduce file reads.

**Note:** `chart.sh` already builds a JSON graph cache at `/tmp/agents-specgraph-*.json`. Evaluate whether extending this (making it persistent, adding materialized views) is sufficient vs. building a separate index.

### Area 2: Auto-Memory Consolidation Against Artifacts

**Hypothesis:** Auto-memory (MEMORY.md + topic files) and the artifact system encode overlapping knowledge with no reconciliation, leading to drift and contradictions.

**What to evaluate:**
- Audit current auto-memory contents against artifacts — how much overlap exists?
- How often does auto-memory contain information that should live in an artifact (or vice versa)?
- Would a periodic consolidation pass (comparing MEMORY.md entries against artifact frontmatter/content) catch staleness?
- What would the consolidation mechanism be? (swain-doctor check? Post-session hook? Manual /memory review?)

**Prototype:** Write a script that diffs auto-memory entries against artifact content, flagging overlaps and contradictions. Run it against current state.

### Area 3: Graph Memory Value Assessment

**Hypothesis:** Concepts from graph memory systems (Zep's temporal knowledge graph, Cognee's triplet extraction, Mem0's entity resolution) could improve swain's cross-artifact reasoning if adapted to the git-first constraint.

**What to evaluate:**
- What do graph memory systems offer that swain's frontmatter cross-references don't? (Temporal validity, entity resolution, multi-hop traversal, community detection)
- Which of these capabilities would actually help swain's use cases? (vs. being solutions to problems swain doesn't have)
- Could any graph concepts be implemented as a generated file (like Area 1) rather than requiring a runtime service?
- What's the simplest graph representation that captures temporal artifact evolution? (Phase transitions already have dates — is that enough?)

**Assessment criteria:**
- Does the added complexity justify the retrieval improvement?
- Can it work within git-first constraints (no external services, no runtime daemons)?
- Does it compose with the existing artifact lifecycle (not replace it)?

## Go/No-Go Criteria

### Go (proceed to implementation specs)

- At least one investigation area demonstrates a measurable improvement (fewer file reads, caught contradictions, faster cross-artifact queries)
- The improvement is achievable with a generated file or lightweight script (no external services)
- The implementation effort is proportional to the value (not a multi-week project for marginal gain)

### No-Go (current approach is sufficient)

- Investigation reveals that current mechanisms (chart.sh graph cache, auto-memory, artifact cross-references) already cover the use cases adequately
- Improvements exist but require external services or architectural changes that violate swain's constraints
- The gap is real but the effort-to-value ratio doesn't justify the investment given other priorities

### Conditional / Hybrid

- Some areas warrant specs (e.g., artifact graph index) while others don't (e.g., graph memory is overkill)
- Partial adoption: extend chart.sh's existing graph cache rather than building a new system

## Pivot Recommendation

If No-Go: Document findings as ADR-NNN explaining why swain's current memory architecture is sufficient. Reference the trove as evidence of the landscape evaluated.

If Go: Create child SPECs under EPIC-044 for the approved areas, starting with the highest-value, lowest-effort improvement.

If Conditional: Create specs for approved areas only. Document rejected areas in the ADR.

## Findings

*To be populated during investigation.*

## Lifecycle

| Phase | Date | Hash |
|-------|------|------|
| Active | 2026-03-23 | 944a30f |
