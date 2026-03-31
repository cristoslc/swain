---
id: s22c-eoqh
status: closed
deps: [s22c-bpzc, s22c-qd0h]
links: []
created: 2026-03-31T03:21:01Z
type: task
priority: 1
assignee: cristos
parent: s22c-33it
tags: [spec:SPEC-194]
---
# Task 7: Final integration test

- [ ] **Step 1: Run readability-check.sh against the SPEC itself**

```bash
bash .agents/bin/readability-check.sh "docs/spec/Active/(SPEC-194)-Flesch-Kincaid-Readability-Enforcement/(SPEC-194)-Flesch-Kincaid-Readability-Enforcement.md"
```

This is a real-world test — if the SPEC itself fails readability, fix it.

- [ ] **Step 2: Run readability-check.sh against a few existing artifacts**

```bash
bash .agents/bin/readability-check.sh docs/spec/Active/*/SPEC-*.md 2>/dev/null | head -20
```

This is informational only — we are not retroactively fixing existing artifacts. But it gives a sense of the baseline.

- [ ] **Step 3: Run the full test suite**

```bash
bash skills/swain-design/tests/test-readability-check.sh
```

Expected: All PASS.

- [ ] **Step 4: Final commit if any fixes were needed**

```bash
git add -A
git commit -m "fix(SPEC-194): readability fixes from integration test"
```

Only if changes were made in steps 1-2.

