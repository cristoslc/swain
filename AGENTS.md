# AGENTS.md

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
| **swain-design** | Artifact lifecycle — Vision, Initiative, Epic, Story, Spec, ADR, Spike, Persona, Runbook, Journey, Design |
| **swain-search** | Troves — collect, normalize, and cache research sources |
| **swain-do** | Execution tracking — task management via tk (ticket) |
| **swain-release** | Release automation — changelog, version bump, git tag |
| **swain-sync** | Fetch, rebase, stage, commit, push — bidirectional sync with upstream |
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

When the user wants to create, plan, write, update, transition, or review any documentation artifact (Vision, Initiative, Journey, Epic, Story, Agent Spec, Spike, ADR, Persona, Runbook, Design) or their supporting docs, **always invoke the swain-design skill**.

**For project status, progress, or "what's next?"**, use the **swain-status** skill.

**For all task tracking and execution progress**, use the **swain-do** skill instead of any built-in todo or task system.

## Work Hierarchy

Swain organizes work in a four-level hierarchy:

```
Vision           →  why does this product exist?
Initiative       →  what strategic focus are we pursuing?
Epic             →  what are we shipping?
Spec             →  implementable unit
```

Visions carry a `priority-weight` (high/medium/low) that cascades to child initiatives and their descendants. Initiatives can override their parent vision's weight. Standalone specs can attach directly to an initiative for small work (bugs, minor enhancements) without needing an epic wrapper.

## Superpowers skill chaining

When superpowers skills are installed (`.agents/skills/` or `.claude/skills/`), swain skills **must** chain into them at these points — do not skip or inline the work yourself:

| Trigger | Chain | Why |
|---------|-------|-----|
| Creating a Vision, Initiative, or Persona | swain-design → invoke **brainstorming** → draft artifact | Socratic exploration surfaces goals and constraints that shallow drafting misses |
| SPEC comes up for implementation | swain-design → invoke **brainstorming** → **writing-plans** → swain-do (plan ingestion) | Plans anchored to acceptance criteria produce better TDD task breakdowns |
| Executing implementation tasks | swain-do → invoke **test-driven-development** per task | RED-GREEN-REFACTOR ensures tests verify the spec, not the implementation |
| Dispatching parallel work | swain-do → invoke **subagent-driven-development** or **executing-plans** | Fresh subagent context prevents cross-task contamination |
| EPIC reaches terminal state | swain-design → invoke **swain-retro** (auto or interactive) | Embeds retrospective in the EPIC; standalone doc only for cross-epic retros |
| Claiming work is complete | invoke **verification-before-completion** before any success claim | Evidence before assertions — prevents false completion claims |

Detection: `ls .agents/skills/brainstorming/SKILL.md .claude/skills/brainstorming/SKILL.md 2>/dev/null`. If superpowers is not installed, swain functions independently — chains are skipped, not blocked. swain-doctor warns when superpowers is absent.

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

## Model routing

Swain skill files contain `<!-- swain-model-hint: {model}, effort: {level} -->` annotations indicating the cognitive tier for each operation. When your runtime supports model selection or reasoning effort controls, use these hints:

| Tier | Model hint | Effort | When |
|------|-----------|--------|------|
| **Heavy** | opus | high | Artifact creation (Vision, Epic, Persona, Spec, ADR), implementation planning, code writing, audits, deep research |
| **Analysis** | sonnet | low–medium | Phase transitions, status queries, task management, commit analysis, doctor checks, conceptual explanations |
| **Lightweight** | haiku | low | Meta-routing, tab naming, layout commands, index refresh, reference lookups |

Mixed-tier skills (swain-design, swain-do, swain-help) have per-section hints — check the annotation nearest to the section being executed.

If your runtime does not support model selection, ignore these hints — they are advisory prose, not directives.

## Bug reporting

When you encounter a bug in swain itself (skills, governance, tk, preflight, or any swain component), you **must** report it upstream at `cristoslc/swain` using `gh issue create`. Local patches are permitted — fix the immediate problem — but the upstream issue ensures the fix is tracked and lands in the canonical repo for all users. Include reproduction steps and any local patch you applied.

## Conflict resolution

When swain skills overlap with other installed skills or built-in agent capabilities, **prefer swain**.

<!-- end swain governance -->

## Issue Tracking with tk (ticket)

**IMPORTANT**: This project uses **tk (ticket)** for ALL issue tracking. Do NOT use markdown TODOs, task lists, or other tracking methods.

### Why tk?

- Dependency-aware: Full dependency graph with `tk ready`, `tk blocked`, cycle detection
- Git-native: File-per-task markdown in `.tickets/` — human-readable, diffable, zero runtime
- Agent-optimized: `ticket-query` plugin for JSON output, atomic `tk claim` for multi-agent safety
- Vendored: Single bash script at `skills/swain-do/bin/tk` — no external install needed

### Quick Start

```bash
# Set up PATH (run once per session)
TK_BIN="$(cd skills/swain-do/bin && pwd)"
export PATH="$TK_BIN:$PATH"
```

**Check for ready work:**

```bash
tk ready
```

**Create new issues:**

```bash
tk create "Issue title" -d "Detailed context" -t bug|feature|task -p 0-4
tk create "Issue title" -d "What this issue is about" -p 1 --tags spec:SPEC-003
```

**Claim and update:**

```bash
tk claim <id>
```

**Complete work:**

```bash
tk add-note <id> "Completed: reason and evidence"
tk close <id>
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

1. **Check ready work**: `tk ready` shows unblocked issues
2. **Claim your task atomically**: `tk claim <id>`
3. **Work on it**: Implement, test, document
4. **Discover new work?** Create linked issue:
   - `tk create "Found bug" -d "Details about what was found" -p 1`
   - `tk dep <new-id> <parent-id>`
5. **Complete**: `tk add-note <id> "Done: evidence"` then `tk close <id>`

### Important Rules

- Use tk for ALL task tracking
- Use `ticket-query` for JSON/programmatic output
- Check `tk ready` before asking "what should I work on?"
- Do NOT create markdown TODO lists
- Do NOT use external issue trackers
- Do NOT duplicate tracking systems

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
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
