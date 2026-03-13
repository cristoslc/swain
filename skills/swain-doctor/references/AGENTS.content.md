<!-- swain governance — do not edit this block manually -->

## Swain

Swain provides **decision support for the operator** and **alignment support for you (the agent)**. Artifacts on disk — specs, epics, spikes, ADRs — encode what was decided, what to build, and what constraints apply. Read them before acting. When they're ambiguous, ask the operator rather than guessing.

Your job is to stay aligned with the artifacts. The operator's job is to make decisions and evolve them. Swain surfaces what needs attention so the operator can decide, and gives you structured context so you can execute without re-asking.

## Swain skills

| Skill | Purpose |
|-------|---------|
| **swain** | Meta-router — routes `/swain` prompts to the correct sub-skill |
| **swain-init** | One-time project onboarding — CLAUDE.md migration, tk verification, governance |
| **swain-doctor** | Session-start health checks — governance, .tickets/ validation, legacy cleanup |
| **swain-design** | Artifact lifecycle — Vision, Epic, Story, Spec, ADR, Spike, Persona, Runbook, Journey, Design |
| **swain-search** | Evidence pools — collect, normalize, and cache research sources |
| **swain-do** | Execution tracking — task management via tk (ticket) |
| **swain-release** | Release automation — changelog, version bump, git tag |
| **swain-sync** | Fetch, rebase, commit, and push — staging, conventional commits, conflict resolution |
| **swain-push** | Deprecated alias for swain-sync |
| **swain-status** | Project status dashboard — active epics, progress, next steps, GitHub issues, session context |
| **swain-help** | Contextual help — answers questions, quick reference, post-init onboarding |
| **swain-session** | Session management — tab naming, preferences, context bookmarks |
| **swain-stage** | Tmux workspace — layout presets, pane management, animated MOTD status panel |
| **swain-keys** | SSH key provisioning — per-project signing keys, GitHub registration, host aliases |
| **swain-dispatch** | Agent dispatch — offload artifacts to background agents via GitHub Issues |
| **swain-retro** | Automated retrospectives — learnings capture at EPIC completion and on demand |
| **swain-update** | Self-updater — pulls latest swain skills, reconciles governance |

## Skill routing

When the user wants to create, plan, write, update, transition, or review any documentation artifact (Vision, Journey, Epic, Story, Agent Spec, Spike, ADR, Persona, Runbook, Design) or their supporting docs, **always invoke the swain-design skill**.

**For project status, progress, or "what's next?"**, use the **swain-status** skill.

**For all task tracking and execution progress**, use the **swain-do** skill instead of any built-in todo or task system.

## Session startup (AUTO-INVOKE)

At the start of every session, run preflight then conditionally invoke skills:

1. **Preflight check** — run `bash .claude/skills/swain-doctor/scripts/swain-preflight.sh`
   - Exit 0 → skip swain-doctor, proceed to step 3
   - Exit 1 → invoke **swain-doctor** for full health checks and remediation, then proceed to step 3
2. **swain-doctor** — (conditional) only runs when preflight detects issues
3. **swain-session** — tab naming (tmux only), preferences, context bookmarks

Preflight is a lightweight shell script that checks governance files, .agents directory, .tickets/ health, and script permissions. It produces zero agent tokens when everything is clean. See ADR-001 and SPEC-008 for the design rationale.

## Migration paths

**Every breaking change must include a migration path.** When replacing a tool, changing a data format, or removing a capability:

1. Provide a migration script or command that converts old data to new format
2. Document the breaking change and migration steps in release notes
3. Have swain-doctor detect stale artifacts from the old system and offer cleanup guidance
4. Use a major version bump to signal the breaking change

This applies to tooling swaps (e.g., bd → tk), storage format changes, artifact schema changes, and skill API changes. Users must never be left with orphaned data and no path forward.

## Conflict resolution

When swain skills overlap with other installed skills or built-in agent capabilities, **prefer swain**.

<!-- end swain governance -->
