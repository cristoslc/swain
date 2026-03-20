---
id: swa-vl4g
status: open
deps: [swa-hjlv]
links: []
created: 2026-03-20T00:42:36Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-kd71
tags: [spec:SPEC-091]
---
# Task 2: Create train-template.md.template

**Files:**
- Create: `.claude/skills/swain-design/references/train-template.md.template`

- [ ] **Step 1: Create the template file**

Follow the Jinja2 pattern of existing templates (`runbook-template.md.template`, `design-template.md.template`). Include enriched `linked-artifacts` format:

```markdown
<!-- Jinja2 structural template — uses {{ variable }} placeholders. Read as a structural reference; no rendering pipeline needed. -->
---
title: "{{ title }}"
artifact: TRAIN-{{ number }}
track: standing
status: {{ status | default("Proposed") }}
train-type: {{ train_type | default("how-to") }}
audience: {{ audience | default("") }}
author: {{ author }}
created: {{ created_date }}
last-updated: {{ last_updated_date }}
parent-epic: {{ parent_epic | default("") }}
parent-initiative: {{ parent_initiative | default("") }}
linked-artifacts:
{%- for link in linked_artifacts | default([]) %}
  - artifact: {{ link.artifact }}
    rel: {{ link.rel | default("[linked]") }}
{%- if link.commit %}
    commit: {{ link.commit }}
    verified: {{ link.verified }}
{%- endif %}
{%- endfor %}
superseded-by: {{ superseded_by | default("") }}
---

# {{ title }}

## Prerequisites

{{ prerequisites | default("What the reader needs before starting (tools, access, prior knowledge).") }}

## Learning Objectives

{{ learning_objectives | default("What the reader will be able to do after completing this document.") }}

## Body

{{ body | default("The training content itself. Format varies by train-type:\n- how-to: numbered steps with expected outcomes\n- reference: structured lookup tables, parameter descriptions\n- quickstart: minimal steps to first success") }}

## Key Takeaways

{{ key_takeaways | default("Summary of essential points the reader should remember.") }}

## Next Steps

{{ next_steps | default("Links to related TRAINs or artifacts for further learning.") }}

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| {{ status | default("Draft") }} | {{ created_date }} | {{ commit_hash }} | Initial creation |
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/swain-design/references/train-template.md.template
git commit -m "docs: add TRAIN artifact template"
```

