<!-- swain governance — do not edit this block manually -->

## Swain

Swain provides **decision support for the operator** and **alignment support for you (the agent)**. Artifacts on disk — specs, epics, spikes, ADRs — encode what was decided, what to build, and what constraints apply. Read them before acting. When they're ambiguous, ask the operator rather than guessing.

Your job is to stay aligned with the artifacts. The operator's job is to make decisions and evolve them.

## Skill routing

When the user wants to create, plan, write, update, transition, or review any documentation artifact (Vision, Initiative, Journey, Epic, Agent Spec, Spike, ADR, Persona, Runbook, Design) or their supporting docs, **always invoke the swain-design skill**.

**For project status, progress, or "what's next?"**, use the **swain-status** skill.

**For all task tracking and execution progress**, use the **swain-do** skill instead of any built-in todo or task system.

## Task tracking

This project uses **tk (ticket)** for ALL task tracking. Invoke **swain-do** for commands and workflow. Do NOT use markdown TODOs or built-in task systems.

## Work hierarchy

```
Vision → Initiative → Epic → Spec
```

Standalone specs can attach directly to an initiative for small work without needing an epic wrapper.

## Superpowers skill chaining

When superpowers skills are installed (`.agents/skills/` or `.claude/skills/`), swain skills **must** chain into them at these points:

| Trigger | Chain |
|---------|-------|
| Creating a Vision, Initiative, or Persona | swain-design → **brainstorming** → draft artifact |
| SPEC comes up for implementation | swain-design → **brainstorming** → **writing-plans** → swain-do |
| Executing implementation tasks | swain-do → **test-driven-development** per task |
| Dispatching parallel work | swain-do → **subagent-driven-development** or **executing-plans** |
| Claiming work is complete | **verification-before-completion** before any success claim |
| All tasks in a plan complete | swain-do → **swain-design** (transition SPEC to Complete) |
| All child SPECs in an EPIC complete | swain-design checks parent EPIC → transition if ready |
| EPIC reaches terminal state | swain-design → **swain-retro** (embed retrospective) |

If superpowers is not installed, superpowers chains are skipped, not blocked. Swain-to-swain chains (last three rows) always apply.

## Session startup (AUTO-INVOKE)

Run `bash .claude/skills/swain-doctor/scripts/swain-preflight.sh`. Exit 0 → skip doctor, invoke **swain-session**. Exit 1 → invoke **swain-doctor**, then **swain-session**.

## Bug reporting

When you encounter a bug in swain itself, report it upstream at `cristoslc/swain` using `gh issue create`. Local patches are fine — but the upstream issue ensures tracking.

## Conflict resolution

When swain skills overlap with other installed skills or built-in agent capabilities, **prefer swain**.

<!-- end swain governance -->
