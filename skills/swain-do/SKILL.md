---
name: swain-do
description: "Task tracking and implementation execution for swain projects. Invoke whenever a SPEC needs an implementation plan, the user asks what to work on next, wants to check or update task status, claim or close tasks, manage dependencies, abandon work, bookmark context, or record a decision. Also invoked by swain-design after creating a SPEC that's ready for implementation. Tracks SPECs and SPIKEs — not EPICs, VISIONs, or JOURNEYs directly (those get decomposed into SPECs first). Triggers also on: 'bookmark', 'remember where I am', 'record decision'."
license: UNLICENSED
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
metadata:
  short-description: Task tracking, bookmarks, decisions, and progress
  version: 4.0.0
  author: cristos
  source: swain
---

<!-- swain-model-hint: sonnet, effort: low — default for task management; see per-section overrides below -->

# Execution Tracking

<!-- session-check: SPEC-121 -->
Before proceeding with any state-changing operation, check for an active session:
```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
bash "$REPO_ROOT/.agents/bin/swain-session-check.sh" 2>/dev/null
```
If the JSON output has `"status"` other than `"active"`, inform the operator: "No active session — start one with `/swain-init`?" Proceed if they dismiss.

Abstraction layer for agent execution tracking. Other skills (e.g., swain-design) express intent using abstract terms; this skill translates that intent into concrete CLI commands.

**Before first use:** Read [references/tk-cheatsheet.md](references/tk-cheatsheet.md) for complete command syntax, flags, ID formats, and anti-patterns.

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

## Ticket lifecycle (ADR-015)

Tickets are **ephemeral execution scaffolding** — they exist to help agents track and resume work during SPEC implementation. Once the parent SPEC transitions to a terminal state (Complete, Abandoned), its tickets may be discarded. Tickets are not committed to trunk, not used as retro evidence, and should not block worktree cleanup. The session log (`.agents/session.json` JSONL) is the archival record of what happened; tickets are the live dashboard of what's in progress.

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

Run `tk ready` for unblocked tasks and `ticket-query '.status == "in_progress"'` for in-flight work. If `.tickets/` is empty or missing, defer to `bash "$(git rev-parse --show-toplevel 2>/dev/null || pwd)/.agents/bin/chart.sh" ready` for artifact-level guidance.

## Context on claim

When claiming a task tagged with `spec:<ID>`, show the Vision ancestry breadcrumb to provide strategic context. Run `bash "$(git rev-parse --show-toplevel 2>/dev/null || pwd)/.agents/bin/chart.sh" scope <SPEC-ID> 2>/dev/null | head -5` to display the parent chain. This tells the agent/operator how the current task connects to project strategy.

## Artifact/tk reconciliation

When specwatch detects mismatches (`TK_SYNC`, `TK_ORPHAN` in `.agents/specwatch.log`), read [references/reconciliation.md](references/reconciliation.md) for the mismatch types, resolution commands, and reconciliation workflow.

## Session bookmark

After state-changing operations, update the bookmark: `bash "$(git rev-parse --show-toplevel 2>/dev/null || pwd)/.agents/bin/swain-bookmark.sh" "<action> <task-description>"`

## Superpowers skill chaining

When superpowers is installed, swain-do invokes these skills at specific points. Skipping them or inlining the work undermines the guarantees they provide — TDD catches regressions before they compound, and verification prevents false completion claims that waste downstream effort:

1. **Before writing code for any task:** Invoke the `test-driven-development` skill. Write a failing test first (RED), then make it pass (GREEN), then refactor. This applies to every task, not just the first one.

2. **When dispatching parallel work:** Invoke `subagent-driven-development` (if subagents are available and tasks are independent) or `executing-plans` (if serial). Read [references/execution-strategy.md](references/execution-strategy.md) for the decision tree.

3. **Before claiming any task or plan is complete:** Invoke `verification-before-completion`. Run the verification commands, read the output, and only then assert success. No completion claims without fresh evidence.

