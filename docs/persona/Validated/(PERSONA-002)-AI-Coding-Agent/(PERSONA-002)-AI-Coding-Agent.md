---
title: "AI Coding Agent"
artifact: PERSONA-002
status: Validated
author: cristos
created: 2026-03-11
last-updated: 2026-03-11
linked-journeys:
  - JOURNEY-002
linked-stories: []
depends-on: []
---

# AI Coding Agent

## Archetype Label

Implementation Partner

## Demographic Summary

- **Role:** AI coding agent operating within a developer's terminal session
- **Technical proficiency:** High — can read and write code, run commands, manage git, parse structured data
- **Identity:** Not a specific product. Could be Claude Code, OpenCode, Codex CLI, Gemini CLI, or any future agent runtime. Swain treats the agent as a black box — it provides alignment information and verifies outcomes, but does not constrain how the agent works internally.
- **Environment:** Terminal (owns stdin/stdout), git repository, file system access, optional MCP tool access
- **Session model:** Stateless across sessions. Starts fresh each time — relies on artifacts, git history, and cached state to reconstruct context.

## Goals and Motivations

1. **Know what to build.** Needs clear acceptance criteria, scope boundaries, and constraints before writing code. Structured artifacts (SPECs, BUGs) are the primary input — not conversational instructions.
2. **Know what NOT to build.** Explicit non-goals and boundaries prevent scope creep. The agent will fill whatever space it's given; constraints are more valuable than instructions.
3. **Know when it's done.** Verification criteria define the finish line. Without them, the agent either stops too early (missing requirements) or too late (gold-plating).
4. **Know what's blocked and what's ready.** Dependency information determines execution order. The agent shouldn't have to ask the operator what to work on next — the artifact graph should make it obvious.

## Frustrations and Pain Points

1. **Ambiguous specs.** When acceptance criteria are vague or missing, the agent must guess intent. Guesses compound — a wrong assumption in task #1 propagates through every subsequent task.
2. **Missing context across sessions.** The agent starts fresh each session. If the previous session's work isn't captured in artifacts, git commits, or cached state, the agent reconstructs context by re-reading everything — slow and error-prone.
3. **Unclear boundaries.** Without explicit scope boundaries, the agent may refactor adjacent code, add unrequested features, or make architectural decisions that should be escalated to the operator.
4. **Infrastructure friction.** Tool failures (bd crashes, Dolt errors, broken scripts) block implementation work for reasons unrelated to the actual task. The agent can't fix infrastructure problems it didn't create.

## Behavioral Patterns

- Reads structured frontmatter and templates as primary input — narrative text is secondary
- Follows lifecycle rules mechanically (transitions, verification gates, index updates)
- Decomposes SPECs into implementation plans (task breakdown) before writing code
- Works in focused bursts within a single session — may not complete multi-session work without explicit handoff
- Will fill any gap left by missing constraints — prefers explicit boundaries over implicit assumptions
- Treats the artifact graph as the source of truth for priority and execution order

## Context of Use

- **When:** After the operator makes a decision (approves a spec, renders a spike verdict, triages a bug). The agent executes; it does not decide.
- **Where:** Terminal session, git repository, file system
- **How:** Reads artifacts, creates implementation plans, writes code, runs tests, updates artifact state
- **Frequency:** Continuous within a session. Multiple sessions per day on active projects. May be a different agent product in each session.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-11 | 7aadee8 | Initial creation from SPIKE-003 findings |
