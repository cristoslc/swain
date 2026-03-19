---
title: "Swarm Safety"
artifact: INITIATIVE-013
track: container
status: Active
author: cristos
created: 2026-03-18
last-updated: 2026-03-18
parent-vision: VISION-002
priority-weight: low
success-criteria:
  - Agents in a multi-agent swarm cannot clobber each other's files
  - Each agent is scoped to its own branch and cannot push to main or another agent's branch
  - A confused or chaotic agent can be terminated without affecting other agents' work
linked-artifacts:
  - SPEC-081
depends-on-artifacts:
  - INITIATIVE-012
addresses: []
evidence-pool: ""
---

# Swarm Safety

## Strategic Focus

Prevent a confused or chaotic agent from disrupting other agents in a multi-agent swarm. When multiple agents work on the same project concurrently — each on their own GitHub issue, each in their own sandbox — they must not interfere with each other's filesystem state, branches, or credentials.

This is coordination safety, not permission granularity. The threat model is not a malicious agent but a confused one: an agent that writes to the wrong directory, pushes to the wrong branch, or consumes another agent's credentials.

## Scope Boundaries

**In scope:** Worktree-scoped filesystem isolation, branch-scoped push access, cross-agent credential isolation, EPIC-scoped containment boundaries.

**Out of scope:** Agent orchestration (assignment, scheduling), agent correctness (did it do the right thing), single-agent sandboxing (covered by INITIATIVE-010/011).

## Child Epics

None yet — scope to be defined after INITIATIVE-012 establishes the runtime architecture.

## Small Work (Epic-less Specs)

- SPEC-081: Worktree-Enforced Sandbox Isolation (Active) — mechanically enforces per-agent worktrees at the sandbox boundary

## Key Dependencies

- INITIATIVE-012 (Unified Runtime Architecture) — swarm safety builds on the multi-runtime sandbox architecture

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-18 | — | Created during VISION-002 decomposition; future work |
| Active | 2026-03-19 | — | INITIATIVE-012 complete; SPEC-081 covers all three success criteria |
