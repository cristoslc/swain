---
id: swa-sc1g
status: open
deps: [swa-oeae]
links: []
created: 2026-03-20T00:42:37Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-kd71
tags: [spec:SPEC-091]
---
# Task 10: Update rebuild-index.sh

**Files:**
- Modify: `.claude/skills/swain-design/scripts/rebuild-index.sh:27-37`

- [ ] **Step 1: Add `train` type mapping**

After the `journey)` line (line ~36), before the `*)` catch-all, add:

```bash
    train)    title="Training Documents" ;;
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/swain-design/scripts/rebuild-index.sh
git commit -m "feat: add train type mapping to rebuild-index.sh"
```

