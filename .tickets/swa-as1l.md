---
id: swa-as1l
status: open
deps: [swa-1u67]
links: []
created: 2026-03-20T00:42:36Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-kd71
tags: [spec:SPEC-091]
---
# Task 4: Update relationship-model.md

**Files:**
- Modify: `.claude/skills/swain-design/references/relationship-model.md:3-37`

- [ ] **Step 1: Add TRAIN entity to the ER diagram**

In the Mermaid ER diagram (lines 3-25), add the TRAIN entity and its relationships:

```mermaid
    TRAIN }o--o| EPIC : "parent-epic"
    TRAIN }o--o| INITIATIVE : "parent-initiative"
    TRAIN }o--o{ SPEC : "documents (enriched)"
    TRAIN }o--o{ RUNBOOK : "documents (enriched)"
    TRAIN }o--o{ EPIC : "documents (enriched)"
```

- [ ] **Step 2: Add `documents` rel type to the relationship vocabulary**

After the existing cross-reference notes (line ~37), add a new section:

```markdown
## Enriched `linked-artifacts` format

Entries in `linked-artifacts` can be plain strings (backward compatible) or objects with explicit relationship type and optional commit pinning:

\`\`\`yaml
linked-artifacts:
  - artifact: SPEC-067
    rel: [documents]
    commit: abc1234
    verified: 2026-03-19
  - DESIGN-003              # plain string = rel: linked (default)
\`\`\`

### Relationship vocabulary

| rel | Semantics | Commit-pinnable? | Currently modeled as |
|---|---|---|---|
| `linked` | Informational cross-reference (default) | no | `linked-artifacts` (plain string) |
| `depends-on` | Blocking. Gates readiness. | no | `depends-on-artifacts` field |
| `addresses` | Traceability. Resolves a pain point. | no | `addresses` field |
| `validates` | Operational. Verifies artifact works. | no | `validates` field |
| `documents` | Content dependency. Teaches humans about this artifact. | **yes** | new (TRAIN) |

An entry can carry multiple rels (e.g., `rel: [documents, depends-on]`).

**Design bet:** The enriched format is experimental. If it proves unwieldy, fall back to a separate `dependencies` field. The commit-pinning mechanism works either way.
```

- [ ] **Step 3: Add TRAIN to the type/track table**

Add a row to the type table:

```markdown
| TRAIN | standing | Proposed → Active → Retired/Superseded | Training document for product users |
```

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/swain-design/references/relationship-model.md
git commit -m "docs: add TRAIN and documents rel type to relationship model"
```

---

## Chunk 2: Enriched `linked-artifacts` Parser

