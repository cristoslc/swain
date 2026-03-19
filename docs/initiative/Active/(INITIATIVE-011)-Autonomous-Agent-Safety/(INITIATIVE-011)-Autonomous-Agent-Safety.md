---
title: "Autonomous Agent Safety"
artifact: INITIATIVE-011
track: container
status: Active
author: cristos
created: 2026-03-18
last-updated: 2026-03-18
parent-vision: VISION-002
priority-weight: high
success-criteria:
  - Credential scoping analysis complete for each sandbox type
  - Docker Sandboxes OAuth limitation documented with workaround or resolution path
  - Unattended agent can run without inheriting the operator's full credential set
linked-artifacts: []
depends-on-artifacts:
  - INITIATIVE-010
addresses: []
evidence-pool: ""
---

# Autonomous Agent Safety

## Strategic Focus

Close the gap between "agent in a box" and "agent I trust to run overnight." The MVP is credential scoping — ensuring each sandbox type provides adequate credential isolation for unattended operation.

Docker Sandboxes gets credential scoping for free (credentials never enter the VM; the proxy injects per-request). The open question: can Tier 1 native sandbox (`claude --sandbox` via Seatbelt/Landlock) provide equivalent credential isolation, or is it inherently leakier because it shares the host environment?

The Docker Sandboxes OAuth/Max subscription bug (docker/desktop-feedback#198) is a blocking concern — it makes the strongest isolation tier unusable for subscription users, forcing a fallback to weaker native sandboxing.

## Scope Boundaries

**In scope:** Credential scoping analysis per sandbox type, Docker Sandboxes OAuth workaround/tracking, security promises documentation ("threat model card").

**Out of scope:** Network allowlists, MCP tool policies (future work if needed), multi-runtime support (INITIATIVE-012).

## Child Epics

None yet — scope may be small enough for epic-less specs.

## Small Work (Epic-less Specs)

None yet.

## Key Dependencies

- INITIATIVE-010 (Isolation Foundations) — completed; provides the sandbox primitives this initiative evaluates
- docker/desktop-feedback#198 — external Docker bug blocking OAuth in Docker Sandboxes

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-18 | — | Created during VISION-002 decomposition |
