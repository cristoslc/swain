---
id: swa-czla
status: open
deps: [swa-bt5d]
links: []
created: 2026-03-20T00:42:37Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-kd71
tags: [spec:SPEC-091]
---
# Task 13: Update phase-transitions.md — SPEC/EPIC hooks and step 4e

**Files:**
- Modify: `.claude/skills/swain-design/references/phase-transitions.md`

- [ ] **Step 1: Extend step 4e to include TRAINs**

At step 4e (line ~20), in the instruction that says "scan for artifacts whose assumptions may be invalidated," add TRAINs to the scope. After point 2 ("Query `chart.sh scope <SPIKE-ID>` to identify sibling artifacts"), add:

```markdown
   2b. Additionally scan `docs/train/` for TRAINs whose `linked-artifacts` contain any artifact in the same parent-vision or parent-initiative scope with `rel: [documents]`.
```

And in point 3, change "For each sibling that is Complete or Active" to:

```markdown
   3. For each sibling (SPEC, EPIC, or TRAIN) that is Complete or Active, check whether any acceptance criteria, documented behavior, or training content contradict the spike's findings.
```

- [ ] **Step 2: Add SPEC completion hook**

After the existing completion rules section, add a new subsection:

```markdown
### TRAIN documentation hooks

**On SPEC completion** (`In Progress → Needs Manual Test` or `Needs Manual Test → Complete`):
1. Scan `docs/train/` for TRAINs whose enriched `linked-artifacts` contain this SPEC with `rel: [documents]`.
2. If found: surface advisory — "SPEC-NNN completed. TRAIN-NNN documents this spec — review for updates." Strong preference for updating existing TRAINs over creating new ones.
3. If not found: no action (documentation is optional per-SPEC).

**On EPIC completion** (`Active → Complete`):
1. Collect all SPECs under this EPIC.
2. Scan `docs/train/` for TRAINs documenting any of those SPECs.
3. If TRAINs found: surface advisory — "EPIC-NNN completed. TRAIN-NNN documents features from this epic — review for updates."
4. If no TRAINs found: surface suggestion — "EPIC-NNN completed with no linked TRAIN artifacts. Consider documenting: [epic title]."
5. The agent/subagent/MCP tool drafts the TRAIN; the operator reviews.
```

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/swain-design/references/phase-transitions.md
git commit -m "feat: add TRAIN hooks to phase transitions (SPEC/EPIC completion, step 4e)"
```

---

## Chunk 6: End-to-End Verification

