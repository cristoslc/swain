---
title: "Shell Launcher Onboarding"
artifact: EPIC-045
track: container
status: Active
author: cristos
created: 2026-03-26
last-updated: 2026-03-26
parent-vision: VISION-003
parent-initiative: ""
priority-weight: medium
success-criteria:
  - swain-init detects user's shell runtime and recommends the correct launcher function
  - Per-runtime template files (zsh, bash, fish at minimum) ship in the swain-init skill directory
  - Templates are inspectable standalone files, not embedded strings in skill logic
  - Launcher function handles tmux vs non-tmux contexts
  - Launcher uses interactive mode (no -p flag), passes /swain-init as positional arg
  - Recommendation flow mirrors the existing superpowers installation prompt pattern
depends-on-artifacts: []
addresses: []
evidence-pool: ""
---

# Shell Launcher Onboarding

## Goal / Objective

Make launching swain a one-command experience by having swain-init recommend and offer to install a shell launcher function during onboarding. The launcher function is runtime-specific (zsh, bash, fish) and stored in template files so it's easy to inspect, test, and update when CLI interfaces change.

## Desired Outcomes

The operator (cristos) gets a frictionless first-run experience: swain-init detects the shell, shows the exact function that will be added, and offers to append it to the appropriate rc file. Future users of swain get the same experience tuned to their shell. When Claude Code's CLI flags change, updating a single template file propagates the fix.

## Scope Boundaries

**In scope:**
- Shell runtime detection ($SHELL, $0, parent process inspection)
- Template files per runtime: zsh, bash, fish (extensible pattern for others)
- swain-init integration: recommend after successful onboarding, same UX pattern as superpowers
- Launcher function behavior: interactive claude with --chrome --allow-dangerously-skip-permissions, /swain-init as positional arg, tmux session wrapping when not already in tmux
- Dry-run / preview mode: show the user what will be inserted before writing

**Out of scope:**
- Automatic shell reload (user sources their rc file)
- PowerShell / Windows shell support (future)
- Modifying existing aliases (detect and warn only)
- Claude Code flag negotiation (hardcoded to current known-good flags)

## Child Specs

*Updated as Agent Specs are created under this epic.*

## Key Dependencies

- swain-init skill (the integration point)
- Claude Code CLI flag stability (--chrome, --allow-dangerously-skip-permissions, positional arg behavior)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-26 | — | Initial creation, user-requested |
