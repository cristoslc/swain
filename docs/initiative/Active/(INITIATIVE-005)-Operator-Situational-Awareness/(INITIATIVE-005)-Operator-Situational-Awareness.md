---
title: "Operator Situational Awareness"
artifact: INITIATIVE-005
track: container
status: Active
author: cristos
created: 2026-03-15
last-updated: 2026-03-15
parent-vision: VISION-001
success-criteria:
  - Operator can answer "what needs my decision?" in <30 seconds
  - Status dashboard shows scope progress with completion ratios
  - Postflight summaries provide context recovery after task completion
  - New users can onboard from README without external help
---

# Operator Situational Awareness

## Strategic Focus

Help the operator see what matters — current state, progress, and what needs attention. This initiative covers everything from first-touch onboarding to real-time dashboards to post-task context recovery. The operator should never need to ask "where are we?" — swain should surface it.

## Scope Boundaries

**In scope:** README onboarding, MOTD panel, swain-status visualizations, postflight summaries, scope progress views.

**Out of scope:** External notification systems (Slack, email), mobile dashboards, historical trend analysis.

## Child Epics

- EPIC-003: README Rewrite for New User Onboarding (Complete)
- EPIC-011: MOTD Panel Improvements (Complete)
- EPIC-018: Work Scope Progress Visualizations for Swain-Status (Proposed)
- EPIC-022: Postflight Summaries (Proposed)

## Small Work (Epic-less Specs)

None.

## Key Dependencies

- EPIC-018 depends on SPIKE-021 (rendering technology decision)
- EPIC-022 depends on SPIKE-024 (invocation mechanism)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-15 | — | Retroactive creation during initiative migration; two epics complete, two proposed |
