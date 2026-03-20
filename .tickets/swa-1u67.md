---
id: swa-1u67
status: open
deps: [swa-vl4g]
links: []
created: 2026-03-20T00:42:36Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-kd71
tags: [spec:SPEC-091]
---
# Task 3: Update SKILL.md — type table and inference table

**Files:**
- Modify: `.claude/skills/swain-design/SKILL.md:23-54`

- [ ] **Step 1: Add TRAIN row to the artifact type table**

After the Design row (line ~34), add:

```markdown
| Training Document (TRAIN-NNN) | Structured product documentation — how-to guides, reference material, and quickstart tutorials for human operators. Uses the Diataxis framework. | [definition](references/train-definition.md) | [template](references/train-template.md.template) |
```

- [ ] **Step 2: Add TRAIN to the "Choosing the right artifact type" inference table**

After the ADR row in the intent table (line ~47), add:

```markdown
| Teach users how to use a feature | **TRAIN** | "document this", "write a guide", "create docs", "how-to for", "reference for", "quickstart" |
```

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/swain-design/SKILL.md
git commit -m "docs: register TRAIN in swain-design artifact type tables"
```

