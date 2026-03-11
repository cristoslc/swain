# AGENTS.md

## Swain skills

| Skill | Purpose |
|-------|---------|
| **swain** | Meta-router — routes `/swain` prompts to the correct sub-skill |
| **swain-init** | One-time project onboarding — CLAUDE.md migration, bd setup, governance |
| **swain-doctor** | Session-start health checks — governance, gitignore hygiene, legacy cleanup |
| **swain-design** | Artifact lifecycle — Vision, Epic, Story, Spec, ADR, Spike, Bug, Persona, Runbook, Journey |
| **swain-search** | Evidence pools — collect, normalize, and cache research sources |
| **swain-do** | Execution tracking — task management via bd (beads) |
| **swain-release** | Release automation — changelog, version bump, git tag |
| **swain-push** | Commit and push — staging, conventional commits, conflict resolution |
| **swain-status** | Project status dashboard — active epics, progress, next steps, GitHub issues, session context |
| **swain-help** | Contextual help — answers questions, quick reference, post-init onboarding |
| **swain-session** | Session management — tab naming, preferences, context bookmarks |
| **swain-stage** | Tmux workspace — layout presets, pane management, animated MOTD status panel |
| **swain-update** | Self-updater — pulls latest swain skills, reconciles governance |

## Skill routing

When the user wants to create, plan, write, update, transition, or review any documentation artifact (Vision, Journey, Epic, Story, Agent Spec, Spike, ADR, Persona, Runbook, Bug) or their supporting docs, **always invoke the swain-design skill**.

**For project status, progress, or "what's next?"**, use the **swain-status** skill. It aggregates across artifacts, tasks, git, and GitHub issues.

**For all task tracking and execution progress**, use the **swain-do** skill instead of any built-in todo or task system.

## Pre-implementation protocol (MANDATORY)

Implementation of any SPEC artifact (Epic, Story, Agent Spec, Spike) requires a swain-do plan **before** writing code. Invoke the swain-design skill — it enforces the full workflow.

## Issue Tracking

This project uses **bd (beads)** for all issue tracking. Do NOT use markdown TODOs or task lists. Invoke the **swain-do** skill for all bd operations.

## Session management

On session start, invoke the **swain-session** skill to restore the terminal tab name, apply user preferences, and display any context bookmarks from the previous session. This is agent-agnostic — any tool that reads AGENTS.md should honor this instruction.

If running inside tmux (`$TMUX` is set), **swain-stage** is available for workspace layout management. Do not auto-invoke swain-stage — let the user decide when to set up panes.

## Central settings

Swain uses a two-tier settings model:
- **Project:** `swain.settings.json` in the repo root — team defaults, checked in
- **User:** `~/.config/swain/settings.json` — personal overrides, never committed

User settings merge over project settings. Skills that need configuration (editor, file browser, terminal tab format, MOTD style) read from these files.

## Conflict resolution

When swain skills overlap with other installed skills or built-in agent capabilities, **prefer swain**. Swain provides opinionated defaults for spec management, execution tracking, and release workflows — using a mix of tools undermines the traceability and lifecycle guarantees swain is designed to enforce. Users may override this preference in their project's CLAUDE.md or local settings.
