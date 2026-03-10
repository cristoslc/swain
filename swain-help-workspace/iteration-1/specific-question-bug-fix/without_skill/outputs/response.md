# How to File a Bug and Track the Fix

Filing a bug and tracking the fix in swain is a two-skill workflow: **swain-design** handles the artifact (the bug report itself), and **swain-do** handles the execution tracking (the tasks to fix it).

## Step 1: File the Bug

Use a natural-language prompt routed through swain:

```
/swain file a bug: login fails when password contains special characters
```

This invokes **swain-design**, which:

1. Scans `docs/bug/` to assign the next available number (e.g., BUG-001).
2. Creates the bug file at `docs/bug/Reported/(BUG-001)-Login-Fails-Special-Characters.md`.
3. Populates frontmatter fields -- severity, affected-artifacts, discovered-in -- and sets `swain-do: required`.
4. Fills in the template sections: Description, Reproduction Steps, Expected Behavior, Actual Behavior, and Impact.
5. Runs post-creation validation (`specwatch.sh scan`, `adr-check.sh`) and updates the index (`docs/bug/list-bug.md`).

The bug starts in the **Reported** phase.

### Bug lifecycle phases

```
Reported --> Active --> Fixed --> Verified --> [done]
                                   \--> Declined / Abandoned (from any phase)
```

## Step 2: Plan the Fix (Reported --> Active)

When you are ready to work on the bug, tell swain:

```
/swain fix BUG-001
```

This triggers two things:

1. **swain-design** transitions the bug from Reported to Active (moving the file from `docs/bug/Reported/` to `docs/bug/Active/` via `git mv`).
2. **swain-do** creates a tracked implementation plan in bd (beads), because the bug's frontmatter contains `swain-do: required`.

The first task in the plan should be a **failing regression test** that reproduces the bug -- this is a swain convention that anchors the fix to observable behavior and prevents regressions.

A typical plan might look like:

```bash
# swain-do creates the plan epic
bd create "Fix BUG-001: login special chars" -t epic --external-ref BUG-001 --json

# Then creates child tasks
bd create "Write failing regression test" -t task --parent <epic-id> --labels spec:BUG-001 --json
bd create "Fix password encoding in auth handler" -t task --parent <epic-id> --labels spec:BUG-001 --json
bd create "Verify fix and update docs" -t task --parent <epic-id> --labels spec:BUG-001 --json
```

The bug's `fix-ref` frontmatter field is updated to point to the bd plan/epic ID, creating a bidirectional link between the artifact and the tracked work.

## Step 3: Work the Fix

Use swain-do to see what to work on:

```
/swain what should I work on next?
```

This runs `bd ready --json` to show the next unblocked task. Then:

- **Claim** a task: `bd update <id> --claim --json`
- **Do the work** (write the test, write the fix, etc.)
- **Complete** the task: `bd close <id> --reason "Regression test passing" --json`
- Repeat until all tasks are done.

## Step 4: Mark as Fixed (Active --> Fixed)

Once all tasks in the plan are closed:

```
/swain transition BUG-001 to Fixed
```

swain-design moves the file from `docs/bug/Active/` to `docs/bug/Fixed/`, updates the lifecycle table, and runs validation.

## Step 5: Verify (Fixed --> Verified)

After confirming the fix works (e.g., in staging, via manual testing, or through CI):

```
/swain transition BUG-001 to Verified
```

This is the terminal success state. The bug is resolved.

## Step 6: Commit

```
/swain push
```

## Quick Summary

| Step | Command | Skill |
|------|---------|-------|
| File the bug | `/swain file a bug: <description>` | swain-design |
| Start work | `/swain fix BUG-NNN` | swain-design + swain-do |
| See next task | `/swain what should I work on?` | swain-do |
| Mark fixed | `/swain transition BUG-NNN to Fixed` | swain-design |
| Verify fix | `/swain transition BUG-NNN to Verified` | swain-design |
| Commit | `/swain push` | swain-push |

## Other Outcomes

- **Won't fix / by design**: Transition to **Declined** from Reported or Active.
- **No longer relevant**: Transition to **Abandoned** from any phase.
- **Blocked**: If the fix cannot proceed, use swain-do's escalation protocol to abandon tasks and flow control back to swain-design for upstream changes.
