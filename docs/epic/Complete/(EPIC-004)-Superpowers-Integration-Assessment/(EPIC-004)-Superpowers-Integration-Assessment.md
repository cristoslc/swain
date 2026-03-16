---
title: "Superpowers Integration Assessment"
artifact: EPIC-004
track: container
status: Complete
author: cristos
created: 2026-03-12
last-updated: 2026-03-12
parent-vision: VISION-001
parent-initiative: INITIATIVE-003
success-criteria:
  - SPIKE-004 research complete with clear mapping between swain and superpowers skill surfaces
  - Decision documented (ADR) on whether to retire swain, integrate superpowers, or coexist
  - If coexistence chosen — integration spec written for superpowers skill adoption within swain
addresses: []
evidence-pool:
linked-artifacts: []
depends-on-artifacts: []
---

# Superpowers Integration Assessment

## Goal / Objective

Evaluate [obra/superpowers](https://github.com/obra/superpowers) (v5.0.1) against swain's skill ecosystem to determine the best path forward: retire swain in favor of superpowers, adopt superpowers skills selectively within swain, or maintain both with a clear boundary.

The key questions are:
1. **Retire?** Does superpowers subsume swain's value proposition, making swain redundant?
2. **Integrate?** Can superpowers' implementation-workflow skills complement swain's lifecycle-management skills when both are installed?
3. **Boundary?** Where does each system's strength end and the other's begin?

## Scope Boundaries

**In scope:**
- Skill-by-skill mapping between swain and superpowers
- Overlap analysis (where both systems cover the same concern)
- Gap analysis (where one system covers something the other doesn't)
- Conflict analysis (where the two systems would interfere if co-installed)
- Recommendation on retirement vs. integration vs. coexistence

**Out of scope:**
- Implementing any integration (that's downstream specs)
- Multi-platform support analysis (superpowers supports Cursor, Codex, Gemini — swain is Claude Code only; this is noted but not actionable here)
- Forking or contributing upstream to superpowers

## Child Specs

- SPIKE-004: Superpowers–Swain Skill Mapping (research) — Complete
- ADR-001: Coexist with Superpowers via Layered Integration
- SPEC-008: Superpowers Integration within Swain

## Key Dependencies

- SPIKE-004 must complete before the ADR can be drafted.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-12 | — | Initial creation |
| Complete | 2026-03-12 | 775306f | All success criteria met: SPIKE-004, ADR-001, SPEC-008 |
