---
title: "Cross-Runtime Portability Substrate"
artifact: SPIKE-029
track: container
status: Active
author: cristos
created: 2026-03-18
last-updated: 2026-03-18
question: "What extension models do non-Claude agent runtimes (opencode, gemini cli, codex, copilot, aider) support, and is there a common substrate that swain could target for cross-runtime portability?"
gate: Pre-MVP
parent-initiative: INITIATIVE-014
risks-addressed:
  - Building per-runtime adapters that share no common foundation
  - Targeting runtimes with unstable or nonexistent extension APIs
evidence-pool: ""
---

# Cross-Runtime Portability Substrate

## Summary

<!-- Populated on completion -->

## Question

What extension models do non-Claude agent runtimes (opencode, gemini cli, codex, copilot, aider) support, and is there a common substrate that swain could target for cross-runtime portability?

## Go / No-Go Criteria

- **Go**: At least 2 non-Claude runtimes support a shared extension mechanism (AGENTS.md, MCP, tool plugins, or system prompt injection) that swain could target with a single adapter
- **No-Go**: Every runtime has a completely bespoke extension model with no overlap, making cross-runtime portability a per-runtime maintenance burden

## Pivot Recommendation

If no common substrate exists, deprioritize cross-runtime portability in favor of Claude-surface-only packaging (SPIKE-028) and revisit when the ecosystem matures. Consider publishing swain's patterns as a specification/protocol rather than runnable code.

## Findings

<!-- Populated by research -->

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-18 | | Initial creation |
