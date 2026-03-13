---
title: "Swain Skill Cognitive Load Classification"
artifact: SPIKE-014
status: Planned
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
question: "Which swain skill operations belong to which cognitive load tier (heavy / analysis / lightweight), and what reasoning effort level is appropriate for each?"
gate: Pre-EPIC-007-specs
risks-addressed:
  - Over-classifying lightweight work as heavy increases cost and latency unnecessarily
  - Under-classifying heavy work as analysis degrades output quality on the most important decisions
  - Some skills contain mixed-tier operations — classification must be at the operation level, not just skill level
linked-artifacts:
  - EPIC-007
  - SPIKE-013
evidence-pool: ""
---

# Swain Skill Cognitive Load Classification

## Question

Which swain skill operations belong to which cognitive load tier (heavy / analysis / lightweight), and what reasoning effort level is appropriate for each?

## Go / No-Go Criteria

**Go:** A complete classification table mapping each swain skill (and significant sub-operations within skills) to: (a) tier (heavy / analysis / lightweight), (b) recommended model for Claude Code (Opus / Sonnet / Haiku), (c) reasoning effort (extended-thinking on/off, budget hint), and (d) rationale.

**No-Go:** Operations within a single skill span multiple tiers in a way that cannot be statically annotated at the skill level. In that case, produce a per-operation annotation plan and flag which skills need internal routing logic.

## Pivot Recommendation

If no-go on static skill-level annotation: design sub-operation annotation blocks within SKILL.md (e.g., section-level `<!-- model: opus -->` hints) and have skill-creator insert them at the section level rather than the file level.

## Classification seed (to validate during investigation)

| Tier | Examples |
|------|---------|
| Heavy (Opus + extended thinking) | swain-design artifact creation, SPIKE investigation, ADR drafting, EPIC decomposition, swain-search evidence gathering, skill-creator |
| Analysis (Sonnet) | swain-status, swain-doctor, specgraph queries, swain-do task management, adr-check, spec-verify, swain-push |
| Lightweight (Haiku) | swain-stage layout/pane ops, swain-session tab naming and bookmarks, swain-keys key provisioning |

## Findings

(Populated during Active phase.)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-13 | — | Initial creation |
