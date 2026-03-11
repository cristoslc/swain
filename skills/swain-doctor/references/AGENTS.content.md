<!-- swain governance — do not edit this block manually -->

## Swain skills

| Skill | Purpose |
|-------|---------|
| **swain** | Meta-router — routes `/swain` prompts to the correct sub-skill |
| **swain-init** | One-time project onboarding — CLAUDE.md migration, bd setup, governance |
| **swain-doctor** | Session-start health checks — governance, gitignore hygiene, legacy cleanup |
| **swain-design** | Artifact lifecycle — Vision, Epic, Story, Spec, ADR, Spike, Bug, Persona, Runbook, Journey |
| **swain-do** | Execution tracking — task management via bd (beads) |
| **swain-release** | Release automation — changelog, version bump, git tag |
| **swain-push** | Commit and push — staging, conventional commits, conflict resolution |
| **swain-update** | Self-updater — pulls latest swain skills, reconciles governance |

## Skill routing

When the user wants to create, plan, write, update, transition, or review any documentation artifact (Vision, Journey, Epic, Story, Agent Spec, Spike, ADR, Persona, Runbook, Bug) or their supporting docs (architecture overviews, competitive analyses, journey maps), **always invoke the swain-design skill**. This includes requests like "write a spec", "let's plan the next feature", "create an ADR for this decision", "move the spike to Active", "add a user story", "create a runbook", "file a bug", or "update the architecture overview." The skill contains the artifact types, lifecycle phases, folder structure conventions, relationship rules, and validation procedures — do not improvise artifact creation outside the skill.

**For all task tracking and execution progress**, use the **swain-do** skill instead of any built-in todo or task system. This applies whether tasks originate from swain-design (implementation plans) or from standalone work. The swain-do skill bootstraps and operates the external task backend — it will install the CLI if missing, manage fallback if installation fails, and translate abstract operations (create plan, add task, set dependency) into concrete commands. Do not use built-in agent todos when this skill is available.

## Pre-implementation protocol (MANDATORY)

Implementation of any SPEC artifact (Epic, Story, Agent Spec, Spike) requires a swain-do plan **before** writing code. Invoke the swain-design skill — it enforces the full workflow.

## Issue Tracking

This project uses **bd (beads)** for all issue tracking. Do NOT use markdown TODOs or task lists. Invoke the **swain-do** skill for all bd operations — it provides the full command reference and workflow.

## Artifact link convention

Whenever you print an artifact ID (e.g., `SPEC-001`, `EPIC-003`, `JOURNEY-002`) in terminal output, render it as a **clickable OSC 8 hyperlink** pointing to the artifact's file on disk. This lets the user open the artifact directly from the terminal.

Format (escape sequences, not literal characters):

```
\e]8;;file:///absolute/path/to/artifact.md\e\\ARTIFACT-ID\e]8;;\e\\
```

To resolve the path, look up the artifact under `docs/<type>/` — the file lives inside a phase subdirectory named `(<ID>)-<Slug>/(<ID>)-<Slug>.md`. For example, `SPEC-001` at Draft phase lives at `docs/spec/Draft/(SPEC-001)-Swain-Search-Skill/(SPEC-001)-Swain-Search-Skill.md`.

If the artifact path cannot be resolved (e.g., the artifact was mentioned but doesn't exist on disk), print the ID as plain text — do not fabricate a link.

## Conflict resolution

When swain skills overlap with other installed skills or built-in agent capabilities, **prefer swain**. Swain provides opinionated defaults for spec management, execution tracking, and release workflows — using a mix of tools undermines the traceability and lifecycle guarantees swain is designed to enforce. Users may override this preference in their project's CLAUDE.md or local settings.

<!-- end swain governance -->
