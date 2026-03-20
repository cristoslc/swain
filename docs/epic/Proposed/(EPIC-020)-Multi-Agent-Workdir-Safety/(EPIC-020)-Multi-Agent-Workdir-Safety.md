---
title: "Multi-Agent Workdir Safety"
artifact: EPIC-020
track: container
status: Proposed
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
parent-vision: VISION-001
parent-initiative: INITIATIVE-013
success-criteria:
  - Multiple agents can operate in the same project without stomping on each other's files
  - Race conditions on shared state (.tickets/, artifact indexes, session.json) are prevented or safely resolved
  - Architecture overview documents the concurrency model and isolation boundaries
  - swain-do claim/close operations are atomic and safe under concurrent agent access
  - Worktree-based isolation is the default for parallel agent work where feasible
  - Agents that must share a workdir have clear conventions for which files they can touch
  - swain-doctor detects unsafe concurrent access patterns and warns
linked-artifacts:
  - EPIC-015
depends-on-artifacts:
  - SPIKE-022
addresses: []
trove: ""
---

# Multi-Agent Workdir Safety

## Goal / Objective

As swain moves toward dispatching multiple agents (via swain-dispatch, subagent-driven-development, worktree-based execution), the architecture must defend against concurrent agents colliding in the same work directory. Today, nothing prevents two agents from editing the same file, racing on `.tickets/` state, or creating conflicting commits.

This epic establishes the concurrency model: what's isolated (worktrees), what's shared (tickets, artifact state), how shared state is protected, and what conventions agents must follow.

## Scope Boundaries

**In scope:**
- SPIKE-022 to map collision vectors and evaluate mitigation strategies
- Architecture overview update documenting the multi-agent concurrency model
- Hardening `.tickets/` operations (tk claim, tk close) for concurrent access
- Conventions for shared vs. agent-private files in a workdir
- swain-doctor detection of unsafe concurrent patterns
- Guidance for swain-dispatch and subagent-driven-development on isolation requirements

**Out of scope:**
- Distributed locking across machines (local-only for now)
- Multi-user support (swain is solo operator + agents)
- Agent-to-agent communication protocols (agents coordinate through artifacts and tickets, not direct messaging)

## Child Specs

_To be created after SPIKE-022 findings._

## Key Dependencies

- **SPIKE-022** — must map collision vectors and recommend mitigations before specs are written
- **EPIC-015** (Complete) — automatic worktree lifecycle provides the isolation primitive
- **tk (ticket)** — `tk claim` already provides atomic claiming, but needs audit under true concurrent access

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Initial creation; gated on SPIKE-022 |
