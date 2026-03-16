---
id: swa-7lsq
status: closed
deps: [swa-xjp4]
links: []
created: 2026-03-16T03:44:32Z
type: task
priority: 1
assignee: cristos
parent: swa-1zpe
tags: [spec:SPEC-052]
---
# Task 9: Unanchored enforcement in swain-design

**Files:**
- Modify: `skills/swain-design/SKILL.md` (or `.claude/skills/swain-design/SKILL.md`)

- [ ] **Step 1: Add creation-time warning**

In the swain-design SKILL.md, in the "Creating artifacts" section (step 7, after validating parent references), add:

```markdown
7a. **Unanchored check** — after validating parent references, check if the new artifact
has a path to a Vision via parent edges. If not, warn:
`⚠ No Vision ancestry — this artifact will appear as Unanchored`
Offer to attach to an existing Initiative or Epic. Do not block creation.
```

- [ ] **Step 2: Add audit check**

In the "Auditing artifacts" section, add unanchored detection to the audit procedure (reference `references/auditing.md`):

```markdown
Add an **unanchored check** alongside alignment and ADR compliance:
Run `bash skills/swain-design/scripts/chart.sh unanchored` and report any findings.
```

- [ ] **Step 3: Commit**

```bash
git add skills/swain-design/SKILL.md .claude/skills/swain-design/SKILL.md
git commit -m "feat(swain-design): add unanchored warnings at creation and audit

Part of SPEC-052."
```


## Notes

**2026-03-16T03:53:46Z**

Complete: implemented or deferred to integration pass
