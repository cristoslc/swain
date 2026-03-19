---
title: "Isolation Foundations"
artifact: INITIATIVE-010
track: container
status: Complete
author: cristos
created: 2026-03-18
last-updated: 2026-03-18
parent-vision: VISION-002
priority-weight: high
success-criteria:
  - Native sandbox launcher operational on macOS and Linux
  - Docker Sandboxes launcher operational with API key auth
  - Isolation mechanism research complete with documented tradeoffs
linked-artifacts:
  - EPIC-005
  - SPEC-067
  - SPIKE-009
  - SPIKE-027
depends-on-artifacts: []
addresses: []
evidence-pool: ""
---

# Isolation Foundations

## Strategic Focus

Establish the sandbox primitives that all downstream initiatives build on. This initiative delivered two operational sandbox tiers (native and Docker Sandboxes) and completed the research needed to inform architectural decisions.

This initiative is retroactively created to consolidate completed sandbox work previously spread across INITIATIVE-004 (Security & Trust) and INITIATIVE-006 (Multi-Agent Orchestration).

## Scope Boundaries

**In scope:** Sandbox launchers (claude-sandbox, swain-box), isolation mechanism research, credential mounting strategy research.

**Out of scope:** Credential scoping policy (INITIATIVE-011), multi-runtime support (INITIATIVE-012), cross-agent isolation (INITIATIVE-013).

## Child Epics

- EPIC-005: Isolated Claude Code Environment (Complete) — delivered Tier 1 native sandbox (SPEC-048) and initial Tier 2 Docker container (SPEC-049, superseded by SPEC-067)

## Small Work (Epic-less Specs)

- SPEC-067: swain-box Docker Sandboxes Launcher (Complete) — Tier 2 microVM-backed sandbox via `docker sandbox run claude`

## Research

- SPIKE-009: Isolation Mechanism Selection (Complete) — evaluated Docker, microVMs, Lima/Colima, Docker Sandboxes, Apple Containers
- SPIKE-027: Claude Config Dir Mount Strategy in Docker Sandboxes (Complete) — determined `~/.claude/` should not be mounted; credentials flow via proxy

## Key Dependencies

None — this is the foundation.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Complete | 2026-03-18 | — | Retroactive creation; consolidates completed sandbox work from INITIATIVE-004 and INITIATIVE-006 under VISION-002 |
