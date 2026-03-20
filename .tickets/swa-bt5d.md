---
id: swa-bt5d
status: open
deps: [swa-rh19]
links: []
created: 2026-03-20T00:42:37Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-kd71
tags: [spec:SPEC-091]
---
# Task 12: Update swain-sync SKILL.md (was Task 11)

**Files:**
- Modify: `.claude/skills/swain-sync/SKILL.md:151` (ADR compliance path list)
- Modify: `.claude/skills/swain-sync/SKILL.md:283` (rebuild-index type loop)

- [ ] **Step 1: Add `docs/train/` to ADR compliance path list**

At line ~151, add `docs/train/` to the comma-separated path list.

- [ ] **Step 2: Add `train` to rebuild-index type loop**

At line ~283, change:

```bash
for type in spec epic spike adr persona runbook design vision journey; do
```

to:

```bash
for type in spec epic spike adr persona runbook design vision journey train; do
```

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/swain-sync/SKILL.md
git commit -m "feat: add train to swain-sync index rebuild and ADR compliance paths"
```

---

## Chunk 5: Phase Transition Hooks

