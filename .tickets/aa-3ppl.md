---
id: aa-3ppl
status: closed
deps: []
links: []
created: 2026-03-17T17:12:31Z
type: task
priority: 1
assignee: cristos
tags: [spec:SPEC-058]
---
# RED — Tests for categories A-D (instruction override, role hijacking, privilege escalation, exfiltration)

Write pytest tests for context file scanner categories A (instruction override), B (role override), C (privilege escalation), D (data exfiltration). Tests should import from context_file_scanner and verify pattern detection. SPEC-058.


## Notes

**2026-03-17T17:14:07Z**

RED complete: 51 tests fail (A-D detection + schema), 8 pass (benign/negative). Tests written for categories A (14 tests), B (12 tests), C (13 tests), D (12 tests), plus schema validation (7 tests).
