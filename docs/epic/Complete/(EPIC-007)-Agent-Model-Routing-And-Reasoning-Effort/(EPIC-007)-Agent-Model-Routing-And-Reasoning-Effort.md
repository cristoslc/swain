---
title: "Agent Model Routing and Reasoning Effort Steering"
artifact: EPIC-007
track: container
status: Complete
author: cristos
created: 2026-03-13
last-updated: 2026-03-14
implementation-commits: 064b3ca
parent-vision: VISION-001
success-criteria:
  - Each swain skill invocation specifies an appropriate model tier (heavy/analysis/lightweight) and reasoning effort level
  - Claude Code runtime routes correctly — Opus for heavy planning/creative, Sonnet for analysis, Haiku for lightweight orchestration
  - Fallback instructions are present for Codex, OpenCode, Cursor, Copilot, and Gemini CLI runtimes
  - skill-creator is used to apply model steering instructions to skill files
  - Consumers running unsupported runtimes receive a graceful no-op (no errors, best-effort behavior)
addresses: []
evidence-pool: ""
linked-artifacts: []
depends-on-artifacts:
  - EPIC-006
---

# Agent Model Routing and Reasoning Effort Steering

## Goal / Objective

Swain skills currently run on whatever model the agent runtime defaults to. Different skill operations have very different cognitive demands — a SPIKE investigation needs deep reasoning, a status check needs fast analysis, and a tmux pane layout needs almost none. Routing each operation to an appropriate model tier reduces cost, improves quality on heavy tasks, and reduces latency on lightweight ones.

The primary runtime target is Claude Code (Opus / Sonnet / Haiku with extended-thinking). Fallback guidance must be provided for Codex, OpenCode, Cursor, Copilot, and Gemini CLI, which expose different or no model selection mechanisms.

Implementation uses **skill-creator** to modify skill files with model steering annotations.

## Scope Boundaries

In scope:
- Classifying every swain skill operation into a cognitive load tier (heavy / analysis / lightweight)
- Embedding model steering instructions into skill SKILL.md files via skill-creator
- Reasoning effort level guidance (extended thinking on/off, budget hints) for Claude Code
- Fallback instruction blocks for Codex, OpenCode, Cursor, Copilot, Gemini CLI
- swain-doctor check that validates model steering annotations are present in skill files

Out of scope:
- Changing what skills do — only when and with what resources they run
- Supporting non-listed runtimes
- Automatic model negotiation at runtime (static annotations only in this epic)

## Child Specs

- SPIKE-013: Model Selection Mechanisms Across Agent Runtimes (Complete)
- SPIKE-014: Swain Skill Cognitive Load Classification (Complete)
- SPEC-026: Model Tier Annotations and Routing (Complete)

## Key Dependencies

- EPIC-006 (Skill Context Footprint Reduction) — model steering annotations add content to skill files; footprint reduction should happen first or in parallel to offset the addition
- SPIKE-013 must complete before runtime-specific fallback specs are written
- SPIKE-014 must complete before per-skill annotation specs are written

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-13 | — | Initial creation |
| Active | 2026-03-13 | 71c4f9b | SPEC-026 complete; remaining criteria (active routing, skill-creator usage) need future specs |
| Complete | 2026-03-14 | bfa8692 | All scoped child specs done; unscoped criteria deferred to future epics |
