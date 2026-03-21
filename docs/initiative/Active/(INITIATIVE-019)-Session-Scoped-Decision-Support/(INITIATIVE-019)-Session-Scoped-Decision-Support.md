---
title: "Session-Scoped Decision Support"
artifact: INITIATIVE-019
track: container
status: Active
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
parent-vision: VISION-004
priority-weight: high
linked-artifacts: []
depends-on-artifacts: []
evidence-pool: session-decision-support@01095c4
---

# Session-Scoped Decision Support

## Strategic Direction

Rebuild swain's session and status infrastructure around a bounded, evidence-indexed session lifecycle. The operator's primary working surface becomes SESSION-ROADMAP.md — a focus-scoped, decision-budgeted document that opens a session, accumulates decision records, and closes with a walk-away signal. ROADMAP.md remains the strategic view; swain-status merges into swain-session.

## Key Outcomes

- Every session has a mandatory focus lane (operator confirms or redirects)
- Session goals are specific, bounded (~3-5 decisions), and coherent (clustered within the focus area)
- SESSION-ROADMAP.md is the operator's reference surface — committed to git, evidence-indexed, recoverable
- swain-session owns the full session lifecycle (start, work, close, resume)
- All skills detect stale/missing sessions and prompt the operator to start one
- ROADMAP.md absorbs swain-status's decision and recommendation sections

## Scope

**In scope:** swain-session rebuild, SESSION-ROADMAP lifecycle, ROADMAP.md decision sections, session detection across all skills, documentation and README updates.

**Out of scope:** Changes to chart.sh data model (it stays stateless), changes to tk/ticket tracking, agent-side session awareness.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | — | Initial creation |
