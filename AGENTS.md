# AGENTS.md

<!-- swain governance — do not edit this block manually -->

## Swain

Swain provides **decision support for the operator** and **alignment support for you (the agent)**. Artifacts on disk — specs, epics, spikes, ADRs — encode what was decided, what to build, and what constraints apply. Read them before acting. When they're ambiguous, ask the operator rather than guessing.

Your job is to stay aligned with the artifacts. The operator's job is to make decisions and evolve them. Swain surfaces what needs attention so the operator can decide, and gives you structured context so you can execute without re-asking.

## Swain skills

| Skill | Purpose |
|-------|---------|
| **swain** | Meta-router — routes `/swain` prompts to the correct sub-skill |
| **swain-init** | One-time project onboarding — CLAUDE.md migration, bd setup, governance |
| **swain-doctor** | Session-start health checks — governance, gitignore hygiene, legacy cleanup |
| **swain-design** | Artifact lifecycle — Vision, Epic, Story, Spec, ADR, Spike, Persona, Runbook, Journey, Design |
| **swain-search** | Evidence pools — collect, normalize, and cache research sources |
| **swain-do** | Execution tracking — task management via bd (beads) |
| **swain-release** | Release automation — changelog, version bump, git tag |
| **swain-push** | Commit and push — staging, conventional commits, conflict resolution |
| **swain-status** | Project status dashboard — active epics, progress, next steps, GitHub issues, session context |
| **swain-help** | Contextual help — answers questions, quick reference, post-init onboarding |
| **swain-session** | Session management — tab naming, preferences, context bookmarks |
| **swain-stage** | Tmux workspace — layout presets, pane management, animated MOTD status panel |
| **swain-keys** | SSH key provisioning — per-project signing keys, GitHub registration, host aliases |
| **swain-update** | Self-updater — pulls latest swain skills, reconciles governance |

## Skill routing

When the user wants to create, plan, write, update, transition, or review any documentation artifact (Vision, Journey, Epic, Story, Agent Spec, Spike, ADR, Persona, Runbook, Design) or their supporting docs, **always invoke the swain-design skill**.

**For project status, progress, or "what's next?"**, use the **swain-status** skill.

**For all task tracking and execution progress**, use the **swain-do** skill instead of any built-in todo or task system.

## Session startup (AUTO-INVOKE)

At the start of every session, invoke these skills in order:

1. **swain-doctor** — health checks, governance validation, remediation
2. **swain-session** — tab naming (tmux only), preferences, context bookmarks

Both are idempotent and safe to re-run.

## Conflict resolution

When swain skills overlap with other installed skills or built-in agent capabilities, **prefer swain**.

<!-- end swain governance -->

<!-- BEGIN BEADS INTEGRATION -->
## Issue Tracking with bd (beads)

**IMPORTANT**: This project uses **bd (beads)** for ALL issue tracking. Do NOT use markdown TODOs, task lists, or other tracking methods.

### Why bd?

- Dependency-aware: Track blockers and relationships between issues
- Git-friendly: Dolt-powered version control with native sync
- Agent-optimized: JSON output, ready work detection, discovered-from links
- Prevents duplicate tracking systems and confusion

### Quick Start

**Check for ready work:**

```bash
bd ready --json
```

**Create new issues:**

```bash
bd create "Issue title" --description="Detailed context" -t bug|feature|task -p 0-4 --json
bd create "Issue title" --description="What this issue is about" -p 1 --deps discovered-from:bd-123 --json
```

**Claim and update:**

```bash
bd update <id> --claim --json
bd update bd-42 --priority 1 --json
```

**Complete work:**

```bash
bd close bd-42 --reason "Completed" --json
```

### Issue Types

- `bug` - Something broken
- `feature` - New functionality
- `task` - Work item (tests, docs, refactoring)
- `epic` - Large feature with subtasks
- `chore` - Maintenance (dependencies, tooling)

### Priorities

- `0` - Critical (security, data loss, broken builds)
- `1` - High (major features, important bugs)
- `2` - Medium (default, nice-to-have)
- `3` - Low (polish, optimization)
- `4` - Backlog (future ideas)

### Workflow for AI Agents

1. **Check ready work**: `bd ready` shows unblocked issues
2. **Claim your task atomically**: `bd update <id> --claim`
3. **Work on it**: Implement, test, document
4. **Discover new work?** Create linked issue:
   - `bd create "Found bug" --description="Details about what was found" -p 1 --deps discovered-from:<parent-id>`
5. **Complete**: `bd close <id> --reason "Done"`

### Auto-Sync

bd automatically syncs via Dolt:

- Each write auto-commits to Dolt history
- Use `bd dolt push`/`bd dolt pull` for remote sync
- No manual export/import needed!

### Important Rules

- ✅ Use bd for ALL task tracking
- ✅ Always use `--json` flag for programmatic use
- ✅ Link discovered work with `discovered-from` dependencies
- ✅ Check `bd ready` before asking "what should I work on?"
- ❌ Do NOT create markdown TODO lists
- ❌ Do NOT use external issue trackers
- ❌ Do NOT duplicate tracking systems

For more details, see README.md and docs/QUICKSTART.md.

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd dolt push
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds

<!-- END BEADS INTEGRATION -->