**Detection:** `ls .agents/skills/test-driven-development/SKILL.md .claude/skills/test-driven-development/SKILL.md 2>/dev/null` — if at least one path exists, superpowers is available. Cache the result for the session.

When superpowers is NOT installed, swain-do uses its built-in TDD enforcement (see [references/tdd-enforcement.md](references/tdd-enforcement.md)) and serial execution.

## Plan ingestion (superpowers integration)

When a superpowers plan file exists, use the ingestion script (`scripts/ingest-plan.py`) instead of manual task decomposition. Read [references/plan-ingestion.md](references/plan-ingestion.md) for usage, format requirements, and when NOT to use it.

## Execution strategy

Selects serial vs. subagent-driven execution based on superpowers availability and task complexity. Read [references/execution-strategy.md](references/execution-strategy.md) for the decision tree, detection commands, and worktree-artifact mapping.

## Pre-plan implementation detection

Before creating a plan for a SPEC, scan for evidence that it's already implemented. This avoids re-implementing work that exists on unmerged branches or was done in a prior session. Run these checks in parallel — they're independent signals that feed a single decision.

### Signal scan

| Signal | Check | Why it matters |
|--------|-------|----------------|
| **Unmerged branches** | `git for-each-ref --format='%(refname:short) %(upstream:trackshort)' refs/heads/ \| grep -i "<SPEC-ID>"` then verify not merged: `git merge-base --is-ancestor <branch> HEAD` | Worktree branches from prior sessions are the strongest signal — they contain commits that never reached trunk. Discovering this mid-plan-creation is disruptive; catching it here is cheap. |
| **Git history** | `git log --oneline --all \| grep -i "<SPEC-ID>"` | Commits referencing the spec ID indicate implementation happened somewhere in the repo's history. |
| **Deliverable files** | Read the spec to identify described outputs (scripts, modules, configs). Check whether they exist on HEAD via `ls` or Glob. | Files on disk without matching commits may indicate partial or uncommitted work. |
| **Tests pass** | Re-run the spec's tests now and read the output. Prior results are not evidence — only fresh execution counts. | This is the critical gate. Agents are prone to rationalizing that "tests passed before" without re-running. The reason this matters: code changes between sessions can silently break previously-passing tests. |

### Decision

- **2+ signals** → take the retroactive-close path (below)
- **1 signal** → proceed with normal plan creation; note the signal in the first task's description
- **0 signals** → proceed normally

### Retroactive-close path

When evidence confirms prior implementation, skip full task decomposition:

1. Create a single tracking task: `tk create "Retroactive verification: <SPEC-ID>" -t task --external-ref <SPEC-ID> -d "Verify prior implementation before closing SPEC."`
2. Claim it: `tk claim <id>`
3. Run `verification-before-completion` (if superpowers installed) or re-run the spec's tests manually.
4. If verification passes: add a note with the evidence, close the task, then invoke swain-design to transition the spec to Complete.
5. If verification fails: fall back to normal plan creation — the prior implementation was incomplete.

## Worktree isolation preamble

All mutating work tracked by swain-do happens in a worktree — regardless of whether it touches source code, artifacts, skill files, or data. This prevents half-finished changes from polluting trunk and avoids collisions between parallel agents. Before any operation that will produce file changes (plan creation, task claim, code writing, artifact editing, skill file changes, spec transitions, execution handoff), run this detection:

```bash
# SPEC-250: Check env var first (set by bin/swain), then git plumbing
if [ -n "${SWAIN_WORKTREE_PATH:-}" ]; then
  IN_WORKTREE=yes
else
  GIT_COMMON=$(git rev-parse --git-common-dir 2>/dev/null)
  GIT_DIR=$(git rev-parse --git-dir 2>/dev/null)
  [ "$GIT_COMMON" != "$GIT_DIR" ] && IN_WORKTREE=yes || IN_WORKTREE=no
fi
```

