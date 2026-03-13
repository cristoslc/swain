---
title: "Skill Context Footprint Reduction"
artifact: EPIC-006
status: Proposed
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
parent-vision: VISION-001
success-criteria:
  - swain-do loads in ≤5% of a standard context window (down from 10-13%)
  - No existing skill functionality is removed — only redundant, verbose, or misplaced content
  - All skills that exceed a size budget are flagged by swain-doctor
depends-on: []
addresses: []
evidence-pool: ""
---

# Skill Context Footprint Reduction

## Goal / Objective

swain skills consume disproportionate context on load. swain-do alone takes 10-13% of the context window before any user work begins, leaving less room for code, artifacts, and reasoning. This epic reduces the loaded context footprint of all swain skills without sacrificing functionality.

## Scope Boundaries

In scope:
- Auditing SKILL.md files for size and content categories (reference material vs. runtime instructions)
- Moving reference-only content out of SKILL.md into external files loaded on demand
- Trimming redundant prose, over-specified examples, and duplicated explanations
- Adding a size-budget lint check to swain-doctor

Out of scope:
- Changing skill behavior or removing features
- Changing the SKILL.md format contract itself (unless an ADR is filed)
- Optimizing non-skill context sources (AGENTS.md, CLAUDE.md)

## Child Specs

To be defined after spikes complete:
- SPIKE-010: Skill Context Footprint Audit
- SPIKE-011: Skill Loading and Compression Strategies

## Key Dependencies

Findings from SPIKE-010 and SPIKE-011 must complete before implementation specs are written.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-13 | — | Initial creation |
