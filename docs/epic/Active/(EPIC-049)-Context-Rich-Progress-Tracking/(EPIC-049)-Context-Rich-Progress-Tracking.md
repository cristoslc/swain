---
title: "Context-Rich Progress Tracking"
artifact: EPIC-049
track: container
status: Active
author: Cristos L-C
created: 2026-03-31
last-updated: 2026-03-31
parent-vision: VISION-004
parent-initiative: INITIATIVE-019
priority-weight: high
success-criteria:
  - Session digests auto-generate at session close with zero operator interaction
  - EPICs and Initiatives accumulate progress logs from session evidence
  - A living Progress synthesis section in each artifact stays current after each session
  - All operator-facing surfaces show context lines (title, scope, progress) instead of bare IDs
  - The artifact-context utility is callable by any skill
depends-on-artifacts: []
addresses: []
linked-artifacts:
  - EPIC-042
  - SPEC-199
  - SPEC-200
  - SPEC-201
  - SPEC-202
evidence-pool: ""
---

# Context-Rich Progress Tracking

## Goal / Objective

Make every artifact reference in operator-facing output carry enough context that the operator never has to look up what an ID means. Ground progress reporting in actual session evidence rather than artifact state counts alone.

## Desired Outcomes

The operator sees plain-language titles, scope summaries, and progress clauses whenever swain surfaces an artifact — in the status dashboard, roadmap, retro summaries, and scope checks. Progress accumulates automatically from session evidence. EPICs and Initiatives become self-contained: reading one tells you not just what's planned but how it's going.

This complements EPIC-042 (Retro Session Intelligence), which deepens the evidence layer for retros. This epic builds the display and accumulation layer that makes that evidence visible to the operator in everyday interactions.

## Scope Boundaries

**In scope:**
- Session digest generation at session close
- Progress log files alongside EPICs and Initiatives
- Progress synthesis sections in EPIC and Initiative artifacts
- Shared artifact-context utility script
- Integration into swain-session, swain-roadmap, swain-retro, and swain-design display surfaces

**Out of scope:**
- Changes to retro evidence capture (that's EPIC-042)
- Changes to artifact lifecycle phases or transitions
- Retroactive progress logs for existing artifacts (future sweep)
- Changes to specgraph queries (this layers context on top of existing outputs)

## Child Specs

- SPEC-199: Session Digest Auto-Generation
- SPEC-200: Progress Log and Synthesis
- SPEC-201: Artifact Context Utility
- SPEC-202: Context-Rich Display Integration

## Key Dependencies

Complementary to EPIC-042 (Retro Session Intelligence). The session digest (SPEC-199) could serve both EPICs — EPIC-042's session summaries and this EPIC's progress log entries can read from the same JSONL source.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | _pending_ | Initial creation |
