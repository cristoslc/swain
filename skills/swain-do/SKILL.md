---
name: swain-do
description: Operate the external task-management CLI (tk) as source of truth for agent execution tracking. Invoke when any SPEC comes up for implementation, when the user asks to track tasks, check what to work on next, see task status, manage work dependencies, or close/abandon tasks. For coordination-tier artifacts (EPIC, VISION, JOURNEY), swain-design must decompose into child SPECs first — this skill tracks the children, not the container.
license: UNLICENSED
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, EnterWorktree, ExitWorktree
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

Run `tk ready` for unblocked tasks and `ticket-query '.status == "in_progress"'` for in-flight work. If `.tickets/` is empty or missing, defer to `bash "$(find "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" -path '*/swain-design/scripts/chart.sh' -print -quit 2>/dev/null)" ready` for artifact-level guidance.

## Context on claim

When claiming a task tagged with `spec:<ID>`, show the Vision ancestry breadcrumb to provide strategic context. Run `bash "$(find "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" -path '*/swain-design/scripts/chart.sh' -print -quit 2>/dev/null)" scope <SPEC-ID> 2>/dev/null | head -5` to display the parent chain. This tells the agent/operator how the current task connects to project strategy.

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

## Pre-plan implementation detection

Before creating a plan for a SPEC, check whether it is already implemented. Perform all three steps:

**Step 1 — Check git history for the spec ID:**
```bash
git log --oneline --all | grep -i "<SPEC-ID>"
```
Matching commits are a strong signal.

**Step 2 — Check whether deliverable files exist:**
Read the spec artifact to identify described deliverables (files, scripts, configs). Check whether those files exist using `ls` or `Glob`.

**Step 3 — Re-run tests fresh (REQUIRED if tests are mentioned in the spec):**
Do NOT trust any prior claim or cached result. Run the tests now and read the actual output. This is the critical evidence gate.

**Decision:**
- **2 or more signals confirm implementation** → offer the retroactive-close path (below)
- **1 signal** → proceed with normal plan creation; note the signal in the first task's description
- **0 signals** → proceed normally

**Retroactive-close path:**
1. Do NOT create a full task decomposition.
2. Create a single tracking task: `tk create "Retroactive verification: <SPEC-ID>" -t task --external-ref <SPEC-ID>`
3. Claim it: `tk claim <id>`
4. Run `verification-before-completion` (if superpowers installed) or re-run the spec's tests manually.
5. If verification passes: add a note with the evidence, close the task, then invoke swain-design to transition the spec to Complete.
6. If verification fails: fall back to normal plan creation — the prior implementation was incomplete.

**Anti-rationalization safeguard (CRITICAL):**
The agent MUST re-run tests during detection — it cannot assume prior passing results are current. "Tests passed before" or "I implemented this earlier" is NOT evidence. Fresh test execution output is evidence.

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

1. Use the `EnterWorktree` tool to create an isolated worktree. This is the only mechanism that actually changes the agent's working directory — manual `git worktree add` + `cd` does not persist across tool calls.

2. After entering, re-run tab naming to reflect the new branch:
   ```bash
   REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
   bash "$(find "$REPO_ROOT" -path '*/swain-session/scripts/swain-tab-name.sh' -print -quit 2>/dev/null)" --path "$(pwd)" --auto
   ```

3. If **`EnterWorktree` fails** — stop. Surface the error to the operator. Do not begin implementation work.

**Note:** swain-session auto-enters a worktree at startup (Step 1.5), so this preamble is a fallback for sessions that skipped isolation or where the operator exited the worktree mid-session.

When all tasks in the plan complete, or when the operator requests, run the plan completion handoff (see below) before exiting the worktree.

## Plan completion and handoff

When all tasks under a plan epic are closed (or the operator declares the work done), execute this chain **before** exiting the worktree. This ensures retros, SPEC transitions, and EPIC cascades fire consistently.

### Step 1 — Detect plan completion

```bash
TK_BIN="$(find "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" -path '*/swain-do/bin/tk' -print -quit 2>/dev/null | xargs dirname 2>/dev/null)"
export PATH="$TK_BIN:$PATH"
# Check if any tasks under the plan epic are still open
OPEN_COUNT=$(ticket-query ".parent == \"<epic-id>\" and .status != \"closed\"" 2>/dev/null | wc -l | tr -d ' ')
```

If `OPEN_COUNT > 0`, the plan is not complete — continue working or ask the operator. If `OPEN_COUNT == 0`, proceed.

### Step 2 — Invoke swain-design for SPEC transition

Identify the SPEC linked to the plan epic (via `--external-ref`):

```bash
tk show <epic-id> 2>/dev/null  # external_ref field contains the SPEC ID
```

Invoke **swain-design** to transition the SPEC forward. The target phase depends on the spec's current state and whether verification is complete:
- If all acceptance criteria have evidence → transition to `Complete`
- If acceptance criteria need manual verification → transition to `Needs Manual Test`
- If implementation is done but untested → transition to `In Progress` (if not already)

swain-design handles the downstream chain automatically:
- Checks whether the parent EPIC should also transition (all child SPECs complete → EPIC Complete)
- If the EPIC reaches a terminal state → invokes **swain-retro** to capture the retrospective

### Step 3 — Offer merge and cleanup

After the SPEC transition completes, offer to merge and clean up:

> All tasks closed. SPEC-NNN transitioned to {phase}. Merge this branch into {base-branch} and clean up the worktree?

If the operator accepts:
1. Ensure all changes are committed
2. Call `ExitWorktree` to return to the main checkout
3. The worktree cleanup is handled by the ExitWorktree tool

If the operator declines, call `ExitWorktree` without merging — the branch is preserved for later.

### Skipping the chain

The operator can say "just exit" or "skip the handoff" to bypass steps 2–3 and go directly to `ExitWorktree`. Log a note on the plan epic: `tk add-note <epic-id> "Exited worktree without completion handoff"`.

## Fallback

If `tk` cannot be found or is unavailable:

1. Log the failure reason.
2. Fall back to a neutral text task ledger (JSONL or Markdown checklist) in the working directory.
3. Use the same status model (`open`, `in_progress`, `blocked`, `closed`) and keep updates externally visible.
