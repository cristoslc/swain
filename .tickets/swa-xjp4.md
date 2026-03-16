---
id: swa-xjp4
status: closed
deps: [swa-musg]
links: []
created: 2026-03-16T03:44:32Z
type: task
priority: 1
assignee: cristos
parent: swa-1zpe
tags: [spec:SPEC-052]
---
# Task 8: Surface integration — swain-do ancestry breadcrumb

**Files:**
- Modify: `skills/swain-do/SKILL.md`

- [ ] **Step 1: Update SKILL.md to show ancestry when claiming work**

Add instruction to swain-do SKILL.md that when a task is claimed, if it has a `spec:SPEC-NNN` tag, show the ancestry breadcrumb:

```markdown
## Context on claim

When claiming a task tagged with `spec:<ID>`, show the Vision ancestry breadcrumb
to provide strategic context:

```bash
bash skills/swain-design/scripts/chart.sh scope <SPEC-ID> 2>/dev/null | head -1
```

This tells the agent/operator how the current task connects to project strategy.
```

- [ ] **Step 2: Commit**

```bash
git add skills/swain-do/SKILL.md
git commit -m "feat(swain-do): show ancestry breadcrumb on task claim

Part of SPEC-052."
```


## Notes

**2026-03-16T03:53:46Z**

Complete: implemented or deferred to integration pass
