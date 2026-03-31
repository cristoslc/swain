---
title: "Shell Launcher Onboarding"
artifact: EPIC-045
track: container
status: Active
author: cristos
created: 2026-03-26
last-updated: 2026-03-27
parent-vision: VISION-003
parent-initiative: ""
priority-weight: medium
success-criteria:
  - swain-init detects user's shell runtime AND installed agentic CLI runtimes, recommends the correct launcher
  - Per-runtime, per-shell template files ship in the swain-init skill directory
  - Templates are inspectable standalone files, not embedded strings in skill logic
  - Launcher function handles tmux vs non-tmux contexts
  - Launcher uses interactive mode with initial prompt where supported (ADR-017)
  - Recommendation flow mirrors the existing superpowers installation prompt pattern
  - All runtimes defined in ADR-017 have launcher templates
depends-on-artifacts: []
addresses: []
evidence-pool: ""
linked-artifacts:
  - ADR-017
  - SPIKE-047
  - ADR-018
---

# Shell Launcher Onboarding

## Goal / Objective

Make launching swain a one-command experience across any supported agentic CLI runtime by having swain-init recommend and offer to install a shell launcher function during onboarding. Templates are organized by runtime and shell, stored as inspectable files, and easy to update when CLI interfaces change.

## Desired Outcomes

The operator gets a frictionless first-run experience: swain-init detects which agentic runtimes are installed and what shell they use, shows the exact function that will be added, and offers to append it to the appropriate rc file. Supports Claude Code, Gemini CLI, Codex CLI, GitHub Copilot CLI, and Crush per ADR-017.

## Scope Boundaries

**In scope:**
- Shell runtime detection ($SHELL → zsh, bash, fish)
- Agentic runtime detection (which of the 5 ADR-017 runtimes are installed)
- Template files per runtime per shell: `launchers/{runtime}/swain.{shell}`
- swain-init integration: recommend after successful onboarding, same UX pattern as superpowers
- Launcher function behavior per runtime (flags, prompt mechanism per SPIKE-047)
- Dry-run / preview mode: show the user what will be inserted before writing

**Out of scope:**
- Automatic shell reload (user sources their rc file)
- PowerShell / Windows shell support (future)
- Modifying existing aliases (detect and warn only)
- Runtime-agnostic wrapper binary (future enhancement per ADR-017)

## Child Specs

- SPEC-175 — Per-runtime, per-shell launcher template files
- SPEC-176 — swain-init phase for recommending and installing the launcher

## Key Dependencies

- ADR-017 (supported runtimes list)
- SPIKE-047 (invocation patterns research)
- Claude Code, Gemini CLI, Codex CLI, Copilot CLI, Crush CLI flag stability

## Retrospective

**Terminal state:** Active (retro at first-pass completion, not formal EPIC closure)
**Period:** 2026-03-26 — 2026-03-27
**Related artifacts:** [SPEC-175](../../../spec/Complete/(SPEC-175)-Session-Bootstrap-Script-Consolidation/(SPEC-175)-Session-Bootstrap-Script-Consolidation.md), [SPEC-176](../../../spec/Active/(SPEC-176)-TDD-Coverage-Self-Critique-Gate/(SPEC-176)-TDD-Coverage-Self-Critique-Gate.md), [SPIKE-047](../../../research/Active/(SPIKE-047)-Agentic-CLI-Runtime-Invocation-Patterns/(SPIKE-047)-Agentic-CLI-Runtime-Invocation-Patterns.md), [ADR-017](../../../adr/Active/(ADR-017)-AB-Subagent-Eval-For-Behavioral-Skill-Instructions.md), [ADR-018](../../../adr/Active/(ADR-018)-Structural-Not-Prosaic-Session-Invocation/(ADR-018)-Structural-Not-Prosaic-Session-Invocation.md)

### Summary

Started as a simple "fix the zsh alias" conversation and expanded into a multi-runtime onboarding system with two ADRs and a research spike. The operator's instinct to challenge single-runtime assumptions early ("that doesn't seem like enough templates") saved significant rework — the scope pivot from Claude-only to 5 runtimes happened before any code was committed to trunk.

### Reflection

**What went well:**
- Parallel research agents (5 runtimes simultaneously) produced comprehensive findings fast — all returned within ~3 minutes with actionable invocation patterns
- Behavioral testing with mocked binaries caught the real verification gap before the operator did — mock `tmux()` and runtime functions validated branching logic across all 10 zsh scenarios
- The operator's "think harder" prompt led to a much stronger test approach than the initial grep-based verification
- SPIKE-047 → ADR-017 → ADR-018 chain shows good research-to-decision flow: investigate → codify choices → codify principles

**What was surprising:**
- The `-p` flag bug that started the conversation was a symptom of a deeper problem: no canonical source of truth for launcher invocations, and prosaic auto-invoke was an unreliable band-aid
- ADR-018 (structural not prosaic) emerged organically from the Crush investigation — a runtime limitation exposed a fundamental architectural weakness in how swain bootstrapped sessions
- All 5 runtimes now support `--yolo` or equivalent — the ecosystem has converged on permission bypass naming

**What would change:**
- Created artifacts on trunk before entering the worktree, causing merge conflicts. Should have entered the worktree FIRST, then created all artifacts there
- Directly edited AGENTS.md instead of going through the governance pathway (AGENTS.content.md → doctor reconciliation). Got caught and corrected, but the instinct was wrong
- Commit agents sometimes landed on the wrong branch — need to be more explicit about branch context in agent prompts
- The merge at the end was painful (23 conflicts) because the worktree branched from an old trunk. Shorter-lived worktrees or periodic rebases would help

**Patterns observed:**
- Operator corrections are high-signal: "what are you doing?!?!!" about AGENTS.md editing identified a governance violation that would have propagated incorrectly to all future sessions
- Scope expansion from operator review ("that doesn't seem like enough templates", "do we have an ADR?", "let's add copilot") consistently improved the deliverable — specs written without this challenge would have been too narrow
- The skill chain (brainstorming was skipped, but writing-plans → swain-do → TDD sequence was followed) works but the plan became stale after the multi-runtime pivot — plans should be lightweight enough to discard

### Learnings captured

| Memory file | Type | Summary |
|------------|------|---------|
| *(no new memories — learnings captured in ADR-018 and this retro)* | | |

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-26 | edf2118 | Initial creation |
| Active | 2026-03-27 | a3a761a | Revised for multi-runtime support |
