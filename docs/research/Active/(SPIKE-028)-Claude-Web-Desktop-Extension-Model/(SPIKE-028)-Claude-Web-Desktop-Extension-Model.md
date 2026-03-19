---
title: "Claude Web & Desktop Extension Model"
artifact: SPIKE-028
track: container
status: Active
author: cristos
created: 2026-03-18
last-updated: 2026-03-18
question: "What capabilities do Claude web (Projects) and Claude desktop offer for extending agent behavior, and how much of swain's value can be projected onto each?"
gate: Pre-MVP
parent-initiative: INITIATIVE-014
risks-addressed:
  - Investing in a packaging approach that the target surfaces can't support
  - Assuming capabilities that don't exist or are about to change
evidence-pool: ""
---

# Claude Web & Desktop Extension Model

## Summary

<!-- Populated on completion -->

## Question

What capabilities do Claude web (Projects) and Claude desktop offer for extending agent behavior, and how much of swain's value can be projected onto each?

## Go / No-Go Criteria

- **Go**: At least one Claude surface (web or desktop) supports enough extensibility to deliver swain's core decision-support loop (artifact awareness, lifecycle guidance, structured recommendations) without requiring CLI access
- **No-Go**: Both surfaces are limited to static system prompts with no file access, tool use, or persistent state — making swain's artifact-driven model infeasible

## Pivot Recommendation

If Claude web/desktop extensibility is too limited, pivot to MCP-first approach (SPIKE-030) targeting Claude desktop's MCP support as the primary surface, treating web as a degraded-mode fallback with prompt-only packaging.

## Findings

<!-- Populated by research -->

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-18 | | Initial creation |
