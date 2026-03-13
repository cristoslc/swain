---
title: "Agent Dispatch Via GitHub Issues"
artifact: EPIC-010
status: Proposed
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
parent-vision: VISION-001
success-criteria:
  - swain-dispatch skill exists and is registered in the swain router
  - Artifacts (SPECs, etc.) can be pushed to GitHub Issues for background agent execution
  - Agent backend is configurable (Claude via @claude, potentially others)
  - Model routing decision: Opus vs Sonnet based on task complexity assessment
  - swain-design can tag artifacts as good candidates for dispatch
depends-on:
  - SPIKE-016
addresses: []
evidence-pool: ""
source-issue: "github:cristoslc/swain#18"
---

# Agent Dispatch Via GitHub Issues

## Goal / Objective

Create a `swain-dispatch` skill that pushes swain-design artifacts to GitHub Issues for background agent execution. The agent backend is configurable (default: Claude via `@claude` mentions) and includes model routing — assessing whether a task is well-scoped for a Sonnet-level agent or requires Opus-level reasoning.

## Scope Boundaries

**In scope:**
- swain-dispatch skill with swain router integration
- Push artifacts (SPECs, etc.) as GitHub Issues with agent invocation
- Configurable agent backend (Claude default, extensible)
- Model/complexity routing (Opus vs Sonnet assessment)
- swain-design integration: tag artifacts as dispatch candidates
- SPIKE-016 to research background agent invocation mechanisms

**Out of scope:**
- Building a custom agent orchestration layer (use existing GitHub/Claude infrastructure)
- Real-time monitoring of dispatched work (rely on GitHub issue updates)
- Non-GitHub dispatch targets (future work)

## Child Specs

- SPIKE-016: Background Agent Invocation Via GitHub (research)
- SPEC: swain-dispatch skill implementation (depends on SPIKE-016)
- SPEC: swain-design dispatch candidacy tagging
- SPEC: Model routing / complexity assessment for dispatch

## Key Dependencies

- SPIKE-016 must clarify how to invoke agents via GitHub Issues before implementation specs can be written
- EPIC-007 (Agent Model Routing) has overlap on the model selection concern — coordinate

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-13 | — | Initial creation from GitHub #18 decision |
