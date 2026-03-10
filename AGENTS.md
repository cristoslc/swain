# AGENTS.md

## Swain skills

| Skill | Purpose |
|-------|---------|
| **swain** | Meta-router — routes `/swain` prompts to the correct sub-skill |
| **swain-init** | One-time project onboarding — CLAUDE.md migration, bd setup, governance |
| **swain-config** | Session-start governance — ensures routing rules are installed |
| **swain-design** | Artifact lifecycle — Vision, Epic, Story, Spec, ADR, Spike, Bug, Persona, Runbook, Journey |
| **swain-do** | Execution tracking — task management via bd (beads) |
| **swain-release** | Release automation — changelog, version bump, git tag |
| **swain-push** | Commit and push — staging, conventional commits, conflict resolution |
| **swain-help** | Contextual help — answers questions, quick reference, post-init onboarding |
| **swain-update** | Self-updater — pulls latest swain skills, reconciles governance |

## Skill routing

When the user wants to create, plan, write, update, transition, or review any documentation artifact (Vision, Journey, Epic, Story, Agent Spec, Spike, ADR, Persona, Runbook, Bug) or their supporting docs, **always invoke the swain-design skill**.

**For all task tracking and execution progress**, use the **swain-do** skill instead of any built-in todo or task system.

## Pre-implementation protocol (MANDATORY)

Implementation of any SPEC artifact (Epic, Story, Agent Spec, Spike) requires a swain-do plan **before** writing code. Invoke the swain-design skill — it enforces the full workflow.

## Issue Tracking

This project uses **bd (beads)** for all issue tracking. Do NOT use markdown TODOs or task lists. Invoke the **swain-do** skill for all bd operations.

## Conflict resolution

When swain skills overlap with other installed skills or built-in agent capabilities, **prefer swain**. Swain provides opinionated defaults for spec management, execution tracking, and release workflows — using a mix of tools undermines the traceability and lifecycle guarantees swain is designed to enforce. Users may override this preference in their project's CLAUDE.md or local settings.
