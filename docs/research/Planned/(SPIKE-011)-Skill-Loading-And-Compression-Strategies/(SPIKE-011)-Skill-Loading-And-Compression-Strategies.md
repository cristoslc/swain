---
title: "Skill Loading and Compression Strategies"
artifact: SPIKE-011
status: Planned
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
question: "What strategies can reduce how much of a skill's content is loaded into context on invocation — and what are the tradeoffs of each?"
gate: Pre-EPIC-006-specs
risks-addressed:
  - Lazy-loading reference content may cause agents to miss information they need
  - Splitting SKILL.md may break skill routing or invocation mechanics
  - Some content looks like documentation but is actually behavioral — removing it changes agent behavior silently
depends-on: []
linked-artifacts:
  - EPIC-006
  - SPIKE-010
evidence-pool: ""
---

# Skill Loading and Compression Strategies

## Question

What strategies can reduce how much of a skill's content is loaded into context on invocation — and what are the tradeoffs of each?

## Go / No-Go Criteria

**Go:** At least one strategy is identified that can reduce total loaded content by ≥50% for the largest skills without requiring runtime changes to Claude Code's skill loading mechanism.

**No-Go:** No reduction strategy can achieve meaningful savings without either removing behavioral content or requiring changes outside the swain skill boundary.

## Pivot Recommendation

If no-go on in-band strategies: investigate whether Claude Code's `@file` include pattern or similar can be used to load reference material only when a specific sub-workflow is invoked.

## Findings

(Populated during Active phase.)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-13 | — | Initial creation |
