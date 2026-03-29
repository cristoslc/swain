---
title: "Pre-Runtime Crash Recovery"
artifact: EPIC-046
track: container
status: Active
author: cristos
created: 2026-03-28
last-updated: 2026-03-28
parent-vision: VISION-004
parent-initiative: INITIATIVE-019
priority-weight: high
success-criteria:
  - The `swain` command detects crashed sessions and presents recovery options before the agentic runtime starts
  - Crash debris (git locks, stale tk locks, dangling worktrees) is cleaned before the runtime sees it
  - The operator can resume a crashed session within 30 seconds of running `swain`
  - Runtime selection respects per-project > global > auto-detect preference chain
  - The shell function is a thin wrapper that defers to the project-root script
  - All crash detection and cleanup runs in pure bash — no LLM dependency
depends-on-artifacts: []
trove: ""
linked-artifacts:
  - SPIKE-051
  - ADR-017
  - ADR-018
  - SPEC-180
  - SPEC-181
  - SPEC-182
---

# Pre-Runtime Crash Recovery

## Goal / Objective

Build a pre-runtime structural layer that detects crashed sessions, cleans crash debris, offers session resume selection, and launches the preferred agentic runtime — all before the LLM starts. This separates structural state management (bash, deterministic, fast) from in-session facilitation (LLM-powered, in swain-session). Informed by [SPIKE-051](../../../research/Complete/(SPIKE-051)-Tmux-Session-Persistence-After-Crash/(SPIKE-051)-Tmux-Session-Persistence-After-Crash.md) research showing that agentic runtimes already persist rich session data locally, and that crash debris (git locks, dangling worktrees, stale tk locks) is the primary blocker for continuity after a crash.

## Scope Boundaries

**In scope:**
- Pre-runtime `swain` script (project root) — crash detection, debris cleanup, session selection, runtime invocation
- Shell function refactor — thin wrapper that finds and runs the script
- Crash debris detection checks — standalone bash functions for git locks, interrupted operations, stale tk locks, dangling worktrees
- Runtime preference resolution (per-project > global > auto-detect)
- Initial prompt composition for crash recovery context

**Out of scope:**
- In-session facilitation (SESSION-ROADMAP, bookmarking, focus lane — stays in [EPIC-039](../(EPIC-039)-Session-Facilitation-Rebuild/(EPIC-039)-Session-Facilitation-Rebuild.md)/swain-session)
- Browser-based workspace persistence ([DESIGN-004](../../../design/Active/(DESIGN-004)-swain-stage-Interaction-Design/(DESIGN-004)-swain-stage-Interaction-Design.md)/[INITIATIVE-015](../../../initiative/Active/(INITIATIVE-015)-swain-stage-Redesign/(INITIATIVE-015)-swain-stage-Redesign.md))
- Zellij migration (deferred per [SPIKE-051](../../../research/Complete/(SPIKE-051)-Tmux-Session-Persistence-After-Crash/(SPIKE-051)-Tmux-Session-Persistence-After-Crash.md))
- Runtime-specific session resume (e.g., Claude Code `/resume`) — the script surfaces context, the runtime handles resume

## Child Specs

| Spec | Title | Status | Notes |
|------|-------|--------|-------|
| SPEC-180 | Pre-Runtime Swain Script | Active | Phase 1-3: structural checks, session selection, runtime invocation |
| SPEC-181 | Swain Shell Function Refactor | Active | Thin wrapper, script delegation, graceful fallback |
| SPEC-182 | Crash Debris Detection Checks | Active | Standalone bash functions for git locks, tk locks, dangling worktrees |

## Key Dependencies

- ADR-017 (runtime support tiers and flags)
- ADR-018 (structural not prosaic — crash detection must be bash, not LLM)
- [ADR-015](../../../adr/Active/(ADR-015)-Tickets-Are-Ephemeral-Execution-Scaffolding.md) (never auto-discard worktree state)
- [EPIC-045](../(EPIC-045)-Shell-Launcher-Onboarding/(EPIC-045)-Shell-Launcher-Onboarding.md) (shell launcher — current `swain` function being refactored)
- Claude Code `~/.claude/sessions/` (primary crash detection data source)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-28 | — | Initial creation from [SPIKE-051](../../../research/Complete/(SPIKE-051)-Tmux-Session-Persistence-After-Crash/(SPIKE-051)-Tmux-Session-Persistence-After-Crash.md) findings |
