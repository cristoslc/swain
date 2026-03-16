---
name: swain-do
description: Bootstrap, install, and operate an external task-management CLI as the source of truth for agent execution tracking (instead of built-in todos). Provides the abstraction layer between swain-design intent (implementation plans and tasks) and concrete CLI commands. MUST be invoked when any implementation-tier artifact (SPEC) comes up for implementation — create a tracked plan before writing code. Optional but recommended for complex SPIKEs. For coordination-tier artifacts (EPIC, VISION, JOURNEY), swain-design must decompose into implementable children first — this skill tracks the children, not the container. Also use for standalone tasks that require backend portability, persistent progress across agent runtimes, or external supervision. Use this skill whenever the user asks to track tasks, create an implementation plan, check what to work on next, see task status, manage dependencies between work items, or close/abandon tasks — even if they don't mention "execution tracking" explicitly.
license: UNLICENSED
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
metadata:
  short-description: Bootstrap and operate external task tracking
  version: 3.1.0
  author: cristos
  source: swain
---

<!-- swain-model-hint: sonnet, effort: low — default for task management; see per-section overrides below -->

# Execution Tracking

Abstraction layer for agent execution tracking. Other skills (e.g., swain-design) express intent using abstract terms; this skill translates that intent into concrete CLI commands.

**Before first use:** Read [skills/swain-do/references/tk-cheatsheet.md](skills/swain-do/references/tk-cheatsheet.md) for complete command syntax, flags, ID formats, and anti-patterns.

## Artifact handoff protocol

This skill receives handoffs from swain-design based on a four-tier tracking model:

| Tier | Artifacts | This skill's role |
|------|-----------|-------------------|
| **Implementation** | SPEC | Create a tracked implementation plan and task breakdown before any code is written |
| **Coordination** | EPIC, VISION, JOURNEY | Do not track directly — swain-design decomposes these into children first, then hands off the children |
| **Research** | SPIKE | Create a tracked plan when the research is complex enough to benefit from task breakdown |
| **Reference** | ADR, PERSONA, RUNBOOK | No tracking expected |

If invoked directly on a coordination-tier artifact (EPIC, VISION, JOURNEY) without prior decomposition, defer to swain-design to create child SPECs first, then create plans for those children.

## Term mapping

Other skills use these abstract terms. This skill maps them to the current backend (`tk`):

| Abstract term | Meaning | tk command |
|---------------|---------|------------|
| **implementation plan** | Top-level container grouping all tasks for a spec artifact | `tk create "Title" -t epic --external-ref <SPEC-ID>` |
| **task** | An individual unit of work within a plan | `tk create "Title" -t task --parent <epic-id>` |
| **origin ref** | Immutable link from a plan to the spec that seeded it | `--external-ref <ID>` flag on epic creation |
| **spec tag** | Mutable tag linking a task to every spec it affects | `--tags spec:<ID>` on create |
| **dependency** | Ordering constraint between tasks | `tk dep <child> <parent>` (child depends on parent) |
| **ready work** | Unblocked tasks available for pickup | `tk ready` |
| **claim** | Atomically take ownership of a task | `tk claim <id>` |
| **complete** | Mark a task as done | `tk add-note <id> "reason"` then `tk close <id>` |
| **abandon** | Close a task that will not be completed | `tk add-note <id> "Abandoned: <why>"` then `tk close <id>` |
| **escalate** | Abandon + invoke swain-design to update upstream artifacts | Abandon, then invoke swain-design skill |

## Configuration and bootstrap

Config stored in `.agents/execution-tracking.vars.json` (created on first run). Read [references/configuration.md](references/configuration.md) for first-run setup questions, config keys, and the 6-step bootstrap workflow.

## Statuses

tk accepts exactly three status values: `open`, `in_progress`, `closed`. Use the `status` command to set arbitrary statuses, but the dependency graph (`ready`, `blocked`) only evaluates these three.

