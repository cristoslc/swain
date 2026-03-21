---
title: "Operator Cognitive Support"
artifact: VISION-004
track: standing
status: Active
product-type: personal
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
priority-weight: high
depends-on-artifacts:
  - VISION-001
evidence-pool: session-decision-support@01095c4
---

# Operator Cognitive Support

## Target Audience

The operator (PERSONA-001) — a solo developer who makes decisions and delegates implementation to AI agents. The operator's cognitive resources are finite, depletable, and currently unmanaged by swain.

## Value Proposition

VISION-001 asks "what needs a decision?" — this vision asks "how many decisions can you make well, and are you done yet?"

Swain currently provides decision *support* (surfacing what needs attention) but not decision *management* (bounding the work, clustering it for efficiency, and signaling completion). The operator is treated as an unbounded decision-making resource. Research on decision fatigue, cognitive load, and goal-setting theory shows this is both inaccurate and harmful: sequential decisions degrade in quality, context-switching between unrelated decisions wastes cognitive resources, and unbounded work creates persistent psychological tension (Zeigarnik effect).

This vision adds the complementary capability: swain manages the operator's cognitive budget across sessions. It proposes coherent, bounded session goals; clusters related decisions within a focus area; caps the decision volume; tracks progress toward session completion; and provides an explicit walk-away signal when the session's work is done.

The operator should be able to sit down, confirm a focus area, make 3-5 well-clustered decisions, see what changed, and walk away knowing nothing else needs them right now.

## Problem Statement

Three specific gaps in current swain:

1. **No session concept.** Swain treats every interaction as a point query against project state. There's no "start of work" or "end of work" — just a perpetual stream of decisions. This means the operator never gets cognitive closure.

2. **No decision budget.** Every invocation of swain-status surfaces *everything* that needs attention, regardless of how many decisions the operator has already made. Decision quality degrades with volume (Baumeister), but swain keeps asking.

3. **No walk-away signal.** The strategic backlog is unbounded by design — it will never be empty. Without explicit "you're done for now" signals, the operator carries the Zeigarnik tension of the entire open backlog between sessions.

## Existing Landscape

- **Kanban WIP limits** constrain *in-progress work* but not *decisions per session*. The operator still sees the entire board.
- **Pomodoro/timeboxing** bounds *time* but not *cognitive output*. The timer ending doesn't mean the work is coherent or complete.
- **Focus modes** (macOS, Android) block *interruptions* but don't structure *what to focus on*.
- **Swain's focus lane** exists but is optional, session-unaware, and provides no completion signal.

## Build vs. Buy

Tier 3 — build from scratch. No existing tool combines decision budgeting, evidence-indexed session records, and AI-assisted focus lane proposals within a git-backed project management workflow. The components (SESSION-ROADMAP, session lifecycle, decision tracking) are swain-specific.

## Maintenance Budget

Low ongoing effort. Once the session lifecycle is built, it's driven by the same graph data that ROADMAP.md already uses. The main maintenance surface is the SESSION-ROADMAP template and the session state file format. The cognitive load research is stable (no need for trove refreshes).

## Success Metrics

- The operator can start a session and confirm a focus lane in under 30 seconds
- Session goals are specific and bounded (not "work on X" but "decide on these 3 items")
- The operator receives an explicit walk-away signal when session decisions are complete
- SESSION-ROADMAP.md is committed to git with evidence index — recoverable, reviewable
- Decision quality does not degrade within a session (subjective, but trackable via decision reversal rate)
- Every skill that detects a stale or missing session prompts the operator to start one

## Non-Goals

- Not a time tracker — sessions are bounded by decisions, not minutes
- Not a replacement for ROADMAP.md — the strategic view remains full-project and unbounded
- Not prescriptive about session frequency — the operator decides when to sit down

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | — | Initial creation from brainstorming session |
