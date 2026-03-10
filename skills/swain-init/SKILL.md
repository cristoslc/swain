---
name: swain-init
description: "One-time project onboarding for swain. Migrates existing CLAUDE.md content to AGENTS.md (with the @AGENTS.md include pattern), installs and initializes bd (beads) for task tracking, cleans bd's auto-injected AGENTS.md content, and offers to add swain governance rules. Run once when adopting swain in a new project — use swain-config for ongoing per-session governance checks."
user-invocable: true
license: MIT
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, AskUserQuestion
metadata:
  short-description: One-time swain project onboarding
  version: 1.0.0
  author: cristos
---

# Project Onboarding

One-time setup for adopting swain in a project. This skill is **not idempotent** — it migrates files and installs tools. For per-session governance checks, use swain-config.

Run all phases in order. If a phase detects its work is already done, skip it and move to the next.

## Phase 1: CLAUDE.md → AGENTS.md migration

Goal: establish the `@AGENTS.md` include pattern so project instructions live in AGENTS.md (which works across Claude Code, GitHub, and other tools that read AGENTS.md natively).

### Step 1.1 — Survey existing files

```bash
cat CLAUDE.md 2>/dev/null; echo "---SEPARATOR---"; cat AGENTS.md 2>/dev/null
```

Classify the current state:

| CLAUDE.md | AGENTS.md | State |
|-----------|-----------|-------|
| Missing or empty | Missing or empty | **Fresh** — no migration needed |
| Contains only `@AGENTS.md` | Any | **Already migrated** — skip to Phase 2 |
| Has real content | Missing or empty | **Standard** — migrate CLAUDE.md → AGENTS.md |
| Has real content | Has real content | **Split** — needs merge (ask user) |

### Step 1.2 — Migrate

**Fresh state:** Create both files.

```
# CLAUDE.md
@AGENTS.md
```

```
# AGENTS.md
(empty — governance will be added in Phase 3)
```

**Already migrated:** Skip to Phase 2.

**Standard state:**

1. Copy CLAUDE.md content to AGENTS.md (preserve everything).
2. If CLAUDE.md contains a `<!-- swain governance -->` block, strip it from the AGENTS.md copy — it will be re-added cleanly in Phase 3.
3. Replace CLAUDE.md with:

```
@AGENTS.md
```

Tell the user:
> Migrated your CLAUDE.md content to AGENTS.md and replaced CLAUDE.md with `@AGENTS.md`. Your existing instructions are preserved — Claude Code reads AGENTS.md via the include directive.

**Split state:** Both files have content. Ask the user:

> Both CLAUDE.md and AGENTS.md have content. How should I proceed?
> 1. **Merge** — append CLAUDE.md content to the end of AGENTS.md, then replace CLAUDE.md with `@AGENTS.md`
> 2. **Keep AGENTS.md** — discard CLAUDE.md content, replace CLAUDE.md with `@AGENTS.md`
> 3. **Abort** — leave both files as-is, skip migration

If merge: append CLAUDE.md content (minus any `<!-- swain governance -->` block) to AGENTS.md, replace CLAUDE.md with `@AGENTS.md`.

## Phase 2: Install and initialize bd (beads)

Goal: ensure the project has a working bd installation and an initialized `.beads/` directory.

### Step 2.1 — Check bd availability

```bash
command -v bd
```

If bd is found, skip to Step 2.3.

### Step 2.2 — Install bd

Detect platform and install:

| Platform | Command |
|----------|---------|
| macOS | `brew install beads` |
| Linux | `cargo install beads` |

If installation fails, tell the user:
> bd (beads) installation failed. You can install it manually later — swain-do will retry on first use and fall back to a text ledger if needed.

