---
title: "Swain Memory Architecture"
artifact: EPIC-044
track: container
status: Active
author: cristos
created: 2026-03-23
last-updated: 2026-03-23
parent-vision: VISION-001
parent-initiative: ""
priority-weight: medium
success-criteria:
  - "Research spike completes with a clear Go/No-Go recommendation"
  - "If Go: at least one child SPEC drafted for the highest-value improvement"
  - "If No-Go: findings documented as an ADR explaining why current approach is sufficient"
depends-on-artifacts: []
addresses: []
evidence-pool:
  - "trove: agent-memory-systems@a824a13"
---

# Swain Memory Architecture

## Goal / Objective

Determine whether swain benefits from a more sophisticated memory system beyond Claude Code's built-in auto-memory, and if so, build it.

Swain currently relies on three memory layers: (1) AGENTS.md + skills for procedural memory, (2) the artifact system (specs, epics, ADRs, troves) for structured semantic memory, and (3) Claude Code's auto-memory (MEMORY.md + topic files) for session-learned facts. These layers evolved organically and are not integrated — auto-memory doesn't know about the artifact graph, artifacts don't consolidate against auto-memory, and there's no traversal mechanism connecting artifacts beyond manual file reads.

The `agent-memory-systems` trove surveys the landscape: coding CLI memory systems (Claude Code, Codex, Gemini CLI, OpenCode), OSS memory frameworks (Mem0, Letta/MemGPT, Cognee), graph memory (Zep/Graphiti), and MCP memory servers (Basic Memory). Key findings suggest that swain's artifact system already exceeds what most tools offer for structured knowledge, but gaps exist in cross-artifact connectivity, memory consolidation, and forgetting.

## Desired Outcomes

1. **Clarity on whether the current memory approach is sufficient** — the spike may conclude that swain's existing layers are adequate and that investment should go elsewhere.
2. **If gaps are real**: a concrete, incremental improvement path — not a wholesale replacement. Swain's git-first, markdown-native, no-external-services constraint is non-negotiable.
3. **Artifact graph traversal** becomes cheaper for agents (fewer file reads to answer cross-cutting questions).

## Scope Boundaries

### In Scope

- Evaluating whether a generated artifact graph index improves agent effectiveness
- Evaluating whether auto-memory consolidation against artifacts reduces drift
- Evaluating whether graph memory concepts (from Zep/Graphiti/Cognee) add value within swain's constraints
- Prototyping the most promising approach in the spike

### Out of Scope

- External services (Neo4j, vector databases, MCP memory servers)
- Replacing Claude Code's auto-memory with a custom system
- Multi-user or multi-agent memory sharing
- Changes to the artifact lifecycle or frontmatter schema (those would be follow-on specs)

## Child Specs

- [SPIKE-044](../../../research/Active/(SPIKE-044)-Memory-Architecture-Spike/(SPIKE-044)-Memory-Architecture-Spike.md) — Research spike: memory architecture investigation

*Additional child specs will be created based on the spike's recommendation.*

## Key Dependencies

None — this is exploratory work with no blocking dependencies.

## Lifecycle

| Phase | Date | Hash |
|-------|------|------|
| Active | 2026-03-23 | 944a30f |
