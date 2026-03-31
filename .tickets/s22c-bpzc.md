---
id: s22c-bpzc
status: closed
deps: [s22c-ymsy]
links: []
created: 2026-03-31T03:21:01Z
type: task
priority: 1
assignee: Cristos L-C
parent: s22c-33it
tags: [spec:SPEC-194]
---
# Task 6: Propagate governance to AGENTS.md

**Files:**
- Modify: `AGENTS.md` — the reconciled governance file

- [ ] **Step 1: Add the readability section to AGENTS.md**

The same text added to AGENTS.content.md needs to appear in the live AGENTS.md between "Skill change discipline" and "Session startup". Copy the exact same paragraph.

- [ ] **Step 2: Verify both files match**

Confirm the governance block in AGENTS.md matches AGENTS.content.md (the reconciliation source of truth).

- [ ] **Step 3: Commit**

```bash
git add AGENTS.md
git commit -m "docs(SPEC-194): propagate readability rule to AGENTS.md"
```