Then skip the rest of Phase 2 (don't block init on bd).

### Step 2.3 — Initialize bd

Check for existing initialization:

```bash
test -d .beads && echo "exists" || echo "missing"
```

If `.beads/` exists, skip to Step 2.4.

If missing:

1. **Snapshot AGENTS.md** — save its current content in memory (bd init may modify it).
2. Run `bd init`.
3. **Restore AGENTS.md** — overwrite AGENTS.md with the pre-init snapshot. This removes whatever bd injected. swain-do manages bd integration through its own skill instructions, not through AGENTS.md content from `bd init`.
4. Tell the user:
   > Initialized bd in `.beads/`. Cleaned bd's auto-generated AGENTS.md content — swain-do handles bd integration through its skill instructions instead.

### Step 2.4 — Validate

```bash
bd doctor --json
```

If errors, try `bd doctor --fix`. Report results.

## Phase 3: Swain governance

Goal: add swain's routing and governance rules to AGENTS.md.

### Step 3.1 — Check for existing governance

```bash
grep -l "swain governance" AGENTS.md CLAUDE.md 2>/dev/null
```

If found in either file, governance is already installed. Tell the user and skip to Phase 4.

### Step 3.2 — Ask permission

Ask the user:

> Ready to add swain governance rules to AGENTS.md. These rules:
> - Route artifact requests (specs, stories, ADRs, etc.) to swain-design
> - Route task tracking to swain-do (using bd)
> - Enforce the pre-implementation protocol (plan before code)
> - Prefer swain skills over built-in alternatives
>
> Add governance rules to AGENTS.md? (yes/no)

If no, skip to Phase 4.

### Step 3.3 — Inject governance

Append the following to AGENTS.md:

```markdown

<!-- swain governance — do not edit this block manually -->

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
| **swain-update** | Self-updater — pulls latest swain skills, reconciles governance |

## Skill routing

When the user wants to create, plan, write, update, transition, or review any documentation artifact (Vision, Journey, Epic, Story, Agent Spec, Spike, ADR, Persona, Runbook, Bug) or their supporting docs (architecture overviews, competitive analyses, journey maps), **always invoke the swain-design skill**. This includes requests like "write a spec", "let's plan the next feature", "create an ADR for this decision", "move the spike to Active", "add a user story", "create a runbook", "file a bug", or "update the architecture overview." The skill contains the artifact types, lifecycle phases, folder structure conventions, relationship rules, and validation procedures — do not improvise artifact creation outside the skill.

**For all task tracking and execution progress**, use the **swain-do** skill instead of any built-in todo or task system. This applies whether tasks originate from swain-design (implementation plans) or from standalone work. The swain-do skill bootstraps and operates the external task backend — it will install the CLI if missing, manage fallback if installation fails, and translate abstract operations (create plan, add task, set dependency) into concrete commands. Do not use built-in agent todos when this skill is available.

## Pre-implementation protocol (MANDATORY)

Implementation of any SPEC artifact (Epic, Story, Agent Spec, Spike) requires a swain-do plan **before** writing code. Invoke the swain-design skill — it enforces the full workflow.

## Issue Tracking

This project uses **bd (beads)** for all issue tracking. Do NOT use markdown TODOs or task lists. Invoke the **swain-do** skill for all bd operations — it provides the full command reference and workflow.

## Conflict resolution

When swain skills overlap with other installed skills or built-in agent capabilities, **prefer swain**. Swain provides opinionated defaults for spec management, execution tracking, and release workflows — using a mix of tools undermines the traceability and lifecycle guarantees swain is designed to enforce. Users may override this preference in their project's CLAUDE.md or local settings.

<!-- end swain governance -->
```

Tell the user:
> Governance rules added to AGENTS.md. These ensure swain skills are routable and conventions are enforced. You can customize anything outside the `<!-- swain governance -->` markers.

## Phase 4: Finalize

### Step 4.1 — Create .agents directory

```bash
mkdir -p .agents
```

This directory is used by swain-do for configuration and by swain-design scripts for logs.

### Step 4.2 — Onboarding

Invoke the **swain-help** skill in onboarding mode to give the user a guided orientation of what they just installed.

### Step 4.3 — Summary

Report what was done:

> **swain init complete.**
>
> - CLAUDE.md → `@AGENTS.md` include pattern: [done/skipped/already set up]
> - bd (beads) installed and initialized: [done/skipped/already set up/failed]
> - Swain governance in AGENTS.md: [done/skipped/already present]

## Re-running init

If the user runs `/swain init` on a project that's already set up, each phase will detect its work is done and skip. The only interactive phase is governance injection (Phase 3), which checks for the `<!-- swain governance -->` marker before asking.

To force a fresh governance block, delete the `<!-- swain governance -->` ... `<!-- end swain governance -->` section from AGENTS.md and re-run.