**Read-only operations skip this check entirely** — proceed in the current context. The explicit read-only allowlist:
- `tk ready`, `tk show`, `tk status`, `tk list`
- `ticket-query` (structured queries)
- Plan inspection (reading plan files without modifying them)
- Status checks and task queries

**If `IN_WORKTREE=yes`:** already isolated. Proceed normally.

**If `IN_WORKTREE=no`** (main worktree) and the operation will produce file changes:

1. **Commit any dirty files before the branch is cut.** A worktree checks out from HEAD — both untracked files and uncommitted modifications to tracked files are invisible inside it. This matters for artifacts created or edited moments earlier in the same session.
   ```bash
   REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
   UNTRACKED=$(git -C "$REPO_ROOT" ls-files --others --exclude-standard 2>/dev/null)
   MODIFIED=$(git -C "$REPO_ROOT" diff --name-only 2>/dev/null)
   if [ -n "$UNTRACKED" ] || [ -n "$MODIFIED" ]; then
     [ -n "$UNTRACKED" ] && echo "$UNTRACKED" | xargs -d '\n' git -C "$REPO_ROOT" add --
     [ -n "$MODIFIED" ] && echo "$MODIFIED" | xargs -d '\n' git -C "$REPO_ROOT" add --
     git -C "$REPO_ROOT" commit -m "chore: stage dirty tree before worktree creation" || {
       echo "ERROR: pre-commit step failed — aborting worktree creation"
       exit 1
     }
   fi
   ```
   If the commit fails (e.g., pre-commit hook rejection), surface the error and stop.

2. **Check for existing worktrees** matching the target spec/work:
   ```bash
   REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
   bash "$REPO_ROOT/.agents/bin/swain-worktree-overlap.sh" "<SPEC-ID>"
   ```
   If the JSON output has `"found": true`, offer to reuse: "Worktree for `<SPEC-ID>` already exists at `<path>`. Reuse it?" If yes, inform the operator to restart the session with `swain --resume <name>`. If no, inform the operator to start a new session with the purpose text.

3. **Worktree creation is handled by bin/swain pre-launch** (SPEC-245, EPIC-056). Most runtimes (Gemini CLI, Codex, Copilot, Crush) cannot change their working directory mid-session — only Claude Code can via `EnterWorktree`, and that is a runtime-specific crutch, not a universal pattern. The correct universal approach is pre-launch isolation via `bin/swain`.

   If `SWAIN_WORKTREE_PATH` is set, the agent is already in a managed worktree. If `IN_WORKTREE=yes` via git plumbing, the agent is in a worktree (possibly entered manually). In both cases, proceed with work.

   If `IN_WORKTREE=no` and the operation requires isolation, inform the operator: "Not in a worktree. Start a new session with `swain \"<purpose>\"` to get worktree isolation."

4. After entering (if worktree was just created by bin/swain), re-run tab naming to reflect the new branch:
   ```bash
   bash "$REPO_ROOT/.agents/bin/swain-tab-name.sh" --path "$(pwd)" --auto
   ```

5. **Record the worktree bookmark** (SPEC-235). After entering a worktree, call swain-bookmark.sh to register it in session.json.
   ```bash
   WT_PATH="$(pwd)"
   WT_BRANCH="$(git branch --show-current 2>/dev/null || echo 'unknown')"
   bash "$REPO_ROOT/.agents/bin/swain-bookmark.sh" worktree add "$WT_PATH" "$WT_BRANCH"
   ```

**Operator override:** If the operator explicitly says "work on trunk" or "don't isolate," respect the override and proceed on trunk. Log a warning: "Proceeding on trunk at operator request — changes will land directly on the development branch."

**Note (SPEC-195):** swain-init does not create worktrees at startup — worktree creation is deferred to this preamble, which runs when swain-do dispatches actual work. This ensures worktree names reflect the work context and allows overlap detection.

When all tasks in the plan complete, or when the operator requests, run the plan completion handoff (see below) before exiting the worktree.

