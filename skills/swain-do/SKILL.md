---
name: swain-do
description: Bootstrap, install, and operate an external task-management CLI as the source of truth for agent execution tracking (instead of built-in todos). Provides the abstraction layer between swain-design intent (implementation plans and tasks) and concrete CLI commands. MUST be invoked when any implementation-tier artifact (SPEC, STORY, BUG) comes up for implementation — create a tracked plan before writing code. Optional but recommended for complex SPIKEs. For coordination-tier artifacts (EPIC, VISION, JOURNEY), swain-design must decompose into implementable children first — this skill tracks the children, not the container. Also use for standalone tasks that require backend portability, persistent progress across agent runtimes, or external supervision. Use this skill whenever the user asks to track tasks, create an implementation plan, check what to work on next, see task status, manage dependencies between work items, or close/abandon tasks — even if they don't mention "execution tracking" explicitly.
license: UNLICENSED
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
metadata:
  short-description: Bootstrap and operate external task tracking
  version: 3.0.0
  author: cristos
  source: swain
---

# Execution Tracking

Abstraction layer for agent execution tracking. Other skills (e.g., swain-design) express intent using abstract terms; this skill translates that intent into concrete CLI commands.

**Before first use:** Read [references/tk-cheatsheet.md](references/tk-cheatsheet.md) for complete command syntax, flags, ID formats, and anti-patterns.

## Artifact handoff protocol

This skill receives handoffs from swain-design based on a four-tier tracking model:

| Tier | Artifacts | This skill's role |
|------|-----------|-------------------|
| **Implementation** | SPEC, STORY, BUG | Create a tracked implementation plan and task breakdown before any code is written |
| **Coordination** | EPIC, VISION, JOURNEY | Do not track directly — swain-design decomposes these into children first, then hands off the children |
| **Research** | SPIKE | Create a tracked plan when the research is complex enough to benefit from task breakdown |
| **Reference** | ADR, PERSONA, RUNBOOK | No tracking expected |

If invoked directly on a coordination-tier artifact (EPIC, VISION, JOURNEY) without prior decomposition, defer to swain-design to create child SPECs or STORYs first, then create plans for those children.

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

## Configuration

The skill stores persistent project-level configuration in `.agents/execution-tracking.vars.json`. This file is created on first run and checked on every subsequent invocation.

### First-run setup

If `.agents/execution-tracking.vars.json` does not exist, create it by asking the user the questions below (use sensible defaults if the user says "just use defaults"):

| Key | Type | Default | Question |
|-----|------|---------|----------|
| `tk_path` | string | `"skills/swain-do/bin/tk"` | "Path to the vendored tk script (relative to project root)" |
| `fallback_format` | `"jsonl"` \| `"markdown"` | `"jsonl"` | "If tk is unavailable, use JSONL or Markdown for the fallback ledger?" |

Write the file as pretty-printed JSON:

```json
{
  "tk_path": "skills/swain-do/bin/tk",
  "fallback_format": "jsonl"
}
```

On subsequent runs, read the file and apply its values — don't re-ask.

### Applying config

