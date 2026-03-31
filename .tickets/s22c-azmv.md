---
id: s22c-azmv
status: closed
deps: []
links: []
created: 2026-03-31T03:21:00Z
type: task
priority: 1
assignee: cristos
parent: s22c-33it
tags: [spec:SPEC-194]
---
# Task 1: Create test fixtures

**Files:**
- Create: `skills/swain-design/tests/fixtures/readability-pass.md`
- Create: `skills/swain-design/tests/fixtures/readability-fail.md`
- Create: `skills/swain-design/tests/fixtures/readability-skip.md`
- Create: `skills/swain-design/tests/fixtures/readability-mixed-content.md`

- [ ] **Step 1: Create a passing fixture (grade <= 9)**

```markdown
---
title: "Simple Spec"
artifact: SPEC-999
status: closed
---

# Simple Spec

## Problem

The cat sat on the mat. The dog ran in the park. Birds fly in the sky.
We need a tool that checks how hard text is to read. The tool scores each
file. If the score is too high, the writer makes the text simpler.
Short words help. Short sentences help more. Active voice is best.
The reader should not need a dictionary. Clear writing saves time for
everyone who reads it. We want all docs to be easy to read.
```

- [ ] **Step 2: Create a failing fixture (grade > 9)**

```markdown
---
title: "Complex Spec"
artifact: SPEC-998
status: closed
---

# Complex Spec

## Problem

The implementation necessitates a comprehensive understanding of the
multifaceted architectural considerations that fundamentally underpin
the sophisticated infrastructure requirements. Furthermore, the
systematization of the organizational methodology requires an
extraordinarily meticulous examination of the interdependent
subsystem configurations and their corresponding operational
characteristics within the broader ecosystem of enterprise-grade
distributed computational frameworks and paradigms.
```

- [ ] **Step 3: Create a skip fixture (< 50 words after stripping)**

```markdown
---
title: "Tiny ADR"
artifact: ADR-999
status: closed
---

# Tiny ADR

## Decision

Use PostgreSQL.
```

- [ ] **Step 4: Create a mixed-content fixture (frontmatter, code, tables, prose)**

This file tests that stripping works correctly — the prose itself is simple but the file contains complex non-prose content.

```markdown
---
title: "Mixed Content Spec"
artifact: SPEC-997
status: closed
parent-initiative: INITIATIVE-019
linked-artifacts:
  - EPIC-042
  - ADR-015
---

# Mixed Content Spec

## Problem

The tool must strip code and tables before scoring. Only prose should count.

## External Behavior

```python
def extraordinarily_complex_implementation_methodology():
    systematization = "multifaceted_architectural_considerations"
    return comprehensively_evaluate_interdependent_subsystems(systematization)
```

| Column With Extraordinarily Long Multisyllabic Header | Another Disproportionately Verbose Column |
|-------------------------------------------------------|------------------------------------------|
| extraordinarily_complex_value | systematization_methodology |

## Scope

The tool reads files and scores the prose. It strips out code blocks,
tables, frontmatter, and inline code like `extraordinarily_complex_method()`.
It also strips URLs like https://extraordinarily-complex-url.example.com/path
and images like ![extraordinarily complex](./image.png).

Simple prose is what remains. The tool scores only that.
```

- [ ] **Step 5: Commit fixtures**

```bash
git add skills/swain-design/tests/fixtures/readability-*.md
git commit -m "test(SPEC-194): add readability check fixtures"
```