To express abandonment, use `tk add-note <id> "Abandoned: ..."` then `tk close <id>` — see [Escalation](#escalation).

## Operating rules

1. **Always include `--description`** (or `-d`) when creating issues — a title alone loses the "why" behind a task. Future agents (or your future self) picking up this work need enough context to act without re-researching.
2. Create/update tasks at the start of work, after each major milestone, and before final response — this keeps the tracker useful as a live dashboard rather than a post-hoc record.
3. Keep task titles short and action-oriented — they appear in `tk ready` output, tree views, and notifications where space is limited.
4. Store handoff notes using `tk add-note <id> "context"` rather than ephemeral chat context — chat history is lost between sessions, but task notes persist and are visible to any agent or observer.
5. Include references to related artifact IDs in tags (e.g., `spec:SPEC-003`) — this enables querying all work touching a given spec.
6. **Prefix abandonment reasons with `Abandoned:`** when closing incomplete tasks — this convention makes abandoned work findable so nothing silently disappears.
7. **Use `ticket-query` for structured output** — when you need JSON for programmatic use, pipe through `ticket-query` (available in the vendored `bin/` directory) instead of parsing human-readable output. Example: `ticket-query '.status == "open"'`

<!-- swain-model-hint: opus, effort: high — plan creation and code implementation require deep reasoning -->
## TDD enforcement

Strict RED-GREEN-REFACTOR with anti-rationalization safeguards and completion verification. Read [references/tdd-enforcement.md](references/tdd-enforcement.md) for the anti-rationalization table, task ordering rules, and evidence requirements.

## Spec lineage tagging

Use `--external-ref SPEC-NNN` on plan epics (immutable origin) and `--tags spec:SPEC-NNN` on child tasks (mutable). Query: `ticket-query '.tags and (.tags | contains("spec:SPEC-003"))'`. Cross-plan links: `tk link <task-a> <task-b>`.

## Escalation

When work cannot proceed as designed, abandon tasks and escalate to swain-design. Read [references/escalation.md](references/escalation.md) for the triage table, abandonment commands, escalation workflow, and cross-spec handling.

## "What's next?" flow

Run `tk ready` for unblocked tasks and `ticket-query '.status == "in_progress"'` for in-flight work. If `.tickets/` is empty or missing, defer to `bash skills/swain-design/scripts/chart.sh ready` for artifact-level guidance.

## Context on claim

When claiming a task tagged with `spec:<ID>`, show the Vision ancestry breadcrumb to provide strategic context. Run `bash skills/swain-design/scripts/chart.sh scope <SPEC-ID> 2>/dev/null | head -5` to display the parent chain. This tells the agent/operator how the current task connects to project strategy.

## Artifact/tk reconciliation

When specwatch detects mismatches (`TK_SYNC`, `TK_ORPHAN` in `.agents/specwatch.log`), read [references/reconciliation.md](references/reconciliation.md) for the mismatch types, resolution commands, and reconciliation workflow.

## Session bookmark

After state-changing operations, update the bookmark: `bash "$(find . .claude .agents -path '*/swain-session/scripts/swain-bookmark.sh' -print -quit 2>/dev/null)" "<action> <task-description>"`

## Superpowers skill chaining

When superpowers is installed, swain-do **must** invoke these skills at the right moments — do not skip them or inline the work:

1. **Before writing code for any task:** Invoke the `test-driven-development` skill. Write a failing test first (RED), then make it pass (GREEN), then refactor. This applies to every task, not just the first one.

2. **When dispatching parallel work:** Invoke `subagent-driven-development` (if subagents are available and tasks are independent) or `executing-plans` (if serial). Read [references/execution-strategy.md](references/execution-strategy.md) for the decision tree.

3. **Before claiming any task or plan is complete:** Invoke `verification-before-completion`. Run the verification commands, read the output, and only then assert success. No completion claims without fresh evidence.

**Detection:** `ls .agents/skills/test-driven-development/SKILL.md .claude/skills/test-driven-development/SKILL.md 2>/dev/null` — if at least one path exists, superpowers is available. Cache the result for the session.

When superpowers is NOT installed, swain-do uses its built-in TDD enforcement (see [references/tdd-enforcement.md](references/tdd-enforcement.md)) and serial execution.

## Plan ingestion (superpowers integration)

When a superpowers plan file exists, use the ingestion script (`skills/swain-do/scripts/ingest-plan.py`) instead of manual task decomposition. Read [references/plan-ingestion.md](references/plan-ingestion.md) for usage, format requirements, and when NOT to use it.

## Execution strategy

Selects serial vs. subagent-driven execution based on superpowers availability and task complexity. Read [references/execution-strategy.md](references/execution-strategy.md) for the decision tree, detection commands, and worktree-artifact mapping.

## Worktree isolation preamble

Before any implementation or execution operation (plan creation, task claim, code writing, execution handoff), run this detection:

```bash
GIT_COMMON=$(git rev-parse --git-common-dir 2>/dev/null)
GIT_DIR=$(git rev-parse --git-dir 2>/dev/null)
[ "$GIT_COMMON" != "$GIT_DIR" ] && IN_WORKTREE=yes || IN_WORKTREE=no
```

**Read-only operations** (`tk ready`, `tk show`, status checks, task queries) skip this check entirely — proceed in the current context.

**If `IN_WORKTREE=yes`:** already isolated. Proceed normally.

**If `IN_WORKTREE=no`** (main worktree) and the operation is implementation or execution:

1. Detect superpowers:
   ```bash
   ls .agents/skills/using-git-worktrees/SKILL.md .claude/skills/using-git-worktrees/SKILL.md 2>/dev/null | head -1
   ```
2. If **superpowers absent** — stop. Report:
   > Worktree isolation requires the `using-git-worktrees` superpowers skill. Install superpowers first, then retry.
   Do not begin implementation work.

3. If **superpowers present** — invoke the `using-git-worktrees` skill to create a linked worktree, then hand off execution into that worktree.

4. If **worktree creation fails** — stop. Surface the error message from `using-git-worktrees` to the operator. Do not begin implementation work.

## Fallback

If `tk` cannot be found or is unavailable:

1. Log the failure reason.
2. Fall back to a neutral text task ledger (JSONL or Markdown checklist) in the working directory.
3. Use the same status model (`open`, `in_progress`, `blocked`, `closed`) and keep updates externally visible.
