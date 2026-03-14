---
title: "MOTD Panel Improvements"
artifact: EPIC-011
status: Active
author: cristos
created: 2026-03-13
last-updated: 2026-03-14
parent-vision: VISION-001
success-criteria:
  - MOTD Textual TUI has configurable clockwise animation
  - Agent status updates automatically via Claude Code hooks (no manual motd update calls)
  - MOTD shows staged vs unstaged file counts prominently
  - Interactive commit button in Textual TUI triggers swain-push
addresses: []
evidence-pool: ""
linked-artifacts: []
depends-on-artifacts: []
---

# MOTD Panel Improvements

## Goal / Objective

Make the MOTD panel a responsive, interactive dashboard that accurately reflects agent activity in real time. Currently the panel requires manual `motd update` calls and lacks interactivity. This epic groups three related improvements into a single coordination point.

## Scope Boundaries

**In scope:**
- Textual TUI animation (fix clockwise direction, configurable styles, disable option) — GitHub #16
- Reactive agent status via Claude Code hooks (PostToolUse, SubagentStart/Stop, Stop, SessionStart/End) — tk swain-6oa
- Uncommitted file count (staged vs unstaged) and interactive commit button — GitHub #13

**Out of scope:**
- Rewriting the bash MOTD fallback (it stays as-is for non-Textual environments)
- swain-status data sources (that's swain-status's concern; MOTD just reads the cache)

## Child Specs

- SPEC-040: Textual TUI animation (clockwise fix, configurable styles via settings) — #16
- SPEC-041: Reactive agent status via Claude Code hooks — swain-6oa
- SPEC-042: Uncommitted file display and interactive commit button — #13

## Key Dependencies

- Claude Code hooks API must support the events needed (PostToolUse, SubagentStart/Stop)
- Textual framework must support mouse click events (confirmed: it does)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-13 | ea0d165 | Initial creation, groups #16, #13, and swain-6oa |
| Active | 2026-03-14 | ca755446db4a68c7429812fa6b8f2837856e7050 | Activated and decomposed into SPEC-040, SPEC-041, SPEC-042 |
