# Epics Without Parent-Initiative — Guided Migration

**When the operator asks to run the migration** (or says "how do I fix the initiative migration?"), guide them through these steps:

## Step 1: Scan and group

Run the scan helper to list all epics without `parent-initiative`, grouped by `parent-vision`:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SCAN_SCRIPT="$(find "$REPO_ROOT" -path '*/swain-doctor/scripts/swain-initiative-scan.sh' -print -quit 2>/dev/null)"
[ -n "$SCAN_SCRIPT" ] && bash "$SCAN_SCRIPT" || echo "swain-initiative-scan.sh not found"
```

Analyze the output and propose initiative clusters. For example:

> "Under VISION-001, you have 8 epics. I'd suggest grouping them into 2-3 initiatives based on theme:
> - **Security Hardening**: EPIC-017, EPIC-023 (both security-related)
> - **Developer Experience**: EPIC-016, EPIC-019, EPIC-022 (workflow improvements)
> - **Product Design**: EPIC-021 (standalone strategic bet)
>
> Does this grouping work, or would you like to adjust?"

Proposals are suggestions, not commitments. Base clustering on epic titles, descriptions, and shared themes visible in the scan output.

## Step 2: Operator decides

The operator approves, adjusts, or rejects each proposed cluster. This is a vision-mode decision — don't rush it. Present one vision's worth of clusters at a time if there are many.

## Step 3: Create initiatives

For each approved cluster, invoke swain-design to create an Initiative artifact:

- Set `parent-vision` to the vision these epics belong to
- Set `priority-weight` if the operator specifies one (otherwise omit — it inherits from the vision)
- List the child epics in the "Child Epics" section of the initiative document

## Step 4: Re-parent epics

For each epic in an approved cluster, add `parent-initiative: INITIATIVE-NNN` to its frontmatter. During the migration period, `parent-vision` can remain alongside `parent-initiative` — specgraph accepts both and resolves the vision ancestor through whichever path exists.

```yaml
# Before
parent-vision: VISION-001

# After (during migration — both fields coexist)
parent-vision: VISION-001
parent-initiative: INITIATIVE-001
```

## Step 5: Set vision weights

Prompt the operator to set `priority-weight` on their visions if not already set:

```yaml
priority-weight: high    # active strategic focus
priority-weight: medium  # maintained, progressing (default if omitted)
priority-weight: low     # parked, not abandoned
```

They can defer — everything defaults to `medium` and the system works without weights.

## Step 6: Verify

Run specgraph to verify the new hierarchy looks correct:

```bash
bash "$(find "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" -path '*/swain-design/scripts/chart.sh' -print -quit 2>/dev/null)"
bash "$(find "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" -path '*/swain-design/scripts/chart.sh' -print -quit 2>/dev/null)" recommend
```

Check that initiatives appear in the tree and that recommendations reflect the new structure.

**Migration is incremental.** The operator can migrate one vision's epics at a time. Unmigrated epics continue to work — they just show this advisory on each session start.
