# Escalation

When work cannot proceed as designed, use this protocol to abandon tasks and flow control back to swain-design for upstream changes before re-planning.

## Triage table

| Scope | Situation | Action |
|-------|-----------|--------|
| Single task | Alternative approach exists | Abandon task, create replacement under same plan |
| Single task | Spec assumption is wrong | Abandon task, invoke swain-design to update SPEC, create replacement task |
| Multiple tasks | Direction change needed | Abandon affected tasks, create ADR + update SPEC via swain-design, seed new tasks |
| Entire plan | Fundamental rethink required | Abandon all tasks, abandon SPEC (and possibly EPIC) via swain-design, create new SPEC if needed |

## Abandoning tasks

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

## Escalation workflow

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

## Cross-spec escalation

When abandoned tasks carry multiple `spec:` tags, each referenced spec may need upstream changes. Check every spec tag on the abandoned tasks and invoke swain-design for each affected spec before re-planning.

```bash
# List spec tags on a task
tk show <id>  # tags are visible in the YAML frontmatter
```