## Plan completion and handoff

When all tasks under a plan epic are closed (or the operator declares the work done), execute this chain **before** exiting the worktree. This ensures retros, SPEC transitions, and EPIC cascades fire consistently.

### Step 1 — Detect plan completion

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
export PATH="$REPO_ROOT/.agents/bin:$PATH"
# Check if any tasks under the plan epic are still open
OPEN_COUNT=$(ticket-query ".parent == \"<epic-id>\" and .status != \"closed\"" 2>/dev/null | wc -l | tr -d ' ')
```

If `OPEN_COUNT > 0`, the plan is not complete — continue working or ask the operator. If `OPEN_COUNT == 0`, proceed.

### Step 2 — Run completion pipeline (SPEC-257)

After detecting plan completion, run the quality gate pipeline before transitioning the SPEC. This ensures BDD tests, smoke tests, and retro all fire automatically.

#### 2a — Create completion state file

Identify the SPEC ID from the plan epic's `--external-ref`:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SPEC_ID=$(tk show <epic-id> 2>/dev/null | grep -i 'external_ref' | awk '{print $NF}')
if [ -z "$SPEC_ID" ]; then
  echo "WARNING: No SPEC linked to plan epic — skipping completion pipeline."
fi
```

If `SPEC_ID` is empty, skip Step 2 entirely and proceed to Step 3. Log the warning.

Create the state file per DESIGN-018:

```bash
mkdir -p "$REPO_ROOT/.agents"
jq -n --arg spec "$SPEC_ID" --arg branch "$(git branch --show-current)" \
  '{spec_id: $spec, branch: $branch, pipeline_started: (now | todate), steps: {bdd_tests: {status: "pending", timestamp: null, detail: null}, smoke_test: {status: "pending", timestamp: null, detail: null}, retro: {status: "pending", timestamp: null, detail: null}}}' \
  > "$REPO_ROOT/.agents/completion-state.json.tmp" \
  && mv "$REPO_ROOT/.agents/completion-state.json.tmp" "$REPO_ROOT/.agents/completion-state.json"
```

#### 2b — Run BDD tests

Check if `swain-test.sh` is available:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SWAIN_TEST="$REPO_ROOT/.agents/bin/swain-test.sh"
```

**If `swain-test.sh` exists:** Run it once, capture output and exit code:

```bash
BDD_OUTPUT=$(bash "$SWAIN_TEST" --artifacts "$SPEC_ID" 2>&1)
BDD_EXIT=$?
```

- If exit code is 0 → update state to `passed`:
  ```bash
  BDD_DETAIL=$(echo "$BDD_OUTPUT" | head -5 | tr '\n' ' ')
  jq --arg status "passed" --arg detail "$BDD_DETAIL" \
    '.steps.bdd_tests.status = $status | .steps.bdd_tests.timestamp = (now | todate) | .steps.bdd_tests.detail = $detail' \
    "$REPO_ROOT/.agents/completion-state.json" > "$REPO_ROOT/.agents/completion-state.json.tmp" \
    && mv "$REPO_ROOT/.agents/completion-state.json.tmp" "$REPO_ROOT/.agents/completion-state.json"
  ```
- If exit code is non-zero → update state to `failed`:
  ```bash
  BDD_DETAIL=$(echo "$BDD_OUTPUT" | tail -10 | tr '\n' ' ')
  jq --arg status "failed" --arg detail "$BDD_DETAIL" \
    '.steps.bdd_tests.status = $status | .steps.bdd_tests.timestamp = (now | todate) | .steps.bdd_tests.detail = $detail' \
    "$REPO_ROOT/.agents/completion-state.json" > "$REPO_ROOT/.agents/completion-state.json.tmp" \
    && mv "$REPO_ROOT/.agents/completion-state.json.tmp" "$REPO_ROOT/.agents/completion-state.json"
  ```
  Stop the pipeline. Report the failure to the operator: "BDD tests failed. Details: {detail}. Say **retry** to re-run, or **skip BDD** to continue without."

**If `swain-test.sh` does not exist:** Warn and mark skipped:

```bash
jq --arg status "skipped" --arg detail "swain-test.sh not available" \
  '.steps.bdd_tests.status = $status | .steps.bdd_tests.timestamp = (now | todate) | .steps.bdd_tests.detail = $detail' \
  "$REPO_ROOT/.agents/completion-state.json" > "$REPO_ROOT/.agents/completion-state.json.tmp" \
  && mv "$REPO_ROOT/.agents/completion-state.json.tmp" "$REPO_ROOT/.agents/completion-state.json"
