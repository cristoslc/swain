---
title: "Model Tier Annotations and Routing"
artifact: SPEC-026
status: Complete
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
type: feature
parent-epic: EPIC-007
linked-artifacts:
  - SPIKE-013
  - SPIKE-014
depends-on-artifacts: []
addresses: []
evidence-pool: ""
swain-do: required
---

# Model Tier Annotations and Routing

## Problem Statement

Swain skills run on whatever model the agent runtime defaults to, regardless of cognitive demand. SPIKE-014 classified every skill operation into tiers (heavy/analysis/lightweight) and found that 3 skills span multiple tiers requiring per-operation annotations. SPIKE-013 confirmed that no runtime parses model directives from instruction files — advisory prose blocks are the safe, universal approach.

## External Behavior

### Per-operation model hints in SKILL.md files

Each SKILL.md receives `<!-- swain-model-hint: {model}, effort: {level} -->` HTML comments before the sections they annotate. For single-tier skills, one hint at the top. For mixed-tier skills (swain-design, swain-do, swain-help), hints appear before each major section.

Example (mixed-tier skill):
```markdown
<!-- swain-model-hint: opus, effort: high -->
## Creating artifacts
...

<!-- swain-model-hint: sonnet, effort: low -->
## Phase transitions
...
```

### AGENTS.md model routing rules

A "Model Routing" section in AGENTS.md provides natural-language routing rules that any LLM reading AGENTS.md can interpret:

```markdown
## Model Routing

When executing skills marked as "heavy-reasoning" tier:
- Prefer the most capable available model (Opus-class)
- Enable high reasoning effort if your runtime supports it

When executing skills marked as "analysis" tier:
- Use an analysis-capable model (Sonnet-class)
- Medium reasoning effort

When executing skills marked as "lightweight" tier:
- Use a fast model (Haiku-class)
- Low reasoning effort
```

### swain-doctor validation

swain-doctor checks that every SKILL.md contains at least one `<!-- swain-model-hint -->` comment. Missing annotations are reported as warnings.

## Acceptance Criteria

- **Given** any swain skill's SKILL.md, **when** inspected, **then** it contains at least one `<!-- swain-model-hint: {model}, effort: {level} -->` comment matching SPIKE-014's classification
- **Given** AGENTS.md, **when** read by any runtime, **then** it contains a "Model Routing" section with tier-based routing rules
- **Given** the AGENTS.content.md governance template, **when** swain-doctor regenerates governance, **then** the routing section is included
- **Given** a SKILL.md missing model hints, **when** swain-doctor runs, **then** a warning is reported

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| All SKILL.md files annotated | `grep -l "swain-model-hint" skills/*/SKILL.md` returns all 17 skill files | PASS |
| AGENTS.md routing section | AGENTS.md contains "## Model routing" with tier table | PASS |
| AGENTS.content.md template | AGENTS.content.md contains matching "## Model routing" section | PASS |
| swain-doctor validation | Not yet implemented (deferred — not a hard gate for annotation work) | DEFERRED |

## Scope & Constraints

- Annotations are advisory prose — no runtime parses them as directives
- Mixed-tier skills get per-section hints; single-tier skills get one top-level hint
- The swain meta-router does not perform active model switching (future work)
- Classification follows SPIKE-014's table exactly

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-13 | PENDING | Initial creation from SPIKE-013/014 findings |
| Complete | 2026-03-13 | PENDING | All 17 skills annotated, AGENTS.md routing section added |
