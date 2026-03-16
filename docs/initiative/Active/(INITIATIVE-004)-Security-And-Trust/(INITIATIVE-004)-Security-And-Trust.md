---
title: "Security & Trust"
artifact: INITIATIVE-004
track: container
status: Active
author: cristos
created: 2026-03-15
last-updated: 2026-03-15
parent-vision: VISION-001
success-criteria:
  - Pre-commit secrets scanning in every sync workflow
  - Multi-vector security scanning skill available on demand
  - Security-sensitive tasks auto-detected and gated in swain-do execution flow
---

# Security & Trust

## Strategic Focus

Prevent leaks and enforce safety gates across the swain workflow. Security is not a bolt-on — it's embedded in the sync workflow (pre-commit hooks), available as a dedicated scanning skill, and woven into the task execution lifecycle.

## Scope Boundaries

**In scope:** Secrets scanning, dependency vulnerability detection, repo hygiene checks, prompt injection detection, security gates in task lifecycle.

**Out of scope:** Runtime application security (WAF, RBAC), infrastructure security, compliance frameworks.

## Child Epics

- EPIC-009: Secrets Leakage Prevention (Superseded by EPIC-012)
- EPIC-012: End-to-End Sync Workflow (Complete)
- EPIC-017: Security Vulnerability Scanning Skill (Proposed)
- EPIC-023: Security Gates in swain-do Execution Flow (Proposed)

## Small Work (Epic-less Specs)

None.

## Key Dependencies

- EPIC-023 depends on EPIC-017 (scanning skill provides the engine for execution gates)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-15 | — | Retroactive creation during initiative migration; EPIC-012 complete, two epics proposed |
