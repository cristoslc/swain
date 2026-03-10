# What to Do After `swain init`

Congrats -- your project is onboarded. You now have CLAUDE.md, AGENTS.md, bd (beads) for issue tracking, and governance rules wired up. Here is what to do next.

## Immediate next steps

1. **Start each new session with `/swain config`** -- This ensures your governance rules (skill routing, conflict resolution preferences) are loaded for the session. It is lightweight and meant to run at the beginning of every conversation.

2. **Define your project vision** -- Use `/swain design` to create a **Vision** artifact. This is the top-level document that describes what your project is, who it serves, and where it is headed. Everything else flows from this.

   Example: `/swain design create vision`

3. **Map out your first artifacts** -- Once you have a Vision, use `/swain design` to create the artifacts that make sense for your stage:
   - **Personas** -- who are your users?
   - **Journeys** -- what workflows matter most?
   - **Epics** -- what are the big chunks of work?
   - **Stories / Specs** -- what are the concrete deliverables within each epic?

## Day-to-day workflow

- **Track work with `/swain do`** -- All task tracking goes through bd (beads), not markdown TODOs or built-in task lists. Use `/swain do` to create, update, and query tasks.

- **Before implementing any spec, create a plan first** -- This is mandatory in swain. When you are ready to implement an Epic, Story, Agent Spec, or Spike, invoke `/swain design` which enforces a swain-do plan before any code gets written.

- **Commit with `/swain push`** -- Handles staging, conventional commit messages, and conflict resolution.

- **Release with `/swain release`** -- When you are ready to cut a version, this handles changelog generation, version bumping, and git tagging.

## Key things to remember

- **Use `/swain` as your entry point when unsure** -- The meta-router will figure out which sub-skill to invoke based on your prompt.
- **Swain skills take priority** over other installed skills or built-in agent capabilities for spec management, execution tracking, and releases.
- **bd is your issue tracker** -- not markdown checklists, not GitHub issues (unless you configure otherwise). All task state lives in bd.
- **Run `/swain update`** periodically to pull in the latest skill versions and reconcile governance files.

## Quick reference: skill cheat sheet

| Command | When to use it |
|---------|---------------|
| `/swain config` | Start of every session |
| `/swain design` | Create or manage any artifact (Vision, Epic, Story, Spec, ADR, Spike, Bug, Persona, Runbook, Journey) |
| `/swain do` | Track tasks, check progress, manage work items |
| `/swain push` | Stage and commit changes |
| `/swain release` | Cut a new version |
| `/swain update` | Update swain skills to latest |
| `/swain help` | Get contextual help on any swain topic |