```

Display: "swain-test not available — skipping BDD gate."

#### 2c — Run smoke tests

Only proceed if `bdd_tests` is `passed` or `skipped`. If `bdd_tests` is `failed`, the pipeline is paused — do not run smoke.

```bash
BDD_STATUS=$(jq -r '.steps.bdd_tests.status' "$REPO_ROOT/.agents/completion-state.json")
```

If `BDD_STATUS` is `passed` or `skipped`:

**If `swain-test.sh` exists:** The smoke test output from `swain-test.sh` includes a `## SMOKE` section with manual verification steps. Extract and present these to the operator:

```bash
SMOKE_SECTION=$(bash "$SWAIN_TEST" --artifacts "$SPEC_ID" 2>&1 | sed -n '/^## SMOKE/,/^## /p' | head -20)
```

Present the smoke instructions and ask for confirmation:

> Smoke test instructions:
> {smoke section content}
>
> Did the smoke test pass? (yes / no / skip)

- **yes** → update `smoke_test` to `passed` with detail "operator confirmed"
- **no** → update `smoke_test` to `failed` with detail from operator. Stop pipeline: "Smoke test failed. Say **retry** to re-check, or **skip smoke** to continue."
- **skip** → update `smoke_test` to `skipped` with detail "operator chose to skip"

Use the same jq update pattern from 2b to write state.

**If `swain-test.sh` does not exist:** Mark skipped with detail "swain-test.sh not available", same as BDD fallback.

#### 2d — Run retrospective

Only proceed if both `bdd_tests` and `smoke_test` are `passed` or `skipped`. Retro **cannot be skipped** — if the operator says "skip retro", refuse: "Retro always runs. It captures learning even from imperfect work."

Invoke the swain-retro skill using the agent's Skill tool (this is a tool invocation, not a bash command):

> Use the **Skill** tool: invoke `swain-retro` with args: `"SPEC completion — run retro for <SPEC-ID> before phase transition."`

After swain-retro completes, update the state:

```bash
jq --arg status "passed" --arg detail "retro captured" \
  '.steps.retro.status = $status | .steps.retro.timestamp = (now | todate) | .steps.retro.detail = $detail' \
  "$REPO_ROOT/.agents/completion-state.json" > "$REPO_ROOT/.agents/completion-state.json.tmp" \
  && mv "$REPO_ROOT/.agents/completion-state.json.tmp" "$REPO_ROOT/.agents/completion-state.json"
```

If swain-retro fails (skill invocation error), update state to `failed` and report. The operator can say **retry** to re-run.

#### 2e — Skip and resume handling

**Skip handling:** At any point during the pipeline, the operator can say:
- "skip BDD" → set `bdd_tests` to `skipped` with detail "operator requested skip", continue to 2c
- "skip smoke" → set `smoke_test` to `skipped` with detail "operator requested skip", continue to 2d
- "skip retro" → **refuse**. Retro always runs. Say: "Retro captures learning even from imperfect work — it cannot be skipped."

**Resume handling:** If a step failed and the operator says "retry" or "continue":
1. Read `.agents/completion-state.json`
2. Find the first step with status `pending` or `failed`
3. Resume the pipeline from that step — do not re-run steps that already `passed` or were `skipped`

**Pipeline gate:** After all three steps, verify completion:

