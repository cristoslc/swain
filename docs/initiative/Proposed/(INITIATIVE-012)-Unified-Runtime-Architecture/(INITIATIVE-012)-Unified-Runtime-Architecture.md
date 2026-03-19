---
title: "Unified Runtime Architecture"
artifact: INITIATIVE-012
track: container
status: Proposed
author: cristos
created: 2026-03-18
last-updated: 2026-03-18
parent-vision: VISION-002
priority-weight: medium
success-criteria:
  - Architecture supports Claude, Copilot, and Codex runtimes in sandboxed environments
  - Clear documentation of which sandbox type serves each runtime and why
  - Security promises documented per sandbox type (what's guaranteed, what's best-effort, what's out of scope)
linked-artifacts:
  - EPIC-030
  - DESIGN-002
depends-on-artifacts:
  - INITIATIVE-011
addresses: []
evidence-pool: ""
---

# Unified Runtime Architecture

## Strategic Focus

Figure out the sandbox architecture that can host multiple agent runtimes (Claude, Copilot, Codex). Today the landscape is fragmented: Docker Sandboxes works for Codex (API key auth) but breaks for Claude (OAuth bug). Native sandbox works for Claude but is Claude-specific. A custom Docker image might handle all of them — or each runtime might need its own sandbox type.

Key decision: one sandbox type for all runtimes, or per-runtime sandbox selection? This likely needs a spike before implementation.

Whatever architecture emerges, it must produce clear security promises documentation — what the sandbox guarantees, what it explicitly doesn't, and what varies by sandbox type.

## Scope Boundaries

**In scope:** Multi-runtime sandbox architecture, per-runtime credential passthrough, security promises documentation, runtime detection and selection UX.

**Out of scope:** Agent orchestration (which agent works on what), agent quality/correctness, swarm coordination (INITIATIVE-013).

## Child Epics

- EPIC-030: swain-box Multi-Agent Runtime Support (Proposed) — runtime detection, selection menu, per-runtime auth passthrough. UX defined by DESIGN-002.

## Small Work (Epic-less Specs)

None yet.

## Key Dependencies

- INITIATIVE-011 (Autonomous Agent Safety) — credential scoping model informs how each runtime receives credentials
- docker/desktop-feedback#198 — if unresolved, shapes the architecture toward per-runtime sandbox selection rather than a unified Docker Sandboxes approach

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-18 | — | Created during VISION-002 decomposition; needs spike before implementation |
