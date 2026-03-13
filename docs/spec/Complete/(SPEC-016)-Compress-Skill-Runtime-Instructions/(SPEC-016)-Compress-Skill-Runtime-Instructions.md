---
title: "Compress Skill Runtime Instructions"
artifact: SPEC-016
status: Complete
type: enhancement
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
parent-epic: EPIC-006
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
linked-artifacts:
  - SPIKE-010
  - SPIKE-011
depends-on-artifacts:
  - SPEC-015
---

# Compress Skill Runtime Instructions

## Problem Statement

After externalization (SPEC-015), the remaining SKILL.md content can be further compressed by tightening prose to imperative instructions, removing obvious fallback branches, and collapsing multi-step bash to single representative examples. SPIKE-011 estimated 15-25% additional savings from compression (Strategy B).

## External Behavior

SKILL.md files are more concise. Instructions read as terse directives rather than explanatory prose. No behavior changes.

### Compression targets

- Replace explanatory sentences with imperative instructions ("If X, do Y" → "X → Y")
- Remove "if not found, skip" branches where the agent can infer the fallback
- Collapse multi-step bash code blocks to single representative examples
- Remove redundant qualifiers and hedging language
- Apply across all 14 skill SKILL.md files, prioritizing the top 3

## Acceptance Criteria

- **Given** all SKILL.md files combined, **when** measured, **then** total tokens are ≤22,000 (down from 31,751 — 30% total reduction when combined with SPEC-015)
- **Given** any compressed instruction, **when** an agent executes the workflow, **then** the outcome is identical to the pre-compression behavior
- **Given** a new contributor reading SKILL.md, **when** they follow the instructions, **then** they can complete the workflow without ambiguity

## Scope & Constraints

- Depends on SPEC-015 completing first (compress what remains after externalization)
- Must preserve all behavioral content — only reduce verbosity
- Do not change the structure or sections of SKILL.md, only their prose density

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-13 | — | Initial creation from EPIC-006 decomposition |
| Implemented | 2026-03-13 | 5dd9e42 | Target met: 20,572 tokens (≤22,000 goal) |
