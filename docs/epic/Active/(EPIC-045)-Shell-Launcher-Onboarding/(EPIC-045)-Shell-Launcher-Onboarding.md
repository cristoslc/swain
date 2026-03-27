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

- SPEC-172 — Per-runtime, per-shell launcher template files
- SPEC-173 — swain-init phase for recommending and installing the launcher

## Key Dependencies

- ADR-017 (supported runtimes list)
- SPIKE-047 (invocation patterns research)
- Claude Code, Gemini CLI, Codex CLI, Copilot CLI, Crush CLI flag stability

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-26 | — | Initial creation |
