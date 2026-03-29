---
title: "Session Facilitation Rebuild"
artifact: EPIC-039
track: container
status: Active
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
parent-vision: VISION-004
parent-initiative: INITIATIVE-019
priority-weight: high
success-criteria:
  - swain-session generates SESSION-ROADMAP.md with focus lane, decision set, session goal, and evidence index
  - SESSION-ROADMAP.md is committed to git on session close with decision records and walk-away signal
  - ROADMAP.md includes Decisions and Recommended Next sections at the top
  - All skills detect stale or missing sessions and prompt the operator to start one
  - swain-status is absorbed into swain-session or becomes a thin alias
  - git log SESSION-ROADMAP.md reads as a session diary
depends-on-artifacts: []
trove: session-decision-support@01095c4
linked-artifacts:
  - SPEC-118
  - SPEC-169
  - SPEC-170
  - SPEC-121
  - SPEC-122
  - SPEC-123
  - SPEC-175
---

# Session Facilitation Rebuild

## Goal / Objective

Rebuild swain-session from the ground up as the session facilitator. It owns the full lifecycle: propose a focus lane, generate a bounded session goal, produce SESSION-ROADMAP.md as the operator's working surface, accumulate decision records with evidence indexes, and close with an explicit walk-away signal. ROADMAP.md gains decision and recommendation sections. swain-status merges into the new swain-session.

## Scope Boundaries

**In scope:**
- swain-session ground-up rebuild (session lifecycle, focus lane as mandatory, decision budget)
- SESSION-ROADMAP.md format, generation, and git lifecycle
- ROADMAP.md decision/recommendation sections (chart.sh roadmap changes)
- Session detection hooks across all skills
- swain-status absorption
- Documentation and README updates
- Alignment audit of all skills and scripts

**Out of scope:**
- chart.sh data model changes (stays stateless; provides JSON data)
- tk/ticket tracking changes
- Agent-side session awareness
- Time tracking or calendar integration

## Child Specs

| Spec | Title | Status |
|------|-------|--------|
| SPEC-118 | SESSION-ROADMAP.md Format and Generation | Active |
| SPEC-169 | Session Lifecycle in swain-session | Active |
| SPEC-170 | ROADMAP.md Decision and Recommendation Sections | Active |
| SPEC-121 | Session Detection Hooks Across All Skills | Active |
| SPEC-122 | Absorb swain-status into swain-session | Active |
| SPEC-123 | Skill and Script Alignment Audit | Active |

## Key Dependencies

- ROADMAP.md and chart.sh roadmap (data source for decision sets and recommendations)
- specgraph recommend, decision-debt, and attention commands (existing data pipeline)
- swain-session existing infrastructure (bookmarks, focus lanes, tab naming — to be rebuilt)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | — | Initial creation |
