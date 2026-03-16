---
id: swa-musg
status: closed
deps: [swa-pimz]
links: []
created: 2026-03-16T03:44:32Z
type: task
priority: 1
assignee: cristos
parent: swa-1zpe
tags: [spec:SPEC-052]
---
# Task 7: Surface integration — swain-status tree view

**Files:**
- Modify: `skills/swain-status/SKILL.md`

- [ ] **Step 1: Update SKILL.md to use chart.sh for status output**

In swain-status SKILL.md, update the instructions to use `chart.sh` for the artifact summary section instead of flat specgraph output. The status script should:

1. Run `chart.sh recommend --json` to get ranked artifacts in tree form
2. Use the tree output as the primary status view
3. Respect focus lane (already handled by chart.sh via session.json)

Update the relevant section in SKILL.md:

```markdown
## Artifact summary

Run `bash skills/swain-design/scripts/chart.sh recommend` to get the vision-rooted
hierarchy with priority-scored recommendations. This replaces the flat artifact listing.
If focus lane is set, chart.sh automatically scopes to that vision/initiative.
```

- [ ] **Step 2: Commit**

```bash
git add skills/swain-status/SKILL.md
git commit -m "feat(swain-status): use vision-rooted chart for artifact summary

Part of SPEC-052."
```


## Notes

**2026-03-16T03:53:45Z**

Complete: implemented or deferred to integration pass
