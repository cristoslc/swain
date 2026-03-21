---
title: "Skill Audit Remediation"
artifact: EPIC-031
track: container
status: Active
author: cristos
created: 2026-03-18
last-updated: 2026-03-18
parent-vision: VISION-001
parent-initiative: INITIATIVE-003
priority-weight: high
success-criteria:
  - All 9 high-severity findings from the 2026-03-18 skill audit are resolved
  - Every swain skill resolves script paths via find-based discovery, not hardcoded relative paths
  - All skill descriptions are 50-150 words with concrete trigger phrases
  - allowed-tools declarations are complete and minimal across all 18 skills
  - Deprecated swain-push skill is pruned
depends-on-artifacts: []
addresses: []
evidence-pool: ""
linked-artifacts:
  - DESIGN-003
  - EPIC-015
  - INITIATIVE-001
  - SPEC-072
  - SPEC-073
  - SPEC-074
  - SPEC-075
  - SPEC-076
  - SPEC-077
  - SPEC-078
  - SPEC-079
  - SPEC-080
  - SPIKE-033
---

# Skill Audit Remediation

## Goal / Objective

Resolve all findings from the 2026-03-18 full skill-creator audit of 18 swain skills. The audit found 9 high-severity, 45 medium, and 45 low issues. Rather than fixing per-skill, this epic groups work by theme — each spec addresses a cross-cutting concern that affects multiple skills.

## Scope Boundaries

**In scope:**
- All findings from `docs/audits/2026-03-18-skill-audit.md`
- Cross-cutting fixes grouped by theme (paths, descriptions, tools, state, disclosure)
- Pruning deprecated skills
- Investigating routing disambiguation (SPIKE)
- Documenting worktree lifecycle UX (DESIGN)

**Out of scope:**
- New skill features not identified in the audit
- Rewriting skill logic (this is remediation, not redesign)
- swain-push findings (deprecated, tilde-sort is intentional — just prune it)

## Child Specs

| Spec | Title | Type | Priority |
|------|-------|------|----------|
| SPEC-072 | Universal find-based script discovery | enhancement | high |
| SPEC-073 | Description enrichment | enhancement | medium |
| SPEC-074 | Fix swain-dispatch functional bugs | bug | high |
| SPEC-075 | Fix swain-sync functional bugs | bug | high |
| SPEC-076 | Fix swain-update functional bugs | bug | high |
| SPEC-077 | allowed-tools hygiene sweep | enhancement | medium |
| SPEC-078 | State location migration | enhancement | medium |
| SPEC-079 | Progressive disclosure cleanup | enhancement | low |
| SPEC-080 | Prune deprecated swain-push | chore | low |
| SPIKE-033 | Skill routing disambiguation | research | medium |
| DESIGN-003 | Worktree lifecycle UX | design | medium |

## Key Dependencies

- INITIATIVE-001 (Worktree-Safe Skill Execution) — SPEC-072 directly addresses its success criteria for path resolution
- EPIC-015 (Automatic Worktree Lifecycle) — DESIGN-003 documents the lifecycle that EPIC-015 established

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-18 | — | Created from 2026-03-18 skill audit findings |
| Complete | 2026-03-21 | — | All 9 specs implemented. SPEC-080/074/075/076/073/077/078 were already complete. SPEC-072 committed (find-based discovery). SPEC-079 committed (progressive disclosure). SPIKE-033 investigated (No-Go). DESIGN-003 reviewed (accurate). |