- **`tk_path`**: Resolve this path relative to the project root to find the vendored tk script. Add its directory to PATH for plugin resolution.
- **`fallback_format`**: Controls the format used by the [Fallback](#fallback) section.

## Bootstrap workflow

1. **Load config:** Read `.agents/execution-tracking.vars.json`. If missing, run [first-run setup](#first-run-setup) above.
2. **Resolve tk:** The vendored tk script lives at the configured `tk_path` (default: `skills/swain-do/bin/tk`). Verify it exists and is executable.
3. **Set up PATH:** Export `PATH` with tk's directory prepended so plugins (`ticket-query`, `ticket-migrate-beads`) are found:
   ```bash
   TK_BIN="$(cd "$(dirname "$tk_path")" && pwd)"
   export PATH="$TK_BIN:$PATH"
   ```
4. **Check for existing data:** look for `.tickets/` directory.
5. **If no `.tickets/`, first use:** tk creates `.tickets/` automatically on first `tk create`.
6. **Verify:** `tk ready` should run without error.

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

## TDD enforcement

Implementation tasks follow strict RED-GREEN-REFACTOR methodology with anti-rationalization safeguards. These rules apply regardless of whether superpowers is installed — they are baked into swain-do's methodology.

### Anti-rationalization table

When creating implementation plans, every task that involves writing code must follow this discipline:

| Rationalization | Why it's wrong | Rule |
|----------------|---------------|------|
| "I'll write the test after the code since I know what I'm building" | Tests written after confirm what was built, not what was specified. They miss edge cases the spec intended. | Write the failing test FIRST. The test is derived from the acceptance criterion, not the implementation. |
| "This is too simple to need a test" | Simplicity today becomes complexity tomorrow. Untested code is unverified code. | Every behavioral change gets a test. If it's truly simple, the test is also simple. |
| "I'll refactor first to make testing easier" | Refactoring without tests means refactoring without a safety net. | RED first. Write the test against the current interface, then refactor under test coverage. |
| "The integration test covers this" | Integration tests are slow and don't isolate failures. A unit test failing tells you exactly what broke. | Unit tests for logic, integration tests for wiring. Both are needed. |
| "I need to see the implementation to know what to test" | This means the spec is unclear, not that you should skip TDD. | If you can't write the test, the acceptance criterion needs clarification — escalate to swain-design. |

### Task ordering

1. **Test first.** For each functional unit, create a test task before its implementation task. The test task writes a failing test derived from the artifact's acceptance criteria.
2. **Small cycles.** Prefer many small red-green pairs over a single "write all tests" → "write all code" split.
3. **Refactor explicitly.** Include a refactor task after green when the implementation warrants cleanup.
4. **Integration tests bookend the plan.** Start with a skeleton integration test (it will fail). The final task verifies it passes.

## Completion verification

No task may be claimed as complete without fresh verification evidence. This applies universally — not just to SPEC acceptance criteria, but to any tk task.

### What counts as evidence

| Task type | Acceptable evidence |
|-----------|-------------------|
| Code implementation | Test passes, manual verification output, screenshot |
| Documentation | Content review, link check, rendered preview |
| Configuration | Applied and tested in target environment |
| Research | Findings documented with sources |

### Enforcement

When closing a task, add a note with evidence before closing:

```bash
# Good — includes evidence
tk add-note <id> "JWT middleware added; test_jwt_validation passes"
tk close <id>

# Bad — no evidence
tk close <id>
```

If a task is closed without evidence, it should be reopened and completed properly. The verification discipline prevents "completion drift" where tasks are marked done based on intent rather than observed behavior.

## Spec lineage tagging

When creating tasks that implement a spec artifact:

```bash
# Create epic with immutable origin ref
tk create "Implement auth" -t epic --external-ref SPEC-003

# Create child tasks with spec tag
tk create "Add JWT middleware" -t task \
  --parent <epic-id> --tags spec:SPEC-003

# Query all work for a spec (via ticket-query)
ticket-query '.tags and (.tags | contains("spec:SPEC-003"))'

# Bidirectional link between tasks in different plans
tk link <task-a> <task-b>
```

## Escalation

When work cannot proceed as designed, use this protocol to abandon tasks and flow control back to swain-design for upstream changes before re-planning.

### Triage table

| Scope | Situation | Action |
|-------|-----------|--------|
| Single task | Alternative approach exists | Abandon task, create replacement under same plan |
| Single task | Spec assumption is wrong | Abandon task, invoke swain-design to update SPEC, create replacement task |
| Multiple tasks | Direction change needed | Abandon affected tasks, create ADR + update SPEC via swain-design, seed new tasks |
| Entire plan | Fundamental rethink required | Abandon all tasks, abandon SPEC (and possibly EPIC) via swain-design, create new SPEC if needed |

### Abandoning tasks

```bash
# Single task
tk add-note <id> "Abandoned: <why>"
tk close <id>

# Batch — close all open tasks under an epic (use ticket-query to find them)
for id in $(ticket-query '.parent == "<epic-id>" and .status == "open"' | jq -r '.id'); do
  tk add-note "$id" "Abandoned: <why>"
  tk close "$id"
done

# Preserve in-progress notes before closing
tk add-note <id> "Abandoning: <context about partial work>"
tk close <id>
```

### Escalation workflow

1. **Record the blocker.** Append notes to the plan epic explaining why work cannot proceed:
   ```bash
   tk add-note <epic-id> "Blocked: <description of blocker>"
   ```

2. **Invoke swain-design.** Choose the appropriate scope:
   - **Spec tweak** — update the SPEC's assumptions or requirements, then return here.
   - **Design pivot** — create an ADR documenting the decision change, update affected SPECs, then return here.
   - **Full abandon** — transition the SPEC (and possibly EPIC) to Abandoned phase via swain-design.

3. **Seed replacement plan** from the updated spec. Create a new implementation plan linked to the same (or new) SPEC via origin ref:
   ```bash
   tk create "Implement <updated approach>" -t epic --external-ref <SPEC-ID>
   ```

4. **Link lineage.** Preserve traceability between abandoned and replacement work:
   - Use the same `spec:<SPEC-ID>` tags on new tasks.
   - Reference abandoned task IDs in the new epic's notes:
     ```bash
     tk add-note <new-epic-id> "Replaces abandoned tasks: <old-id-1>, <old-id-2>"
     ```

### Cross-spec escalation

When abandoned tasks carry multiple `spec:` tags, each referenced spec may need upstream changes. Check every spec tag on the abandoned tasks and invoke swain-design for each affected spec before re-planning.

```bash
# List spec tags on a task
tk show <id>  # tags are visible in the YAML frontmatter
```

## "What's next?" flow

When asked what to work on next, show ready work from the execution backend:

```bash
# Check for tk availability and initialization
[ -d .tickets ]

# Show unblocked tasks (blocker-aware)
tk ready

# If there are in-progress tasks, show those too
ticket-query '.status == "in_progress"'
```

If `.tickets/` exists and has tasks, present the results. If `.tickets/` doesn't exist or has no tasks, report that and defer to the swain-design skill's `specgraph.sh next` for artifact-level guidance.

When invoked from the swain-design skill's combined "what's next?" flow, this skill provides the **task layer** — concrete claimable work items — complementing the spec layer's artifact-level readiness view.

## Artifact/tk reconciliation

When specwatch detects mismatches between artifact status and tk item state (via `specwatch.sh tk-sync` or `specwatch.sh scan`), this skill is responsible for cleanup. The specwatch log (`.agents/specwatch.log`) contains `TK_SYNC` and `TK_ORPHAN` entries identifying the mismatches.

### Mismatch types and resolution

| Log entry | Meaning | Resolution |
|-----------|---------|------------|
| `TK_SYNC` artifact Implemented, tk open | Spec is done but tasks linger | Close open tk items: `tk add-note <id> "Reconciled: artifact already Implemented"` then `tk close <id>` |
| `TK_SYNC` artifact Abandoned, tk open | Spec was killed but tasks linger | Abandon open tk items: `tk add-note <id> "Abandoned: parent artifact Abandoned"` then `tk close <id>` |
| `TK_SYNC` all tk closed, artifact active | All work done but spec not transitioned | Invoke swain-design to transition the artifact forward (e.g., Approved → Implemented) |
| `TK_ORPHAN` tk refs non-existent artifact | tk items reference an artifact ID not found in docs/ | Investigate: artifact may have been renamed/deleted. Close or re-tag the tk items |

### Reconciliation workflow

1. **Read the log:** `grep '^TK_SYNC\|^TK_ORPHAN' .agents/specwatch.log`
2. **For each mismatch**, apply the resolution from the table above.
3. **Re-run sync check:** `specwatch.sh tk-sync` to confirm all mismatches resolved.

### Automated invocation

Specwatch runs `tk-sync` as part of `specwatch.sh scan` and during watch-mode event processing (when tk is available). When mismatches are found, the output directs the user to invoke swain-do for reconciliation.

## Observer pattern expectations

1. Maintain compact current-status view: `tk ready` and `tk blocked`.
2. Ensure blockers are explicit: `tk blocked` shows issues with unsatisfied deps.
3. Use consistent tags so supervisors can filter by stream, owner, or phase.

## Session bookmark

After completing any state-changing operation (creating, completing, or updating tasks), update the session bookmark via `swain-bookmark.sh`:

```bash
BOOKMARK="$(find . .claude .agents -path '*/swain-session/scripts/swain-bookmark.sh' -print -quit 2>/dev/null)"
bash "$BOOKMARK" "Completed 'implement auth middleware', started 'write tests'"
```

- Note format: "{action} {task-description}"

## Plan ingestion (superpowers integration)

When a superpowers plan file exists (produced by the `writing-plans` skill), use the ingestion script instead of manually decomposing tasks. The script parses the plan's `### Task N:` blocks and registers them in tk with full spec lineage.

**Script location:** `scripts/ingest-plan.py` (relative to this skill)

### When to use

- A superpowers plan file exists at `docs/plans/YYYY-MM-DD-<name>.md`
- The plan follows the `writing-plans` format (header + `### Task N:` blocks)
- You have an origin-ref artifact ID to link the plan to

### Usage

```bash
# Parse and register in tk
uv run python3 scripts/ingest-plan.py <plan-file> <origin-ref>

# Parse only (preview without creating tk tasks)
uv run python3 scripts/ingest-plan.py <plan-file> <origin-ref> --dry-run

# With additional tags
uv run python3 scripts/ingest-plan.py <plan-file> <origin-ref> --tags epic:EPIC-009
```

### What it does

1. Parses the plan header (title, goal, architecture, tech stack)
2. Splits on `### Task N:` boundaries
3. Creates a tk epic with `--external-ref <origin-ref>`
4. Creates child tasks with `--tags spec:<origin-ref>` and full task body as description
5. Wires sequential dependencies (Task N+1 depends on Task N)

### When NOT to use

- The plan file doesn't follow superpowers format — fall back to manual task breakdown
- You need non-sequential dependencies — use the script, then adjust deps manually with `tk dep`
- The plan is very short (1-2 tasks) — manual creation is faster

## Execution strategy

When dispatching implementation work, swain-do selects the execution strategy based on environment and task characteristics.

### Strategy selection

```
superpowers installed?
├── YES → prefer subagent-driven development
│         ├── Complex task (multi-file, >5 min) → dispatch subagent with worktree
│         ├── Simple task (<5 min, single file) → serial execution (subagent overhead not worth it)
│         └── Research task → dispatch parallel investigation agents
└── NO  → tk-tracked serial execution (current default)
```

**Detection:** Check whether superpowers' execution skills exist:

```bash
ls .claude/skills/subagent-driven-development/SKILL.md .agents/skills/subagent-driven-development/SKILL.md \
   .claude/skills/using-git-worktrees/SKILL.md .agents/skills/using-git-worktrees/SKILL.md 2>/dev/null
```

If at least one path exists for each skill, subagent-driven development is available.

### Worktree-artifact mapping

When a spec is implemented via a git worktree (superpowers' `using-git-worktrees` skill), swain-do records the mapping in the tk epic's notes:

```bash
tk add-note <epic-id> "Worktree: branch <branch-name> implements <SPEC-ID>"
```

This enables:
- Status queries to show which worktrees are active for which specs
- Cleanup checks after spec completion (orphaned worktrees)
- Traceability between the spec artifact and its implementation branch

When the spec transitions to Implemented, verify the worktree has been cleaned up or merged.

## Fallback

If `tk` cannot be found or is unavailable:

1. Log the failure reason.
2. Fall back to a neutral text task ledger (JSONL or Markdown checklist) in the working directory.
3. Use the same status model (`open`, `in_progress`, `blocked`, `closed`) and keep updates externally visible.