```bash
PENDING=$(jq -r '.steps | to_entries[] | select(.value.status == "pending" or .value.status == "failed") | .key' "$REPO_ROOT/.agents/completion-state.json")
```

If `PENDING` is empty (all steps `passed` or `skipped`), proceed to Step 3 (SPEC transition). If not, the pipeline is blocked — report which steps remain.

### Step 3 — Invoke swain-design for SPEC transition

**Pipeline gate (SPEC-257):** Only proceed to SPEC transition if the completion pipeline passed. Check: `jq -r '.steps | to_entries[] | select(.value.status == "pending" or .value.status == "failed") | .key' "$REPO_ROOT/.agents/completion-state.json"`. If any steps are `pending` or `failed`, do not transition — return to Step 2 to resolve.

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
- If the EPIC reaches a terminal state → invokes **swain-retro** for the EPIC-level retrospective (the SPEC-level retro already ran in Step 2d)

### Step 4 — Offer merge and cleanup

After the SPEC transition completes, offer to merge and clean up:

> All tasks closed. SPEC-NNN transitioned to {phase}. Merge this branch into {base-branch} and clean up the worktree?

If the operator accepts:
1. Ensure all changes are committed
2. Run `/swain-sync` to merge and push (marks lockfile `ready_for_cleanup`)
3. Worktree cleanup is handled by bin/swain after the runtime exits (SPEC-245)

If the operator declines, the branch is preserved. bin/swain will show it in the menu next launch.

**Note (ADR-015):** `.tickets/` files in the worktree are ephemeral scaffolding and should not block cleanup. Tickets have no archival value after SPEC completion.

### Skipping the chain

The operator can say "just exit" or "skip the handoff" to bypass Steps 2–4 and go directly to `ExitWorktree`. Log a note on the plan epic: `tk add-note <epic-id> "Exited without completion handoff"`. The worktree remains for the next session.

**Note:** Skipping the chain means the completion pipeline did not run. If `.agents/completion-state.json` was already created (Step 2a ran), any `pending` steps remain pending. swain-teardown will detect this and invoke the missing steps before sync.

## Bookmark management (ADR-023)

Bookmarks track what the operator is working on. They persist across sessions so the next session can pick up where this one left off.

### Set bookmark

When the operator says "bookmark this", "remember where I am", or after state-changing operations:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
bash "$REPO_ROOT/.agents/bin/swain-bookmark.sh" "<context note>"
```

Infer the note from conversation context or the operator's explicit text. Do not prompt for a note if the context is clear.

### Worktree bookmarks

When entering a worktree (already handled in the worktree isolation preamble, Step 5), the worktree is registered:

```bash
bash "$REPO_ROOT/.agents/bin/swain-bookmark.sh" worktree add "$WT_PATH" "$WT_BRANCH"
```

### Clear bookmark

When the operator says "clear bookmark" or "fresh start":

```bash
bash "$REPO_ROOT/.agents/bin/swain-bookmark.sh" --clear
```

## Decision recording (ADR-023)

When the operator or agent makes a significant decision (approves a spec, chooses an approach, sets direction), record it:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
bash "$REPO_ROOT/.agents/bin/swain-session-state.sh" record-decision --note "Approved SPEC-119 implementation approach"
```

Decisions are tracked against the session's decision budget. When the budget is reached, inform the operator and suggest running `/swain-teardown`.

## Progress log (ADR-023)

After completing tasks or reaching milestones, update the progress log:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
bash "$REPO_ROOT/.agents/bin/swain-progress-log.sh" --digest "$REPO_ROOT/.agents/session-log.jsonl"
```

This updates each touched EPIC/Initiative's `progress.md` and `## Progress` section.

## Fallback

If `tk` cannot be found or is unavailable:

1. Log the failure reason.
2. Fall back to a neutral text task ledger (JSONL or Markdown checklist) in the working directory.
3. Use the same status model (`open`, `in_progress`, `blocked`, `closed`) and keep updates externally visible.
